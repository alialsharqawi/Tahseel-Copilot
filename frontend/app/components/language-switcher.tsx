"use client";

import { useLocale } from "../i18n/locale-provider";

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useLocale();
  const nextLocale = locale === "en" ? "ar" : "en";

  return (
    <button
      type="button"
      aria-label={t(
        locale === "en"
          ? "language.switchToArabicLabel"
          : "language.switchToEnglishLabel",
      )}
      onClick={() => setLocale(nextLocale)}
    >
      {t(locale === "en" ? "language.switchToArabic" : "language.switchToEnglish")}
    </button>
  );
}
