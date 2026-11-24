"use client";

import Link from "next/link";

import { getNavigationForRole, type Role } from "../navigation";
import { useLocale } from "../i18n/locale-provider";

export function RoleNavigation({ role }: { role: Role }) {
  const { t } = useLocale();

  return (
    <nav className="app-navigation" aria-label={t("navigation.primary")}>
      <ul>
        {getNavigationForRole(role).map((item) => (
          <li key={item.href}>
            <Link href={item.href}>{t(item.label)}</Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
