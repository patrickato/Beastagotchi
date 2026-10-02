# Presentation Transition Planning — v0.19

Beastagotchi now models Native Pwnagotchi, Korrie71 Theme Manager, and Beast UI
as explicit presentation owners.

This milestone adds transition planning only. Physical one-tap switching remains
locked until the exact sequence is validated on the target Pi.

## Current Theme Manager compatibility finding

The current Korrie71 Theme Manager plugin has a clean unload path. On unload it:

- stops its running loops
- saves pending achievement state
- unwraps modified UI elements
- removes its render callback
- restores original display render/clear methods
- clears frame/font caches
- drops its UI reference

That gives Beast a practical compatibility strategy today even before a new
Theme Manager API exists.

## Compatibility strategy

Beast to Theme Manager:

1. release Beast display ownership using the validated rollback configuration
2. restore native Pwnagotchi display
3. enable Theme Manager
4. restart/observe Pwnagotchi
5. verify Beast UI is inactive and Theme Manager owns presentation

Theme Manager to Beast:

1. disable Theme Manager so its unload cleanup runs
2. restart/observe Pwnagotchi
3. claim the display using the validated Beast handoff sequence
4. verify Beast UI, Beast Core and Pwnagotchi health

Theme Manager to Native:

1. disable Theme Manager
2. verify native Pwnagotchi rendering

## Limitation today

Compatibility mode toggles the whole Theme Manager plugin. Therefore its own
WebUI is unavailable while Theme Manager is disabled.

The preferred future integration remains a managed presentation mode in Theme
Manager where the plugin can stay loaded in web-only/standby state and expose
explicit release/acquire hooks. The planner already distinguishes
compatibility_toggle from managed mode so that upgrade does not require a new
Beast architecture.

## Safety

The planner is available through Beast Studio Operations and the Action Broker
as presentation.plan. It is read-only.

presentation.switch execution remains disabled until:

- off-screen transition simulation passes
- exact command/rollback sequence is packaged
- bounded physical TFT test passes
- recovery remains possible without the WebUI
