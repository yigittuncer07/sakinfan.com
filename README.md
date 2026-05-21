# sakinfan.com

Sakin hayranlarinin bulusabilecegi bir web sitesi — an oldschool forum built with FastAPI, PostgreSQL, and Redis.

## Prerequisites

- Docker and Docker Compose
- PostgreSQL running on the host machine
- A Cloudflare tunnel token (for external access)

## Setup

1. Copy the example environment file and fill in your values:

   ```bash
   cp .env.example .env
   ```

2. Configure your `.env` with the correct `DATABASE_URL` pointing to your host PostgreSQL instance (use `host.docker.internal` as the host), `SECRET_KEY`, and `TUNNEL_TOKEN`.

3. Build and start the services:

   ```bash
   docker compose up -d --build
   ```

4. Run database migrations:

   ```bash
   docker compose exec web alembic upgrade head
   ```

5. The forum is now accessible at `http://localhost` (via nginx).

## Creating Boards

Boards must be created directly in the database. Connect to your PostgreSQL instance and insert rows:

```sql
INSERT INTO boards (name, description, display_order) VALUES
  ('General Discussion', 'Talk about anything', 0),
  ('Announcements', 'Site announcements and news', 1);
```

## Architecture

- **FastAPI** — server-side rendered HTML with Jinja2 templates
- **PostgreSQL** — persistent data (runs on host, not in Docker)
- **Redis** — session storage
- **nginx** — reverse proxy and static file serving
- **cloudflared** — tunnel for external access

## Development

To view logs:

```bash
docker compose logs -f web
```

To restart after code changes:

```bash
docker compose restart web
```
