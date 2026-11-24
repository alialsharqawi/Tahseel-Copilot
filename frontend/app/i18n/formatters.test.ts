import { describe, expect, it } from "vitest";

import { formatCurrency, formatDate, formatNumber } from "./formatters";

describe("locale formatters", () => {
  it("uses Western digits for Arabic numbers, dates, and EGP currency", () => {
    const formattedValues = [
      formatNumber(1234567.89, "ar"),
      formatDate(new Date("2026-01-02T00:00:00.000Z"), "ar"),
      formatCurrency(310000, "ar"),
    ];

    for (const formattedValue of formattedValues) {
      expect(formattedValue).toMatch(/[0-9]/);
      expect(formattedValue).not.toMatch(/[\u0660-\u0669\u06f0-\u06f9]/);
    }
  });

  it("uses Intl locale formatting for numbers, dates, and EGP", () => {
    expect(formatNumber(1234567.89, "en")).toBe(
      new Intl.NumberFormat("en-EG", { numberingSystem: "latn" }).format(1234567.89),
    );
    expect(formatDate(new Date("2026-01-02T00:00:00.000Z"), "ar")).toBe(
      new Intl.DateTimeFormat("ar-EG", {
        numberingSystem: "latn",
        dateStyle: "medium",
      }).format(new Date("2026-01-02T00:00:00.000Z")),
    );
    expect(formatCurrency(310000, "ar")).toBe(
      new Intl.NumberFormat("ar-EG", {
        numberingSystem: "latn",
        style: "currency",
        currency: "EGP",
      }).format(310000),
    );
  });
});
