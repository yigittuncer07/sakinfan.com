# sakinfan.com

A lightweight, self-hosted oldschool forum web application built with FastAPI and PostgreSQL. Designed for small communities with a retro aesthetic and minimal frontend complexity.

## Overview

**sakinfan.com** is a server-side rendered forum application targeting approximately 50 concurrent users. It prioritizes simplicity and self-hosting capabilities, with zero modern frontend frameworks. All HTML is rendered on the server, forms use standard submissions, and any JavaScript is vanilla and minimal.

The application runs on a single machine via Docker Compose, exposed externally through a cloudflared tunnel, and sits behind an nginx reverse proxy.

## Tech Stack

| Layer              | Technology                                        |
| ------------------ | ------------------------------------------------- |
| Language           | Python 3.12                                       |
| Web Framework      | FastAPI                                           |
| Web Server         | gunicorn + uvicorn                                |
| ORM                | SQLAlchemy 2.x (async)                            |
| Database           | PostgreSQL 16                                     |
| Database Driver    | asyncpg                                           |
| Templating         | Jinja2                                            |
| Authentication     | bcrypt (password hashing)                         |
| Session Management | Starlette SessionMiddleware (client-side cookies) |
| Security           | asgi-csrf (CSRF protection)                       |
| Content Processing | bleach, markdown                                  |
| Frontend           | Vanilla HTML + hand-written CSS                   |
| Reverse Proxy      | nginx                                             |
| Tunnel             | cloudflared                                       |
| Containerization   | Docker Compose                                    |

## Project Structure

```
app/
├── main.py                  # FastAPI app, middleware setup, router registration
├── config.py               # Pydantic settings loaded from .env
├── database.py             # SQLAlchemy async engine and session factory
├── dependencies.py         # FastAPI dependency injection (get_db, get_current_user)
├── models/                 # SQLAlchemy ORM models
│   ├── user.py            # User entity with auth fields
│   ├── board.py           # Forum boards/categories
│   ├── thread.py          # Discussion threads
│   └── post.py            # Individual forum posts
├── routers/               # HTTP endpoint handlers
│   ├── auth.py            # Registration, login, logout
│   ├── boards.py          # Board listing and viewing
│   ├── threads.py         # Thread creation and viewing
│   └── posts.py           # Post creation and viewing
├── services/              # Business logic layer
│   ├── auth.py            # Password hashing/verification
│   ├── boards.py          # Board operations
│   ├── threads.py         # Thread operations
│   └── posts.py           # Post operations, text sanitization
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base layout template
│   ├── index.html         # Homepage
│   ├── board.html         # Board listing
│   ├── thread.html        # Thread view
│   ├── thread_new.html    # New thread form
│   └── auth/
│       ├── login.html
│       └── register.html
└── static/                # CSS and minimal JavaScript

docker-compose.yml         # PostgreSQL service definition
```

## Database Schema

### Users

- **id** (UUID): Primary key
- **username** (String, unique): Display name
- **email** (String, unique): Email address
- **password_hash** (String): bcrypt hash
- **is_admin** (Boolean): Admin privileges
- **is_banned** (Boolean): Ban status
- **created_at** (DateTime): Account creation timestamp

### Boards

- **id** (Integer, auto-increment): Primary key
- **name** (String, unique): Board title
- **description** (String, nullable): Board description
- **display_order** (Integer): Order for UI listing
- **created_at** (DateTime): Creation timestamp
- **threads** (Relationship): One-to-many with Thread

### Threads

- **id** (UUID): Primary key
- **board_id** (Integer): Foreign key to Board
- **author_id** (UUID): Foreign key to User
- **title** (String): Thread title
- **is_locked** (Boolean): Cannot add new posts when true
- **is_pinned** (Boolean): Pinned to top of board
- **created_at** (DateTime): Creation timestamp
- **board** (Relationship): Many-to-one with Board
- **posts** (Relationship): One-to-many with Post
- **author** (Relationship): Many-to-one with User

### Posts

- Inferred from usage: likely contains user_id, thread_id, content, created_at fields

## Architecture

```
Browser
  ↓ GET/POST (HTML forms + CSRF tokens)
  ↓
cloudflared tunnel
  ↓
nginx (reverse proxy, serves static files)
  ↓
FastAPI (gunicorn + uvicorn workers)
  ├── routers → services → models
  ├── templates (Jinja2 rendering)
  └── static (CSS/minimal JS)
  ↓
PostgreSQL (data persistence)
```

### Request Flow

1. **User submits form** via standard HTML form (POST with CSRF token)
2. **nginx** receives request, forwards to FastAPI
3. **Router** validates request and extracts parameters
4. **Service** executes business logic (password verification, text sanitization, etc.)
5. **Models** (SQLAlchemy) interact with PostgreSQL asynchronously
6. **Template** renders response HTML server-side
7. **Response** sent back to browser

## Features

### Authentication

- User registration with bcrypt password hashing
- Login/logout with session management
- Optional admin privileges and ban system

### Forum Structure

- Multiple discussion boards/categories
- Threads (topics) within boards
- Posts (replies) within threads
- Thread locking and pinning capabilities

### Security

- CSRF protection on all state-changing operations
- Password hashing with bcrypt
- Server-side session management
- Jinja2 autoescape enabled for XSS prevention
- Content sanitization with bleach

### Content Processing

- Markdown parsing with markdown library
- HTML sanitization with bleach
- Plain text content preservation

## Configuration

Settings are loaded from `.env` file via Pydantic:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
SECRET_KEY=your-secret-key
SESSION_COOKIE_NAME=sakinfan_session  # default
SESSION_TTL_SECONDS=604800            # 7 days default
DEBUG=false                            # default
```

## Deployment

### Local Development

1. Ensure PostgreSQL is running
2. Create `.env` with required settings
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `uvicorn app.main:app --reload`

### Docker Compose

```bash
docker-compose up -d
```

Starts PostgreSQL on port 5432 with persistent volume.

### Production

- FastAPI runs behind gunicorn + uvicorn workers
- nginx reverse proxy handles SSL and static assets
- cloudflared tunnel exposes to external internet
- PostgreSQL persists in Docker volume

## Design Philosophy

1. **Simplicity**: Server-side rendering, standard HTML forms, minimal JavaScript
2. **Self-hosting**: Single machine deployment via Docker Compose
3. **Performance**: Async database operations with SQLAlchemy, connection pooling
4. **Security**: CSRF protection, bcrypt hashing, content sanitization
5. **Retro aesthetic**: Oldschool forum UX with no modern frameworks
6. **Small scale**: Designed for ~50 concurrent users

## No Modern Frontend Stack

This project intentionally avoids:

- Frontend build systems (webpack, vite, etc.)
- TypeScript
- Frontend frameworks (React, Vue, etc.)
- JSON API responses (uses HTML)
- Client-side state management

All responses are complete HTML documents rendered server-side, keeping the codebase focused and maintainable.
