"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useSyncExternalStore,
  type ReactNode,
} from "react";

import { dictionaries, type Locale, type TranslationKey } from "./dictionaries";

const localeStorageKey = "tahseel-locale";
const localeListeners = new Set<() => void>();

type LocaleContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: TranslationKey) => string;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

function getLocaleSnapshot(): Locale {
  const storedLocale = window.localStorage.getItem(localeStorageKey);
  return storedLocale === "en" || storedLocale === "ar" ? storedLocale : "en";
}

function getServerLocaleSnapshot(): Locale {
  return "en";
}

function subscribeToLocale(listener: () => void) {
  localeListeners.add(listener);
  window.addEventListener("storage", listener);

  return () => {
    localeListeners.delete(listener);
    window.removeEventListener("storage", listener);
  };
}

function setLocale(locale: Locale) {
  window.localStorage.setItem(localeStorageKey, locale);
  localeListeners.forEach((listener) => listener());
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  const locale = useSyncExternalStore(
    subscribeToLocale,
    getLocaleSnapshot,
    getServerLocaleSnapshot,
  );

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === "ar" ? "rtl" : "ltr";
    document.title = dictionaries[locale]["document.title"];
  }, [locale]);

  const value = useMemo<LocaleContextValue>(
    () => ({
      locale,
      setLocale,
      t: (key) => dictionaries[locale][key],
    }),
    [locale],
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const context = useContext(LocaleContext);
  if (!context) {
    throw new Error("useLocale must be used within a LocaleProvider");
  }
  return context;
}
