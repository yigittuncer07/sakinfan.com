# sakinfan.com specification

## Overview

A self-hosted, oldschool forum web application. Small scale (target: 50 concurrent users max),
server-side rendered, no modern frontend frameworks. Runs on a single machine via Docker Compose,
exposed externally via a cloudflared tunnel.

---

## Tech Stack

| Layer | Choice |
| --- | --- |
| Language | Python 3.12 |
| Web framework | FastAPI |
| Form parsing | python-multipart |
| DB driver | asyncpg |
| ORM | SQLAlchemy 2.x (async) |
| DB | PostgreSQL (external, already running on host) |
| Sessions | Starlette SessionMiddleware (client-side cookies) |
| Security | asgi-csrf (CSRF protection) |
| Auth | passlib[bcrypt] (Password hashing) |
| Templating | Jinja2 (via fastapi.templating.Jinja2Templates with autoescape=True) |
| Frontend | Vanilla HTML + hand-written CSS, no JS frameworks |
| Reverse proxy | nginx |
| Tunnel | cloudflared |
| Containerization | Docker Compose |

---

## Architecture

```
Browser
  │  GET/POST (full page loads, HTML forms + CSRF tokens)
  ▼
cloudflared tunnel
  │
  ▼
nginx                  ← reverse proxy, serves /static directly
  │
  ▼
FastAPI (gunicorn + uvicorn workers)
  ├── routers/         ← thin request handlers
  ├── services/        ← business logic, password hashing, text sanitization
  ├── models/          ← SQLAlchemy ORM models
  ├── templates/       ← Jinja2 HTML templates
  └── static/          ← CSS and any static assets
  │
  └── PostgreSQL       ← persistent data


```

All HTML is rendered server-side. Forms use standard  and are parsed via python-multipart. There is no frontend build step, no bundler, no TypeScript. JavaScript is only used where absolutely necessary (e.g. confirm-before-delete), and must be vanilla JS inline or in a single static/main.js file.

---

## Project Structure

```
forum/
├── app/
│   ├── main.py              # FastAPI app factory, router registration, lifespan, session/CSRF middleware
│   ├── config.py            # Settings via pydantic-settings, loaded from .env
│   ├── database.py          # Async SQLAlchemy engine and session factory
│   ├── dependencies.py      # FastAPI dependencies (get_db, get_current_user)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── board.py
│   │   ├── thread.py
│   │   └── post.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── boards.py
│   │   ├── threads.py
│   │   └── posts.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py          # bcrypt hashing and verification
│   │   ├── boards.py
│   │   ├── threads.py
│   │   └── posts.py         # BBCode/Markdown parsing and sanitization
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── board.html
│   │   ├── thread.html
│   │   └── auth/
│   │       ├── login.html
│   │       └── register.html
│   └── static/
│       ├── style.css
│       └── main.js          # minimal vanilla JS only, may be empty
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── alembic/
│   └── versions/
└── .env.example


```

---

## Configuration

All configuration via environment variables loaded through pydantic-settings in config.py.

```
# .env.example
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/forum
SECRET_KEY=changeme
SESSION_COOKIE_NAME=forum_session
SESSION_TTL_SECONDS=604800   # 7 days
DEBUG=false


```

DATABASE_URL uses postgresql+asyncpg:// scheme.

---

## Database Models

Use SQLAlchemy 2.x declarative ORM with async support. All models inherit from a shared Base = DeclarativeBase().

### User

```
id            UUID, primary key, default uuid4
username      String(50), unique, not null, indexed
email         String(255), unique, not null
password_hash String(255), not null # Must use bcrypt
is_admin      Boolean, default False
is_banned     Boolean, default False
created_at    DateTime(timezone=True), default now


```

### Board

```
id            Integer, primary key, autoincrement
name          String(100), unique, not null
description   String(500)
display_order Integer, default 0
created_at    DateTime(timezone=True), default now


```

Relationships: Board has many Threads.

### Thread

```
id            UUID, primary key, default uuid4
board_id      Integer, FK boards.id, not null
author_id     UUID, FK users.id, not null
title         String(200), not null
is_locked     Boolean, default False
is_pinned     Boolean, default False
created_at    DateTime(timezone=True), default now


```

Relationships: Thread belongs to Board, belongs to User (author), has many Posts.

### Post

```
id            UUID, primary key, default uuid4
thread_id     UUID, FK threads.id, not null
author_id     UUID, FK users.id, not null
body          Text, not null # Stored as sanitized HTML or raw Markdown/BBCode
created_at    DateTime(timezone=True), default now
updated_at    DateTime(timezone=True), nullable


```

Relationships: Post belongs to Thread, belongs to User (author).

---

## Sessions & Security

Sessions are managed via Starlette's SessionMiddleware using cryptographically signed cookies.

On login, store the user's ID in the session dictionary:

```python
request.session["user_id"] = str(user.id)


```

The middleware automatically handles setting the cookie named SESSION_COOKIE_NAME with httponly=True and samesite="lax". Use secure=True only if not in DEBUG mode. Set the max age using SESSION_TTL_SECONDS.

On each request, a get_current_user dependency reads the user_id from the session, queries the PostgreSQL database to fetch the user, and verifies the user exists and is_banned is False. If invalid, the session is cleared and it returns None.

### CSRF Protection

asgi-csrf middleware must be configured in main.py. The CSRF token must be injected into the template context and included as a hidden input field in every state-changing form.

---

## Routes

### Auth (/)

| Method | Path | Description |
| --- | --- | --- |
| GET | /login | Render login form |
| POST | /login | Authenticate, set session, redirect to / |
| GET | /register | Render registration form |
| POST | /register | Create user, set session, redirect to / |
| POST | /logout | Clear session, redirect to /login |

### Boards (/)

| Method | Path | Description |
| --- | --- | --- |
| GET | / | List all boards with thread/post counts |

### Threads (/board/{board_id})

| Method | Path | Description |
| --- | --- | --- |
| GET | /board/{board_id} | List threads in a board (paginated) |
| GET | /board/{board_id}/new | Render new thread form (auth required) |
| POST | /board/{board_id}/new | Create thread + first post, redirect to thread |

### Posts (/thread/{thread_id})

| Method | Path | Description |
| --- | --- | --- |
| GET | /thread/{thread_id} | View thread and all posts (paginated) |
| POST | /thread/{thread_id}/reply | Add a reply post (auth required) |
| POST | /post/{post_id}/delete | Delete a post (author or admin only) |
| POST | /thread/{thread_id}/delete | Delete a thread and all posts (admin only) |
| POST | /thread/{thread_id}/lock | Toggle lock on thread (admin only) |
| POST | /thread/{thread_id}/pin | Toggle pin on thread (admin only) |

All protected routes check get_current_user. If not authenticated, redirect to /login.
If authenticated but not authorized (e.g. non-admin trying admin action), return HTTP 403.

Use HTTP redirects (303 See Other) after all successful POST actions.

Pagination: 20 threads per page, 25 posts per page. Use ?page=N query param.

---

## Services Layer

Keep routers thin. All database logic lives in services/. Routers call services, services interact with the DB session. Services are async functions that accept an AsyncSession as their first argument.

Example signature:

```python
async def get_thread_with_posts(
    db: AsyncSession,
    thread_id: UUID,
    page: int = 1
) -> tuple[Thread, list[Post]]:
    ...


```

### Content Formatting

The posts.py service must process raw user input using a lightweight BBCode or Markdown parser. The resulting HTML must be strictly sanitized (e.g., using bleach) to prevent XSS before rendering or saving.

---

## Dependencies

app/dependencies.py must provide:

* get_db — yields an AsyncSession from the session factory
* get_current_user — reads user_id from session cookie, loads user from DB, checks ban status. Returns User | None.
* require_user — calls get_current_user, raises HTTPException(401) or redirects to /login if not authenticated. Returns User.
* require_admin — calls require_user, raises HTTPException(403) if not admin.

---

## Frontend & Templates

### Base Template (base.html)

* Standard HTML5 document
* Links to /static/style.css
* Contains a site header with: site name (hardcoded "sakinfan.com"), navigation links (Home, Login/Register or Username + Logout depending on session)
* A {% block content %}{% endblock %} for page content
* Simple footer with current year

### Aesthetic Guidelines

* Oldschool forum look. Think phpBB 2.x, early 2000s message boards.
* Table-based layout for thread and post lists (actual  elements)
* Muted color palette: off-white background, dark navy or grey header, visible borders
* No shadows, no rounded corners, no gradients (or very minimal)
* Fixed-width container (~900px max), centered
* Post bodies use a monospace or serif font
* Username, timestamp, post count shown clearly on each post
* CSS must be a single hand-written style.css file. No frameworks, no preprocessors.
* Ensure Jinja2's autoescape=True is enabled by default to prevent XSS injections.

### Forms

* All forms use standard HTML form elements
* **Must** include a hidden CSRF token field: 
* Show validation errors inline below the relevant field
* Errors passed from route handler to template via template context

---

## Error Handling

* 404: render a simple 404.html template ("Thread not found", "Board not found", etc.)
* 403: render a simple 403.html template ("You don't have permission to do that.")
* 500: render a simple 500.html template. Do not expose stack traces in production.
* Add a global exception handler in main.py for unhandled exceptions.

---

## Migrations

This is not a priority at all
Use Alembic for database migrations.

* alembic.ini configured to use async SQLAlchemy
* Initial migration creates all tables
* Include instructions in README for running migrations:

```
docker compose exec web alembic upgrade head


```

---

## Docker Setup

### Dockerfile

* Base image: python:3.12-slim
* Install dependencies from requirements.txt (must include python-multipart, passlib[bcrypt], asgi-csrf)
* Copy app source
* Run with: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

### docker-compose.yml

Services:

* web — the FastAPI app, depends on postgre
* postgre — the database
* nginx — nginx:alpine, config from ./nginx/nginx.conf, ports 80:80
#- tunnel — cloudflare/cloudflared:latest, runs tunnel --no-autoupdate run do not implement at first
* Requires TUNNEL_TOKEN env var

### nginx/nginx.conf

* Reverse proxy to web:8000
* Serve /static files directly from the container volume