# Control room interaction contract

User goal: discuss a project request with the real repository architect, approve a plan, and inspect specialist execution and review evidence.

Source: user-authorized React development and root architect's `/api` contract. There was no external design reference or existing web design system. The Persian RTL dark palette and native control composition are reversible UI choices.

## Path and ownership

1. Bootstrap reads actual manifest metadata, connection status, project root and durable history. Query owns server records. No seeded agent work or simulated success.
2. Connect accepts an optional key or existing CLI login. Key input clears after each attempt; mutation cache resets, and no browser persistence exists. Server probe checks local authentication availability, not model entitlement or future request success.
3. New meeting validates nonblank root/request, then creates a planning-only run. RHF owns local drafts. Failure preserves inputs.
4. Clarifications use indexed field paths mapped to exact backend question IDs. Run identity resets the draft. Pending submissions disable fields and repeat submit.
5. Planned tasks show owner, dependencies, scope, acceptance criteria and real status. Explicit approval sends execute=true.
6. Busy run polls every second; connection bootstrap/history poll every five seconds. Failed reads retain cached content and offer retry. Browser reconnect/focus use Query defaults.
7. Interrupted or blocked runs require explicit recovery. No-plan recovery sends execute=false and returns to planning; it never approves an unseen plan. Task recovery identifies failed, blocked, running, ready or review tasks and asks the user to inspect side effects and stale locks first.
8. Actual events, task results, audit and architect acceptance remain inspectable. Terminal runs stop run polling. Simultaneous same-owner operations use counts, and activity never appears active when busy=false.

## Responsive and accessibility contract

DOM order: history/navigation, main header, team, primary workflow, connection/help. At 1200px primary workflow and connection stack; at 800px sidebar becomes a top section; at 600px cards use two columns and task cards use one. Essential controls remain available at all widths.

Native forms/buttons/details/select controls provide keyboard interaction. Visible focus uses the accent outline. Labels and validation IDs associate errors with fields. Pending text and read/mutation failures are announced with status/alert semantics. No dialogs, focus traps, animation, inline styling, or hidden essential mobile actions.

## Acceptance scenarios

- Empty request: show a field error, focus invalid input and send no run creation.
- Failed connection: clear key, display error and do not claim authentication succeeded.
- Valid request: create one run and show actual server state; never render fabricated plan results.
- Dotted or arbitrary question ID: submit a flat answer record whose keys exactly match original IDs.
- Interrupted planning: recovery requests execute=false; plan approval remains a later explicit action.
- Planned run: approval enables real execution, then status/events update while busy.
- Failed query: show retry with stale data preserved. Reconnection can refresh without losing an editable form draft.

## Verification boundary

TypeScript and Vite production build pass. npm reports zero known vulnerabilities for the installed dependency set. Static schema, import, line-limit, form and semantic checks are recorded in the development handoff. No CUA browser surface was available; visual, viewport, keyboard, screen-reader and actual paid model execution coverage remain unverified and must not be described as passed.
