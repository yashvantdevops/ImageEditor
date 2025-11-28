# Canvas3T

Canvas3T is a three-tier painting studio featuring a Flask REST API, a React single-page experience, and a Rust/WebAssembly toolchain for high-performance canvas operations. Metadata lives in SQLite while image assets and thumbnails persist on disk via Docker volumes.

Highlights:

- Advanced canvas engine in WASM (brush, eraser, fill, blur/sharpen/invert filters, undo/redo).
- Import art from any URL (server-side proxy normalizes formats) or from local files.
- Save/export in PNG, JPEG, or WEBP; metadata is searchable (folder, tags, format, full-text).
- Built-in auth panel in the SPA for registering/logging in users, plus gallery filters (format + tags) that stay in sync with the backend query params.

## Project Structure

```
backend/      Flask app, models, REST endpoints, tests
frontend/     Vite + React SPA with gallery + editor
wasm/         Rust crate compiled to WebAssembly for canvas tooling
data/         Host-mounted folders for SQLite database + image assets
```

## Requirements

- Python 3.11+
- Node.js 18+
- Rust + `wasm-pack` (for WASM helpers)

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run --debug
```

First boot seeds a default studio user (`studio / canvas3t-demo`), which the SPA uses automatically.
Environment variables:

| Variable          | Default                      | Description                                   |
| ----------------- | ---------------------------- | --------------------------------------------- |
| `IMAGE_DIR`       | `../data/images`             | Directory for uploaded images                 |
| `THUMBNAIL_DIR`   | `../data/images/thumbnails`  | Directory for thumbnails                      |
| `DB_PATH`         | `../data/db/app.db`          | SQLite file path                              |
| `RESULTS_PER_PAGE`| `20`                         | Pagination default                            |
| `SECRET_KEY`      | `canvas3t-dev-secret`        | Used for auth token signing                   |
| `ENABLE_RATE_LIMITS` | `true`                    | Toggle API rate limiting                      |

## Frontend Setup

```bash
cd frontend
npm install
npm run build:wasm   # compile the Rust canvas engine once
npm run dev
```

Set `VITE_API_URL` to the backend origin when running against Docker or remote APIs.

The header includes a compact auth panel. Use the seeded `studio / canvas3t-demo` user or create a new account; once authenticated, paintings automatically save under your user id.

## WASM Tools

All advanced canvas operations (brush, eraser, fill, filters, undo/redo) are implemented in Rust and compiled to WebAssembly.

```bash
cd wasm
wasm-pack build --release --target web --out-dir ../frontend/src/wasm/pkg
```

Local development: run `npm run build:wasm` inside `frontend/` whenever you change the Rust code. Docker builds run this step automatically using the multi-stage frontend image.

## Docker-Only Workflow

All services are containerized; no local Python/Node installs are required.

```bash
docker compose build        # builds backend, frontend, wasm
docker compose up -d        # starts containers, volumes, network
docker compose ps           # verify canvas3t_api + canvas3t_frontend are healthy
```

Named resources:

- Containers: `canvas3t_api`, `canvas3t_frontend`
- Volumes: `canvas3t_images` (uploaded art), `canvas3t_db` (SQLite file). Inspect data via `docker volume inspect canvas3t_db` or open a shell: `docker compose run --rm web ls /app/db`.
- Network: `canvas3t_net`

Run backend tests inside Docker:

```bash
docker compose run --rm web pytest
```

Run frontend tests:

```bash
docker compose run --rm frontend npm run test
```

The React build is served via `canvas3t_frontend` on host port 5173; Flask (`gunicorn`) is exposed on port 5000.

## Testing

- Backend: `pytest` inside `backend/`
- Frontend: `npm run test`
- WASM: `cargo test --target wasm32-unknown-unknown`

## API Overview

Key endpoints (see `docs/ARCHITECTURE.md` for details):

- `POST /api/users` (register; requires `password`)
- `POST /api/auth/login` (returns signed token + user payload)
- `POST /api/paintings`
- `POST /api/paintings/import-url` (proxy + normalize remote images for the editor)
- `GET /api/paintings`, `GET /api/paintings/<id>`
- `PUT /api/paintings/<id>`
- `DELETE /api/paintings/<id>`
- `GET /api/search`

All painting responses include `image_url`, `thumbnail_url`, and the stored `format`, `width`, and `height`.

