import type { TranslationKey } from "./i18n/dictionaries";

export const roles = ["collector", "finance_manager", "owner"] as const;

export type Role = (typeof roles)[number];

export type NavigationItem = {
  href: string;
  label: Extract<TranslationKey, `navigation.${string}`>;
  roles: readonly Role[];
};

const allRoles = ["collector", "finance_manager", "owner"] as const satisfies readonly Role[];
const managers = ["finance_manager", "owner"] as const satisfies readonly Role[];

export const navigationItems = [
  { href: "/dashboard", label: "navigation.dashboard", roles: managers },
  { href: "/queue", label: "navigation.collectionQueue", roles: ["collector"] },
  { href: "/customers", label: "navigation.customers", roles: allRoles },
  { href: "/tasks", label: "navigation.tasks", roles: allRoles },
  { href: "/import", label: "navigation.import", roles: managers },
  { href: "/policies", label: "navigation.policies", roles: managers },
  { href: "/settings", label: "navigation.settings", roles: managers },
  { href: "/audit", label: "navigation.auditLog", roles: managers },
  { href: "/users", label: "navigation.users", roles: ["owner"] },
] as const satisfies readonly NavigationItem[];

export function getNavigationForRole(role: Role) {
  return navigationItems.filter((item) =>
    item.roles.some((allowedRole) => allowedRole === role),
  );
}
