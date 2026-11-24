import { globSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const stylesheetPaths = globSync("**/*.css", {
  cwd: process.cwd(),
  exclude: ["node_modules/**", ".next/**", "coverage/**", "dist/**"],
});
const stylesheets = stylesheetPaths
  .map((path) => readFileSync(resolve(process.cwd(), path), "utf8"))
  .join("\n");

function ruleStyles(selector: string): string {
  const escapedSelector = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return stylesheets.match(
    new RegExp(`(?:^|\\n)${escapedSelector}\\s*\\{([^}]*)\\}`, "m"),
  )?.[1] ?? "";
}

describe("directional layout styles", () => {
  it("uses a viewport-height flex shell with main content filling the remaining space", () => {
    const body = ruleStyles("body");
    const main = ruleStyles("main");

    expect(body).toMatch(/\bdisplay\s*:\s*flex\b/);
    expect(body).toMatch(/\bflex-direction\s*:\s*column\b/);
    expect(body).toMatch(/\bmin-block-size\s*:\s*100vh\b/);
    expect(body).toMatch(/\bmin-block-size\s*:\s*100dvh\b/);
    expect(main).toMatch(/\bflex\s*:\s*1\b/);
    expect(main).not.toMatch(/\bmin-(?:height|block-size)\s*:\s*100(?:d)?vh\b/);
  });

  it("does not use physical directional properties or values in any frontend stylesheet", () => {
    const physicalDirectionalStyles = [
      /\b(?:left|right|inset)\s*:/i,
      /\b(?:margin|padding|inset|scroll-margin|scroll-padding)-(?:left|right)\s*:/i,
      /\bborder-(?:left|right)(?:-(?:width|style|color))?\s*:/i,
      /\bborder-(?:top|bottom)-(?:left|right)-radius\s*:/i,
      /\b(?:text-align|float|clear)\s*:\s*(?:left|right)\b/i,
      /\b(?:background-position|object-position)(?:-[xy])?\s*:[^;{}]*(?:\bleft\b|\bright\b)/i,
    ];

    for (const physicalDirectionalStyle of physicalDirectionalStyles) {
      expect(stylesheets).not.toMatch(physicalDirectionalStyle);
    }
    expect(stylesheetPaths.length).toBeGreaterThan(0);
  });
});
