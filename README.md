# UniFrames

Create university-branded profile photos from your browser. Upload a photo, crop it, pick your university, choose a frame from Cloudflare R2, preview, and download. Optionally, generate frames via Google Gemini.

This is a monorepo containing a Next.js frontend and a FastAPI backend, plus supporting scripts and docs.

## Features

- Step-by-step UI: upload → crop → select university → choose frame → preview & download
- FastAPI backend serving frame metadata and images stored in Cloudflare R2
- On-demand DB sync from R2 by university name or id
- Optional frame generation using Google Gemini
- Turborepo + pnpm workspace structure

## Monorepo Layout

- `apps/frontend`: Next.js 15 + React 19 + Tailwind CSS UI
- `apps/backend`: FastAPI app exposing REST endpoints; integrates with SQLite and Cloudflare R2
- `apps/scripts`: Python utility scripts (scaffolding)
- `docs/`: Prompt snippets and guidance for frame generation

## Quick Start

Prerequisites:
- Node.js 18.18+ (or Node 20+ recommended)
- pnpm 8+
- Python 3.11+

Optional (enables R2-backed frames and Gemini generation):
- Cloudflare R2 account and credentials
- Google Gemini API key

### 1) Backend setup

Terminal A:

```
cd apps/backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in `apps/backend` with your settings:

```
# Google Gemini (required for /gemini-frames)
GEMINI_API_KEY=your_gemini_api_key

# Cloudflare R2 (required for R2-backed endpoints)
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET=frame-images
R2_PUBLIC_DOMAIN=https://<your-public-r2-domain>   # e.g. https://pub-xxxxxxxxxxxxxxxxxxxxxxxxxxxx.r2.dev

# SQLite DB
# Point this to your SQLite file with Universities + frames tables
UNIV_DB_PATH=/absolute/path/to/apps/backend/univ.db
```

Run the API:

```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Key entrypoint: `apps/backend/main.py:1`

### 2) Frontend setup

Terminal B:

```
cd apps/frontend
pnpm install
```

Create `.env.local` in `apps/frontend`:

```
NEXT_PUBLIC_API_SERVER=http://localhost:8000
```

Start the dev server:

```
pnpm dev
```

Open http://localhost:3000

Note: If your R2 public domain differs from the default, update `apps/frontend/next.config.ts:7` to include it under `images.remotePatterns`.

## How It Works

- Upload and crop happen in the browser, producing a square image.
- The frontend queries the backend for available frames per university and renders them as overlays.
- Final image is composed client-side on a high-DPI canvas and exported as PNG.
- Optionally, the backend can generate frames via the Gemini API.

## Configuration

- Frontend → Backend URL: `apps/frontend/lib/universities.ts:3` expects `NEXT_PUBLIC_API_SERVER`.
- Allowed image domains: `apps/frontend/next.config.ts:7` must include your R2 public domain.
- Backend env (examples above) power R2 and Gemini integrations.

## API Reference (selected)

Base URL: `http://localhost:8000/api/v1`

- `GET /frames/universities/from-r2`
  - Query: `strict_check` (bool, optional). Lists university folder names found in R2.
- `GET /frames/get-frame?name=<University Name>`
  - Returns public URLs for `1.png` frames under the university folder (recursively).
- `GET /frames/universities`
  - Lists universities that have frames in the DB.
- `GET /frames/by-name?name=<University Name>&sync_if_empty=true`
  - Looks up by name; if none in DB, syncs from R2 then returns frames.
- `GET /frames/by-id?uid=<id>`
  - Returns frames by university id.
- `POST /gemini-frames/`
  - Form fields: `university_name`, `university_mascot`, `image` (file). Generates a framed image using Gemini.

Swagger UI: `http://localhost:8000/docs`

Relevant files:
- Backend router index: `apps/backend/app/routers/__init__.py:1`
- R2 client: `apps/backend/app/services/r2_client.py:1`
- University/frame service: `apps/backend/app/services/univ_frames_service.py:1`
- Gemini service: `apps/backend/app/services/gemini_frame_service.py:1`

## Data & Storage

- Frames in R2 are organized by top-level folders per university. The backend exposes helpers to:
  - List folders in the bucket
  - Check for `1.png` under each university (optionally recursive)
  - Build public URLs using `R2_PUBLIC_DOMAIN`
- SQLite stores `Universities` and `frames` metadata. Point `UNIV_DB_PATH` to a DB with those tables.
- An on-demand sync fills the `frames` table based on R2 contents when requested by name or id.

## Development Notes

- Frontend
  - Build: `pnpm -C apps/frontend build`
  - Type-check: `pnpm -C apps/frontend type-check`
- Backend
  - Run: `uvicorn main:app --reload`
  - Docs: `http://localhost:8000/docs`

## Troubleshooting

- CORS errors: The backend enables broad CORS in dev; ensure you’re hitting the right port and URL.
- Images not loading: Add your R2 `hostname` to `apps/frontend/next.config.ts` and restart the dev server.
- Empty frames list: Verify R2 credentials and `R2_PUBLIC_DOMAIN`; try `GET /api/v1/frames/universities/from-r2` to validate access.
- DB path: Ensure `UNIV_DB_PATH` points to a valid SQLite file. Example file included at `apps/backend/univ.db`.

## Docs & Prompts

- Prompt guide: `docs/nano-banana-prompt-guide.md:1`
- Example prompt JSON: `docs/prompt-v1.json:1`

## Security

- Do not commit secrets. Keep API keys and credentials in `.env` files or your secrets manager.

## License

Add a license if you plan to open-source. Otherwise, treat this repository as proprietary.
