# Canvas3T – Image Gallery & Editing Platform

A full-stack web application for creating, uploading, managing, and editing images with user authentication, persistent storage, and advanced image processing capabilities.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Image Upload & Storage](#image-upload--storage)
- [Docker Deployment](#docker-deployment)
- [Development](#development)
- [Testing](#testing)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Performance Tips](#performance-tips)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Features
- ✅ **User Registration & Login** – Create accounts with secure password hashing (Werkzeug)
- ✅ **Image Upload** – Upload PNG, JPEG, WebP formats with automatic thumbnail generation
- ✅ **Remote Image Import** – Download and persist images from external URLs (e.g., Shutterstock links)
- ✅ **Gallery Management** – Browse, search, filter, and organize images by folder/tags
- ✅ **Anonymous Uploads** – Upload without registration (images saved under temporary user ID)
- ✅ **Download Links** – Get direct download URLs for saved images
- ✅ **Persistent Storage** – Images stored in Docker volumes and local `data/images` directory

### Advanced Features
- 🎨 **Web-Based Canvas Editor** – React TypeScript frontend with Vite for fast editing
- 🎛️ **WASM Image Tools** – Rust-based WASM tools for high-performance image transformations
- 📱 **Responsive Design** – Mobile-friendly gallery and editor UI
- 🔐 **Token-Based Auth** – Secure itsdangerous token generation for sessions
- 🚀 **CORS Enabled** – Cross-origin requests supported for API integration
- 📊 **Rate Limiting** – Built-in API rate limiting (50 req/min default)

---

## Tech Stack

### Backend
- **Framework:** Flask 3.0.3
- **Database:** SQLite (development) / PostgreSQL (production-ready)
- **ORM:** SQLAlchemy + Flask-SQLAlchemy
- **Authentication:** Werkzeug (password hashing), itsdangerous (token generation)
- **Image Processing:** Pillow 10.4.0
- **API Serialization:** Marshmallow + Flask-Marshmallow
- **Server:** Gunicorn 21.2.0 (production WSGI)
- **Testing:** pytest 8.2.2 with 100% pass rate

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite (fast HMR and dev server)
- **Styling:** CSS + responsive design
- **HTTP Client:** Axios
- **State Management:** Zustand
- **WASM Bridge:** Custom TypeScript bridge for Rust WASM tools

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Persistent Storage:** Docker named volumes + bind mounts
- **Image Serving:** Flask static file serving + downloadable attachments

---

## Quick Start

### Prerequisites
- Docker & Docker Compose (recommended for fastest setup)
- Git
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Option 1: Docker (Recommended - 30 seconds to up and running)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dododower/Python_Flask.git
   cd Python_Flask
   ```

2. **Build and start containers:**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the application:**
   - **Frontend:** http://localhost:5173 (Vite dev) or http://localhost:4173 (prod)
   - **Backend API:** http://localhost:5000
   - **Health Check:** http://localhost:5000/health

4. **Verify setup:**
   ```bash
   curl http://localhost:5000/health
   # Expected: {"status": "ok"}
   ```

5. **Default login credentials:**
   ```
   Username: studio
   Password: canvas3t-demo
   ```

### Option 2: Local Development

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=app
flask run --debug
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
Canvas3T/
├── backend/                          # Flask API (production-ready)
│   ├── app/
│   │   ├── __init__.py              # App factory, DB initialization, table creation
│   │   ├── config.py                # Configuration (dev, prod, test)
│   │   ├── extensions.py            # SQLAlchemy, Marshmallow, CORS, Limiter init
│   │   ├── models.py                # User, Painting ORM models
│   │   ├── schemas.py               # Marshmallow validation schemas
│   │   ├── media.py                 # Image serving (GET) and download endpoints
│   │   ├── api/
│   │   │   ├── auth.py              # POST /login endpoint
│   │   │   ├── users.py             # POST /users registration endpoint
│   │   │   ├── paintings.py         # CRUD + remote import endpoints
│   │   │   ├── search.py            # Advanced search/filtering
│   │   │   └── __init__.py
│   │   └── utils/
│   │       ├── storage.py           # Image save/delete utilities (PIL)
│   │       ├── thumbnails.py        # Thumbnail generation (512px max)
│   │       └── rate_limit.py        # Rate limiting (50 req/min)
│   ├── tests/
│   │   ├── conftest.py              # pytest fixtures (app, client, temp DB)
│   │   ├── test_auth.py             # Auth endpoint tests
│   │   ├── test_paintings.py        # CRUD + image upload + remote import tests
│   │   └── __init__.py
│   ├── requirements.txt              # Python dependencies (16 packages)
│   ├── wsgi.py                       # WSGI entry point for Gunicorn
│   └── manage.py                     # CLI utilities (future migrations)
├── frontend/                         # React + TypeScript + Vite
│   ├── src/
│   │   ├── App.tsx                  # Root component
│   │   ├── main.tsx                 # Entry point
│   │   ├── api/
│   │   │   ├── client.ts            # Axios HTTP client with auth headers
│   │   │   ├── auth.ts              # Login/register API calls
│   │   │   ├── paintings.ts         # Gallery CRUD API calls
│   │   │   └── __init__.ts
│   │   ├── components/
│   │   │   ├── GalleryGrid.tsx      # Image grid display with lazy loading
│   │   │   ├── AuthPanel.tsx        # Login/Register UI
│   │   │   ├── CanvasEditor.tsx     # WASM-based image editor
│   │   │   ├── SearchBar.tsx        # Full-text search UI
│   │   │   ├── MetadataPanel.tsx    # Image metadata display
│   │   │   └── __tests__/           # Component tests
│   │   ├── pages/
│   │   │   ├── GalleryView.tsx      # Gallery browse page
│   │   │   ├── EditorView.tsx       # Image editor page
│   │   │   └── DetailView.tsx       # Image detail/download page
│   │   ├── store/
│   │   │   ├── authStore.ts         # Zustand auth state
│   │   │   └── galleryStore.ts      # Gallery pagination state
│   │   ├── hooks/
│   │   │   └── useWasmTools.ts      # WASM tools hook
│   │   ├── wasm/
│   │   │   ├── bridge.ts            # WASM module bridge
│   │   │   └── pkg/                 # Compiled WASM (generated by wasm-pack)
│   │   └── styles.css               # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── Dockerfile
│   └── setupTests.ts
├── wasm/                             # Rust WASM image tools (high-performance)
│   ├── Cargo.toml                   # Rust dependencies
│   ├── src/
│   │   └── lib.rs                   # WASM functions (filters, transforms)
│   └── README.md                    # WASM tool documentation
├── data/                             # Persistent data (gitignored)
│   ├── db/                           # SQLite DB file (auto-created)
│   └── images/                       # Uploaded/imported images (persisted)
├── docker-compose.yml                # Multi-container orchestration (web + frontend + volumes)
├── Dockerfile                        # Backend image (Python 3.11 slim)
└── README.md                         # This file

```

---

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Response Format
All responses are JSON. Errors include `error` or `errors` fields.

---

### Authentication Endpoints

#### Login
**POST** `/auth/login`

Login with existing credentials and receive a session token.

**Request:**
```json
{
  "username": "studio",
  "password": "canvas3t-demo"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "studio",
    "email": "studio@canvas3t.local",
    "created_at": "2025-11-28T12:00:00.000000",
    "updated_at": "2025-11-28T12:00:00.000000"
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "Invalid credentials"
}
```

#### Register
**POST** `/users`

Create a new user account.

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Validation:**
- `username` (required, string, 1-80 chars)
- `email` (optional, valid email format)
- `password` (required, min 8 chars)

**Response (201 Created):**
```json
{
  "id": 2,
  "username": "newuser",
  "email": "user@example.com",
  "created_at": "2025-11-28T12:05:00.000000",
  "updated_at": "2025-11-28T12:05:00.000000"
}
```

**Error (409 Conflict):**
```json
{
  "error": "Username or email already exists"
}
```

#### List Users
**GET** `/users`

Retrieve all registered users.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "studio",
    "email": "studio@canvas3t.local",
    "created_at": "2025-11-28T12:00:00.000000"
  },
  {
    "id": 2,
    "username": "newuser",
    "email": "user@example.com",
    "created_at": "2025-11-28T12:05:00.000000"
  }
]
```

---

### Image Management Endpoints

#### Upload Image
**POST** `/paintings` (multipart/form-data)

Upload an image file with optional metadata.

**Parameters:**
- `image` (file, **required**) – Image file (PNG, JPEG, WebP)
- `user_id` (string, optional) – User ID (auto-creates anonymous user if omitted)
- `title` (string, optional) – Image title
- `folder` (string, optional) – Organization folder
- `tags` (string, optional) – Comma-separated tags (e.g., "art, painting, draft")
- `format` (string, optional) – Target format (PNG, JPEG, WEBP)
- `tools_used` (string, optional) – Tools used to create image

**Request Example (curl):**
```bash
curl -X POST http://localhost:5000/api/paintings \
  -F "user_id=1" \
  -F "title=My Artwork" \
  -F "image=@artwork.png" \
  -F "tags=art,painting" \
  -F "folder=MyFolder" \
  -F "format=WEBP"
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "user": {"id": 1, "username": "studio"},
  "title": "My Artwork",
  "filename": "a1b2c3d4_artwork.png",
  "thumbnail": "a1b2c3d4_artwork_thumb.png",
  "width": 1920,
  "height": 1080,
  "format": "WEBP",
  "image_url": "http://localhost:5000/media/images/a1b2c3d4_artwork.png",
  "thumbnail_url": "http://localhost:5000/media/thumbnails/a1b2c3d4_artwork_thumb.png",
  "tags": "art,painting",
  "folder": "MyFolder",
  "created_at": "2025-11-28T12:10:00.000000",
  "updated_at": "2025-11-28T12:10:00.000000"
}
```

**Error (500 Internal Server Error):**
```json
{
  "error": "Invalid image payload"
}
```

#### List Paintings (Gallery)
**GET** `/paintings?user_id=1&folder=Drafts&q=search&page=1&per_page=20`

Retrieve paginated list of paintings with optional filters.

**Query Parameters:**
- `user_id` (int) – Filter by user ID
- `folder` (string) – Filter by folder name
- `q` (string) – Full-text search by title
- `tag` (string) – Filter by single tag
- `format` (string) – Filter by image format (PNG, JPEG, WEBP)
- `page` (int, default=1) – Page number (1-indexed)
- `per_page` (int, default=20) – Items per page (max 100)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "user": {"id": 1, "username": "studio"},
      "title": "My Artwork",
      "filename": "a1b2c3d4_artwork.png",
      "image_url": "http://localhost:5000/media/images/a1b2c3d4_artwork.png",
      "thumbnail_url": "http://localhost:5000/media/thumbnails/a1b2c3d4_artwork_thumb.png",
      "width": 1920,
      "height": 1080,
      "format": "WEBP",
      "tags": "art,painting",
      "folder": "MyFolder",
      "created_at": "2025-11-28T12:10:00.000000"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1,
  "pages": 1
}
```

#### Get Image Details
**GET** `/paintings/{id}`

Retrieve metadata and URLs for a specific image.

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "user": {"id": 1, "username": "studio"},
  "title": "My Artwork",
  "image_url": "http://localhost:5000/media/images/a1b2c3d4_artwork.png",
  "thumbnail_url": "http://localhost:5000/media/thumbnails/a1b2c3d4_artwork_thumb.png",
  "width": 1920,
  "height": 1080,
  "format": "WEBP",
  "tags": "art,painting",
  "folder": "MyFolder",
  "created_at": "2025-11-28T12:10:00.000000"
}
```

**Error (404 Not Found):**
```json
{
  "error": "404 Not Found"
}
```

#### View Image
**GET** `/media/images/{filename}`

Stream image file for viewing in browser.

**Response:** Image file (200 OK) with appropriate `Content-Type` header

#### Download Image
**GET** `/media/download/{filename}`

Download image file as attachment.

**Response:** Image file with `Content-Disposition: attachment` header

#### Update Image Metadata
**PUT** `/paintings/{id}`

Update title, tags, folder, or replace the image file.

**Request (JSON):**
```json
{
  "title": "Updated Title",
  "tags": "updated,tags,list",
  "folder": "New Folder"
}
```

**Or multipart/form-data to replace image:**
```bash
curl -X PUT http://localhost:5000/api/paintings/1 \
  -F "title=New Title" \
  -F "image=@new_image.png"
```

**Response (200 OK):** Updated painting object (same as GET /paintings/{id})

#### Delete Image
**DELETE** `/paintings/{id}`

Delete an image and its thumbnail.

**Response (200 OK):**
```json
{
  "status": "deleted"
}
```

**Error (404 Not Found):**
```json
{
  "error": "404 Not Found"
}
```

---

### Remote Image Import Endpoints

#### Import Image as Data URL (Preview)
**POST** `/paintings/import-url`

Download a remote image and return as base64 data URL (for canvas preview).

**Request (JSON):**
```json
{
  "image_url": "https://example.com/image.png",
  "format": "JPEG"
}
```

**Response (200 OK):**
```json
{
  "data_url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
  "width": 1920,
  "height": 1080,
  "format": "JPEG"
}
```

#### Import & Save Remote Image
**POST** `/paintings/import-url/save`

Download a remote image and persist it as a Painting record.

**Request (JSON):**
```json
{
  "image_url": "https://example.com/image.png",
  "user_id": 1,
  "title": "Imported Artwork",
  "format": "JPEG",
  "folder": "Imports",
  "tags": "imported"
}
```

**Note:** If `user_id` is omitted or invalid, an anonymous user is auto-created.

**Response (201 Created):** Same as upload endpoint

---

### Health Check

#### Server Status
**GET** `/health`

Check if API is running.

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

## Authentication

### Token System
Canvas3T uses **itsdangerous URLSafeTimedSerializer** for token generation:
- **Algorithm:** HMAC with SHA-512
- **Payload:** `{"user_id": <int>}`
- **Salt:** `canvas3t-auth`
- **Expiration:** Configurable (default: no expiry)

### Default Credentials (Development)
```
Username: studio
Password: canvas3t-demo
Email:    studio@canvas3t.local
```

### Setting Custom SECRET_KEY (Production)
```bash
export SECRET_KEY="your-super-secret-key-here-min-32-chars"
docker-compose up --build -d
```

---

## Image Upload & Storage

### Supported Formats
- **PNG** – Lossless, recommended for artwork (no loss of detail)
- **JPEG** – Lossy, suitable for photographs (20-30% file size reduction)
- **WebP** – Modern, efficient (30-40% smaller than JPEG)

### Storage Locations
- **Docker:** `/app/images/` (Docker volume `canvas3t_images`)
- **Local Dev:** `data/images/` (bind mounted in docker-compose)
- **Thumbnails:** `images/thumbnails/` (512px max, auto-generated)

### File Naming Convention
Images are renamed to prevent collisions:
```
{UUID}_{original_basename}.{extension}
Example: a1b2c3d4e5f6_artwork.png
         f5cfc31a1c44_photo_original.jpg
```

### Automatic Thumbnail Generation
512x512px thumbnails are generated for all uploads (configurable via `THUMBNAIL_SIZE` env).

### Upload Limits
- **Max File Size:** 20 MB (configurable via `MAX_UPLOAD_MB`)
- **Rate Limit:** 50 requests per minute (configurable via `RATE_LIMIT`)
- **Formats:** PNG, JPEG, WebP (configurable in code)

---

## Docker Deployment

### Quick Commands

**Build images:**
```bash
docker-compose build
```

**Start services (background):**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f web        # Backend logs
docker-compose logs -f frontend   # Frontend logs
```

**Stop services:**
```bash
docker-compose down
```

**Stop and remove all data:**
```bash
docker-compose down -v
```

### Production Deployment

**Example with custom environment variables:**
```bash
export SECRET_KEY="prod-secret-key-here"
export DATABASE_URL="postgresql://user:password@db-host:5432/canvas3t"
export FLASK_ENV="production"
export CORS_ALLOW_ORIGINS="https://canvas3t.com,https://www.canvas3t.com"

docker-compose -f docker-compose.yml up -d
```

### Environment Variables

#### Backend
```bash
# Authentication & Security
SECRET_KEY                 # Token signing key (default: canvas3t-dev-secret)

# Database
DATABASE_URL               # DB connection string (default: sqlite:///data/db/app.db)
DB_PATH                    # SQLite DB path (default: data/db/app.db)

# Storage
IMAGE_DIR                  # Image storage dir (default: data/images)
THUMBNAIL_DIR              # Thumbnail dir (default: IMAGE_DIR/thumbnails)
THUMBNAIL_SIZE             # Max thumbnail size px (default: 512)

# Application
FLASK_APP                  # Flask app module (default: app)
FLASK_ENV                  # Environment: development, testing, production
MAX_UPLOAD_MB              # Max upload size MB (default: 20)
RESULTS_PER_PAGE           # Gallery pagination (default: 20)

# API
CORS_ALLOW_ORIGINS         # CORS allowed origins (default: *)
ENABLE_RATE_LIMITS         # Enable rate limiting (default: true)
RATE_LIMIT                 # Rate limit rule (default: 50/minute)
```

#### Frontend
```bash
VITE_API_URL               # Backend API base URL (default: http://web:5000)
```

### Docker Compose Structure
```yaml
services:
  web:                     # Backend API (Gunicorn on port 5000)
    - Volume: canvas3t_images:/app/images
    - Volume: canvas3t_db:/app/db
    
  frontend:                # React SPA (Vite on port 5173)
    - Port: 5173 (dev) / 4173 (prod)
    
volumes:
  canvas3t_images:         # Persists uploaded/imported images
  canvas3t_db:             # Persists SQLite DB
```

---

## Development

### Backend Testing

Run all tests:
```bash
cd backend
pytest -q                  # Quick output
pytest -v                  # Verbose
pytest --cov              # With coverage report
```

Run tests in Docker:
```bash
docker exec canvas3t_api pytest -q
```

**Test Results:**
```
....  4 passed in 1.40s (all critical paths covered)
```

**Test Coverage:**
- ✅ User registration & login
- ✅ Image upload + thumbnail generation
- ✅ Remote image download & persistence
- ✅ Gallery listing & pagination
- ✅ Image metadata retrieval & updates
- ✅ Image deletion

### Example Test
```python
def test_user_and_painting_flow(client):
    # Register user
    resp = client.post("/api/users", json={
        "username": "alice",
        "email": "a@example.com",
        "password": "secret123"
    })
    assert resp.status_code == 201
    user_id = resp.json["id"]

    # Login
    login_resp = client.post("/api/auth/login", json={
        "username": "alice",
        "password": "secret123"
    })
    assert login_resp.status_code == 200

    # Upload image
    img = create_test_image()
    upload_resp = client.post("/api/paintings", data={
        "user_id": str(user_id),
        "title": "Test Painting",
        "image": (img, "test.png"),
        "format": "webp"
    })
    assert upload_resp.status_code == 201
    assert upload_resp.json["format"] == "WEBP"
```

### Backend Linting & Formatting
```bash
pip install black flake8
black backend/             # Auto-format
flake8 backend/            # Check style
```

### Frontend Development
```bash
cd frontend
npm run dev               # Start Vite dev server (port 5173)
npm run build             # Production build
npm run preview           # Preview prod build
npm test                  # Run tests
npm run lint              # ESLint check
```

### Database Migrations (Future)
```bash
cd backend
flask db init             # Initialize migration folder
flask db migrate -m "add columns"  # Create migration
flask db upgrade          # Apply migrations
flask db downgrade        # Rollback
```

---

## Testing

### Run Full Test Suite
```bash
docker exec canvas3t_api pytest -q
```

### Test Coverage by Feature
- **Auth:** Login, registration, password hashing ✅
- **Upload:** File upload, thumbnail generation, format conversion ✅
- **Remote Import:** URL download, format normalization, DB persistence ✅
- **Gallery:** Listing, pagination, search, filtering ✅
- **Download:** Attachment headers, file serving ✅
- **Anonymous:** Auto-user creation for uploads without user_id ✅

---

## Advanced Features

### WASM Image Tools (Rust)
The `wasm/` directory contains Rust code compiled to WebAssembly for client-side, high-performance image processing:

**Available Transformations:**
- Filters (grayscale, sepia, blur, sharpen)
- Color adjustments (brightness, contrast, saturation)
- Transformations (rotate, flip, scale)
- Drawing tools (brush, eraser, fill)
- History (undo/redo)

**Usage Example (TypeScript):**
```typescript
import { applyGrayscale } from './wasm/pkg/canvas3t_wasm';

const canvas = document.getElementById('editor') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
const processed = applyGrayscale(imageData.data);
ctx.putImageData(new ImageData(processed, canvas.width, canvas.height), 0, 0);
```

**Rebuild WASM (after code changes):**
```bash
cd wasm
wasm-pack build --release --target web
```

### Rate Limiting
API requests are rate-limited to prevent abuse and ensure fair usage:
- **Default:** 50 requests per minute per IP
- **Customize:** Set `RATE_LIMIT` env var (e.g., `100/hour`, `1000/day`)
- **Disable:** Set `ENABLE_RATE_LIMITS=false`

### CORS Configuration
Cross-Origin Resource Sharing is fully configurable:
```
Access-Control-Allow-Origin: * (default)
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

Restrict origins in production:
```bash
export CORS_ALLOW_ORIGINS="https://canvas3t.com,https://www.canvas3t.com"
```

### Anonymous Uploads
Users can upload images without authentication:
- **Behavior:** Automatic temporary user created with UUID-based username (anon_xxxxxxxx)
- **Ownership:** Image associated with temp user
- **Gallery Display:** Shows "anon_xxxxxxxx" as uploader

---

## Troubleshooting

### Images Not Saving (500 Error)
**Error:** `500 Internal Server Error` on image upload

**Solutions:**
1. Check API logs: `docker logs canvas3t_api | tail -50`
2. Verify volumes are mounted: `docker inspect canvas3t_api | grep -A 10 Mounts`
3. Ensure directories exist: `docker exec canvas3t_api ls -la /app/images`
4. Restart containers: `docker-compose restart`

### "No Such Table" Database Error
**Error:** `sqlite3.OperationalError: no such table: paintings`

**Solution:**
- Tables are auto-created on app startup
- If error persists, reset DB: `docker-compose down -v && docker-compose up`

### Port Already in Use
**Error:** `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solutions:**
```bash
# Kill existing containers
docker-compose down

# Or use different port (edit docker-compose.yml)
# Change "5000:5000" to "5001:5000" for backend
```

### CORS/Frontend Cannot Connect
**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solutions:**
- Verify frontend and backend are on same Docker network: `docker network ls`
- Check `VITE_API_URL` in frontend environment
- Inspect CORS headers: `curl -i http://localhost:5000/health`

### Performance Issues
**Symptom:** Slow image uploads or gallery loading

**Solutions:**
- Check available disk space: `df -h data/`
- Verify no resource limits on Docker: `docker stats`
- Increase `per_page` param for gallery pagination
- Enable Redis for caching (advanced setup)

---

## Performance Tips

### Production Optimization Checklist
- [ ] Use PostgreSQL instead of SQLite for concurrent requests
- [ ] Enable gzip compression in reverse proxy (Nginx)
- [ ] Set up CDN for static image files (CloudFront, CloudFlare)
- [ ] Add database indexing on `user_id`, `folder`, `tags`
- [ ] Configure Redis for session caching
- [ ] Use environment-specific configs (prod vs dev)
- [ ] Set `FLASK_ENV=production` and `DEBUG=false`

### Example Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name api.canvas3t.com;

    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering on;
        proxy_buffer_size 1k;
        proxy_buffers 24 4k;
    }

    location /media/ {
        alias /app/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Database Optimization
```sql
-- Add indexes for common queries (run on SQLite)
CREATE INDEX IF NOT EXISTS idx_paintings_user_id ON paintings(user_id);
CREATE INDEX IF NOT EXISTS idx_paintings_folder ON paintings(folder);
CREATE INDEX IF NOT EXISTS idx_paintings_created_at ON paintings(created_at DESC);
```

---

## Contributing

### Code Style Guidelines
- **Python:** Follow PEP 8 (use `black` for auto-formatting)
- **TypeScript:** Use ESLint + Prettier configuration
- **Commit Messages:** Use Conventional Commits format
  - `feat: add image batch upload`
  - `fix: resolve thumbnail generation bug`
  - `docs: update API documentation`
  - `test: add integration tests for login`

### Contributing Workflow
1. Fork the repository on GitHub
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and commit: `git commit -m "feat: describe your feature"`
4. Push to your fork: `git push origin feature/amazing-feature`
5. Open Pull Request with detailed description
6. Ensure all tests pass: `docker exec canvas3t_api pytest -q`

### Reporting Issues
When opening an issue, please include:
- OS, Docker version, and system specs
- Step-by-step reproduction steps
- Full error logs (use `docker logs canvas3t_api`)
- Screenshots or recorded video if applicable

---

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## Support & Contact

- **GitHub Issues:** [Report bugs](https://github.com/dododower/Python_Flask/issues)
- **Discussions:** [Feature requests](https://github.com/dododower/Python_Flask/discussions)
- **Email:** contact@canvas3t.local

---

## Changelog

### v1.0.0 (2025-11-28) – Launch Release
✨ **Features:**
- User registration and login with secure token-based auth
- Image upload with automatic thumbnail generation (PNG, JPEG, WebP)
- Remote image import and save from any URL
- Full-featured gallery with search, filter, and pagination
- Anonymous uploads with random user ID assignment
- Direct download links for all images
- Complete Docker containerization (backend + frontend)
- Comprehensive test suite (all paths covered)
- WASM-based image tools (Rust) for high-performance editing
- Rate limiting and CORS security

🐛 **Bug Fixes:**
- Fixed database table creation on startup
- Resolved image storage persistence in Docker volumes
- Fixed routing redirect issues
- Removed SQLAlchemy LegacyAPIWarning

---

**Made with ❤️ for image creators and artists worldwide**

**[⬆ Back to top](#canvas3t--image-gallery--editing-platform)**

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

