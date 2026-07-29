# TaskTracker (formerly MultiProductivity)

A personal task manager built to go deeper into async backend architecture and real frontend development — auth, ownership-scoped CRUD, categories, priorities, subtasks with parent auto-completion, and due dates, all built incrementally with a real GitHub Issues + PR workflow.

## Scope

This project is intentionally scoped to a single individual's task management — no habits, no collaboration. Those ideas were split off into a separate project (in planning) focused on multi-user features, WebSockets, and Redis, so each project stays focused and shippable on its own.

## Status: complete ✅

### Backend (FastAPI + PostgreSQL)

- **Auth**: registration, login, and token refresh, using JWT (access + refresh tokens) and Argon2 password hashing
- **Tasks CRUD**: create, list, partially update, and delete tasks — all protected, with ownership enforced directly in the database query (`WHERE id AND id_user`), not as a separate check
- **Categories**: system defaults (seeded, shared across users) plus user-created ones; deleting a user's category reassigns its tasks to a system fallback ("Others") before the delete runs
- **Priority**: a free-form integer (1-1000) rather than a fixed enum, letting the user express fine-grained relative importance
- **Subtasks**: a self-referential foreign key (id_parent_task) limited to one level of nesting; completing all of a task's subtasks automatically marks the parent as completed, and un-completing one reverts it - resolved in the application layer rather than a database trigger, for testability
- **Due dates and reminders**: storage-only for now (no delivery mechanism yet)
- **Async by design**: SQLAlchemy 2.0 with asyncpg, built from the start to avoid blocking the event loop under concurrent load - a limitation identified in an earlier project (FinTrack) and addressed here from day one
- **Security details worth noting**: refresh tokens travel through a dedicated X-Refresh-Token header (via APIKeyHeader), separate from the Authorization: Bearer flow used for access tokens; PATCH /tasks/{id} only updates fields that were actually provided, instead of overwriting untouched fields with empty values

### Frontend (vanilla JavaScript, no framework)

Built without a framework on purpose, to actually learn the DOM, events, and fetch before adding a framework layer on top of them (React is being explored in a separate project instead of retrofitted here).

- Forms for register, login, create/edit/delete tasks, categories, priority, due dates, and subtasks, with a dynamically rendered task list
- A shared call_fetch() helper centralizing headers, conditional Content-Type, and error handling
- Automatic token refresh: expired sessions are renewed transparently in the background via a recursive interceptor with retry-loop protection, without interrupting what the user is doing

## Known limitations / not implemented

- No cross-field validation yet between due_date and reminder_at (a reminder can currently be set without a due date)
- No past-date validation on due_date
- Visual design is minimal - functional HTML/CSS, not a polished UI

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL (Neon), asyncpg
- **Auth**: JWT (PyJWT), Argon2 (pwdlib)
- **Frontend**: HTML, vanilla JavaScript (fetch, DOM APIs)
