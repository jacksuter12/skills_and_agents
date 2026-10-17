# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.40"]
# ///
"""Screenshot an HTML/SVG diagram to PNG and lint its geometry.

Usage:
    uv run .claude/skills/html-diagram/scripts/render.py <diagram.html> [--output out.png] [--scale 2]
                                                          [--width N] [--chromium PATH] [--json]

Prints the PNG path, then a lint report. Exit code is 0 when the lint is clean,
1 when it found errors (warnings alone do not fail), 2 on usage/setup problems.

The lint relies on the markup conventions in SKILL.md:
    <svg id="diagram">                    the diagram root (required)
    <g data-node="id">shape + text</g>    a node: its text must fit inside its shape
    <g data-region="id">...</g>           a section boundary: may contain other things
    <path data-edge data-from="a" data-to="b">   a connector between two nodes

First-time setup (only if no Chromium is available):
    uv run --with playwright playwright install chromium
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# Runs inside the page. Returns {"svg": {...}, "issues": [...]}. Every coordinate
# is in CSS pixels relative to the page, so checks are independent of viewBox scaling.
LINT_JS = r"""
() => {
  const issues = [];
  const add = (severity, check, message) => issues.push({severity, check, message});
  const svg = document.querySelector('svg#diagram');
  if (!svg) {
    add('error', 'structure', 'No <svg id="diagram"> found');
    return {svg: null, issues};
  }

  const SHAPES = 'rect, ellipse, circle, polygon, path';
  const box = el => el.getBoundingClientRect();
  const label = el => {
    const n = el.closest('[data-node]');
    if (n) return `node "${n.dataset.node}"`;
    const t = (el.textContent || '').trim().replace(/\s+/g, ' ');
    return t ? `"${t.slice(0, 40)}"` : `<${el.tagName}>`;
  };
  const intersect = (a, b, slack = 0) =>
    a.left + slack < b.right && b.left + slack < a.right &&
    a.top + slack < b.bottom && b.top + slack < a.bottom;

  // Map a page point (scroll-adjusted) into an element's own coordinates for isPointInFill.
  const inFill = (shape, x, y) => {
    const m = shape.getScreenCTM();
    if (!m || !shape.isPointInFill) return false;
    const p = new DOMPoint(x - window.scrollX, y - window.scrollY).matrixTransform(m.inverse());
    return shape.isPointInFill(p);
  };
  const pageBox = el => {
    const r = box(el);
    return {left: r.left + scrollX, right: r.right + scrollX, top: r.top + scrollY,
            bottom: r.bottom + scrollY, width: r.width, height: r.height};
  };

  // The node's shape is the element marked data-shape, else its first shape child.
  const nodes = [...svg.querySelectorAll('[data-node]')].map(g => {
    const shape = g.querySelector('[data-shape]') || g.querySelector(SHAPES);
    return {id: g.dataset.node, g, shape, box: shape ? pageBox(shape) : null};
  });
  const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
  for (const n of nodes) if (!n.shape) add('error', 'structure', `node "${n.id}" has no shape element`);

  // 1. Clipping: anything drawn outside the svg viewport is cut off.
  const svgBox = pageBox(svg);
  for (const el of svg.querySelectorAll('text, ' + SHAPES + ', line, polyline')) {
    if (el.closest('defs, marker')) continue;
    const r = pageBox(el);
    if (r.width === 0 && r.height === 0) continue;
    if (r.left < svgBox.left - 1 || r.right > svgBox.right + 1 ||
        r.top < svgBox.top - 1 || r.bottom > svgBox.bottom + 1) {
      add('error', 'clipped', `${label(el)} extends outside the svg viewBox`);
    }
  }

  // 2. Text must fit inside its node's shape (all four corners in the fill, 3px inset).
  for (const n of nodes) {
    if (!n.shape) continue;
    for (const t of n.g.querySelectorAll('text')) {
      const r = pageBox(t), i = 3;
      const corners = [[r.left + i, r.top + i], [r.right - i, r.top + i],
                       [r.left + i, r.bottom - i], [r.right - i, r.bottom - i]];
      if (!corners.every(([x, y]) => inFill(n.shape, x, y))) {
        add('error', 'text-overflow', `text "${t.textContent.trim().slice(0, 40)}" overflows node "${n.id}"`);
      }
    }
  }

  // 3. Text overlapping other text.
  const texts = [...svg.querySelectorAll('text')].filter(t => !t.closest('defs'));
  const tboxes = texts.map(pageBox);
  for (let a = 0; a < texts.length; a++)
    for (let b = a + 1; b < texts.length; b++)
      if (intersect(tboxes[a], tboxes[b], 1))
        add('error', 'text-overlap', `${label(texts[a])} overlaps ${label(texts[b])}`);

  // 4. Node shapes overlapping each other (nested nodes are allowed).
  for (let a = 0; a < nodes.length; a++)
    for (let b = a + 1; b < nodes.length; b++) {
      const A = nodes[a], B = nodes[b];
      if (!A.box || !B.box || A.g.contains(B.g) || B.g.contains(A.g)) continue;
      if (intersect(A.box, B.box, 2)) add('error', 'node-overlap', `node "${A.id}" overlaps node "${B.id}"`);
    }

  // 5. Edges: endpoints land on their nodes, and the path avoids everything else.
  const distToBox = (x, y, r) => Math.hypot(Math.max(r.left - x, 0, x - r.right),
                                            Math.max(r.top - y, 0, y - r.bottom));
  const tips = [];
  for (const e of svg.querySelectorAll('[data-edge]')) {
    const name = `edge ${e.dataset.from || '?'}→${e.dataset.to || '?'}`;
    if (!e.getTotalLength) { add('error', 'structure', `${name} is not a path/line`); continue; }
    const len = e.getTotalLength();
    const m = e.getScreenCTM();
    const at = d => {
      const p = e.getPointAtLength(d).matrixTransform(m);
      return [p.x + scrollX, p.y + scrollY];
    };
    for (const [end, d] of [['from', 0], ['to', len]]) {
      const id = e.dataset[end];
      if (!id) continue;
      const n = byId[id];
      if (!n) { add('error', 'structure', `${name}: no node "${id}"`); continue; }
      const [x, y] = at(d);
      const gap = distToBox(x, y, n.box);
      if (gap > 10) add('error', 'edge-endpoint', `${name} ${end}-end is ${Math.round(gap)}px away from node "${id}"`);
      else if (inFill(n.shape, x, y)) {
        const depth = Math.min(x - n.box.left, n.box.right - x, y - n.box.top, n.box.bottom - y);
        if (depth > 6) add('warning', 'edge-endpoint', `${name} ${end}-end sits ${Math.round(depth)}px inside node "${id}" (arrowhead hidden?)`);
      }
    }
    // Sample the path; skip the first/last 12px so touching the endpoints is fine.
    const hitNodes = new Set(), hitTexts = new Set();
    for (let d = 12; d < len - 12; d += 3) {
      const [x, y] = at(d);
      // Includes the edge's own endpoints: away from its ends, it shouldn't run inside them either.
      for (const n of nodes) {
        if (!n.shape || n.g.contains(e)) continue;
        if (distToBox(x, y, n.box) === 0 && inFill(n.shape, x, y)) hitNodes.add(n.id);
      }
      texts.forEach((t, i) => {
        const r = tboxes[i];
        if (x > r.left + 1 && x < r.right - 1 && y > r.top + 1 && y < r.bottom - 1) hitTexts.add(i);
      });
    }
    if (e.getAttribute('marker-end')) tips.push({name, to: e.dataset.to, xy: at(len)});
    for (const id of hitNodes) add('error', 'edge-crossing', `${name} passes through node "${id}"`);
    for (const i of hitTexts) add('warning', 'edge-crossing', `${name} crosses text ${label(texts[i])}`);
  }

  // Arrowheads landing on the same spot merge into one blob; spread them along the edge.
  for (let a = 0; a < tips.length; a++)
    for (let b = a + 1; b < tips.length; b++)
      if (Math.hypot(tips[a].xy[0] - tips[b].xy[0], tips[a].xy[1] - tips[b].xy[1]) < 8)
        add('warning', 'stacked-arrowheads', `${tips[a].name} and ${tips[b].name} end at the same point`);

  // 6. Readability: text that will be hard to read at 1x.
  for (const t of texts) {
    const px = parseFloat(getComputedStyle(t).fontSize) * (svgBox.width / svg.viewBox.baseVal.width || 1);
    if (px < 11) add('warning', 'small-text', `${label(t)} renders at ${px.toFixed(1)}px`);
  }

  const vb = svg.viewBox.baseVal;
  if (vb && vb.width && svgBox.width < vb.width - 1)
    add('warning', 'scaled', `svg is drawn at ${Math.round(svgBox.width)}px but its viewBox is ${vb.width}px wide; text is shrunk`);

  return {svg: {viewBoxWidth: vb ? vb.width : null, renderedWidth: svgBox.width}, issues};
}
"""


def find_chromium(explicit: str | None) -> str | None:
    """A Chromium executable to fall back to when Playwright's bundled one is missing."""
    for candidate in (explicit, os.environ.get("HTML_DIAGRAM_CHROMIUM")):
        if candidate:
            return candidate
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        if path := shutil.which(name):
            return path
    browsers = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if browsers and (Path(browsers) / "chromium").exists():
        return str(Path(browsers) / "chromium")
    return None


def launch(p, explicit: str | None):
    if explicit:
        return p.chromium.launch(executable_path=explicit)
    try:
        return p.chromium.launch()
    except Exception as first_error:
        # Usually a version mismatch between the playwright package and the installed browser.
        fallback = find_chromium(None)
        if fallback:
            return p.chromium.launch(executable_path=fallback)
        print(f"ERROR: could not launch Chromium: {first_error}", file=sys.stderr)
        print("Fix: uv run --with playwright playwright install chromium", file=sys.stderr)
        print("  or pass --chromium /path/to/chrome (or set HTML_DIAGRAM_CHROMIUM)", file=sys.stderr)
        sys.exit(2)


def render(html_path: Path, output: Path, scale: int, width: int | None, chromium: str | None) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run this script with `uv run`.", file=sys.stderr)
        sys.exit(2)

    external_requests: list[str] = []
    with sync_playwright() as p:
        browser = launch(p, chromium)
        page = browser.new_page(viewport={"width": width or 1600, "height": 100}, device_scale_factor=scale)
        page.on("request", lambda r: external_requests.append(r.url)
                if not r.url.startswith(("file:", "data:", "about:")) else None)
        # A short viewport makes the full-page screenshot exactly as tall as the content.
        page.goto(html_path.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")

        if width is None:
            # Size the viewport so the svg draws at its natural (viewBox) width, plus page padding.
            natural = page.evaluate("""() => {
                const s = document.querySelector('svg#diagram');
                if (!s || !s.viewBox.baseVal || !s.viewBox.baseVal.width) return null;
                const cs = getComputedStyle(document.body);
                return s.viewBox.baseVal.width + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight)
                       + parseFloat(cs.marginLeft) + parseFloat(cs.marginRight);
            }""")
            if natural:
                page.set_viewport_size({"width": int(natural) + 2, "height": 100})

        report = page.evaluate(LINT_JS)
        page.screenshot(path=str(output), full_page=True)
        browser.close()

    for url in sorted(set(external_requests)):
        report["issues"].append({"severity": "warning", "check": "not-self-contained",
                                 "message": f"page fetched an external resource: {url}"})
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Screenshot an HTML/SVG diagram and lint its layout")
    parser.add_argument("input", type=Path, help="Path to the diagram .html file")
    parser.add_argument("--output", "-o", type=Path, help="PNG path (default: next to the input)")
    parser.add_argument("--scale", "-s", type=int, default=2, help="Device scale factor (default: 2)")
    parser.add_argument("--width", "-w", type=int, help="Viewport width in px (default: fit the svg's viewBox)")
    parser.add_argument("--chromium", help="Path to a Chromium/Chrome executable")
    parser.add_argument("--json", action="store_true", help="Print the lint report as JSON")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: file not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    output = args.output or args.input.with_suffix(".png")
    report = render(args.input, output, args.scale, args.width, args.chromium)
    issues = report["issues"]
    errors = [i for i in issues if i["severity"] == "error"]

    print(output)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"lint: {len(errors)} error(s), {len(issues) - len(errors)} warning(s)")
        for i in issues:
            print(f"  [{i['severity']}] {i['check']}: {i['message']}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
