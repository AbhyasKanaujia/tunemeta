"""Minimal desktop UI for tunemeta: pick a file, look up a track, write the tags.

Built on pywebview: a native OS window (WKWebView on macOS, WebView2 on
Windows, WebKitGTK on Linux) rendering plain HTML/CSS/JS, bridged to Python
via `js_api`. No bundled browser engine (unlike Electron), a real native
file-open dialog (unlike a page running in a system browser tab), and it
freezes cleanly with PyInstaller into a single EXE/app per platform.

Three steps, always in that order: choose a file, look up a track, review
and write. All lookup/tagging logic stays in the existing provider/artwork/
tagging modules -- this file is the bridge (Api) and presentation (HTML/JS)
only.
"""

from __future__ import annotations

import base64
import io
import json
import os
from dataclasses import replace

import webview
from PIL import Image

from tunemeta import artwork, tagging
from tunemeta.models import TrackMetadata
from tunemeta.providers import DEFAULT_PROVIDER, PROVIDERS

EMBEDDED_ART_SIZE = 800

# (TrackMetadata attribute, on-screen label) -- the fields a user can review
# and correct before writing tags. Anything not listed here (track/disc
# totals, explicit, source_url, artwork_url) passes through untouched.
EDITABLE_FIELDS = [
    ("title", "Title"),
    ("artist", "Artist"),
    ("album", "Album"),
    ("album_artist", "Album Artist"),
    ("genre", "Genre"),
    ("year", "Year"),
    ("track_number", "Track #"),
    ("disc_number", "Disc #"),
]
_INT_FIELDS = {"year", "track_number", "disc_number"}

PAGE_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>tunemeta</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0; padding: 28px 24px; color: #1d1d1f; background: #fff;
    overflow-y: auto;
  }
  @media (prefers-color-scheme: dark) { body { color: #f2f2f2; background: #1c1c1e; } }
  h1 { font-size: 18px; font-weight: 600; margin: 0 0 20px; }
  label { display: block; font-size: 12px; color: #86868b; margin-bottom: 4px; }
  input, select {
    width: 100%; height: 38px; padding: 0 10px; font-size: 14px; border-radius: 8px;
    border: 1px solid #d2d2d7; background: transparent; color: inherit;
    -webkit-appearance: none; appearance: none;
  }
  @media (prefers-color-scheme: dark) { input, select { border-color: #48484a; } }
  select {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2386868b' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 8px center; background-size: 14px;
    padding-right: 28px;
  }
  .row { display: flex; gap: 10px; align-items: flex-end; }
  .row > div { flex: 1; }
  button {
    padding: 9px 16px; font-size: 14px; font-weight: 500; border-radius: 8px;
    border: none; background: #0071e3; color: #fff; cursor: pointer; white-space: nowrap;
  }
  button:disabled { background: #a1a1a6; cursor: default; }
  button.link {
    background: none; color: #0071e3; padding: 0; font-size: 13px; font-weight: 400;
    text-decoration: underline;
  }
  .hide { display: none !important; }
  .lineinfo { font-size: 13px; color: #86868b; margin: 0 0 16px; display: flex; gap: 8px; align-items: center; }
  #fileLine { word-break: break-all; }
  .card {
    display: flex; gap: 14px; align-items: flex-start; padding: 12px 16px;
    border-radius: 12px; background: rgba(0, 0, 0, 0.035); border: 1px solid #e2e2e7;
    margin-bottom: 18px;
  }
  @media (prefers-color-scheme: dark) { .card { background: rgba(255, 255, 255, 0.05); border-color: #3a3a3c; } }
  .artCol { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: none; }
  .artCaption { font-size: 10px; color: #a1a1a6; text-align: center; }
  #currentArtwork {
    width: 56px; height: 56px; object-fit: cover; border-radius: 8px; background: #e8e8ed;
    visibility: hidden; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  }
  .cardText { min-width: 0; }
  .cardTitle { font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .cardSubtitle { font-size: 13px; color: #6e6e73; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  @media (prefers-color-scheme: dark) { .cardSubtitle { color: #a1a1a6; } }
  .cardMeta { font-size: 11px; color: #a1a1a6; margin-top: 4px; letter-spacing: .2px; }
  .hint { color: #86868b; margin: 0 0 16px; }
  .center { text-align: center; padding: 30px 0; }
  #stepSearch { margin-bottom: 20px; }
  #stepReview { padding-top: 16px; border-top: 1px solid #d2d2d7; }
  @media (prefers-color-scheme: dark) { #stepReview { border-color: #48484a; } }
  #preview { display: flex; gap: 20px; margin-bottom: 16px; }
  #artwork { width: 120px; height: 120px; object-fit: cover; border-radius: 8px; background: #e8e8ed; visibility: hidden; }
  #fields { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 10px 14px; align-content: start; }
  .actions { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
  #status { font-size: 13px; color: #86868b; }
</style>
</head>
<body>
<p id="fileLine" class="lineinfo hide"></p>
<div id="currentTagsRow" class="card hide">
  <div class="artCol">
    <img id="currentArtwork" alt="">
    <div id="currentArtworkCaption" class="artCaption"></div>
  </div>
  <div class="cardText">
    <div id="currentTitle" class="cardTitle"></div>
    <div id="currentSubtitle" class="cardSubtitle"></div>
    <div id="currentMeta" class="cardMeta"></div>
  </div>
</div>

<section id="stepFile" class="center">
  <p class="hint">Choose an MP3 file to tag.</p>
  <button id="browseBtn" disabled>Choose File…</button>
</section>

<section id="stepSearch" class="hide">
  <label>Search</label>
  <div class="row">
    <input id="identifier" placeholder="Song title, artist, or a music link">
    <div style="flex: 0 0 110px;"><select id="provider"></select></div>
    <button id="lookupBtn">Search</button>
  </div>
</section>

<section id="stepReview" class="hide">
  <div id="preview">
    <div class="artCol">
      <img id="artwork" alt="">
      <div id="artworkCaption" class="artCaption"></div>
    </div>
    <div id="fields"></div>
  </div>
  <div class="actions">
    <span id="status"></span>
    <button id="tagBtn">Write Tags</button>
  </div>
</section>

<script>
const FIELDS = __FIELDS_JSON__;
const PROVIDERS = __PROVIDERS_JSON__;
const DEFAULT_PROVIDER = "__DEFAULT_PROVIDER__";

const el = (id) => document.getElementById(id);
const show = (id) => el(id).classList.remove('hide');
const hide = (id) => el(id).classList.add('hide');

const providerSelect = el('provider');
for (const p of PROVIDERS) {
  const opt = document.createElement('option');
  opt.value = p; opt.textContent = p; opt.selected = (p === DEFAULT_PROVIDER);
  providerSelect.appendChild(opt);
}

const inputs = {};
const fieldsEl = el('fields');
for (const [key, label] of FIELDS) {
  const wrap = document.createElement('div');
  const lbl = document.createElement('label');
  lbl.textContent = label;
  const inp = document.createElement('input');
  inp.id = 'field-' + key;
  inputs[key] = inp;
  wrap.append(lbl, inp);
  fieldsEl.appendChild(wrap);
}

const statusEl = el('status');
const browseBtn = el('browseBtn');
const lookupBtn = el('lookupBtn');
const tagBtn = el('tagBtn');
const artworkImg = el('artwork');
const identifierInput = el('identifier');

const state = { path: '' };

function setImage(imgEl, dataUrl) {
  if (dataUrl) {
    imgEl.src = dataUrl;
    imgEl.style.visibility = 'visible';
  } else {
    imgEl.removeAttribute('src');
    imgEl.style.visibility = 'hidden';
  }
}

function renderFileLine(fileSize) {
  el('fileLine').textContent = '';
  const span = document.createElement('span');
  span.textContent = '🎵 ' + state.path + (fileSize ? ' · ' + fileSize : '');
  const change = document.createElement('button');
  change.className = 'link';
  change.textContent = 'Change';
  change.addEventListener('click', backToFileStep);
  el('fileLine').append(span, change);
  show('fileLine');
}

function renderCurrentInfo(tags, artworkDataUrl, artworkDimensions) {
  setImage(el('currentArtwork'), artworkDataUrl);
  el('currentArtworkCaption').textContent = artworkDimensions || '';

  if (Object.keys(tags).length === 0 && !artworkDataUrl) { hide('currentTagsRow'); return; }

  el('currentTitle').textContent = tags.title || 'No title tag';
  el('currentSubtitle').textContent = [tags.artist, tags.album].filter(Boolean).join(' — ');

  const metaParts = [];
  if (tags.genre) metaParts.push(tags.genre);
  if (tags.year) metaParts.push(tags.year);
  if (tags.track_number) metaParts.push('Track ' + tags.track_number);
  if (tags.disc_number) metaParts.push('Disc ' + tags.disc_number);
  el('currentMeta').textContent = metaParts.join(' · ');

  show('currentTagsRow');
}

function backToFileStep() {
  state.path = '';
  hide('fileLine');
  hide('currentTagsRow');
  hide('stepSearch');
  hide('stepReview');
  show('stepFile');
}

window.addEventListener('pywebviewready', () => {
  browseBtn.disabled = false;
});

browseBtn.addEventListener('click', async () => {
  const result = await window.pywebview.api.browse_file();
  if (!result) return;
  state.path = result.path;
  identifierInput.value = result.guess || '';
  renderFileLine(result.file_size);
  renderCurrentInfo(result.current_tags || {}, result.current_artwork_data_url, result.artwork_dimensions);
  hide('stepFile');
  show('stepSearch');
  identifierInput.focus();
});

lookupBtn.addEventListener('click', async () => {
  const identifier = identifierInput.value.trim();
  if (!identifier) { alert('Enter something to search for.'); return; }
  lookupBtn.disabled = true;
  lookupBtn.textContent = 'Searching…';
  const data = await window.pywebview.api.lookup(identifier, providerSelect.value);
  lookupBtn.disabled = false;
  lookupBtn.textContent = 'Search';
  if (!data.ok) {
    alert(data.error);
    return;
  }
  for (const [key] of FIELDS) inputs[key].value = data.fields[key] ?? '';
  setImage(artworkImg, data.artwork_data_url);
  el('artworkCaption').textContent = data.artwork_dimensions
    ? data.artwork_dimensions + (data.artwork_size ? ' · ' + data.artwork_size : '')
    : '';
  show('stepReview');
  statusEl.textContent = `Found "${data.fields.title ?? identifier}" — review the fields, then write tags.`;
});

tagBtn.addEventListener('click', async () => {
  const fields = {};
  for (const [key] of FIELDS) fields[key] = inputs[key].value.trim();
  tagBtn.disabled = true;
  tagBtn.textContent = 'Writing…';
  statusEl.textContent = 'Writing tags…';
  const data = await window.pywebview.api.tag(state.path, fields);
  tagBtn.disabled = false;
  tagBtn.textContent = 'Write Tags';
  if (!data.ok) {
    statusEl.textContent = 'Writing tags failed.';
    alert(data.error);
    return;
  }
  statusEl.textContent = 'Tags written.';
});
</script>
</body>
</html>
"""


def _render_page() -> str:
    return (
        PAGE_HTML.replace("__FIELDS_JSON__", json.dumps(EDITABLE_FIELDS))
        .replace("__PROVIDERS_JSON__", json.dumps(sorted(PROVIDERS)))
        .replace("__DEFAULT_PROVIDER__", DEFAULT_PROVIDER)
    )


def _filename_stem(path: str) -> str:
    """The filename without its extension, verbatim -- no cleanup, no
    guessing at what's clutter. The user reviews it in the Search field
    before it's ever sent anywhere."""
    return os.path.splitext(os.path.basename(path))[0]


def _search_guess(path: str, current_tags: dict) -> str:
    """Prefill for the search box: existing title/artist/album if the file
    already has them, otherwise the filename. No scoring, no cleverness --
    whichever of those three fields are present, in that order, else the
    filename guess."""
    tag_parts = [current_tags[key] for key in ("title", "artist", "album") if current_tags.get(key)]
    return " ".join(tag_parts) if tag_parts else _filename_stem(path)


def _parse_int(text: str, label: str) -> int | None:
    text = text.strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"{label} must be a number.") from None


def _metadata_to_fields(metadata: TrackMetadata) -> dict:
    return {key: getattr(metadata, key) for key, _ in EDITABLE_FIELDS}


def _fields_to_overrides(fields: dict) -> dict:
    overrides = {}
    for key, label in EDITABLE_FIELDS:
        raw = str(fields.get(key, ""))
        overrides[key] = _parse_int(raw, label) if key in _INT_FIELDS else (raw.strip() or None)
    return overrides


def _to_data_url(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def _format_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _image_dimensions(data: bytes) -> str | None:
    try:
        with Image.open(io.BytesIO(data)) as img:
            return f"{img.width}×{img.height}"
    except Exception:
        return None


def _existing_artwork_info(path: str) -> tuple[str | None, str | None]:
    """(data_url, dimensions) for a file's current embedded art, if any.

    No size here on purpose -- the existing file's size already covers that;
    dimensions are the only new fact this adds.
    """
    existing = tagging.read_artwork(path)
    if existing is None:
        return None, None
    data, mime = existing
    return _to_data_url(data, mime), _image_dimensions(data)


def _new_artwork_info(artwork_jpeg: bytes | None) -> tuple[str | None, str | None, str | None]:
    """(data_url, size, dimensions) for artwork about to be embedded."""
    if artwork_jpeg is None:
        return None, None, None
    return _to_data_url(artwork_jpeg, "image/jpeg"), _format_size(len(artwork_jpeg)), _image_dimensions(artwork_jpeg)


class Api:
    """The JS <-> Python bridge. One instance per window; state lives here,
    not in globals, because each window gets its own Api."""

    def __init__(self) -> None:
        self.window: webview.Window | None = None
        self._metadata: TrackMetadata | None = None
        self._artwork_jpeg: bytes | None = None

    def browse_file(self) -> dict | None:
        assert self.window is not None
        result = self.window.create_file_dialog(
            webview.OPEN_DIALOG, file_types=("MP3 Files (*.mp3)", "All files (*.*)")
        )
        if not result:
            return None
        path = result[0]
        current_tags = tagging.read_tags(path)
        current_artwork_data_url, artwork_dimensions = _existing_artwork_info(path)

        return {
            "path": path,
            "guess": _search_guess(path, current_tags),
            "current_tags": current_tags,
            "file_size": _format_size(os.path.getsize(path)),
            "current_artwork_data_url": current_artwork_data_url,
            "artwork_dimensions": artwork_dimensions,
        }

    def lookup(self, identifier: str, provider_name: str) -> dict:
        try:
            identifier = (identifier or "").strip()
            if not identifier:
                raise ValueError("Enter a URL, ID, or search text to look up.")
            provider = PROVIDERS[provider_name]
            metadata = provider.lookup(identifier)

            artwork_jpeg = None
            url = provider.artwork_url(metadata, EMBEDDED_ART_SIZE)
            if url:
                artwork_jpeg = artwork.resize_jpeg(artwork.fetch(url), EMBEDDED_ART_SIZE)

            self._metadata = metadata
            self._artwork_jpeg = artwork_jpeg

            data_url, artwork_size, artwork_dimensions = _new_artwork_info(artwork_jpeg)

            return {
                "ok": True,
                "fields": _metadata_to_fields(metadata),
                "artwork_data_url": data_url,
                "artwork_size": artwork_size,
                "artwork_dimensions": artwork_dimensions,
            }
        except Exception as exc:  # surfaced to the UI, not a stack trace
            return {"ok": False, "error": str(exc)}

    def tag(self, mp3_path: str, fields: dict) -> dict:
        try:
            mp3_path = (mp3_path or "").strip()
            if not mp3_path:
                raise ValueError("Choose an MP3 file first.")
            if self._metadata is None:
                raise ValueError("Look up a track first.")
            metadata = replace(self._metadata, **_fields_to_overrides(fields))
            tagging.write_tags(mp3_path, metadata, self._artwork_jpeg)
            return {"ok": True}
        except Exception as exc:  # surfaced to the UI, not a stack trace
            return {"ok": False, "error": str(exc)}


def main() -> None:
    api = Api()
    window = webview.create_window(
        "tunemeta", html=_render_page(), js_api=api, width=680, height=720, min_size=(560, 480)
    )
    api.window = window
    webview.start()


if __name__ == "__main__":
    main()
