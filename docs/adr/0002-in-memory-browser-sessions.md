# Game sessions are in-memory and scoped to a browser

**Status:** accepted

## Context

The app has no accounts and no database, but it must remember each child's racha, consecutive failures, challenge progress, and the quiz awaiting an answer. Answers are checked by the server.

## Decision

The backend keeps one session per browser in a process-local dictionary. The browser receives an opaque session id, stores it in `localStorage`, sends it as `X-Session-Id`, and also receives it as a cookie; an unknown or missing id starts a new session. The frontend mirrors the racha for display only; the backend is authoritative. Ephemeral progress was accepted to keep the app runnable as a single Python process with no infrastructure.

## Consequences

- Restarting the backend, or running more than one worker, loses or fragments sessions and rachas.
- Only the most recently served quiz can be verified; requesting a new quiz replaces the verifiable answer.
- Verification does not consume the last quiz, so the same answer can be submitted more than once.
- Inactive sessions are never evicted, so memory grows until restart.
- Persisting progress or scaling horizontally requires a shared store or self-contained signed state.
