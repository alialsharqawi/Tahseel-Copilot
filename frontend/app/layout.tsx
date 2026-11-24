import type { Metadata } from "next";
import type { ReactNode } from "react";

import { dictionaries } from "./i18n/dictionaries";
import { LocaleProvider } from "./i18n/locale-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: dictionaries.en["document.title"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en" dir="ltr">
      <body>
        <LocaleProvider>{children}</LocaleProvider>
      </body>
    </html>
  );
}
