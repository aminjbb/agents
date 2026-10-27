---
name: scaffold-redux-slice
description: Create a typed Redux Toolkit model for justified global client state with explicit actions, selectors, reducer registration, and FSD public exports, excluding server caches and isolated UI state.
---

# Scaffold Redux Slice

## Inputs

- `project_root`, owning `layer`/`slice_name`, client-state contract, transitions, consumers, and reset requirements.
- Optional `source_root` and `dry_run` (default false).
- Inspect existing RTK, React Redux, store assembly, naming, public APIs, and instructions. Resolve target paths independently of this file.

## Execution rules

1. Prove client authority and cross-screen/workflow lifetime. Server records/status belong to Query; isolated toggles/fields belong to local state. Do not generate Redux for either category.
2. Validate destination names and resolved paths, including symlinks/junctions. Reject traversal and collisions; reuse identical files and preserve other implementations. Merge existing code only within authorized scope.
3. Put state, actions, reducers, and selectors in the owner's `model/`. Keep store assembly and Providers in `app`. Do not create an application store per slice.
4. Use explicit domain transitions, typed payloads, pure reducers, serializable values, and narrow selectors. No network calls, query cache mirrors, generic arbitrary setters, or middleware-check suppressions.
5. Maintain downward cross-slice dependencies and root `index.ts` imports. No sibling dependencies, own-barrel imports, wildcard exports, or cycles, including type-only cycles.

## Exact example tree

For an approved client-owned, cross-screen appearance preference:

```text
src/entities/preferences/
  model/
    preferences.types.ts
    preferences.slice.ts
    preferences.selectors.ts
  index.ts
```

Use this domain only when applicable; otherwise substitute the confirmed state contract. If the server owns the preference, use Query instead. Browser persistence is not implied by this scaffold.

### model/preferences.types.ts

```ts
export type Theme = "light" | "dark" | "system";

export interface PreferencesState {
  theme: Theme;
}

export interface PreferencesStateContainer {
  preferences: PreferencesState;
}
```

### model/preferences.slice.ts

```ts
import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { PreferencesState, Theme } from "./preferences.types";

function createInitialState(): PreferencesState {
  return { theme: "system" };
}

const preferencesSlice = createSlice({
  name: "preferences",
  initialState: createInitialState(),
  reducers: {
    themeChanged(state, action: PayloadAction<Theme>) {
      state.theme = action.payload;
    },
    preferencesReset: () => createInitialState(),
  },
});

export const { themeChanged, preferencesReset } = preferencesSlice.actions;
export const preferencesReducer = preferencesSlice.reducer;
```

### model/preferences.selectors.ts

```ts
import type { PreferencesStateContainer } from "./preferences.types";

export const selectTheme = (state: PreferencesStateContainer) =>
  state.preferences.theme;
```

The container is the slice's minimal structural contract, not an import from application `RootState`. If the actual store uses another shape, adapt it in higher-level composition rather than weakening types or importing `app` into this slice. Memoize only computations that need it.

### index.ts — merge explicit public exports

```ts
export {
  preferencesReducer,
  preferencesReset,
  themeChanged,
} from "./model/preferences.slice";
export { selectTheme } from "./model/preferences.selectors";
export type {
  PreferencesState,
  PreferencesStateContainer,
  Theme,
} from "./model/preferences.types";
```

### app/providers/store.ts — integration example

Merge registration into the existing store without replacing reducers, middleware, enhancers, persistence, or tests. Only create this full file when store initialization is part of the assigned task and no store exists:

```ts
import { configureStore } from "@reduxjs/toolkit";
import { preferencesReducer } from "@/entities/preferences";

export const store = configureStore({
  reducer: {
    preferences: preferencesReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

Keep these inferred application types in `app`; lower layers MUST NOT import them or application-typed hooks. Lower consumers may use React Redux with slice-owned structural selectors and supported action contracts. Shared generic bindings must not import business reducers. Never erase typing with `any` or blanket casts.

Integrate the stable store with the existing React Redux Provider at application assembly. Do not replace QueryClientProvider or recreate a store on render. Persistence/hydration and lifecycle resets require an explicit contract; do not add them speculatively.

## Verification and output

- Verify initial state, typed transitions, reset semantics, selector results, unchanged-state references where meaningful, and registration/Provider behavior.
- Validate external or persisted values before dispatch; TypeScript types are not runtime input validation.
- Confirm no remote records, loading/error mirrors, UI-only toggles, nonserializable objects, or application imports entered the model.
- Run applicable existing type checks, lint, tests, build, and boundary/cycle checks. Every authored source file/component must stay within 150 physical lines.
- Report `CREATED`, `UPDATED`, `UNCHANGED`, `PLANNED`, or `BLOCKED`, with the ownership rationale, paths, public exports, registration changes, actual checks, and gaps. Dry runs write nothing; reruns do not duplicate registration/exports.

Reference: [Redux Toolkit createSlice](https://redux-toolkit.js.org/api/createSlice).
