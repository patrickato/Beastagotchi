# Beast Experiences — v0.19 draft/preview model

An Experience is a declarative composition profile carried by a Mission Pack or
built-in Mission. It may reference:

- a Theme;
- a Face profile;
- an Animation profile;
- a Board or Layout composition;
- a Context Deck.

The key safety/UX rule is that **selecting an Experience never writes live
preferences**.

In Beast Studio the flow is:

```
Experience
    ↓
resolve currently available content
    ↓
load into Studio draft
    ↓
exact live-data preview
    ↓
user edits anything desired
    ↓
existing APPLY TO BEAST transaction
```

Board/Layout widgets are copied into the draft. The source Pack remains
read-only, so a user can customize the resulting Dashboard without mutating
downloaded content. Disabling/removing the source Pack later does not destroy
the applied widget copy.

Unavailable optional pieces are reported as warnings rather than silently
substituted. Missing required capabilities block the Experience draft.

This model is intentionally useful for radically different complete identities:
a WOPR/NORAD Experience, field-instrument Experience, playful digital-pet
Experience, LCARS Experience, aircraft-spotter Experience, and future community
designs can combine several safe content layers without changing Beast Core.
