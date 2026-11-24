import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { RoleNavigation } from "./role-navigation";
import { LocaleProvider } from "../i18n/locale-provider";
import type { Role } from "../navigation";

afterEach(() => {
  cleanup();
  window.localStorage.clear();
});

function renderNavigation(role: Role) {
  return render(
    <LocaleProvider>
      <RoleNavigation role={role} />
    </LocaleProvider>,
  );
}

function navigationLinks() {
  const navigation = screen.getByRole("navigation", { name: "Primary navigation" });
  return within(navigation).getAllByRole("link").map((link) => ({
    label: link.textContent,
    href: link.getAttribute("href"),
  }));
}

describe("RoleNavigation", () => {
  it("shows assigned-customer work and no manager-only links to collectors", () => {
    renderNavigation("collector");

    const links = navigationLinks();
    expect(links).toEqual([
      { label: "Collection queue", href: "/queue" },
      { label: "Customers", href: "/customers" },
      { label: "Tasks", href: "/tasks" },
    ]);
    expect(links.some(({ label }) => label === "Assign tasks")).toBe(false);
  });

  it("shows finance management links without owner-only user management", () => {
    renderNavigation("finance_manager");

    expect(navigationLinks()).toEqual([
      { label: "Executive dashboard", href: "/dashboard" },
      { label: "Customers", href: "/customers" },
      { label: "Tasks", href: "/tasks" },
      { label: "Import receivables", href: "/import" },
      { label: "Policies and rules", href: "/policies" },
      { label: "Settings", href: "/settings" },
      { label: "Audit log", href: "/audit" },
    ]);
  });

  it("shows all configured navigation links to owners", () => {
    renderNavigation("owner");

    expect(navigationLinks()).toEqual([
      { label: "Executive dashboard", href: "/dashboard" },
      { label: "Customers", href: "/customers" },
      { label: "Tasks", href: "/tasks" },
      { label: "Import receivables", href: "/import" },
      { label: "Policies and rules", href: "/policies" },
      { label: "Settings", href: "/settings" },
      { label: "Audit log", href: "/audit" },
      { label: "Users and roles", href: "/users" },
    ]);
  });

  it("translates navigation labels into Arabic", () => {
    window.localStorage.setItem("tahseel-locale", "ar");
    renderNavigation("collector");

    const navigation = screen.getByRole("navigation", { name: "التنقل الرئيسي" });
    expect(within(navigation).getByRole("link", { name: "قائمة التحصيل" })).toBeTruthy();
  });
});
