import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import Home from "./page";
import { LocaleProvider } from "./i18n/locale-provider";

function renderHome() {
  return render(
    <LocaleProvider>
      <Home />
    </LocaleProvider>,
  );
}

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  window.localStorage.clear();
});

describe("Home localization", () => {
  it("renders English, switches to Arabic, and updates document direction", async () => {
    renderHome();

    expect(screen.getByRole("heading", { name: "Welcome to Tahseel" })).toBeTruthy();
    await waitFor(() => {
      expect(document.documentElement.lang).toBe("en");
      expect(document.documentElement.dir).toBe("ltr");
      expect(document.title).toBe("Tahseel | Credit Control Copilot");
    });

    fireEvent.click(screen.getByRole("button", { name: "Switch language to Arabic" }));

    expect(screen.getByRole("heading", { name: "مرحبًا بك في تحصيل" })).toBeTruthy();
    await waitFor(() => {
      expect(document.documentElement.lang).toBe("ar");
      expect(document.documentElement.dir).toBe("rtl");
      expect(document.title).toBe("تحصيل | مساعد إدارة الائتمان");
    });

    fireEvent.click(screen.getByRole("button", { name: "تغيير اللغة إلى الإنجليزية" }));

    expect(screen.getByRole("heading", { name: "Welcome to Tahseel" })).toBeTruthy();
    await waitFor(() => {
      expect(document.documentElement.lang).toBe("en");
      expect(document.documentElement.dir).toBe("ltr");
      expect(document.title).toBe("Tahseel | Credit Control Copilot");
      expect(window.localStorage.getItem("tahseel-locale")).toBe("en");
    });
  });

  it("restores and persists the saved language preference", async () => {
    window.localStorage.setItem("tahseel-locale", "ar");
    const { unmount } = renderHome();

    expect(
      await screen.findByRole("heading", { name: "مرحبًا بك في تحصيل" }),
    ).toBeTruthy();
    await waitFor(() => {
      expect(document.documentElement.lang).toBe("ar");
      expect(document.documentElement.dir).toBe("rtl");
    });

    unmount();
    window.localStorage.clear();
    renderHome();
    fireEvent.click(screen.getByRole("button", { name: "Switch language to Arabic" }));

    await waitFor(() => {
      expect(window.localStorage.getItem("tahseel-locale")).toBe("ar");
    });
  });

  it("uses English when the stored locale is unsupported", async () => {
    window.localStorage.setItem("tahseel-locale", "fr");
    renderHome();

    expect(screen.getByRole("heading", { name: "Welcome to Tahseel" })).toBeTruthy();
    await waitFor(() => {
      expect(document.documentElement.lang).toBe("en");
      expect(document.documentElement.dir).toBe("ltr");
      expect(document.title).toBe("Tahseel | Credit Control Copilot");
    });
  });
});
