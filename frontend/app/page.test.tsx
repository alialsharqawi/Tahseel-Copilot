import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import Home from "./page";

afterEach(cleanup);

describe("Home language toggle", () => {
  it("switches between English and Arabic content and direction", () => {
    render(<Home />);

    const main = screen.getByRole("main");
    expect(main.getAttribute("lang")).toBe("en");
    expect(main.getAttribute("dir")).toBe("ltr");
    expect(screen.getByRole("heading", { name: "Welcome to Tahseel" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Switch language to Arabic" }));

    expect(main.getAttribute("lang")).toBe("ar");
    expect(main.getAttribute("dir")).toBe("rtl");
    expect(screen.getByRole("heading", { name: "مرحبًا بك في تحصيل" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "تغيير اللغة إلى الإنجليزية" }));

    expect(main.getAttribute("lang")).toBe("en");
    expect(main.getAttribute("dir")).toBe("ltr");
    expect(screen.getByRole("heading", { name: "Welcome to Tahseel" })).toBeTruthy();
  });
});
