# Claude Independent Visual Review — Response

**Date:** 2026-09-27
**Workspace:** `claude/beastagotchi-visual-review-2026-09-27`
**Responds to:** `collaboration/claude/BEASTAGOTCHI_VISUAL_REVIEW_REQUEST_2026-09-27.md`
**Status:** advisory input to the owner / OpenAI / Claude discussion. No production code changed.

**Code reviewed:** the five Experience renderers (`beastui/experience_{atlas,forge,observatory,habitat,monolith}.py`), shared `design.py` / `components.py` / `experience_registry.py`, the runtime `engine.py` / `pages.py` / `home_scenes.py`, and the proof tools. The five renderer files are byte-identical on this branch (`c1a10ac`), `v0.19-unified-experience` (`c425deb`) and `openai/v019-architecture-foundation-tranche1` (`0abb0af`), so this review applies to all three. The unmerged creature-led Beast page on `openai/v019-beast-page-fidelity` (`28c5d38`) was also rendered.

---

## TL;DR

1. **The structural goal was achieved; the shared layer was bypassed.** The five bodies really are different grammars. But none of the five renderers imports the shared `design.py` tokens or `components.py`. What must be *identical* across Experiences — how truth is rendered, how you navigate, how problems surface, how big text is, who the creature is — is re-invented (or missing) in each file.
2. **The truth model is violated in the pixels, and CI can't see it.** A canned route polyline is labelled `ROUTE // LIVE`, `RF FABRIC ONLINE` is printed in green during a total radio failure, `QUALITY: CAPTURED` is hard-coded, and every unknown value renders as `0`. CI renders one healthy fixture that never reaches those branches.
3. **Most text is physically unreadable on the 3.5" panel.** 82% of text-size call sites are ≤9 px; 7 px text subtends 4.4 arcminutes at arm's length, below the ~5′ limit of 20/20 acuity.
4. **The Experiences can't run on the TFT yet.** `engine.py` has no Experience path, and the Experience pages have no navigation or touch map (1 touch declaration across 10 pages) while occupying the band the shared nav footer uses. Gate 1's physical session needs integration work, not "physical-only fixes".
5. **Recommendation:** build a thin shared **Beast shell** (status sentence, nav rail, attention ladder, Readings/truth states, type ramp, touch map, one creature rig), give each Experience its own paint for it, and keep total freedom in the body. Three changes carry most of the value (§6).

My ranking of the current Homes, closest to final first: **Monolith › Habitat › Atlas › Observatory › Forge**.

---

## How I reviewed (so every claim can be checked)

- **Docs:** the five required docs, plus the Experience prototype briefs, North Star archive, gate status and fidelity-pass notes.
- **Code:** all five renderers line by line, the shared tokens and components, the registry, and how `engine.py` and `beaststudio/server.py` consume (or don't consume) the Experiences.
- **Pixels, not layout:** I rendered all 10 registered pages through `render_experience_page()` under seven states — the sanitized real capture CI uses, plus six **synthetic review states** derived from it (GPS route short/long, busy 2.4 GHz air, low battery, critical fault, cold-boot unknown). They are labelled synthetic everywhere and exist only to reach branches the single CI fixture never reaches. Tool: `collaboration/claude/tools/experience_state_matrix.py`.
- **Comparison:** current TFT runtime frames (via `tools/render_v019_ux_gallery.render()` against a scratch copy of `beastui/`), and the unmerged Beast page.
- **Physics:** legibility from the real panel geometry (480×320 over 3.5″ = 165 ppi, 0.154 mm pitch), measured DejaVu Sans cap heights, and WCAG contrast (also after RGB565 quantization).
- **Not done:** I have not seen the physical TFT. The Pi remains final visual truth. Appendix C gives a 480×320 test card to settle type size on the real panel in minutes.

Evidence images are in `collaboration/claude/visual-review-2026-09-27/` (index in Appendix B).

---

## 1. Strongest 10 observations

### 1. Hard-coded truth claims ship in the pixels, invisible to CI
- **Atlas** draws a fixed zig-zag labelled `ROUTE // LIVE` whenever GPS has a fix (`experience_atlas.py:229–230`). I rendered a 42-point / 1.84 km route and a 400-point / 12.4 km route: the field canvas is **pixel-identical** (diff bbox = none; only the margin distance text differs). Evidence `03`.
- **Forge** prints `RF FABRIC ONLINE` in OK-green unconditionally (`experience_forge.py:206`). It still says so with Pwnagotchi and Bettercap failed and no radio. `POLICY GUARDS ACTIVE` is also unconditional (`:424`). Evidence `01`.
- **Observatory Spectrum** prints `QUALITY: CAPTURED` unconditionally (`experience_observatory.py:375`). It would be wrong for live data.

These survive because CI renders one healthy, no-GPS-fix fixture. **The review process is the blind spot, not only the code.**

### 2. Unknown renders as zero, everywhere
Every renderer has a `_i`/`_f` (`_ival`/`_fval`) helper that defaults to `0`. On a cold boot you get `0 C`, `00%`, `CH 00`, `00°`, level `0`, and `0 ATTENTION` next to a red lamp. The worst case is semantic: with the radio down, `0 NEARBY` and an empty spectrum axis *assert* "there is nothing here". This directly contradicts "Unknown remains unknown". Evidence `02`.

### 3. The type scale is below physical legibility for this panel
Of 181 text-size call sites in the five renderers, **82% are ≤9 px and 71% are ≤8 px**. The renderers hard-code sizes rather than using the tokens, and the tokens themselves define `font_micro=6`, `font_tiny=7`.

| DejaVu Sans | cap height | at 60 cm (arm's length) | at 35 cm (in hand) |
|---:|---:|---:|---:|
| 7 px | 0.77 mm | **4.4′** | 7.6′ |
| 9 px | 1.08 mm | 6.2′ | 10.6′ |
| 11 px | 1.23 mm | 7.1′ | 12.1′ |
| 15 px | 1.70 mm | 9.7′ | 16.6′ |
| 18 px | 2.00 mm | 11.5′ | 19.7′ |
| 24 px | 2.77 mm | 15.9′ | 27.2′ |
| 30 px | 3.39 mm | 19.4′ | 33.3′ |

20/20 acuity resolves about 5′. Common display-ergonomics guidance (ISO 9241-303 / ANSI-HFES 100) puts comfortable character height around 16–22′. So only **24–30 px** reads at arm's length, and **15–18 px** reads in hand. The current UI carries primary meaning (GPS state, mood, fault, provenance) at 7–8 px.

### 4. There is no shared alarm language
In the synthetic critical-fault state (Pwnagotchi/Bettercap failed, 81 °C, SURVIVAL):
- **Atlas:** the Home looks nominal. The companion sketch is pixel-identical to the healthy state and keeps smiling (`beast.expression="fault"` falls through to the default smile); only its 7 px caption changes.
- **Habitat:** the creature is essentially unchanged: 95 of 48,840 creature-region pixels (0.2%) differ, a small mouth arc. `CRITICAL` is 8 px in the corner.
- **Forge:** claims the RF fabric is online.
- **Monolith:** only the Overview page says `CRITICAL` at a readable size.

Each renderer computes "health" its own way. Evidence `01`.

### 5. The Experiences have no navigation or touch model
Across 10 pages there is exactly one declared touch target (`experience_monolith.py:274`, "hold for detail"). There is no prev/next, Home or page index.

The Experiences also draw their own content in y ≈ 277–320, which is exactly where the shared footer lives (`TOKENS.footer_y=278`). Integration will collide.

Meanwhile the **current runtime already has the project's best interaction asset**: a nav rail with *named* prev/next targets (`‹ EXPEDITION` … `SYSTEM ›`), a group label (`IDENTITY · 1/11`) and page dots. Evidence `06`.

### 6. The Experiences are not wired into the device (planning risk)
`beastui/engine.py` never imports `experience_registry`; only Beast Studio, the proof tools and tests do. The gate docs already say TRY ON has "no physical executor", but the roadmap's V19-2 → V19-3 sequence ("stage → physical session → fix only physical findings") assumes something Experience-shaped can run on the TFT. It can't yet, and building that is real design and integration work. This needs an owner decision (§7.1).

### 7. The creature is five unrelated drawings with a broken input — but the brand exists
- **Different creatures:** a sketch cat (Atlas), a `BEAST` text hexagon (Forge, whose registered mood/level signals draw nothing), a faceted optic (Observatory), a portrait (Habitat), and a bust (Monolith).
- **Drift within one Experience:** Habitat Home and Habitat Beast draw *different* creatures (different eyes and muzzle).
- **Two competing moods on screen:** `pwnagotchi.mood` and `beast.expression`, e.g. Habitat's strip shows `AWAKE … GPS SEARCH`.
- **No link to identity:** roster, heritage and face packs don't reach any Experience.
- **Broken input:** `beast.expression` is effectively stuck on `gps-searching` / `hunting` because of the personality cascade (see Appendix D). The fixture itself shows `gps-searching`.

**The good news:** Habitat, Monolith, the legacy raster portraits and LCARS all share one **pointed-ear head silhouette**; that is a real brand anchor. And **Monolith's eye glint is health-coloured**, which proves "creature body language = truth" already works.

### 8. Identity is spent on the wrong pixels
- **Wordmark headers:** `ATLAS`, `FORGE` and `OBSERVATORY` wordmarks take the most prominent pixels on every page. The user chose the Experience; they don't need reminding.
- **Truth by caption:** truth is asserted in 7–8 px disclaimers (`DIAGRAMMATIC, NOT GEOGRAPHIC`, `NO SYNTHETIC HISTORY`, `LIVE CANONICAL STATE`) rather than by design. These are developer-facing sentences on a consumer surface.
- **Self-contradiction:** Atlas draws a north-pointing compass rose on the very diagram it captions "not geographic", and the compass ignores `gps.heading_deg`.

### 9. Decoration imitates instruments
- **Forge:** heat-sink fins, braces, fasteners, a `RF COUPLER` label, three *unlabelled* port icons, and a "frequency ruler" whose ticks mean nothing.
- **Atlas:** terrain contours that drift with `phase`. On a map, moving contours read as moving ground.
- **Observatory:** tick marks with no values.
- **Habitat:** decorative circles that look like tappable buttons, next to informational circles that aren't.
- **Colour misuse:** Atlas uses its alert colour for `GPS SEARCHING`, a normal indoor state, which trains the eye to ignore alert colour.

The prototype brief already says it: *"ornamental machinery with no informational role"* is to be avoided.

### 10. The bodies are genuinely distinct, and several motifs are strong
All 70 renders (10 pages × 7 states, including cold boot and critical fault) completed without exceptions. That is real robustness.

The structural diversification succeeded: in grayscale these are five different silhouettes. Strong, keepable motifs:
- **Monolith:** restraint, sculpture and a single fact line.
- **Habitat:** creature-first composition with "habitat objects as instruments".
- **Atlas:** ruled notebook margin plus the bottom expedition ledger.
- **Observatory:** open axes and the observer-in-a-lens.
- **Forge:** the one-chassis-plus-bus metaphor and the Doctor fault lamp.

The problems are overwhelmingly in the layer that should have been shared. That is good news, because it's fixable once rather than five times.

---

## 2. Retain / modify / reject — major current motifs

| Motif | Where | Verdict | Why / how |
|---|---|---|---|
| Nav rail: named prev/next + group + dots | runtime `engine` footer | **RETAIN → promote** | Best learnability asset in the product. Make it the shared nav primitive, painted natively per Experience. |
| Experience wordmark header | all five | **MODIFY** | Replace with the status sentence (§3.3). Show the Experience name only on switch and in the Control Center. |
| Microtext truth disclaimers | Atlas, Observatory | **REJECT** | Replace with Reading quality states and a page-level watermark (§3.2). |
| Field canvas + ruled margin + bottom ledger | Atlas | **RETAIN** | Right structure. The ledger moves up one band to make room for the nav rail. |
| Terrain contour lines (animated) | Atlas | **MODIFY** | Static paper texture only; never animated; never terrain unless backed by elevation data. |
| Compass rose | Atlas | **REJECT** unless bound | Only when `gps.heading_deg` is real and moving. Never on a non-geographic diagram. |
| `ROUTE // LIVE` polyline | Atlas | **REJECT** | Replace with the real `expedition_points` path, scaled to fit (or the self-revealing grid, §4). |
| Relative RF "channel→bearing" scatter | Atlas home/recon | **MODIFY** | The index term (`:106`, `:338`) makes positions reorder-dependent and the legend false. Use a ranked nearby list, or a stable key and no "bearing" wording. |
| Sketch companion | Atlas | **RETAIN style / MODIFY** | Drive it from the shared rig and `beast.expression`; enlarge to about 90 px; never smile through a fault. |
| One chassis + machine bus | Forge | **RETAIN** | Strong metaphor. Bus segments should light for *real* links (radio, GPS USB, UPS I²C), not a phase pulse. |
| Ornaments (fins, braces, fasteners, coupler, unlabelled ports, tick ruler) | Forge | **REJECT** | No informational role, and they produce the text collisions. Labelled ports only. |
| Big channel numeral | Forge | **RETAIN** | But `NO RADIO`, not `00`, when unknown or down. |
| `BEAST` hexagon emblem | Forge | **REJECT** | Replace with the creature as the machine core: the rig's eyes inside the core. |
| Doctor fault lamp | Forge | **RETAIN → promote** | Bigger, tappable, and leads to evidence. Forge is where Doctor should feel native. |
| Open scientific axes | Observatory | **RETAIN / MODIFY** | Add tick values and units (dBm), and use a split-band channel axis (§4). |
| Observer-in-a-lens creature | Observatory | **RETAIN** | Best "secondary creature" in the set. Let its gaze point at the plotted datum it's reacting to. |
| Provenance margin | Observatory | **MODIFY** | Put real provenance there (source, age, sample rate, capture date). Move CPU/MEM out; they aren't provenance. |
| Band-distribution strip | Observatory | **MODIFY** | Prefer real history (channel_history samples) as the secondary region. |
| Creature-first composition | Habitat | **RETAIN** | The right answer for Habitat. |
| Informational "stones" (TODAY / MEMORY) | Habitat | **RETAIN / MODIFY** | Fix labels: `TODAY` counts per Core session, not per day. Give tappable objects a visible handle. |
| Decorative circles / nodes | Habitat | **MODIFY** | Fewer, and visually unlike tappable objects. |
| Growth vine / path | Habitat | **MODIFY** | Say what it measures: `LV 7 → 8 · 75%`. |
| Sculptural bust + plinth | Monolith | **RETAIN** | Closest thing to a finished product surface. |
| Health-coloured eye glint | Monolith | **RETAIN → generalize** | The model for the body-language contract (§3.7). |
| Single fact line | Monolith | **RETAIN** | Centre it properly (the Overview fact row sits about 20 px right of centre), and always make it the most important truth. |
| "HOLD FOR DETAIL" | Monolith | **MODIFY → universal** | Make Inspect a shared gesture on every Reading, with a consistent affordance. |
| Pointed-ear head silhouette | Habitat, Monolith, legacy portraits, LCARS | **RETAIN as brand anchor** | Formalize it as the canonical creature rig. |
| Raster concept portraits | runtime Classic / Cyberpunk / Black Ice | **RETAIN for legacy themes** | The most evocative creature art in the repo. Use as the art-direction target for the rig's expression set. |
| Scanline drawn above overlays | runtime `engine.py:2249–2254` | **REJECT over content** | It sweeps through Apps, Control Center and other modal text. Decorative sweeps belong under content. |
| 6–8 px type; `font_micro` / `font_tiny` tokens | tokens, all five | **REJECT on TFT** | Physically illegible (§1.3). Keep only for Studio. |

---

## 3. Shared design-system primitives — "the Beast shell"

**Principle: consistency lives in semantics and geometry; freedom lives in paint.** Every Experience renders the same primitives with the same meaning, the same hit zones and the same priorities, but in its own material. Inside the body it may do anything that stays truthful.

### 3.1 Frame geometry (480×320)

| Band | y | Contents | Hit zone |
|---|---|---|---|
| Status line | 0–32 | status sentence (Read tier) + ≤3 lamps | 0–44: tap = "why?" sheet (Doctor when attention exists) |
| Body | 32–272 | Experience-owned composition | per-Experience declared zones, each ≥48 px |
| Nav rail | 272–320 | prev · page index · next | thirds: 0–144 / 144–336 / 336–480 |

The rail is 48 px because `touch_min` is 48. Today's `footer_h=42` contradicts the project's own touch token. On critical attention, the status line may grow to 0–56 (§3.4). Monolith may paint the rail as a hairline plus dots, **but its hit zones stay identical**. Navigation can recede visually without becoming unlearnable.

### 3.2 Readings and truth states (answers Q8)

Replace every `_i` / `_f` / `_ival` / `_fval` with one shared `Reading = (value | None, quality, age, source)` and one formatter.

| Quality | Rendering rule |
|---|---|
| LIVE | normal |
| DERIVED / ESTIMATED | `≈` prefix (e.g. `≈23%` battery estimate) |
| STALE (older than freshness budget) | value dimmed plus age, e.g. `48C · 4m` |
| UNKNOWN (not reported yet) | `—` in the value slot, same size, `unknown` colour. **Never 0.** |
| ABSENT capability (no UPS, no GPS) | **reflow**: the slot disappears or becomes a short "add…" hint. Absence is layout, not an error. |
| CAPTURED / REPLAY / SIMULATED | page-level watermark in the status line (e.g. `CAPTURED 2026-09-22`), never per value |
| SOURCE DOWN (radio / collector failed) | the dependent plot or count says `NO SOURCE` rather than drawing empty axes or `0` |

Status words (`ONLINE`, `ACTIVE`, `READY`, `LIVE`, `CAPTURED`) come only from a status vocabulary function keyed on state. **Literal status strings in renderers are forbidden** and can be linted for.

In one line: **absent → reflow; unknown → dash; old → dim + age; source down → say so; never zero.**

### 3.3 Status sentence (answers Q7)

One plain-language line, generated by a shared function from canonical state and painted by the Experience, answering *"what is happening?"* at Read tier (15–18 px). Priority order: critical cause › warning › activity › idle. Examples:

- `Watching · 6 nearby · 2 new`
- `No GPS fix · 3 satellites`
- `Walking · 1.8 km · 12 new`
- `Docked · charging 64%`
- `Pwnagotchi stopped · tap for Doctor`

It is presentation-only (like template tokens, it never polls and never becomes a second source of truth). Every Experience shows the **same sentence** for the same state.

### 3.4 Attention ladder (shared, non-optional)

| Level | Status line | Creature | Body | Rail |
|---|---|---|---|---|
| Nominal | activity sentence | per state | normal | — |
| Attention | problem sentence, attention colour | worried (brow, ears back) | normal | badge on page index |
| Critical | grows to 0–56: cause at 18 px + `Tap for Doctor ›` | fault posture | dimmed ~25% (never hidden) | badge |

Each Experience paints the band in its own material:
- **Atlas:** a red-ink stamp across the notebook.
- **Forge:** a hazard bar under the lamps.
- **Observatory:** `MEASUREMENT INVALID — NO SOURCE` over plots whose source is down.
- **Habitat:** the room dims and the creature curls.
- **Monolith:** the one statement becomes the problem.

No Experience may opt out. The ladder reads the existing `overview.attention` and health model; renderers must not each derive "health" differently.

### 3.5 Type ramp (replaces micro / tiny tokens)

| Tier | Size | Viewing | Use | Budget per page |
|---|---|---|---|---|
| Glance | 24–30 px | arm's length (≈16–19′ at 60 cm) | the page's one answer | 1–2 |
| Read | 15–18 px | in hand (≈17–20′ at 35 cm) | status sentence, primary values and labels | ~6 |
| Label | 11–13 px | in hand, close | secondary labels | ~8 |
| Fine | 9 px | close / Inspect only | metadata; **never the sole carrier of a state** | few |
| — | ≤8 px | — | banned on TFT (Studio may use) | 0 |

Rule of thumb: if a page needs more than about 16 text items at Label tier or above, it's two pages or a drill-in. Forge Home currently draws 37 text items.

### 3.6 Touch map and gestures — "same hands, different rooms" (answers Q5)

Identical in every Experience:
- **Swipe left/right** in the body: previous/next page.
- **Nav rail thirds:** tap prev / page index / next.
- **Swipe down from the top:** Control Center (existing).
- **Tap the status line:** the "why?" sheet (Doctor when there's attention).
- **Tap any Reading:** Inspect (source, age, quality, recent history, Doctor link).
- **Long-press:** context (existing semantics).
- **Consequential actions:** a hold-to-commit ring rather than a single tap. Resistive panels register accidental presses.

Per Experience: body zones declared through `SceneLayerSpec(touch=…)`, at least 48 px (72 for primary). Anything tappable carries that Experience's **handle** mark (Atlas tab, Forge bracketed plate, Observatory corner tick, Habitat stone handle, Monolith underline), and decoration must never imitate the handle.

### 3.7 Creature rig and body-language contract (answers Q6)

- **One rig:** the pointed-ear head topology Habitat and Monolith already nearly share (ears, brow, eyes, muzzle, jaw). Parameters:
  - ear angle;
  - eye openness;
  - gaze offset;
  - brow tilt;
  - mouth curve;
  - flush tint;
  - head drop.
- **One input:** `beast.expression` plus attention level. Pwnagotchi's mood is an *input* to Beast personality, never a second mood on screen.
- **Five materials:** ink sketch (Atlas), eyes-in-the-core (Forge), faceted optic (Observatory), living portrait (Habitat), carved stone (Monolith). The same Beast in five rooms.
- **Truth channels.** Honest mappings only, each documented; everything else is labelled ambient:
  - eyes or glint ← health;
  - gaze up ← GPS searching;
  - ears forward ← new discovery in the last N seconds;
  - flush ← thermal band;
  - eyes closed ← docked plus night plus idle;
  - curl or head drop ← critical.
- **Rules:**
  - The creature never covers a Reading.
  - It never carries information that isn't also available as text.
  - It *reports*, it doesn't *demand*: no meters, currencies or streak nags in everyday surfaces. That is what keeps Beast from becoming a pet game.
- **Size budgets:** Atlas about 90 px, Forge about 50 px, Observatory about 70 px, Habitat about 200 px, Monolith about 180 px.

### 3.8 Colour roles

Each palette defines `ink`, `muted`, `accent` (identity only), `ok`, `attention`, `critical`, and `unknown` (a neutral grey).
- Normal conditions never use `attention` or `critical`. Atlas's `GPS SEARCHING` in alert colour violates this.
- `critical` must be the warmest, most saturated colour in every palette.
- **Contrast floors:** Read tier ≥ 7:1 against its local background; Label ≥ 4.5:1.
- **Atlas specifically:** the outdoor Experience currently has the *lowest* contrast in the set (muted-on-field 4.1:1; RGB565 4.2:1). A transmissive SPI TFT in daylight will cut that further.

### 3.9 Motion classes

- **ambient:** decorative. Static under reduced motion and at governor REDUCED or above.
- **event:** at most 1.5 s, triggered by a real event.
- **measured:** redraws only when the data changes.

**Nothing drawn in instrument vocabulary (contours, dials, bars, bus pulses, sweeps) moves unless its data moved.**

---

## 4. Experience DNA and 480×320 page families

Every Experience inherits the shell (§3) plus the shared Control Center, Apps launcher and Doctor model. Pages without a native translation fall back to a neutral "Standard" grammar inside the shell, so nothing is lost. The registry has no fallback today.

### ATLAS — field notebook
- **Essence:** where am I, what's around me, what have I found.
- **Dominant object:**
  - with GPS: the real route drawn from `expedition_points` (or the self-revealing explored grid);
  - without GPS: the canvas *becomes* a ranked nearby list. The drawing changes; no disclaimer needed.
- **Creature:** margin sketch; gaze turns to the newest discovery.
- **Grammar:**
  - ruled margin annotations;
  - event stamps (`FIRST SIGHTING`, `GPS LOCK`);
  - the ledger as the notebook's last ruled line;
  - highest-contrast palette in the set, since it's the outdoor Experience.
- **Never:** fake geography, a compass without heading, animated terrain, alert colour for normal states.

| Page | Canonical | Glance answer |
|---|---|---|
| Field | home | distance / new finds this trip |
| Survey | recon, networks | strongest nearby (ranked), by band |
| Route | map, expedition | where we've been (real points / explored cells) |
| Log | captures, timeline | notebook entries with stamps |
| Kit | system | field readiness checklist ✓ (battery, storage, GPS, radio, temp) |

### FORGE — machine bay
- **Essence:** is the machine OK, and what's attached.
- **Dominant object:** at most 4 bays (RADIO · COMPUTE/THERMAL · POWER · STORAGE), each with **one lamp** (the arm's-length channel), one big numeral and a faceplate label; the Doctor fault panel below.
- **Creature:** eyes inside the machine core; the core looks at the faulting bay.
- **Grammar:**
  - stamped faceplates (Label tier, caps);
  - lamps;
  - big tabular numerals;
  - bus segments lit by real links;
  - jobs and bench as physical trays.
- **Never:** ornaments without information, unlabelled ports, fake scales, hiding battery percentage when a UPS is present (today's Power bay only says `TELEMETRY KNOWN`).

| Page | Canonical | Glance answer |
|---|---|---|
| Bay | home | four lamps: what's wrong, if anything |
| Radio Bay | recon, spectrum | adapter, monitor mode, channel, hop activity (radio-vitals later) |
| Power & Thermal | system | battery % (`≈` where estimated), W, temperature trend |
| Doctor Bench | diagnostics, incidents | fault → evidence → action |
| Ports | hardware, connectivity | USB / I²C / GPIO devices and roles |

### OBSERVATORY — measurement station
- **Essence:** what the air is doing, measured honestly.
- **Dominant object:** one plot per page, with labelled axes, units and a provenance stamp (`LIVE · 2s` / `CAPTURED 2026-09-22`).
- **Channel axis:** split by band. A 2.4 GHz panel (ch 1–13, labelled 1/6/11) and a compressed 5 GHz panel with a band break; y-axis in dBm with labelled gridlines. Today's linear 0–165 axis crushes the 2.4 GHz majority of a realistic street (29 of 34 APs in the busy review state) into about 24 px and merges the labels into `13 6 9113` (evidence `04`).
- **Creature:** observer in the lens; its gaze points at the plotted datum it's reacting to (a datum, never a physical bearing).
- **Grammar:** axis-first composition, units always, cursor/readout on tap, measured vs derived vs captured explicitly styled.
- **Never:** empty axes when the source is down (say `NO SOURCE`), values without units, graph confetti.

| Page | Canonical | Glance answer |
|---|---|---|
| Spectrum | home, spectrum | occupancy and strength by channel |
| Waterfall | (history) | channel activity over time, from real samples |
| Inspector | networks | one network's dossier and measurement history (sanitized) |
| Sky | (GNSS) | skyplot of satellites gpsd already reports (when GPS present) |
| Instrument | system | collector freshness, sample rates, radio health: provenance of the whole station |

### HABITAT — living companion space
- **Essence:** how is my Beast, and what have we been through.
- **Dominant object:** the creature, large, in a room that reflects *real* context:
  - light follows `ambient.day_phase`;
  - docked vs field changes the setting;
  - a fault dims the room.
- **Creature:** the hero. Its expression *is* the device state in companion language; critical faults bring an "Ask the Doctor" object into the room.
- **Grammar:** habitat objects are the only instruments, each with one meaning; soft forms; warm light; memories are real journal events; progression is visible in the creature's form.
- **Never:** circles that look tappable but aren't, "TODAY" that isn't today, "ROAMING" on the dock (`expedition.active` is always true; use dock state or motion), two moods at once.

| Page | Canonical | Glance answer |
|---|---|---|
| Den | home | how is it (face) + one context line |
| Growth | beast | level/stage/lineage as form: `LV 7 → 8 · 75%` |
| Journal | expedition, timeline | real remembered events (first sightings, places, peers, rare moments) |
| Friends | (PeerDex) | Pwnagotchis and Beasts met |
| Care | system, backups | maintenance framed as care; opens Doctor |

### MONOLITH — austere artifact
- **Essence:** one object, one truth.
- **Dominant object:** the sculpture plus one statement or one fact line, which is **always the most important truth** (in a fault it *becomes* the fault).
- **Creature:** carved bust; eye glint = health (keep); minimal posture change.
- **Grammar:** typography-led; one accent; slow deliberate transitions; depth only by drill-in (Inspect); hold-to-commit for commands.
- **Never:**
  - a readable-only-up-close footer (today's footer is 8 px muted);
  - raw enums (`GUARDED` → human words or hidden unless abnormal);
  - units omitted (`48°`);
  - off-centre groups.

| Page | Canonical | Glance answer |
|---|---|---|
| Presence | home | sculpture + the one most important fact |
| Statement | overview | one sentence + three facts |
| Signal | recon | one number + delta ("6 nearby · 2 new") |
| Machine | system | three facts, one per line |
| Journal | timeline | one event per screen |

---

## 5. Minimum coherent screen family for owner approval (answers Q9)

Approve **states, not just screens.** For each Experience, four pages × three states, rendered 1:1 by CI:

- **Pages:**
  - Atlas: Field, Survey, Kit, Log;
  - Forge: Bay, Radio Bay, Power & Thermal, Doctor Bench;
  - Observatory: Spectrum, Waterfall, Instrument, Inspector;
  - Habitat: Den, Growth, Journal, Care;
  - Monolith: Presence, Statement, Signal, Machine.
- **States:**
  1. nominal (the sanitized real capture);
  2. critical attention;
  3. cold-boot unknown.

That makes **five sheets** (one per Experience, 4 rows × 3 columns), each including the shell (status line, rail, attention band). Add one photo of the type-ladder card on the real TFT (Appendix C). The state-matrix tool already produces the states; it needs only the new pages.

---

## 6. Three highest-value implementation changes

1. **Truth layer + state-matrix CI** *(small; do first)*
   - Add a shared `Reading` type and formatter.
   - Mechanically replace the five `_i` / `_f` helper sets.
   - Delete the hard-coded status strings.
   - Add a status-vocabulary function.
   - Make CI render every registered page under the state matrix, with a test that no unknown renders as `0`.

   This fixes observations 1 and 2 and closes the CI blind spot.
2. **The Beast shell** *(medium; prerequisite for TFT)*
   - Status line, nav rail, attention ladder, new type tokens and the touch map, implemented once with per-Experience paint (about five small draw hooks per Experience: status line, rail, lamp, attention band, handle).
   - Reserve the bands in all Experience pages.
   - This is also the natural unit to wire into `engine.py` behind the Presentation Broker / TRY ON transaction.

   It fixes observations 3, 4, 5 and 8, and unblocks 6.
3. **One creature rig** *(medium)*
   - Formalize the shared head topology.
   - Map `beast.expression` + attention to rig parameters.
   - Paint five materials and bind the truth channels.
   - **Prerequisite:** fix the personality cascade (Appendix D), otherwise every creature is permanently "searching". Without the fix, the rig will faithfully express a broken signal.

   This fixes observation 7 and makes the creature meaningful without any pet-game mechanics.

---

## 7. Owner decisions that genuinely need you

1. **What does Gate 1 accept?**
   - **(a)** v0.19 ships the legacy themes on the TFT, with the five Experiences as clearly-labelled Studio previews.
   - **(b)** At least two Experiences run natively on the TFT through the shell for the physical session.

   I recommend **(b) with Monolith + Atlas**. Monolith proves the shell at its most minimal; Atlas proves the outdoor, field and creature-in-margin case and the real route. Habitat can follow once the creature rig lands. If you choose (b), that is integration work, not "physical-only fixes", and the roadmap's V19-2/V19-3 wording should say so.
2. **Creature silhouette policy.**
   - Fixed brand topology (pointed-ear head) with lineage accents (ears, horns, markings, palette)?
   - Or per-lineage silhouettes (heritage already lists orb / avian / mech / insectoid …)?

   Per-lineage silhouettes multiply art cost by the number of lineages × 5 materials. I recommend a fixed topology through v1, with per-lineage silhouettes later as Packs.
3. **Atlas daylight variant.** May Atlas switch automatically to a light "paper" variant outdoors (dark ink on paper) if the test card shows the dark palette washing out? Decide after a 2-minute outdoor look at Appendix C's card.

---

## 8. Top three "obviously better" ideas — realistic now (answers Q10)

1. **The top line is the answer.** Replace five wordmarks with one shared status sentence (§3.3). It gives the biggest legibility gain for the fewest pixels, identical truth in every Experience, and a natural home for Doctor and attention.
2. **The creature is the status light, and it can explain itself.** Bind body language to real signals (§3.7). Monolith's health glint already proves it. Then **long-press the creature** and it cites the signal behind its face: *"Looking up: no GPS fix, 3 satellites visible"* with a `Doctor ›` link when relevant. The creature becomes an **index into truth instead of a veil over it**, and the roles stay clean: the creature explains its *feeling*, the Doctor explains *causes and repairs*.
3. **Same hands, different rooms.** Identical touch geometry and gestures across all five Experiences, with native paint (§3.6). Muscle memory transfers, so the Experiences can diverge wildly in look without costing learnability. This is what lets "five genuinely different grammars" coexist with "learnable".

Honourable mention (Atlas-specific): **the map draws itself.** A self-revealing grid of explored cells from real expedition points needs no map tiles, can't be faked, and is the truthful replacement for the canned route.

---

## 9. Light-bulb ideas — **SPECULATIVE, not recommendations yet**

- 💡 **Experience voices for the status sentence.** Same structured truth, different phrasing register: Atlas `Walking · 12 new since the bridge`, Forge `RADIO OK · 6 AP · CH 6`, Monolith `Six nearby.` Risk: verbosity and localization cost.
- 💡 **"Changes clothes" transition.** Switching Experience morphs the same rig from one material to the next (about 600 ms), so it's obvious it's the same Beast in a different room.
- 💡 **Gaze follows your finger.** The creature glances toward the touch point on any tap. It's truthful (a response to real input), cheap, and makes the device feel alive without inventing state.
- 💡 **Habitat window.** The room's light follows real day phase and dock state, e.g. dusk through the window when `ambient.day_phase=dusk`.
- 💡 **Observatory "experiment log".** Each Observatory session auto-titles itself like a lab notebook entry (time, location class, source, sample count), reusing Expedition records.
- 💡 **Forge bench trays.** Jobs (backup, index, update) appear as physical trays sliding into the bay, with progress only from real task progress.

---

## 10. Answers to the ten questions — index

| # | Question | Where |
|---|---|---|
| 1 | Motifs worth keeping | §1.10, §2 (RETAIN rows) |
| 2 | Too generic / game-like / decorative / tiny | §1.3, §1.8, §1.9, §2 (REJECT / MODIFY rows) |
| 3 | What's shared across all five | §3 (the Beast shell) |
| 4 | What stays unique | §4 (DNA + page families) |
| 5 | Learnable navigation without sameness | §3.6, §8.3 |
| 6 | Meaningful creature without obscuring truth | §3.7, §8.2 |
| 7 | Hierarchy at arm's length | §1.3, §3.3, §3.5 |
| 8 | Missing / unknown data | §3.2 |
| 9 | Minimum screen family for approval | §5 |
| 10 | Top three "obviously better" | §8 |

---

## Appendix A — Defect list for implementers (file:line on `c1a10ac`)

**Truth**
- `experience_atlas.py:229–230` — canned route polyline labelled `ROUTE // LIVE`.
- `experience_atlas.py:106`, `:338` — AP angle includes list index; legend `:349` claims channel→bearing.
- `experience_atlas.py:219`, `:216` — fixed north compass on a diagram captioned "not geographic".
- `experience_atlas.py:232–233` — normal `GPS SEARCHING` drawn in alert colour.
- `experience_forge.py:206` — `RF FABRIC ONLINE` unconditional.
- `experience_forge.py:424` — `POLICY GUARDS ACTIVE` unconditional.
- `experience_forge.py:197` — channel `00` when unknown or down.
- `experience_forge.py:216–229`, `:403–410` — power bays never show battery % / V / W even when `power.*` exists.
- `experience_forge.py:239–251` — creature layer registers mood/level signals but draws static text.
- `experience_observatory.py:375` — `CAPTURED` quality unconditional.
- `experience_observatory.py:96`, `:349` — linear 0–165 channel axis, no tick values or units.
- `experience_observatory.py:265–276` — CPU/MEM listed under PROVENANCE.
- `experience_habitat.py:50`, `:241` — `TODAY` from per-session unique count.
- `experience_habitat.py:271–274`, `:396` — `ROAMING` from always-true `expedition.active`.
- `experience_habitat.py:48`, `:282–284` — creature driven by `pwnagotchi.mood`; strip shows two moods.
- `experience_habitat.py:109–204` vs `:319–352` — two different creature drawings in one Experience.
- `experience_monolith.py:36`, `:245`, `:258–262` — Pwnagotchi mood as creature mood; `°` without unit; raw governor enum.
- Default-zero helpers: `experience_atlas.py:33–44`, `experience_forge.py:30–41`, `experience_observatory.py:30–41`, `experience_habitat.py:29–40`, `experience_monolith.py:27–29`.
- `pages.py:643`, `:667–668` (Beast page, both current and fidelity branches) — `XP 0` / `0 TO NEXT` beside a 75% bar when XP is unknown.

**Legibility / layout** (evidence `05`)
- `experience_forge.py:189` vs `:89` — `HEAT SINK` collides with `CPU LOAD`.
- `experience_forge.py:206` vs `:240` — hexagon cuts `RF FABRIC ONLINE`.
- `experience_observatory.py:205–206` — wordmark runs into subtitle.
- `experience_observatory.py:133` vs `:234` — bar value and bar overwrite the section title.
- `experience_atlas.py:359` — `GPS SEARCHING` (11 px) clipped by the 66 px margin.
- `experience_monolith.py:241–250` — fact row about 20 px right of centre.
- `design.py:45–46` — 6 / 7 px tokens; `design.py:19` `footer_h=42` below `touch_min=48` (`:36`).

**Runtime**
- `engine.py` — no Experience render path.
- `engine.py:2249–2254` — decorative scanline painted above all overlays.

## Appendix B — Evidence index (`collaboration/claude/visual-review-2026-09-27/`)

| File | Shows |
|---|---|
| `00_baseline_all_registered_pages.png` | all 10 registered pages from the real capture (what CI renders), 1:1 |
| `01_status_truth_failures.png` | fault + low-battery states: RF "online", `00` channel, no battery %, unchanged creatures |
| `02_unknown_renders_as_zero.png` | cold-boot state: `0 C`, `00%`, `LV 0`, red `0 ATTENTION` |
| `03_atlas_route_is_canned.png` | two very different routes → identical field canvas |
| `04_observatory_linear_channel_axis_busy.png` | realistic 2.4 GHz street collapsing into the left edge |
| `05_text_collisions_and_clipping_3x.png` | 3× nearest-neighbour crops of collisions and clipping |
| `06_runtime_nav_shell_vs_experience.png` | runtime nav rail vs Experience page with none |
| `07_type_ladder_testcard_480x320.png` | exactly 480×320: 7–30 px on black and on Atlas olive, with arcminutes at 60 cm |

Every Experience frame in `00`–`06` is produced by `collaboration/claude/tools/experience_state_matrix.py` (the images are captioned composites / crops of its output). The `06` runtime frame comes from `tools/render_v019_ux_gallery.render()` with a scratch copy of `beastui/` as `--root`. `07` is a standalone test card. Synthetic states are labelled synthetic.

## Appendix C — Settle type size on the real panel in 2 minutes

Copy `07_type_ladder_testcard_480x320.png` to the Pi. During a normal display test claim (`sudo /opt/beast-ui/bin/claim_display_test.sh`, whose rollback timer stays armed), briefly stop the UI and write the card with the repo's own framebuffer writer:

```bash
sudo systemctl stop beast-ui.service
sudo env PYTHONPATH=/opt/beast-ui:/opt/beast-python/site-packages /opt/.pwn/bin/python3 -c \
  "from PIL import Image; from beastui.framebuffer import FrameBuffer; FrameBuffer('/dev/fb1').write(Image.open('07_type_ladder_testcard_480x320.png'))"
# look at it at arm's length, then in hand, indoors and outdoors
sudo systemctl start beast-ui.service      # or: sudo /opt/beast-ui/bin/release_display.sh
```

The smallest row you can read *at arm's length* is your Glance floor. The smallest you can read *in hand* is your Read floor.

## Appendix D — Relationship to the 2026-09-26 creature review

On branch `claude/clever-cori-fq74wu`, `collaboration/claude/BEASTAGOTCHI_CREATURE_IDEAS_AND_FINDINGS_2026-09-26.md` (finding F1) showed, by running the real `PersonalityEngine`, that `beast.expression` is effectively stuck. The cause is the always-active auto-expedition plus a "quiet" timer keyed on AP-count changes. The result is `gps-searching` 100% of the time indoors with GPS attached, and `hunting` about 94% otherwise. `personality.py` is unchanged on every v0.19 branch. Any creature rig in this review inherits that signal, so fixing F1 is a prerequisite for §6.3.
