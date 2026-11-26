from __future__ import annotations

import operator
import os
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import jwt
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import (
    BinaryExpression,
    BindParameter,
    BooleanClauseList,
    ColumnElement,
    Null,
)
from sqlalchemy.sql.functions import Function
from sqlalchemy.sql.schema import Column

from auth.dependencies import enforce_recommendation_approval_role
from auth.permissions import Permission, Role, has_permission
from auth.security import (
    JWT_ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from core.config import (
    AuthConfigurationError,
    get_access_token_ttl_minutes,
    get_auth_secret_key,
    get_database_url,
)
from db.models import AuditLog, Customer, Tenant, User
from db.session import get_db
from db.tenant_access import TenantContext, TenantScopedDataAccess
from main import app

BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_CONFIG = BACKEND_DIR / "alembic.ini"
TEST_SECRET = "synthetic-test-secret-key-at-least-32-bytes-long"


class _ScalarResult:
    def __init__(self, rows: list[Any]) -> None:
        self._rows = rows

    def all(self) -> list[Any]:
        return list(self._rows)


class _ExecuteResult:
    def __init__(self, rowcount: int) -> None:
        self.rowcount = rowcount


class InMemorySession:
    """Minimal SQLAlchemy Session double evaluating real TenantScopedDataAccess clauses."""

    def __init__(self) -> None:
        self.tables: dict[type[Any], list[Any]] = {
            Tenant: [],
            User: [],
            Customer: [],
            AuditLog: [],
        }

    def add(self, record: Any) -> None:
        if isinstance(record, User):
            for existing in self.tables[User]:
                if (
                    existing.tenant_id == record.tenant_id
                    and existing.email.lower() == record.email.lower()
                ):
                    raise IntegrityError(
                        "INSERT INTO users",
                        {},
                        Exception("uq_users_tenant_lower_email"),
                    )
        if getattr(record, "id", None) is None:
            record.id = uuid4()
        if (
            hasattr(record, "created_at")
            and getattr(record, "created_at", None) is None
        ):
            record.created_at = datetime.now(timezone.utc)
        self.tables.setdefault(type(record), []).append(record)

    def flush(self) -> None:
        return None

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def refresh(self, _record: Any) -> None:
        return None

    def close(self) -> None:
        return None

    def scalar(self, statement: Any) -> Any | None:
        rows = self._select_rows(statement)
        return rows[0] if rows else None

    def scalars(self, statement: Any) -> _ScalarResult:
        return _ScalarResult(self._select_rows(statement))

    def execute(self, statement: Any) -> _ExecuteResult:
        table = statement.table
        model = self._model_for_table_name(table.name)
        rows = self.tables.get(model, [])
        whereclause = getattr(statement, "whereclause", None)
        matched = [
            row
            for row in rows
            if whereclause is None or self._eval_expr(whereclause, row)
        ]
        values = {
            key.key if hasattr(key, "key") else str(key): self._eval_expr(val, None)
            for key, val in statement._values.items()
        }
        for row in matched:
            if model is User and "email" in values:
                new_email = str(values["email"]).lower()
                for existing in rows:
                    if (
                        existing.id != row.id
                        and existing.tenant_id == row.tenant_id
                        and existing.email.lower() == new_email
                    ):
                        raise IntegrityError(
                            "UPDATE users",
                            {},
                            Exception("uq_users_tenant_lower_email"),
                        )
            for field_name, value in values.items():
                setattr(row, field_name, value)
        return _ExecuteResult(len(matched))

    def _model_for_table_name(self, name: str) -> type[Any]:
        for model in self.tables:
            if model.__tablename__ == name:
                return model
        raise KeyError(f"Unsupported model table: {name}")

    def _select_rows(self, statement: Any) -> list[Any]:
        entity = statement.column_descriptions[0]["entity"]
        rows = self.tables.get(entity, [])
        whereclause = getattr(statement, "whereclause", None)
        if whereclause is None:
            return list(rows)
        return [row for row in rows if self._eval_expr(whereclause, row)]

    def _eval_expr(self, expr: Any, row: Any) -> Any:
        if isinstance(expr, BooleanClauseList):
            results = [bool(self._eval_expr(clause, row)) for clause in expr.clauses]
            if expr.operator is operator.and_:
                return all(results)
            if expr.operator is operator.or_:
                return any(results)
            raise NotImplementedError(f"Unsupported boolean op: {expr.operator}")

        if isinstance(expr, BinaryExpression):
            left = self._eval_expr(expr.left, row)
            right = self._eval_expr(expr.right, row)
            op = expr.operator
            if op is operator.eq or getattr(op, "__name__", "") == "is_":
                return left == right
            if op is operator.ne or getattr(op, "__name__", "") == "is_not":
                return left != right
            raise NotImplementedError(f"Unsupported binary op: {op}")

        if isinstance(expr, Function):
            if expr.name.lower() == "lower":
                args = [self._eval_expr(clause, row) for clause in expr.clauses]
                return str(args[0]).lower() if args[0] is not None else None
            raise NotImplementedError(f"Unsupported SQL function: {expr.name}")

        if isinstance(expr, Column):
            return getattr(row, expr.key)

        if isinstance(expr, BindParameter):
            return expr.value

        if isinstance(expr, Null):
            return None

        if isinstance(expr, ColumnElement):
            raise NotImplementedError(f"Unsupported ColumnElement: {type(expr)}")

        return expr


@pytest.fixture
def env_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("APP_SECRET_KEY", TEST_SECRET)
    monkeypatch.setenv("ACCESS_TOKEN_TTL_MINUTES", "30")
    return TEST_SECRET


@pytest.fixture
def fake_db() -> InMemorySession:
    return InMemorySession()


@pytest.fixture
def client(env_secret: str, fake_db: InMemorySession) -> Iterator[TestClient]:
    def _override_get_db() -> Iterator[InMemorySession]:
        yield fake_db

    app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def _seed_two_tenants(fake_db: InMemorySession) -> dict[str, Any]:
    tenant_a = Tenant(id=uuid4(), name="Synthetic Tenant A", industry="distribution")
    tenant_b = Tenant(id=uuid4(), name="Synthetic Tenant B", industry="distribution")
    fake_db.add(tenant_a)
    fake_db.add(tenant_b)

    owner_a = User(
        id=uuid4(),
        tenant_id=tenant_a.id,
        name="Owner A",
        email="owner.a@example.synthetic",
        password_hash=hash_password("OwnerPass123!"),
        role=Role.OWNER.value,
    )
    manager_a = User(
        id=uuid4(),
        tenant_id=tenant_a.id,
        name="Manager A",
        email="manager.a@example.synthetic",
        password_hash=hash_password("ManagerPass123!"),
        role=Role.FINANCE_MANAGER.value,
    )
    collector_a1 = User(
        id=uuid4(),
        tenant_id=tenant_a.id,
        name="Collector A1",
        email="collector.a1@example.synthetic",
        password_hash=hash_password("CollectorPass123!"),
        role=Role.COLLECTOR.value,
    )
    collector_a2 = User(
        id=uuid4(),
        tenant_id=tenant_a.id,
        name="Collector A2",
        email="collector.a2@example.synthetic",
        password_hash=hash_password("CollectorPass123!"),
        role=Role.COLLECTOR.value,
    )
    owner_b = User(
        id=uuid4(),
        tenant_id=tenant_b.id,
        name="Owner B",
        email="owner.b@example.synthetic",
        password_hash=hash_password("OwnerBPass123!"),
        role=Role.OWNER.value,
    )
    for user in (owner_a, manager_a, collector_a1, collector_a2, owner_b):
        fake_db.add(user)

    cust_a1 = Customer(
        id=uuid4(),
        tenant_id=tenant_a.id,
        name="Customer A Assigned",
        phone="+20 100 000 0001",
        email="cust.a1@example.synthetic",
        credit_limit=None,
        payment_terms="Net 30",
        tier="regular",
        sales_rep=None,
        assigned_collector=collector_a1.id,
        preferred_channel="call",
        contact_person=None,
        status="active",
    )
    cust_a2 = Customer(
        id=uuid4(),
        tenant_id=tenant_a.id,
        name="Customer A Other Collector",
        phone="+20 100 000 0002",
        email="cust.a2@example.synthetic",
        credit_limit=None,
        payment_terms="Net 30",
        tier="strategic",
        sales_rep="Rep A",
        assigned_collector=collector_a2.id,
        preferred_channel="whatsapp",
        contact_person=None,
        status="active",
    )
    cust_a_unassigned = Customer(
        id=uuid4(),
        tenant_id=tenant_a.id,
        name="Customer A Unassigned",
        phone=None,
        email=None,
        credit_limit=None,
        payment_terms="Net 45",
        tier="regular",
        sales_rep=None,
        assigned_collector=None,
        preferred_channel=None,
        contact_person=None,
        status="active",
    )
    cust_b1 = Customer(
        id=uuid4(),
        tenant_id=tenant_b.id,
        name="Customer B",
        phone=None,
        email=None,
        credit_limit=None,
        payment_terms="Net 30",
        tier="regular",
        sales_rep=None,
        assigned_collector=None,
        preferred_channel=None,
        contact_person=None,
        status="active",
    )
    for customer in (cust_a1, cust_a2, cust_a_unassigned, cust_b1):
        fake_db.add(customer)

    return {
        "tenant_a": tenant_a,
        "tenant_b": tenant_b,
        "owner_a": owner_a,
        "manager_a": manager_a,
        "collector_a1": collector_a1,
        "collector_a2": collector_a2,
        "owner_b": owner_b,
        "cust_a1": cust_a1,
        "cust_a2": cust_a2,
        "cust_a_unassigned": cust_a_unassigned,
        "cust_b1": cust_b1,
    }


def _login_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_password_hashing_and_jwt_validation(env_secret: str) -> None:
    hashed = hash_password("StrongPassword123!")
    assert hashed != "StrongPassword123!"
    assert verify_password("StrongPassword123!", hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False

    user_id = uuid4()
    tenant_id = uuid4()
    token, expires_in = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        role=Role.FINANCE_MANAGER,
    )
    assert expires_in == 1800

    claims = decode_access_token(token)
    assert claims.user_id == user_id
    assert claims.tenant_id == tenant_id
    assert claims.role == Role.FINANCE_MANAGER

    expired_token, _ = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        role=Role.COLLECTOR,
        expires_delta=timedelta(seconds=-10),
    )
    with pytest.raises(Exception, match="Invalid or expired"):
        decode_access_token(expired_token)

    tampered = token[:-4] + ("aaaa" if not token.endswith("aaaa") else "bbbb")
    with pytest.raises(Exception, match="Invalid or expired"):
        decode_access_token(tampered)

    wrong_type = jwt.encode(
        {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "role": Role.OWNER.value,
            "type": "refresh",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        },
        env_secret,
        algorithm=JWT_ALGORITHM,
    )
    with pytest.raises(Exception, match="Invalid token type"):
        decode_access_token(wrong_type)

    wrong_secret = jwt.encode(
        {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "role": Role.OWNER.value,
            "type": "access",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        },
        "a-completely-different-32-byte-secret-key",
        algorithm=JWT_ALGORITHM,
    )
    with pytest.raises(Exception, match="Invalid or expired"):
        decode_access_token(wrong_secret)

    alg_none = jwt.encode(
        {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "role": Role.OWNER.value,
            "type": "access",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        },
        "",
        algorithm="none",
    )
    with pytest.raises(Exception, match="Invalid or expired"):
        decode_access_token(alg_none)


def test_auth_configuration_validation_and_secret_preservation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_SECRET_KEY", "too-short")
    with pytest.raises(AuthConfigurationError, match="APP_SECRET_KEY"):
        create_access_token(user_id=uuid4(), tenant_id=uuid4(), role=Role.OWNER)

    monkeypatch.setenv("APP_SECRET_KEY", " " * 40)
    with pytest.raises(AuthConfigurationError, match="empty or whitespace-only"):
        get_auth_secret_key()

    secret_with_spaces = "  preserved-secret-key-at-least-32-bytes  "
    monkeypatch.setenv("APP_SECRET_KEY", secret_with_spaces)
    assert get_auth_secret_key() == secret_with_spaces

    for bad_ttl in ("0", "-5", "not-an-int"):
        monkeypatch.setenv("ACCESS_TOKEN_TTL_MINUTES", bad_ttl)
        with pytest.raises(AuthConfigurationError, match="ACCESS_TOKEN_TTL_MINUTES"):
            get_access_token_ttl_minutes()

    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(AuthConfigurationError, match="DATABASE_URL"):
        get_database_url()


def test_login_and_me_success_and_failure_paths(
    client: TestClient, fake_db: InMemorySession
) -> None:
    data = _seed_two_tenants(fake_db)

    # Case-insensitive email login works and logs auth.login without password leakage.
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "  OWNER.A@example.synthetic ", "password": "OwnerPass123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["id"] == str(data["owner_a"].id)
    assert body["user"]["role"] == "OWNER"
    assert "password_hash" not in body["user"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "owner.a@example.synthetic"

    # Wrong password -> 401
    wrong_pw = client.post(
        "/api/v1/auth/login",
        json={"email": "owner.a@example.synthetic", "password": "WrongPassword!"},
    )
    assert wrong_pw.status_code == 401

    # Unknown email -> 401
    unknown = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.synthetic", "password": "OwnerPass123!"},
    )
    assert unknown.status_code == 401

    # Missing, non-Bearer, empty, malformed, or tampered bearer tokens -> 401
    assert client.get("/api/v1/auth/me").status_code == 401
    for bad_header in (
        "Basic dXNlcjpwYXNz",
        "Bearer ",
        "Bearer",
        "Bearer not.a.jwt",
    ):
        assert (
            client.get(
                "/api/v1/auth/me",
                headers={"Authorization": bad_header},
            ).status_code
            == 401
        )

    # Deleted / missing DB user with otherwise valid signed token -> 401
    ghost_token, _ = create_access_token(
        user_id=uuid4(),
        tenant_id=data["tenant_a"].id,
        role=Role.OWNER,
    )
    assert (
        client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {ghost_token}"},
        ).status_code
        == 401
    )


def test_login_disambiguates_same_email_across_tenants(
    client: TestClient, fake_db: InMemorySession
) -> None:
    data = _seed_two_tenants(fake_db)
    shared_email = "shared@example.synthetic"
    fake_db.add(
        User(
            id=uuid4(),
            tenant_id=data["tenant_a"].id,
            name="Shared A",
            email=shared_email,
            password_hash=hash_password("SharedSecret123!"),
            role=Role.COLLECTOR.value,
        )
    )
    fake_db.add(
        User(
            id=uuid4(),
            tenant_id=data["tenant_b"].id,
            name="Shared B",
            email=shared_email,
            password_hash=hash_password("SharedSecret123!"),
            role=Role.FINANCE_MANAGER.value,
        )
    )

    ambiguous = client.post(
        "/api/v1/auth/login",
        json={"email": shared_email, "password": "SharedSecret123!"},
    )
    assert ambiguous.status_code == 409

    scoped = client.post(
        "/api/v1/auth/login",
        json={
            "email": shared_email,
            "password": "SharedSecret123!",
            "tenant_id": str(data["tenant_b"].id),
        },
    )
    assert scoped.status_code == 200
    assert scoped.json()["user"]["tenant_id"] == str(data["tenant_b"].id)
    assert scoped.json()["user"]["role"] == "FINANCE_MANAGER"


def test_user_management_is_owner_only_and_tenant_scoped(
    client: TestClient, fake_db: InMemorySession
) -> None:
    data = _seed_two_tenants(fake_db)
    owner_headers = _login_headers(client, "owner.a@example.synthetic", "OwnerPass123!")
    manager_headers = _login_headers(
        client, "manager.a@example.synthetic", "ManagerPass123!"
    )
    collector_headers = _login_headers(
        client, "collector.a1@example.synthetic", "CollectorPass123!"
    )
    owner_b_headers = _login_headers(
        client, "owner.b@example.synthetic", "OwnerBPass123!"
    )

    # All user-management operations require authentication before role checks.
    unauthenticated_create = {
        "name": "Unauthorized User",
        "email": "unauth@example.synthetic",
        "password": "ValidPassword123!",
        "role": "COLLECTOR",
    }
    assert client.get("/api/v1/users").status_code == 401
    assert client.get(f"/api/v1/users/{data['collector_a1'].id}").status_code == 401
    assert client.post("/api/v1/users", json=unauthenticated_create).status_code == 401
    assert (
        client.patch(
            f"/api/v1/users/{data['collector_a1'].id}",
            json={"name": "Unauthorized Update"},
        ).status_code
        == 401
    )

    # Owner can list and retrieve only users in their tenant; responses omit hashes.
    owner_list = client.get("/api/v1/users", headers=owner_headers)
    assert owner_list.status_code == 200
    assert {user["id"] for user in owner_list.json()} == {
        str(data[key].id)
        for key in ("owner_a", "manager_a", "collector_a1", "collector_a2")
    }
    owner_user = client.get(
        f"/api/v1/users/{data['collector_a1'].id}", headers=owner_headers
    )
    assert owner_user.status_code == 200
    assert owner_user.json()["id"] == str(data["collector_a1"].id)
    assert "password_hash" not in owner_user.json()
    assert (
        client.get(f"/api/v1/users/{uuid4()}", headers=owner_headers).status_code == 404
    )

    # Non-owners cannot list, view, create, or update users.
    for headers in (manager_headers, collector_headers):
        assert client.get("/api/v1/users", headers=headers).status_code == 403
        assert (
            client.get(
                f"/api/v1/users/{data['collector_a1'].id}", headers=headers
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/v1/users",
                headers=headers,
                json={
                    "name": "Unauthorized User",
                    "email": "unauth@example.synthetic",
                    "password": "ValidPassword123!",
                    "role": "COLLECTOR",
                },
            ).status_code
            == 403
        )
        assert (
            client.patch(
                f"/api/v1/users/{data['collector_a1'].id}",
                headers=headers,
                json={"role": "OWNER"},
            ).status_code
            == 403
        )

    # Owner creates user in their own tenant even if client attempts to inject tenant_id.
    create_resp = client.post(
        "/api/v1/users",
        headers=owner_headers,
        json={
            "name": "New Collector",
            "email": "new.collector@example.synthetic",
            "password": "CollectorNew123!",
            "role": "COLLECTOR",
            "tenant_id": str(data["tenant_b"].id),
        },
    )
    assert create_resp.status_code == 201
    created_user = create_resp.json()
    assert created_user["tenant_id"] == str(data["tenant_a"].id)
    assert created_user["role"] == "COLLECTOR"
    assert "password_hash" not in created_user

    # Duplicate email within the same tenant is rejected.
    dup_resp = client.post(
        "/api/v1/users",
        headers=owner_headers,
        json={
            "name": "Dup Collector",
            "email": "NEW.COLLECTOR@example.synthetic",
            "password": "CollectorNew123!",
            "role": "COLLECTOR",
        },
    )
    assert dup_resp.status_code == 409

    # Weak password, whitespace-only name, empty PATCH, and unknown role are rejected.
    assert (
        client.post(
            "/api/v1/users",
            headers=owner_headers,
            json={
                "name": "Weak PW",
                "email": "weak@example.synthetic",
                "password": "short",
                "role": "COLLECTOR",
            },
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/users",
            headers=owner_headers,
            json={
                "name": "   ",
                "email": "blankname@example.synthetic",
                "password": "ValidPassword123!",
                "role": "COLLECTOR",
            },
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/users",
            headers=owner_headers,
            json={
                "name": "Bad Role",
                "email": "badrole@example.synthetic",
                "password": "ValidPassword123!",
                "role": "SUPERADMIN",
            },
        ).status_code
        == 422
    )
    assert (
        client.patch(
            f"/api/v1/users/{created_user['id']}",
            headers=owner_headers,
            json={},
        ).status_code
        == 422
    )
    assert (
        client.patch(
            f"/api/v1/users/{created_user['id']}",
            headers=owner_headers,
            json={"name": "   "},
        ).status_code
        == 422
    )

    # Updating a user's email to an existing email in the same tenant fails with 409.
    dup_patch = client.patch(
        f"/api/v1/users/{created_user['id']}",
        headers=owner_headers,
        json={"email": "MANAGER.A@example.synthetic"},
    )
    assert dup_patch.status_code == 409

    # Owner updates user role.
    patch_resp = client.patch(
        f"/api/v1/users/{created_user['id']}",
        headers=owner_headers,
        json={"role": "FINANCE_MANAGER"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["role"] == "FINANCE_MANAGER"

    # Last Owner cannot demote themselves.
    self_demote = client.patch(
        f"/api/v1/users/{data['owner_a'].id}",
        headers=owner_headers,
        json={"role": "FINANCE_MANAGER"},
    )
    assert self_demote.status_code == 409

    # Cross-tenant Owner cannot read or update Tenant A users.
    assert (
        client.get(
            f"/api/v1/users/{data['collector_a1'].id}", headers=owner_b_headers
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/users/{data['collector_a1'].id}",
            headers=owner_b_headers,
            json={"role": "OWNER"},
        ).status_code
        == 404
    )

    # Audit logs recorded without password hashes.
    user_audits = [
        entry
        for entry in fake_db.tables[AuditLog]
        if entry.action in {"user.create", "user.update"}
    ]
    assert len(user_audits) == 2
    for entry in user_audits:
        assert "password_hash" not in (entry.after or {})
        assert "password" not in (entry.after or {})


def test_auth_and_user_management_openapi_contract(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    expected_responses = {
        ("/api/v1/auth/login", "post"): {"200", "401", "409", "422", "500"},
        ("/api/v1/auth/me", "get"): {"200", "401"},
        ("/api/v1/users", "get"): {"200", "401", "403"},
        ("/api/v1/users", "post"): {"201", "401", "403", "409", "422"},
        ("/api/v1/users/{user_id}", "get"): {
            "200",
            "401",
            "403",
            "404",
            "422",
        },
        ("/api/v1/users/{user_id}", "patch"): {
            "200",
            "401",
            "403",
            "404",
            "409",
            "422",
        },
    }

    for (path, method), response_codes in expected_responses.items():
        operation = paths[path][method]
        assert set(operation["responses"]) == response_codes
        assert operation["summary"]

    assert "security" not in paths["/api/v1/auth/login"]["post"]
    for path, method in (
        ("/api/v1/auth/me", "get"),
        ("/api/v1/users", "get"),
        ("/api/v1/users", "post"),
        ("/api/v1/users/{user_id}", "get"),
        ("/api/v1/users/{user_id}", "patch"),
    ):
        assert paths[path][method]["security"] == [{"HTTPBearer": []}]

    schemas = schema["components"]["schemas"]
    assert set(schemas["UserResponse"]["properties"]) == {
        "id",
        "tenant_id",
        "name",
        "email",
        "role",
        "created_at",
    }
    assert "example" in schemas["TokenResponse"]
    assert "example" in schemas["UserCreateRequest"]
    assert schemas["ErrorResponse"]["properties"]["detail"]["type"] == "string"
    assert (
        paths["/api/v1/auth/login"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/LoginRequest"
    )
    assert (
        paths["/api/v1/users"]["post"]["requestBody"]["content"]["application/json"][
            "schema"
        ]["$ref"]
        == "#/components/schemas/UserCreateRequest"
    )
    assert (
        paths["/api/v1/users/{user_id}"]["patch"]["requestBody"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/UserUpdateRequest"
    )
    user_id_parameter = paths["/api/v1/users/{user_id}"]["get"]["parameters"][0]
    assert user_id_parameter["name"] == "user_id"
    assert user_id_parameter["required"] is True
    assert user_id_parameter["schema"]["format"] == "uuid"


def test_role_change_in_db_takes_effect_immediately_on_existing_token(
    client: TestClient, fake_db: InMemorySession
) -> None:
    data = _seed_two_tenants(fake_db)
    owner_headers = _login_headers(client, "owner.a@example.synthetic", "OwnerPass123!")
    manager_headers = _login_headers(
        client, "manager.a@example.synthetic", "ManagerPass123!"
    )

    # Manager initially sees all customers in tenant A.
    assert len(client.get("/api/v1/customers", headers=manager_headers).json()) == 3

    # Owner demotes Manager A to Collector; existing token immediately becomes Collector.
    demote = client.patch(
        f"/api/v1/users/{data['manager_a'].id}",
        headers=owner_headers,
        json={"role": "COLLECTOR"},
    )
    assert demote.status_code == 200

    assert client.get("/api/v1/customers", headers=manager_headers).json() == []
    assert (
        client.get(
            f"/api/v1/customers/{data['cust_a1'].id}", headers=manager_headers
        ).status_code
        == 403
    )


def test_collector_assigned_only_and_cross_tenant_customer_isolation(
    client: TestClient, fake_db: InMemorySession
) -> None:
    data = _seed_two_tenants(fake_db)
    owner_headers = _login_headers(client, "owner.a@example.synthetic", "OwnerPass123!")
    manager_headers = _login_headers(
        client, "manager.a@example.synthetic", "ManagerPass123!"
    )
    collector1_headers = _login_headers(
        client, "collector.a1@example.synthetic", "CollectorPass123!"
    )
    owner_b_headers = _login_headers(
        client, "owner.b@example.synthetic", "OwnerBPass123!"
    )

    # Owner and Finance Manager see all 3 Tenant A customers (never Tenant B).
    for headers in (owner_headers, manager_headers):
        listed = client.get("/api/v1/customers", headers=headers)
        assert listed.status_code == 200
        ids = {item["id"] for item in listed.json()}
        assert ids == {
            str(data["cust_a1"].id),
            str(data["cust_a2"].id),
            str(data["cust_a_unassigned"].id),
        }
        assert (
            client.get(
                f"/api/v1/customers/{data['cust_b1'].id}", headers=headers
            ).status_code
            == 404
        )

    # Collector A1 sees only cust_a1.
    c1_list = client.get("/api/v1/customers", headers=collector1_headers)
    assert c1_list.status_code == 200
    assert [item["id"] for item in c1_list.json()] == [str(data["cust_a1"].id)]

    # Collector A1 can fetch assigned customer, gets 403 on unassigned/other-collector customers,
    # and gets 404 on cross-tenant customers.
    assert (
        client.get(
            f"/api/v1/customers/{data['cust_a1'].id}", headers=collector1_headers
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/api/v1/customers/{data['cust_a2'].id}", headers=collector1_headers
        ).status_code
        == 403
    )
    assert (
        client.get(
            f"/api/v1/customers/{data['cust_a_unassigned'].id}",
            headers=collector1_headers,
        ).status_code
        == 403
    )
    assert (
        client.get(
            f"/api/v1/customers/{data['cust_b1'].id}", headers=collector1_headers
        ).status_code
        == 404
    )

    # Tenant B Owner only sees Tenant B customer.
    b_list = client.get("/api/v1/customers", headers=owner_b_headers)
    assert b_list.status_code == 200
    assert [item["id"] for item in b_list.json()] == [str(data["cust_b1"].id)]


def test_ac014_and_d15_d30_permissions_matrix(
    fake_db: InMemorySession,
) -> None:
    data = _seed_two_tenants(fake_db)
    from auth.dependencies import AuthenticatedUser

    access_a = TenantScopedDataAccess(fake_db, TenantContext(data["tenant_a"].id))
    collector = AuthenticatedUser(
        id=data["collector_a1"].id,
        tenant_id=data["tenant_a"].id,
        name=data["collector_a1"].name,
        email=data["collector_a1"].email,
        role=Role.COLLECTOR,
    )
    manager = AuthenticatedUser(
        id=data["manager_a"].id,
        tenant_id=data["tenant_a"].id,
        name=data["manager_a"].name,
        email=data["manager_a"].email,
        role=Role.FINANCE_MANAGER,
    )
    owner = AuthenticatedUser(
        id=data["owner_a"].id,
        tenant_id=data["tenant_a"].id,
        name=data["owner_a"].name,
        email=data["owner_a"].email,
        role=Role.OWNER,
    )

    # Collector can approve routine recommendation ONLY for assigned customer.
    approved_customer = enforce_recommendation_approval_role(
        access_a,
        collector,
        data["cust_a1"].id,
        requires_manager_review=False,
    )
    assert approved_customer.id == data["cust_a1"].id

    # Collector cannot approve manager-flagged recommendation even on assigned customer.
    with pytest.raises(Exception) as exc_info:
        enforce_recommendation_approval_role(
            access_a,
            collector,
            data["cust_a1"].id,
            requires_manager_review=True,
        )
    assert getattr(exc_info.value, "status_code", None) == 403

    # Collector cannot approve even routine recommendations for unassigned/other-collector customers.
    for forbidden_customer_id in (data["cust_a2"].id, data["cust_a_unassigned"].id):
        with pytest.raises(Exception) as unassigned_exc:
            enforce_recommendation_approval_role(
                access_a,
                collector,
                forbidden_customer_id,
                requires_manager_review=False,
            )
        assert getattr(unassigned_exc.value, "status_code", None) == 403

    # Cross-tenant customer returns 404 even for recommendation approval check.
    with pytest.raises(Exception) as cross_tenant_exc:
        enforce_recommendation_approval_role(
            access_a,
            owner,
            data["cust_b1"].id,
            requires_manager_review=False,
        )
    assert getattr(cross_tenant_exc.value, "status_code", None) == 404

    for privileged in (manager, owner):
        enforce_recommendation_approval_role(
            access_a,
            privileged,
            data["cust_a_unassigned"].id,
            requires_manager_review=False,
        )
        enforce_recommendation_approval_role(
            access_a,
            privileged,
            data["cust_a_unassigned"].id,
            requires_manager_review=True,
        )

    # D15 / D30 matrix assertions
    assert has_permission(Role.OWNER, Permission.MANAGE_USERS) is True
    assert has_permission(Role.FINANCE_MANAGER, Permission.MANAGE_USERS) is False
    assert has_permission(Role.COLLECTOR, Permission.MANAGE_USERS) is False

    for manager_only in (
        Permission.IMPORT_DATA_AND_POLICIES,
        Permission.VIEW_ALL_CUSTOMERS,
        Permission.APPROVE_MANAGER_REVIEW_RECOMMENDATION,
        Permission.ASSIGN_TASKS,
        Permission.VIEW_AUDIT_LOG,
        Permission.CLEAR_DISPUTE,
        Permission.OVERRIDE_REMINDER_CAP,
        Permission.MANAGE_POLICY_RULES,
        Permission.EDIT_TENANT_SETTINGS,
        Permission.SOFT_DELETE_MEMORY,
        Permission.VIEW_EXECUTIVE_DASHBOARD,
    ):
        assert has_permission(Role.OWNER, manager_only) is True
        assert has_permission(Role.FINANCE_MANAGER, manager_only) is True
        assert has_permission(Role.COLLECTOR, manager_only) is False

    for collector_allowed in (
        Permission.VIEW_ASSIGNED_CUSTOMERS,
        Permission.APPROVE_ROUTINE_RECOMMENDATION,
        Permission.RECORD_CUSTOMER_MEMORY,
        Permission.DISPUTE_INVOICE,
    ):
        assert has_permission(Role.COLLECTOR, collector_allowed) is True


def test_concurrent_duplicate_email_and_cross_tenant_reuse(
    client: TestClient,
    fake_db: InMemorySession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = _seed_two_tenants(fake_db)
    owner_a_headers = _login_headers(
        client, "owner.a@example.synthetic", "OwnerPass123!"
    )
    owner_b_headers = _login_headers(
        client, "owner.b@example.synthetic", "OwnerBPass123!"
    )

    # Same email is permitted in a different tenant.
    cross_tenant_create = client.post(
        "/api/v1/users",
        headers=owner_b_headers,
        json={
            "name": "Tenant B Manager Copy",
            "email": "manager.a@example.synthetic",
            "password": "ValidPassword123!",
            "role": "FINANCE_MANAGER",
        },
    )
    assert cross_tenant_create.status_code == 201

    # Simulate a concurrent race where the pre-insert SELECT misses a simultaneous insert
    # and the DB unique index raises IntegrityError on commit/insert.
    rollback_calls = 0
    original_rollback = fake_db.rollback

    def counting_rollback() -> None:
        nonlocal rollback_calls
        rollback_calls += 1
        original_rollback()

    monkeypatch.setattr(fake_db, "rollback", counting_rollback)

    original_list = TenantScopedDataAccess.list

    def stale_list(
        self: TenantScopedDataAccess,
        model: type[Any],
        *conditions: Any,
        limit: int | None = None,
        for_update: bool = False,
    ) -> list[Any]:
        if model is User and conditions:
            return []
        return original_list(
            self, model, *conditions, limit=limit, for_update=for_update
        )

    monkeypatch.setattr(TenantScopedDataAccess, "list", stale_list)

    raced_create = client.post(
        "/api/v1/users",
        headers=owner_a_headers,
        json={
            "name": "Race Duplicate",
            "email": "manager.a@example.synthetic",
            "password": "ValidPassword123!",
            "role": "COLLECTOR",
        },
    )
    assert raced_create.status_code == 409
    assert rollback_calls == 1

    raced_update = client.patch(
        f"/api/v1/users/{data['collector_a1'].id}",
        headers=owner_a_headers,
        json={"email": "manager.a@example.synthetic"},
    )
    assert raced_update.status_code == 409
    assert rollback_calls == 2


def test_last_owner_protection_uses_row_locking_and_serializes_demotions(
    client: TestClient, fake_db: InMemorySession
) -> None:
    data = _seed_two_tenants(fake_db)
    owner_headers = _login_headers(client, "owner.a@example.synthetic", "OwnerPass123!")

    # Verify PostgreSQL SQL compiles FOR UPDATE after tenant_id filtering.
    stmt = (
        select(User)
        .where(User.tenant_id == data["tenant_a"].id, User.role == Role.OWNER.value)
        .with_for_update()
    )
    compiled_sql = str(stmt.compile(dialect=postgresql.dialect())).lower()
    assert "where users.tenant_id =" in compiled_sql
    assert compiled_sql.endswith("for update")

    # Promote Manager A to a second Owner.
    promote = client.patch(
        f"/api/v1/users/{data['manager_a'].id}",
        headers=owner_headers,
        json={"role": "OWNER"},
    )
    assert promote.status_code == 200

    # Demote original Owner A -> allowed because Manager A is now also Owner.
    first_demote = client.patch(
        f"/api/v1/users/{data['owner_a'].id}",
        headers=owner_headers,
        json={"role": "FINANCE_MANAGER"},
    )
    assert first_demote.status_code == 200

    # Existing Owner A token immediately reflects FINANCE_MANAGER and cannot manage users.
    assert (
        client.patch(
            f"/api/v1/users/{data['manager_a'].id}",
            headers=owner_headers,
            json={"role": "COLLECTOR"},
        ).status_code
        == 403
    )

    # Now Manager A (the sole remaining Owner) cannot demote themselves.
    second_owner_headers = _login_headers(
        client, "manager.a@example.synthetic", "ManagerPass123!"
    )
    final_demote = client.patch(
        f"/api/v1/users/{data['manager_a'].id}",
        headers=second_owner_headers,
        json={"role": "FINANCE_MANAGER"},
    )
    assert final_demote.status_code == 409


def test_password_update_and_existing_token_behavior(
    client: TestClient, fake_db: InMemorySession
) -> None:
    data = _seed_two_tenants(fake_db)
    owner_headers = _login_headers(client, "owner.a@example.synthetic", "OwnerPass123!")
    collector_headers = _login_headers(
        client, "collector.a1@example.synthetic", "CollectorPass123!"
    )

    reset_resp = client.patch(
        f"/api/v1/users/{data['collector_a1'].id}",
        headers=owner_headers,
        json={"password": "NewCollectorPass123!"},
    )
    assert reset_resp.status_code == 200

    # Old password is rejected immediately; new password succeeds.
    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "collector.a1@example.synthetic",
                "password": "CollectorPass123!",
            },
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "collector.a1@example.synthetic",
                "password": "NewCollectorPass123!",
            },
        ).status_code
        == 200
    )

    # Documented current behavior: without a token_version/password_changed_at column,
    # already-issued access tokens remain valid until exp.
    assert client.get("/api/v1/auth/me", headers=collector_headers).status_code == 200


def test_get_db_session_rollback_on_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import Mock
    import db.session as db_session

    mock_session = Mock()
    monkeypatch.setattr(
        db_session, "get_session_factory", lambda: (lambda: mock_session)
    )

    # Normal completion closes without rollback.
    gen = db_session.get_db()
    yielded = next(gen)
    assert yielded is mock_session
    with pytest.raises(StopIteration):
        next(gen)
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()

    # Unhandled exception triggers rollback and close.
    mock_session.reset_mock()
    gen_err = db_session.get_db()
    next(gen_err)
    with pytest.raises(RuntimeError, match="boom"):
        gen_err.throw(RuntimeError("boom"))
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


@pytest.fixture
def pg_session(monkeypatch: pytest.MonkeyPatch) -> Iterator[Session]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL auth integration tests.")

    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(Config(str(ALEMBIC_CONFIG)), "head")

    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            session = Session(
                bind=connection,
                join_transaction_mode="create_savepoint",
            )
            try:
                yield session
            finally:
                session.close()
                transaction.rollback()
    finally:
        engine.dispose()


def test_postgresql_end_to_end_auth_users_and_collector_scope(
    pg_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_SECRET_KEY", TEST_SECRET)
    tenant_a = Tenant(name="PG Tenant A", industry="distribution")
    tenant_b = Tenant(name="PG Tenant B", industry="distribution")
    pg_session.add_all((tenant_a, tenant_b))
    pg_session.flush()

    owner_a = User(
        tenant_id=tenant_a.id,
        name="PG Owner A",
        email="pg.owner.a@example.synthetic",
        password_hash=hash_password("PgOwnerPass123!"),
        role=Role.OWNER.value,
    )
    collector_a = User(
        tenant_id=tenant_a.id,
        name="PG Collector A",
        email="pg.collector.a@example.synthetic",
        password_hash=hash_password("PgCollectorPass123!"),
        role=Role.COLLECTOR.value,
    )
    owner_b = User(
        tenant_id=tenant_b.id,
        name="PG Owner B",
        email="pg.owner.b@example.synthetic",
        password_hash=hash_password("PgOwnerBPass123!"),
        role=Role.OWNER.value,
    )
    pg_session.add_all((owner_a, collector_a, owner_b))
    pg_session.flush()

    assigned_customer = Customer(
        tenant_id=tenant_a.id,
        name="PG Assigned",
        payment_terms="Net 30",
        tier="regular",
        assigned_collector=collector_a.id,
        status="active",
    )
    unassigned_customer = Customer(
        tenant_id=tenant_a.id,
        name="PG Unassigned",
        payment_terms="Net 30",
        tier="regular",
        assigned_collector=None,
        status="active",
    )
    other_tenant_customer = Customer(
        tenant_id=tenant_b.id,
        name="PG Tenant B Customer",
        payment_terms="Net 30",
        tier="regular",
        assigned_collector=None,
        status="active",
    )
    pg_session.add_all((assigned_customer, unassigned_customer, other_tenant_customer))
    pg_session.flush()

    # Keep savepoint isolation by turning route commits into flushes in this test session.
    monkeypatch.setattr(pg_session, "commit", pg_session.flush)
    app.dependency_overrides[get_db] = lambda: pg_session
    try:
        with TestClient(app) as test_client:
            owner_headers = _login_headers(
                test_client, "pg.owner.a@example.synthetic", "PgOwnerPass123!"
            )
            collector_headers = _login_headers(
                test_client, "pg.collector.a@example.synthetic", "PgCollectorPass123!"
            )

            created = test_client.post(
                "/api/v1/users",
                headers=owner_headers,
                json={
                    "name": "PG Finance Manager",
                    "email": "pg.fm.a@example.synthetic",
                    "password": "PgManagerPass123!",
                    "role": "FINANCE_MANAGER",
                },
            )
            assert created.status_code == 201
            assert created.json()["tenant_id"] == str(tenant_a.id)

            # Duplicate case-insensitive email in same tenant -> 409; in Tenant B -> 201.
            assert (
                test_client.post(
                    "/api/v1/users",
                    headers=owner_headers,
                    json={
                        "name": "PG Duplicate FM",
                        "email": "PG.FM.A@example.synthetic",
                        "password": "PgManagerPass123!",
                        "role": "FINANCE_MANAGER",
                    },
                ).status_code
                == 409
            )
            owner_b_headers = _login_headers(
                test_client, "pg.owner.b@example.synthetic", "PgOwnerBPass123!"
            )
            assert (
                test_client.post(
                    "/api/v1/users",
                    headers=owner_b_headers,
                    json={
                        "name": "PG Tenant B FM",
                        "email": "pg.fm.a@example.synthetic",
                        "password": "PgManagerPass123!",
                        "role": "FINANCE_MANAGER",
                    },
                ).status_code
                == 201
            )

            # Last Owner demotion blocked on PostgreSQL.
            assert (
                test_client.patch(
                    f"/api/v1/users/{owner_a.id}",
                    headers=owner_headers,
                    json={"role": "FINANCE_MANAGER"},
                ).status_code
                == 409
            )

            assert (
                test_client.post(
                    "/api/v1/users",
                    headers=collector_headers,
                    json={
                        "name": "Should Fail",
                        "email": "fail@example.synthetic",
                        "password": "PgManagerPass123!",
                        "role": "COLLECTOR",
                    },
                ).status_code
                == 403
            )

            collector_customers = test_client.get(
                "/api/v1/customers", headers=collector_headers
            )
            assert collector_customers.status_code == 200
            assert [c["id"] for c in collector_customers.json()] == [
                str(assigned_customer.id)
            ]
            assert (
                test_client.get(
                    f"/api/v1/customers/{unassigned_customer.id}",
                    headers=collector_headers,
                ).status_code
                == 403
            )
            assert (
                test_client.get(
                    f"/api/v1/customers/{other_tenant_customer.id}",
                    headers=collector_headers,
                ).status_code
                == 404
            )
    finally:
        app.dependency_overrides.clear()
