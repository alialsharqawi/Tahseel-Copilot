"use client";

import { useState } from "react";

const messages = {
  en: {
    heading: "Welcome to Tahseel",
    description: "The frontend foundation is running.",
    language: "العربية",
    languageLabel: "Switch language to Arabic",
  },
  ar: {
    heading: "مرحبًا بك في تحصيل",
    description: "الواجهة الأولية تعمل.",
    language: "English",
    languageLabel: "تغيير اللغة إلى الإنجليزية",
  },
} as const;

type Locale = keyof typeof messages;

export default function Home() {
  const [locale, setLocale] = useState<Locale>("en");
  const text = messages[locale];

  return (
    <main lang={locale} dir={locale === "ar" ? "rtl" : "ltr"}>
      <section className="welcome">
        <p className="brand">Tahseel</p>
        <h1>{text.heading}</h1>
        <p>{text.description}</p>
        <button
          type="button"
          aria-label={text.languageLabel}
          onClick={() => setLocale(locale === "en" ? "ar" : "en")}
        >
          {text.language}
        </button>
      </section>
    </main>
  );
}
