# MultiProductivity

A productivity platform that goes beyond a simple to-do list — combining task management, habit tracking, and collaborative projects in a single system. Built as a hands-on way to go deeper into async backend architecture, real frontend development, and infrastructure tools not covered in earlier projects (Redis, WebSockets, professional Git workflow).

## Vision

The end goal is a productivity app with three connected modules:

- **Tasks** — categorized, prioritized, with subtasks (v1/v2 scope)
- **Habits** — recurring goals with streaks and tracking (planned)
- **Projects** — workspaces that can be personal or collaborative, with real-time updates between team members (planned)

Each module is being built incrementally, as a separate milestone, rather than all at once — prioritizing a working, testable product at every stage over a big upfront design.

## Current Status: v2 complete ✅

v1 covered the foundation (auth + a working task manager, backend and frontend). v2 built on top of that with cleanup and refactoring: shared JS logic extracted into reusable functions, and `201 Created` now used for resource creation instead of `200`.

### Backend (FastAPI + PostgreSQL)

- **Auth**: registration, login, and token refresh, using JWT (access + refresh tokens) and Argon2 password hashing
- **Tasks CRUD**: create, list, partially update, and delete tasks — all protected, with ownership enforced directly in the database query (`WHERE id AND id_user`), not as a separate check
- **Async by design**: SQLAlchemy 2.0 with `asyncpg`, built from the start to avoid blocking the event loop under concurrent load — a limitation identified in an earlier project (FinTrack) and addressed here from day one
- **Security details worth noting**: refresh tokens travel through a dedicated `X-Refresh-Token` header (via `APIKeyHeader`), separate from the `Authorization: Bearer` flow used for access tokens; `PATCH /tasks/{id}` only updates fields that were actually provided, instead of overwriting untouched fields with empty values

### Frontend (vanilla JavaScript, no framework yet)

Deliberately built without React first, to actually learn the DOM, events, and `fetch` before adding a framework layer on top of them.

- Forms for register, login, create/edit/delete tasks, and a dynamically rendered task list
- A shared `call_fetch()` helper centralizing headers, conditional `Content-Type`, request logic, and error handling — repeated fetch/try-catch code from v1 was consolidated here in v2
- Automatic token refresh: expired sessions are renewed transparently in the background, without interrupting what the user is doing

## What's next

- **v3+**: habits module, then collaborative projects — this is where Redis (pub/sub for real-time updates, distributed locks), WebSockets, and a proper Git branching workflow (one branch per ticket, PRs, squash merges) come into play
- Possibly migrating the frontend to React once the vanilla JS foundation feels solid
- Further UI polish is still open, independent of the module roadmap above

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL (Neon), `asyncpg`
- **Auth**: JWT (`PyJWT`), Argon2 (`pwdlib`)
- **Frontend**: HTML, vanilla JavaScript (`fetch`, DOM APIs) — React planned for a later version
- **Planned**: Redis, WebSockets, Docker (multi-stage builds, multi-service Compose), pytest