# HOLLER — Logo System Usage Note, Rationale & Deliverable Manifest

- **Public Asset Repository (Direct Browsable SVGs & PNGs):** https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/holler-logo-system
- **Comparison Sheet Evidence (`16 px` Mark & `160 px` Lockup on Light, Dark & Video Still):** `holler-comparison-sheet.png`

---

## 1. Design Rationale (Tied to Audience & "No Red Record Dot" Brief)

**Audience & Core Idea:** Holler is built for internet-native gaming and creator-culture fans (ages 18–30) where being the loudest, most electric voice in the arena is the whole point. Startup minimalism reads as quiet; a fan-culture platform needs **arcade-meets-arena physical weight** that punches through stream overlays, Discord/social avatars, and dark browser tabs.

1. **Moving Away from the Red Record Dot ("Camera-On" Fix):**
   - A red circular dot in a desktop browser tab or app header triggers immediate user anxiety ("Is my webcam or mic recording while I forgot this tab was open?").
   - Instead of a recording dot, our **Standalone Mark ("The Megaphone-H")** builds the concept of *voice* directly into the architecture of the letter **H**: the left pillar is a planted stadium column (`8°` forward slant), while the right pillar flares outward like a **stadium megaphone horn** projecting **twin angular sonic shockwave chevrons (`))`)** in Electric Yellow (`#FFD60A`) and Cyber Green (`#39FF6A`).
   - There are **zero circles and zero red dots** anywhere in the system—even the interior counter of the letter **O** in `HOLLER` is an angular stadium diamond cut.
2. **Arcade-Meets-Arena Chunky Letterforms:**
   - All six letters (`H-O-L-L-E-R`) are custom-drawn from scratch using heavy geometric polygon paths (`<path>`) with an `8°` forward lean, hard-edge arcade drop extrusions (`#FF2BD6` Magenta & `#0A9BFF` Azure), and an Electric Yellow (`#FFD60A`) focal `O` that anchors the center of the wordmark.
3. **Micro-Scale Legibility (`16 px` & `160 px`):**
   - Because the standalone mark uses wide interior counters and three high-contrast geometric shapes (`H` + two angled sonic wave bars inside a `#070B14` stadium badge), it remains unmistakably recognizable at **16×16 px** in a browser tab.
   - The primary lockup uses a compact `3.75 : 1` aspect ratio (`1920 × 512` viewBox) with generous tracking and thick strokes so `HOLLER` reads cleanly at **160 px wide (`43 px` tall)** across light, dark, and noisy video backgrounds.

---

## 2. One-Page Usage Note

### A. Color Palette
| Role | Name | Hex | RGB | Usage |
|---|---|---|---|---|
| **Primary Brand Fill** | **Arcade Azure** | `#0A9BFF` | `rgb(10, 155, 255)` | Main `H` mark face, pill border rim, even-letter arcade extrusions |
| **Neon Edge Kick** | **Hyper Magenta** | `#FF2BD6` | `rgb(255, 43, 214)` | 3D arcade drop-shadow extrusion & crown accent |
| **Sonic Burst 1** | **Electric Yellow** | `#FFD60A` | `rgb(255, 214, 10)` | Inner sonic wave chevron & focal `O` letterform |
| **Sonic Burst 2** | **Cyber Green** | `#39FF6A` | `rgb(57, 255, 106)` | Outer sonic wave chevron & wordmark energy baseline |
| **Arena Surface** | **Near-Black** | `#070B14` | `rgb(7, 11, 20)` | Primary dark canvas, stadium badge backing, and Single-Color mark |
| **Reversed Fill** | **Pure White** | `#FFFFFF` | `rgb(255, 255, 255)` | Wordmark front faces and Reversed monochrome variant |

### B. Clear Space & Minimum Size
- **Clear Space (`X`-Unit Rule):** Let `X` equal the width of the left pillar of the `H` (or `25%` of the standalone mark's total height). Maintain at least **`1X` (`0.25 × height`)** of unobstructed clear space around all four sides of the mark and lockup.
- **Minimum Sizes:**
  - **Standalone Mark:** **`16 × 16 px`** minimum (browser favicons, mobile status indicators, compact stream HUD bugs).
  - **Primary Lockup:** **`160 px` wide (`43 px` tall)** minimum (app navigation headers, video lower-thirds, merch tags).

### C. Background Pairing Rules
1. **Dark Backgrounds (`#070B14` to `#1E293B`):** Use `holler-lockup-full-color` / `holler-mark-full-color` (primary) or `holler-lockup-reversed` / `holler-mark-reversed` (monochrome white).
2. **Light Backgrounds (`#FFFFFF` to `#E2E8F0`):** Use `holler-lockup-full-color` (whose built-in `#070B14` stadium pill preserves the neon edge contrast on white) or `holler-lockup-single-color` / `holler-mark-single-color` (`#070B14` monochrome).
3. **Busy Video / Live Stream Overlays:** Use `holler-lockup-full-color` or `holler-mark-full-color` (the self-contained `#070B14` stadium badge with `#0A9BFF` rim shields the letterforms from explosions, stage lights, and chroma noise), or place `holler-lockup-reversed` over a `rgba(7, 11, 20, 0.78)` pill scrim.

### D. Originality & Third-Party Asset / Font License Disclosure
- **Logo Vector Artwork (`holler-mark-*.svg` & `holler-lockup-*.svg`):** **100% original custom-drawn geometric vector `<path>` outlines created from scratch** specifically for this brief. Zero third-party fonts, zero stock vectors, zero templates, and zero traced assets are used in any logo file.
- **Comparison Sheet Annotations (`holler-comparison-sheet.png`):** Labels on the evidence comparison sheet are rendered using standard Windows system UI fonts (`Segoe UI` and `Consolas`); the logo files themselves contain **zero `<text>` or font dependencies**.

---

## 3. Complete File Inventory (All 26 Deliverable Files Included)

### Editable Vector Sources & SVGs (6 Files)
1. `holler-mark-full-color.svg` — Standalone Mark (Full-Color)
2. `holler-mark-single-color.svg` — Standalone Mark (Single-Color `#070B14`)
3. `holler-mark-reversed.svg` — Standalone Mark (Reversed `#FFFFFF`)
4. `holler-lockup-full-color.svg` — Primary Lockup (Full-Color)
5. `holler-lockup-single-color.svg` — Primary Lockup (Single-Color `#070B14`)
6. `holler-lockup-reversed.svg` — Primary Lockup (Reversed `#FFFFFF`)

### Transparent PNG Exports at 512 px, 1024 px, and 2048 px (18 Files)
7. `holler-mark-full-color-512.png` (`512 × 512 px`, transparent RGBA)
8. `holler-mark-full-color-1024.png` (`1024 × 1024 px`, transparent RGBA)
9. `holler-mark-full-color-2048.png` (`2048 × 2048 px`, transparent RGBA)
10. `holler-mark-single-color-512.png` (`512 × 512 px`, transparent RGBA)
11. `holler-mark-single-color-1024.png` (`1024 × 1024 px`, transparent RGBA)
12. `holler-mark-single-color-2048.png` (`2048 × 2048 px`, transparent RGBA)
13. `holler-mark-reversed-512.png` (`512 × 512 px`, transparent RGBA)
14. `holler-mark-reversed-1024.png` (`1024 × 1024 px`, transparent RGBA)
15. `holler-mark-reversed-2048.png` (`2048 × 2048 px`, transparent RGBA)
16. `holler-lockup-full-color-512.png` (`512 × 137 px`, transparent RGBA)
17. `holler-lockup-full-color-1024.png` (`1024 × 273 px`, transparent RGBA)
18. `holler-lockup-full-color-2048.png` (`2048 × 546 px`, transparent RGBA)
19. `holler-lockup-single-color-512.png` (`512 × 137 px`, transparent RGBA)
20. `holler-lockup-single-color-1024.png` (`1024 × 273 px`, transparent RGBA)
21. `holler-lockup-single-color-2048.png` (`2048 × 546 px`, transparent RGBA)
22. `holler-lockup-reversed-512.png` (`512 × 137 px`, transparent RGBA)
23. `holler-lockup-reversed-1024.png` (`1024 × 273 px`, transparent RGBA)
24. `holler-lockup-reversed-2048.png` (`2048 × 546 px`, transparent RGBA)

### Comparison Evidence, Usage Note & Complete Bundle (3 Files)
25. `holler-comparison-sheet.png` — Side-by-side comparison sheet at `16 px` (mark) and `160 px` (lockup) on Light, Dark, and Busy Video Still + browser tab preview + file list
26. `HOLLER-USAGE-NOTE-AND-RATIONALE.md` — One-page usage note, rationale, license disclosure & file manifest
27. `holler-logo-system-complete.zip` — Complete ZIP archive containing all 26 files above
