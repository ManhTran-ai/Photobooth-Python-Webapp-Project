<!-- Photobooth hybrid template feature plan -->

# Photobooth hybrid template feature

## Goal

Build a seamless, integrated template feature so that after capturing 4 photos the user sees a default white template with the 4 images placed, a right-side control panel to pick colors, icons and template variants, and a final "Export" action that produces a high-quality PNG server-side.

## High-level architecture

```mermaid
flowchart LR
  Client[User Browser]
  Client -->|preview interactions (canvas/SVG)| PreviewUI
  PreviewUI -->|POST /api/collage (final)| API
  API -->|reads| OriginalsFolder[ORIGINALS_FOLDER]
  API --> TemplateEngine[TemplateEngine (Pillow)]
  TemplateEngine --> CollagesFolder[COLLAGES_FOLDER]
  API -->|returns URL| Client
```

## Phases & tasks

### Phase 0 — Preparations (quick)

- Create static folders for templates and decorations under `static/`.
  - `static/templates/previews/`  (small preview PNGs)
  - `static/templates/assets/`    (full-size PNG template images you already have)
  - `static/templates/decorations/` (SVG icons)

- Update `app.py` to ensure `COLLAGES_FOLDER` (already present) is configured (no change needed if present).

### Phase 1 — Server: TemplateEngine and endpoints

- Add `models/template_engine.py` implementing a Pillow-based renderer that:
  - Accepts: image_paths (length N), template_name, color_vars, decorations, fill_mode
  - Supports layout metadata, gradients, rounded corners, shadows
  - Can rasterize SVG decorations (or accept pre-rendered PNGs)
  - Saves high-res PNG into `app.config['COLLAGES_FOLDER']`

- Add API endpoints in `routes/api.py`:
  - `GET /api/templates` — return template metadata and preview URLs
  - `POST /api/collage` — synchronous render, accepts JSON payload and returns `collage_url`

- Implement fill strategies for insufficient images: `duplicate`, `placeholder`, `center`, and a `slots` detection per-template.

### Phase 2 — Assets and metadata

- Create `models/template_metadata.py` or a JSON file `static/templates/templates.json` storing each template's metadata (positions, photo_size, supports_color_vars, layout).
- Place your 10 PNG templates into `static/templates/assets/` and create small preview thumbnails into `static/templates/previews/`.
- Add SVG icon set to `static/templates/decorations/` (use inline-friendly SVGs, each with simple colorizable fills).

### Phase 3 — Frontend preview UI (session page)

- Update `templates/session.html` (used by `routes.views.session_view`) to include:
  - A main canvas/SVG area that places the 4 thumbnails into the default white template.
  - A right-side control panel with:
    - Color palette controls (3 color variables: bg, accent, border)
    - Icons picker (grid of SVGs)
    - Template selector (show previews from `/api/templates`)
    - Fill-mode selector for fewer images
  - Buttons: `Apply` (on-client preview) and `Export` (POST to `/api/collage` for final render).

- Implement JS to:
  - Fetch session photos (`/api/sessions/<id>/photos`) and template list
  - Render preview using SVG composition (preferred) or canvas
  - Allow drag/drop placement of icons and color updates
  - When Export clicked, POST assembled options to `/api/collage` and show returned URL/preview

### Phase 4 — Integrations and UX polish

- Wire `capture` flow to redirect to `/session/<session_id>` after last photo is saved.
- Add preview thumbnails and allow user to re-order photos before exporting.
- Add simple undo/clear for decorations on preview.

### Phase 5 — Tests, performance, and production hardening

- Add unit test for `TemplateEngine.create_collage` with various payloads (1–4 images, decorations, gradients).
- Add basic load testing (a few concurrent renders) to estimate CPU usage.
- Add caching for generated collages for identical payloads (hash payload → existing file).
- Optional: if load rises, migrate render to background queue (Celery/RQ) and make `/api/collage` asynchronous.

## Important file list (to edit/create)

- `models/template_engine.py`  (new)
- `models/template_metadata.py` or `static/templates/templates.json` (new)
- `routes/api.py` — add `/api/templates` and `/api/collage` handlers
- `templates/session.html` — add preview UI and JS
- `static/js/session_collage.js` — new JS for client preview and export
- `static/templates/assets/` — paste your 10 PNG templates here
- `static/templates/previews/` — thumbnails of above
- `static/templates/decorations/` — SVG icons

## Example API payload (POST /api/collage)

```json
{
  "session_id": "<uuid>",
  "template": "pastel_pink",
  "colors": {"bg":"#FFFFFF","accent":"#FF69B4","border":"#000000"},
  "decorations": [{"name":"heart","x":520,"y":1200,"scale":0.8,"color":"#FF69B4"}],
  "fill_mode": "duplicate"
}
```

## Minimal server-side implementation notes

- Use `Image.open(...)` and carefully `convert('RGBA')` before pasting.
- For SVG decorations, prefer `cairosvg.svg2png(url=...)` to rasterize, or pre-render server-side into PNG for performance.
- When pasting images with borders, account for additional border size when computing positions.
- Save final image to `app.config['COLLAGES_FOLDER']` with a deterministic filename or random suffix.

## Acceptance criteria (done when)

- After capturing 4 photos, `session.html` shows a white template with photos placed and a control panel to change color/icons/templates.
- Clicking `Export` returns a URL to a high-res PNG stored in `COLLAGES_FOLDER` that matches the preview selection.
- For <4 photos, the UI respects `fill_mode` and server returns a correct collage.
- Templates and decorations are stored under `static/templates/...` and can be updated by pasting new assets.

## Risks & mitigations

- CPU-heavy renders: mitigate with caching, image size limits, and optional background jobs.
- SVG rasterization: use `cairosvg` or pre-rendered PNGs for simplicity and speed.

### Progress

- Assets placed: 10 template PNG files have been added to `static/templates/assets/`.  
  - Previews (thumbnails) should be placed in `static/templates/previews/`.  
  - Decorations (SVG icons) should be placed in `static/templates/decorations/`.

### To-dos (current)

- [x] Create static folders for templates and decorations
- [in_progress] Add Pillow-based TemplateEngine in models
- [ ] Add /api/templates and /api/collage endpoints
- [ ] Add template metadata JSON or module
- [x] Paste 10 PNG templates and SVG icons into static/templates folders
- [ ] Implement session preview UI (SVG/canvas) and control panel
- [ ] Wire Export button to POST /api/collage and show result
- [ ] Add tests for TemplateEngine and run basic load tests
- [ ] Document usage and update README with asset paths


