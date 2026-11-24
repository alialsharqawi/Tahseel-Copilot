import type { Locale } from "./dictionaries";

const localeTags: Record<Locale, string> = {
  en: "en-EG",
  ar: "ar-EG",
};

const westernDigits = { numberingSystem: "latn" } as const;

export function formatNumber(value: number, locale: Locale): string {
  return new Intl.NumberFormat(localeTags[locale], westernDigits).format(value);
}

export function formatDate(value: Date | number, locale: Locale): string {
  return new Intl.DateTimeFormat(localeTags[locale], {
    ...westernDigits,
    dateStyle: "medium",
  }).format(value);
}

export function formatCurrency(value: number, locale: Locale): string {
  return new Intl.NumberFormat(localeTags[locale], {
    ...westernDigits,
    style: "currency",
    currency: "EGP",
  }).format(value);
}
