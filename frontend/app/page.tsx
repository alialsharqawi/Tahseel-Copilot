"use client";

import { LanguageSwitcher } from "./components/language-switcher";
import { useLocale } from "./i18n/locale-provider";

export default function Home() {
  const { locale, t } = useLocale();

  return (
    <>
      <header className="app-header">
        <p className="brand">{t("brand")}</p>
        <LanguageSwitcher />
      </header>
      <main lang={locale} dir={locale === "ar" ? "rtl" : "ltr"}>
        <section className="welcome">
          <h1>{t("welcome.title")}</h1>
          <p>{t("welcome.description")}</p>
        </section>
      </main>
    </>
  );
}
