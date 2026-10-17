---
name: html-diagram
description: Create diagrams as self-contained HTML files with inline SVG that make visual arguments, then screenshot and lint them in a render-validate loop until clean. Use when the user wants to visualize a workflow, architecture, system, process, or concept as a diagram they can open in a browser, embed, or share.
---

# HTML Diagram Creator

Generate self-contained `.html` files with one inline `<svg>` that **argue visually**, not just display information. Then screenshot them with Playwright, inspect the PNG, and fix until clean.

## Files in This Skill

| File | Purpose | When to read |
|------|---------|--------------|
| `references/color-palette.md` | All colors and brand styles: the single source of truth | Before every diagram |
| `references/visual-patterns.md` | Sketches of each layout pattern (fan-out, timeline, tree...) | Design Step 2 |
| `references/starter.html` | Page shell: CSS tokens, text/shape classes, arrow markers, one example of each convention | Copy it as the start of every diagram |
| `scripts/render.py` | Screenshots the HTML to PNG and lints the geometry | Run after every edit (see Render & Validate) |
| `examples/` | Two finished diagrams with their PNGs | When you want a reference for density and style |

To restyle every diagram for a brand, edit `color-palette.md` (and the matching tokens in `starter.html`). Everything else is universal method.

---

## Two Decisions Already Made (Don't Relitigate Per Diagram)

### 1. Everything is SVG. HTML is only the page around it.

Boxes, text, arrows, and code blocks all live in one `<svg id="diagram">`. Do not build boxes from HTML/CSS (flexbox/grid divs) with an SVG overlay for connectors.

**Why:** a diagram is a geometry problem, and arrows need exact coordinates for both ends. With all-SVG, every node and every arrow share one coordinate system that is written in the file, so you can compute an arrow endpoint by arithmetic and fix it by editing a number. With HTML boxes, positions come out of the browser's layout engine: they aren't in the source, they shift with fonts and viewport width, and connectors then need JavaScript that measures boxes at runtime. That's a second program to debug, and the reader's viewport can differ from the one you validated. The costs of all-SVG are real but smaller: SVG text doesn't wrap (break lines yourself with `<tspan>`) and its width isn't known until rendered (the lint measures it and reports overflow).

`<foreignObject>` (HTML inside SVG) is off by default: it's the one place you'd get text wrapping, but it renders inconsistently outside browsers and the lint can't check it. Use it only if the user needs paragraphs inside a shape.

### 2. No Graphviz or D2 for layout. Place coordinates by hand.

**Why:** the methodology demands that layout *mirror the concept*: fan-outs, timelines, cycles, side-by-side comparisons, free-floating annotations, code blocks placed beside the step they illustrate. Auto-layout engines optimize for a different goal (layered graphs with few edge crossings), so they flatten every diagram into the same top-down hierarchy, which is exactly the "uniform boxes" output this skill exists to avoid. They also add a binary dependency and produce SVG that's awkward to restyle and annotate.

**The exception:** a genuinely graph-shaped subject (roughly 15+ nodes with many cross-links, like a dependency graph) where crossings are the main problem. There, run `dot -Tplain` (Graphviz) only to get node coordinates, then draw the nodes yourself with this skill's styles and conventions. Say you're doing this and why.

---

## Core Philosophy

**Diagrams should ARGUE, not DISPLAY.**

A diagram isn't formatted text. It's a visual argument that shows relationships, causality, and flow that words alone can't express. The shape should BE the meaning.

**The Isomorphism Test**: If you removed all text, would the structure alone communicate the concept? If not, redesign.

**The Education Test**: Could someone learn something concrete from this diagram, or does it just label boxes? A good diagram teaches—it shows actual formats, real event names, concrete examples.

---

## Depth Assessment (Do This First)

Before designing, determine what level of detail this diagram needs:

### Simple/Conceptual Diagrams
Use abstract shapes when:
- Explaining a mental model or philosophy
- The audience doesn't need technical specifics
- The concept IS the abstraction (e.g., "separation of concerns")

### Comprehensive/Technical Diagrams
Use concrete examples when:
- Diagramming a real system, protocol, or architecture
- The diagram will be used to teach or explain (e.g., YouTube video)
- The audience needs to understand what things actually look like
- You're showing how multiple technologies integrate

**For technical diagrams, you MUST include evidence artifacts** (see below).

---

## Research Mandate (For Technical Diagrams)

**Before drawing anything technical, research the actual specifications.**

If you're diagramming a protocol, API, or framework:
1. Look up the actual JSON/data formats
2. Find the real event names, method names, or API endpoints
3. Understand how the pieces actually connect
4. Use real terminology, not generic placeholders

Bad: "Protocol" → "Frontend"
Good: "AG-UI streams events (RUN_STARTED, STATE_DELTA, A2UI_UPDATE)" → "CopilotKit renders via createA2UIMessageRenderer()"

**Research makes diagrams accurate AND educational.**

---

## Evidence Artifacts

Evidence artifacts are concrete examples that prove your diagram is accurate and help viewers learn. Include them in technical diagrams.

**Types of evidence artifacts** (choose what's relevant to your diagram):

| Artifact Type | When to Use | How to Render |
|---------------|-------------|---------------|
| **Code snippets** | APIs, integrations, implementation details | Dark rectangle + syntax-colored text (see color palette for evidence artifact colors) |
| **Data/JSON examples** | Data formats, schemas, payloads | Dark rectangle + colored text (see color palette) |
| **Event/step sequences** | Protocols, workflows, lifecycles | Timeline pattern (line + dots + labels) |
| **UI mockups** | Showing actual output/results | Nested rectangles mimicking real UI |
| **Real input content** | Showing what goes IN to a system | Rectangle with sample content visible |
| **API/method names** | Real function calls, endpoints | Use actual names from docs, not placeholders |

**Example**: For a diagram about a streaming protocol, you might show:
- The actual event names from the spec (not just "Event 1", "Event 2")
- A code snippet showing how to connect
- What the streamed data actually looks like

**Example**: For a diagram about a data transformation pipeline:
- Show sample input data (actual format, not "Input")
- Show sample output data (actual format, not "Output")
- Show intermediate states if relevant

The key principle: **show what things actually look like**, not just what they're called.

---

## Multi-Zoom Architecture

Comprehensive diagrams operate at multiple zoom levels simultaneously. Think of it like a map that shows both the country borders AND the street names.

### Level 1: Summary Flow
A simplified overview showing the full pipeline or process at a glance. Often placed at the top or bottom of the diagram.

*Example*: `Input → Processing → Output` or `Client → Server → Database`

### Level 2: Section Boundaries
Labeled regions that group related components. These create visual "rooms" that help viewers understand what belongs together.

*Example*: Grouping by responsibility (Backend / Frontend), by phase (Setup / Execution / Cleanup), or by team (User / System / External)

### Level 3: Detail Inside Sections
Evidence artifacts, code snippets, and concrete examples within each section. This is where the educational value lives.

*Example*: Inside a "Backend" section, you might show the actual API response format, not just a box labeled "API Response"

**For comprehensive diagrams, aim to include all three levels.** The summary gives context, the sections organize, and the details teach.

### Bad vs Good

| Bad (Displaying) | Good (Arguing) |
|------------------|----------------|
| 5 equal boxes with labels | Each concept has a shape that mirrors its behavior |
| Card grid layout | Visual structure matches conceptual structure |
| Icons decorating text | Shapes that ARE the meaning |
| Same container for everything | Distinct visual vocabulary per concept |
| Everything in a box | Free-floating text with selective containers |

### Simple vs Comprehensive (Know Which You Need)

| Simple Diagram | Comprehensive Diagram |
|----------------|----------------------|
| Generic labels: "Input" → "Process" → "Output" | Specific: shows what the input/output actually looks like |
| Named boxes: "API", "Database", "Client" | Named boxes + examples of actual requests/responses |
| "Events" or "Messages" label | Timeline with real event/message names from the spec |
| "UI" or "Dashboard" rectangle | Mockup showing actual UI elements and content |
| ~30 seconds to explain | ~2-3 minutes of teaching content |
| Viewer learns the structure | Viewer learns the structure AND the details |

**Simple diagrams** are fine for abstract concepts, quick overviews, or when the audience already knows the details. **Comprehensive diagrams** are needed for technical architectures, tutorials, educational content, or when you want the diagram itself to teach.

---

## Container vs. Free-Floating Text

**Not every piece of text needs a shape around it.** Default to free-floating text. Add containers only when they serve a purpose.

| Use a Container When... | Use Free-Floating Text When... |
|------------------------|-------------------------------|
| It's the focal point of a section | It's a label or description |
| It needs visual grouping with other elements | It's supporting detail or metadata |
| Arrows need to connect to it | It describes something nearby |
| The shape itself carries meaning (decision diamond, etc.) | Typography alone creates sufficient hierarchy |
| It represents a distinct "thing" in the system | It's a section title, subtitle, or annotation |

**Typography as hierarchy**: Use font size, weight, and color to create visual hierarchy without boxes. A 28px title doesn't need a rectangle around it.

**The container test**: For each boxed element, ask "Would this work as free-floating text?" If yes, remove the container.

---

## Design Process (Do This BEFORE Writing SVG)

### Step 0: Assess Depth Required
Before anything else, determine if this needs to be:
- **Simple/Conceptual**: Abstract shapes, labels, relationships (mental models, philosophies)
- **Comprehensive/Technical**: Concrete examples, code snippets, real data (systems, architectures, tutorials)

**If comprehensive**: Do research first. Look up actual specs, formats, event names, APIs.

### Step 1: Understand Deeply
Read the content. For each concept, ask:
- What does this concept **DO**? (not what IS it)
- What relationships exist between concepts?
- What's the core transformation or flow?
- **What would someone need to SEE to understand this?** (not just read about)

### Step 2: Map Concepts to Patterns
For each concept, find the visual pattern that mirrors its behavior. Sketches and usage notes for each pattern are in `references/visual-patterns.md`.

| If the concept... | Use this pattern |
|-------------------|------------------|
| Spawns multiple outputs | **Fan-out** (radial arrows from center) |
| Combines inputs into one | **Convergence** (funnel, arrows merging) |
| Has hierarchy/nesting | **Tree** (lines + free-floating text) |
| Is a sequence of steps | **Timeline** (line + dots + free-floating labels) |
| Loops or improves continuously | **Spiral/Cycle** (arrow returning to start) |
| Is an abstract state or context | **Cloud** (overlapping ellipses) |
| Transforms input to output | **Assembly line** (before → process → after) |
| Compares two things | **Side-by-side** (parallel with contrast) |
| Separates into phases | **Gap/Break** (visual separation between sections) |

### Step 3: Ensure Variety
For multi-concept diagrams: **each major concept must use a different visual pattern**. No uniform cards or grids.

### Step 4: Sketch the Flow
Before writing markup, mentally trace how the eye moves through the diagram. There should be a clear visual story.

### Step 5: Build the HTML/SVG
Only now write the file, starting from `references/starter.html`. Lay out on a 20px grid and write down the key coordinates (columns, rows, node centers) before placing anything. **See below for how to handle large diagrams.**

### Step 6: Render & Validate (MANDATORY)
After writing the file, you MUST run the render-view-fix loop until the diagram looks right. This is not optional — see the **Render & Validate** section below for the full process.

---

## Large / Comprehensive Diagram Strategy

**For comprehensive or technical diagrams, build the SVG one section at a time.** Don't write the whole file in one pass. A comprehensive diagram can exceed the per-response output limit, and even when it fits, one section per pass gives each section real attention.

### The Section-by-Section Workflow

**Phase 1: Build each section**

1. **Create the file** from `references/starter.html`: set the `<title>`, the `viewBox`, and add the first section.
2. **Add one section per edit**, each in its own `<g id="sec-...">`. Think about this section's layout, its spacing, and how it connects to what's already there.
3. **Use descriptive ids** (`data-node="trigger"`, `id="sec-backend"`) so cross-section edges are readable: `data-from="trigger" data-to="router"`.
4. **Keep a coordinate plan** in an HTML comment at the top of the svg (column x's, row y's, section bounds). Every later section and every edge reads from it, and it's how you fix spacing without guessing.

**Phase 2: Review the whole**

Read through the complete file and check:
- Does every `data-from`/`data-to` name a `data-node` that exists?
- Is spacing balanced, or are some sections cramped while others are sparse?
- Does the `viewBox` contain everything, with ~40px margin?

**Phase 3: Render & validate** (below).

### Section Boundaries

Plan sections around the natural groupings from your design. A typical large diagram:

- **Section 1**: Entry point / trigger
- **Section 2**: First decision or routing
- **Section 3**: Main content (hero section, may be the largest)
- **Section 4-N**: Remaining phases, outputs, etc.

Each section should be understandable on its own: its elements, internal edges, and any edges to adjacent sections.

### What NOT to Do

- **Don't generate the entire diagram in one response.** It may truncate, and quality drops.
- **Don't delegate the drawing to a subagent.** It won't have this skill's rules in context, and coordination costs more than it saves.
- **Don't write a generator script** (Python/JS that emits the SVG). It adds a layer of indirection between what you see in the PNG and what you edit. Hand-written SVG with descriptive ids is easier to debug. Doing the arithmetic for a coordinate in your head or in a quick calculation is fine; emitting the markup from code is not.

---

## Shape Meaning

Choose shape based on what it represents—or use no shape at all:

| Concept Type | Shape | Why |
|--------------|-------|-----|
| Labels, descriptions, details | **none** (free-floating text) | Typography creates hierarchy |
| Section titles, annotations | **none** (free-floating text) | Font size/weight is enough |
| Markers on a timeline | small `<circle>` (10-20px across) | Visual anchor, not container |
| Start, trigger, input | `<ellipse>` | Soft, origin-like |
| End, output, result | `<ellipse>` | Completion, destination |
| Decision, condition | diamond `<polygon>` | Classic decision symbol |
| Process, action, step | `<rect rx="8">` | Contained action |
| Abstract state, context | overlapping `<ellipse>`s | Fuzzy, cloud-like |
| Hierarchy node | lines + text (no boxes) | Structure through lines |

**Rule**: Default to no container. Add shapes only when they carry meaning. Aim for <30% of text elements to be inside containers.

---

## Color as Meaning

Colors encode information, not decoration. Every color choice should come from `references/color-palette.md` — the semantic shape colors, text hierarchy colors, and evidence artifact colors are all defined there.

**Key principles:**
- Each semantic purpose (start, end, decision, AI, error, etc.) has a specific fill/stroke pair
- Free-floating text uses color for hierarchy (titles, subtitles, details — each at a different level)
- Evidence artifacts (code snippets, JSON examples) use their own dark background + colored text scheme
- Always pair a darker stroke with a lighter fill for contrast

**Do not invent new colors.** If a concept doesn't fit an existing semantic category, use Primary/Neutral or Secondary.

---

## Modern Aesthetics

For clean, professional diagrams:

### Stroke Width
- `stroke-width: 1` — Thin, elegant. Good for lines, dividers, subtle connections.
- `stroke-width: 2` — Standard. Good for shapes and primary arrows.
- `stroke-width: 3` — Bold. Use sparingly for emphasis (main flow line, key connections).

### Opacity
**Never use `opacity` or translucent fills.** Use color, size, and stroke width to create hierarchy instead of transparency.

### Small Markers Instead of Shapes
Instead of full shapes, use small dots (10-20px circles) as:
- Timeline markers
- Bullet points
- Connection nodes
- Visual anchors for free-floating text

---

## Layout Principles

### Hierarchy Through Scale
- **Hero**: 300×150 - visual anchor, most important
- **Primary**: 180×90
- **Secondary**: 120×60
- **Small**: 60×40

### Whitespace = Importance
The most important element has the most empty space around it (200px+).

### Flow Direction
Guide the eye: typically left→right or top→bottom for sequences, radial for hub-and-spoke.

### Connections Required
Position alone doesn't show relationships. If A relates to B, there must be an arrow.

---

## SVG Mechanics

### The Page

- Start from `references/starter.html`. Keep its `<style>` block; add classes only for things the palette defines.
- **One root: `<svg id="diagram">`**, with the `viewBox` width equal to the `width` attribute (e.g. `viewBox="0 0 1200 760" width="1200" height="760"`) so it draws 1:1. Typical widths: 800-1000 for simple diagrams, 1200-1400 for comprehensive ones.
- Give the svg a `<title>` that states what the diagram argues (screen readers announce it).
- **Self-contained:** no external fonts, scripts, stylesheets, or images. The font stacks in the starter use locally installed fonts. If the user wants a web font, ask, since it breaks the self-contained property.

### Markup Conventions (The Lint Depends on These)

| Markup | Meaning | What the lint checks |
|--------|---------|---------------------|
| `<g data-node="id">` + one shape + its `<text>` | A thing that arrows connect to | Text fits inside the shape; shape doesn't overlap other nodes |
| `data-shape` on an element inside a node | Which element is the node's outline, when the first shape isn't | (selects the shape for the checks above) |
| `<g data-region="id">` | A section boundary (dashed outline, may contain nodes) | Excluded from overlap checks |
| `<path data-edge data-from="a" data-to="b">` | A connector | Ends land on their nodes; path doesn't run through any node; warns if it crosses text |
| `marker-end` on a `data-edge` | An arrowhead | Warns when two arrowheads land on the same point (they merge into a blob) |
| any `<text>` | | Doesn't overlap other text; isn't clipped by the viewBox; renders ≥ 11px |

Evidence artifacts (code blocks, JSON samples) should be `data-node`s too, so their text is checked for overflow.

### Text

- SVG text doesn't wrap. Break lines yourself: `<text x="300" y="100"><tspan x="300" dy="0">first line</tspan><tspan x="300" dy="20">second</tspan></text>`.
- Size containers before rendering with rough widths: sans 15px ≈ 8px per character, mono 13px ≈ 8px per character. Then add 24px of horizontal padding. The lint catches what the estimate misses.
- Centered labels: classes `center` (`text-anchor: middle; dominant-baseline: central`) with x/y at the shape's center.
- Text on a dark fill: add class `on-dark`.
- Label on or beside an edge: give it a halo so it stays legible where it touches the line: `style="paint-order: stroke; stroke: #fff; stroke-width: 4px;"`.
- Font sizes: title 26, section heading 17, node label 15, body 14, code 13. Nothing below 12.

### Arrows

- Draw edges as `<path>` with `marker-end="url(#arrow)"`. The starter's markers put the arrowhead tip exactly at the path's last point, so **end the path on the target's boundary**, not its center.
- Boundary points: rect → the edge's midpoint (`x + w/2, y`); ellipse at (cx, cy) with radii rx, ry → `(cx ± rx, cy)` or `(cx, cy ± ry)`; diamond → its four tips.
- When several arrows converge on one node, spread their endpoints 12-16px apart along its edge; arrowheads meeting at one point merge into a blob.
- Prefer straight or orthogonal routes (`M x1,y1 L x2,y1 L x2,y2`). To route around something, add a corner, not a curve. Use a cubic curve (`C`) only for loops/cycles where a curve is the meaning.
- Each arrow color needs its own `<marker>`; the starter has `#arrow` (primary) and `#arrow-slate`. Copy one and change its fill to add a semantic color.

### Code Blocks and Data Samples

`<rect class="s-code" rx="6">` with `<text class="t-code">` lines as `<tspan x="…" dy="20">`s. The starter sets `white-space: pre` on `.t-code tspan` so indentation survives. Keep it on the tspans, not the `<text>`: on the `<text>` it also preserves the newlines between tspans in your markup and every line grows wider. For syntax color, set `fill` per `<tspan>` (keys, strings, comments). Data/JSON samples use `--code-data` green per the palette.

---

## Render & Validate (MANDATORY)

You cannot judge a diagram from its markup. After writing or editing the file, screenshot it, look at the PNG, read the lint, and fix, in a loop until it's right. This is part of the workflow, not a final check.

### How to Render

```bash
uv run .claude/skills/html-diagram/scripts/render.py path/to/diagram.html
```

It writes `path/to/diagram.png` next to the HTML (`-o` to change), prints the path, then a lint report. Exit code 1 means the lint found errors. Then use the **Read tool on the PNG** to look at it.

Useful flags: `--scale 1` for a faster, smaller image; `--width 700` to see how it reads on a narrow screen; `--json` for machine-readable lint.

**The lint is a second pair of eyes, not the judge.** It finds geometric defects that are easy to miss at screenshot scale (an arrowhead 6px short, a label 2px into a border). It can't tell whether the diagram makes sense. A clean lint with a confusing picture is not done.

### The Loop

**1. Render & view.** Run the script, Read the PNG, read the lint output.

**2. Audit against your original design.** Before hunting bugs, compare the picture to Steps 1-4:
- Does the visual structure match the conceptual structure you planned?
- Does each section use the pattern you intended (fan-out, convergence, timeline...)?
- Does the eye move through the diagram in the order you designed?
- Is the hierarchy right: hero elements dominant, supporting elements smaller?
- For technical diagrams: are the evidence artifacts readable and next to what they illustrate?

**3. Check for visual defects** (lint errors first, then by eye):
- Text clipped by or overflowing its container
- Text or shapes overlapping
- Arrows running through elements instead of around them
- Arrows landing on the wrong element, stopping short, or pointing into empty space
- Labels floating ambiguously (not clearly attached to what they describe)
- Uneven spacing between elements that should be evenly spaced
- Cramped sections next to sparse ones
- Text too small to read
- A lopsided composition

**4. Fix.** Edit the HTML. Common fixes:
- Widen a shape (and recenter its text) when text overflows
- Move a node by editing its coordinates, then update every edge that touches it (search for its id in `data-from`/`data-to`)
- Add a corner to a path to route around a node
- Move a label closer to what it describes
- Grow the `viewBox` when something is clipped

**5. Re-render & re-view.**

**6. Repeat** until it passes both the design audit and the defect check. Usually 2-4 rounds. Don't stop at "no lint errors" if the composition could be better.

### When to Stop

- The picture matches the conceptual design
- The lint reports 0 errors, and every remaining warning is one you've looked at and judged harmless
- Arrows route cleanly and connect to the right elements
- Spacing is consistent and the composition is balanced
- You'd show it to someone without caveats

Deliver the `.html` (the diagram) and mention the `.png` (the preview).

### Setup

`uv` installs Playwright automatically on first run (the script declares its dependency inline). It needs a Chromium: if the script reports it can't launch one, run `uv run --with playwright playwright install chromium`, or point it at an existing Chrome/Chromium with `--chromium PATH` or `HTML_DIAGRAM_CHROMIUM=PATH`. The script also falls back to a `chromium`/`google-chrome` on PATH.

---

## Quality Checklist

### Depth & Evidence (Check First for Technical Diagrams)
1. **Research done**: Did you look up actual specs, formats, event names?
2. **Evidence artifacts**: Are there code snippets, JSON examples, or real data?
3. **Multi-zoom**: Does it have summary flow + section boundaries + detail?
4. **Concrete over abstract**: Real content shown, not just labeled boxes?
5. **Educational value**: Could someone learn something concrete from this?

### Conceptual
6. **Isomorphism**: Does each visual structure mirror its concept's behavior?
7. **Argument**: Does the diagram SHOW something text alone couldn't?
8. **Variety**: Does each major concept use a different visual pattern?
9. **No uniform containers**: Avoided card grids and equal boxes?

### Container Discipline
10. **Minimal containers**: Could any boxed element work as free-floating text instead?
11. **Lines as structure**: Are tree/timeline patterns using lines + text rather than boxes?
12. **Typography hierarchy**: Are font size and color creating hierarchy (reducing the need for boxes)?

### Structural
13. **Connections**: Every relationship has an arrow or line
14. **Flow**: Clear visual path for the eye to follow
15. **Hierarchy**: Important elements are larger/more isolated

### Technical
16. **Self-contained**: One `.html` file, no external requests (the lint warns on any)
17. **Conventions**: Every node is a `data-node`, every connector a `data-edge` with `data-from`/`data-to`
18. **Colors from the palette only**, via the starter's classes/tokens
19. **No opacity or translucent fills**
20. **Container ratio**: <30% of text elements inside containers
21. **Accessible name**: the svg's `<title>` states what the diagram argues

### Visual Validation (Render Required)
22. **Rendered and viewed**: You have Read the latest PNG
23. **Lint clean**: 0 errors; warnings reviewed
24. **Even spacing**: Similar elements have consistent spacing
25. **Arrows land correctly**: on the intended element, without crossing others
26. **Readable**: Text is legible in the PNG at scale 1
27. **Balanced composition**: No large empty voids or overcrowded regions

---

*Design methodology adapted from [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill); the HTML/SVG output, conventions, and render/lint script are specific to this skill.*
