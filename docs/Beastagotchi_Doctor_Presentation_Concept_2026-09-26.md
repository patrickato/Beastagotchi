# Beastagotchi Doctor Presentation Concept

**Date:** 2026-09-26  
**Status:** active jam / visual-product candidate; not final UI canon

## Goal

Doctor should feel like a signature Beastagotchi capability, not a generic diagnostics/settings page.

Presentation should support both beginners and experts while following the selected default behavior:

> **Quiet caretaker normally; visibly communicative when Doctor is opened, a serious issue occurs, owner approval/input is needed, or verbose/expert mode is enabled.**

## 1. Ambient Doctor presence

Doctor is normally quiet.

Potential surfaces:

- small health/status indicator in Beast UI;
- unobtrusive Doctor badge when attention exists;
- creature/animation reaction to significant system health state;
- notification/history entry when a silent repair completed;
- summary such as `Doctor corrected 2 minor issues today`;
- no constant nagging for trivial transient events.

The owner should be able to tell whether the machine is healthy without living inside Doctor.

## 2. Active Doctor / treatment view

When Doctor is opened or actively working, show a live truthful workflow rather than a static log dump.

Possible structure:

### Top/status area
- current problem / case title;
- severity;
- current state (`Investigating`, `Repair ready`, `Repairing`, `Verifying`, `Waiting for owner`, `Resolved`);
- live activity/progress.

### Main visual
Possible visual metaphor: a layered patient/system path rather than a literal human body.

Example stack:

`HARDWARE -> LINUX -> PWNAGOTCHI/BETTERCAP -> BEAST -> EXPERIENCE`

Healthy layers remain calm/normal; affected dependency/path highlights where Doctor is currently looking.

For a radio problem, the highlighted chain may be:

`Wi-Fi chipset -> driver -> PHY -> monitor interface -> Bettercap -> Pwnagotchi -> capture pipeline`

For display:

`SPI -> overlay/device tree -> driver -> framebuffer -> renderer -> TFT`

This lets users understand *where* the problem sits visually without reading shell output.

### Current reasoning/activity
Human-readable stages such as:

- `Checking display hardware...`
- `Framebuffer found.`
- `Comparing last known-good configuration...`
- `2 possible causes remain.`
- `Testing renderer output...`
- `Cause confirmed.`

No fake percentages when the total work is unknown.

## 3. Hypothesis / evidence presentation

Doctor should make reasoning inspectable without burdening beginners.

Default concise view:

> `Likely cause: Pwnagotchi is rendering to the wrong framebuffer.`

Expandable:

- supported hypotheses;
- contradicted hypotheses;
- evidence that mattered;
- confidence state;
- relevant previous local case;
- relevant Global Doctor cases;
- official/community source evidence.

Possible confidence vocabulary:

- Possible;
- Supported;
- Likely;
- Strongly supported;
- Confirmed;
- Contradicted.

## 4. Repair plan view

Before consequential work, Doctor presents a concise plan:

- what will change;
- why;
- source/artifact if needed;
- risk/authority level;
- snapshot/backup available;
- rollback plan;
- whether reboot/service interruption is expected.

Example:

> `Repair available`  
> `Change: restore display target to /dev/fb1`  
> `Backup: ready`  
> `Rollback: automatic`  
> `[Repair] [Technical details]`

## 5. Live progress / current action

Reuse the shared Beast progress/status primitive.

Examples:

`Downloading -> Verifying -> Extracting -> Installing -> Testing -> Cleaning`

or:

`Probe 4/7: checking monitor-interface packet flow`

If measurable, show a truthful bar/count. If not measurable, show stage/activity only.

## 6. User/physical handoff

When Doctor needs the owner:

- clearly say **why** machine evidence cannot answer the remaining question;
- request one physical observation/action at a time;
- watch machine state live where possible and acknowledge completion automatically.

Example:

> `Please unplug the RTL-SDR.`  
> `Waiting for USB removal...`  
> `Removed.`  
> `Plug it back in.`  
> `Device returned, but the driver did not bind.`

## 7. Resolved view

On success:

- explain what was wrong;
- what Doctor changed;
- how it verified success;
- whether temporary files/resources were cleaned;
- whether a reboot remains pending;
- whether the case contributed to local/global Doctor knowledge (subject to policy);
- allow `View technical record`.

Avoid unnecessary celebratory clutter for minor repairs; major/interesting recoveries may allow Beast/creature choreography later.

## 8. Deep technical view

Experts/Owner Space should be able to drill all the way down.

Possible details:

- exact probes run;
- commands/arguments;
- stdout/stderr;
- relevant files/config excerpts;
- diffs;
- package/driver versions;
- System Graph path;
- hypotheses and evidence weights;
- official/community sources;
- exact Procedure/Action/Transaction;
- rollback journal;
- Global Doctor match breakdown;
- raw evidence bundle.

Principle:

> **Simple by default, never dumbed down.**

## 9. TFT vs Studio/WebUI

### TFT
Focus on:
- status;
- progress;
- clear problem summary;
- next action;
- simple visual dependency path;
- repair/approval buttons;
- brief results.

### Studio/WebUI
Can provide:
- detailed case timeline;
- side-by-side Known-Good/current diff;
- System Graph;
- probe/evidence explorer;
- Global Doctor similar-case analysis;
- sources/manuals;
- raw technical output;
- repair history.

The two surfaces should represent the same Doctor case, not separate systems.

## 10. Doctor personality / character question

Open for later creative discussion:

Doctor may have a visual/personality identity integrated with Beastagotchi, but should never obscure technical truth.

Possible range:
- purely professional system physician;
- subtle character/medical-bay visual language;
- creature-linked Doctor expressions/animations;
- optional more playful presentation.

Do not finalize visual character before broader UI/Experience work and physical 480x320 validation.

## 11. Global Doctor network presentation

Collective evidence can be surfaced compactly:

> `43 similar cases`  
> `31 close matches`  
> `28 successful with this repair`  
> `3 failed on a different driver revision`

Expanded view explains matching dimensions and source/evidence tiers.

Never turn popularity alone into automatic truth.

## Principle

> **Doctor should show the owner what it is doing, why it believes what it believes, and where it is in the repair—without forcing the owner to read a terminal unless they want to.**
