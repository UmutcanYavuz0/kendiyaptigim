import threading
from typing import Callable

from services.gemini_service import generate_album_metadata
from services.lastfm_service import build_tracklist
from services.image_service import generate_cover_image


class AlbumController:
    """
    Runs the generation pipeline in a background thread and
    reports progress/results back via callbacks.
    """

    def __init__(
        self,
        on_status: Callable[[str], None],
        on_success: Callable,
        on_error: Callable[[str], None],
    ):
        self._on_status  = on_status
        self._on_success = on_success
        self._on_error   = on_error

    def generate(self, journal: str, genre: str, era: str, track_count: int) -> None:
        threading.Thread(
            target=self._worker,
            args=(journal, genre, era, track_count),
            daemon=True,
        ).start()

    # ── private ──────────────────────────────────────────────────────────────

    def _worker(self, journal: str, genre: str, era: str, track_count: int) -> None:
        try:
            self._on_status("🤖 Gemini is thinking...")
            album_data = generate_album_metadata(journal, genre, era, track_count)

            self._on_status("🎵 Fetching tracks from Last.fm...")
            tags = album_data.get("lastfm_tags", [])
            tracklist = build_tracklist(tags, track_count)
            if not tracklist:
                tracklist = build_tracklist([genre.lower()], track_count)
            album_data["tracklist"] = tracklist

            self._on_status("🎨 Generating cover art...")
            cover = generate_cover_image(album_data.get("cover_prompt", "abstract album cover"))

            self._on_success(album_data, tracklist, cover)

        except Exception as exc:
            self._on_error(str(exc))
