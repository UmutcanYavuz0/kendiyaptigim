import requests

from config import LASTFM_API_KEY, LASTFM_BASE_URL

_HEADERS = {"User-Agent": "AlbumCoverStudio/1.0"}


def fetch_tracks_by_tag(tag: str, limit: int = 20) -> list:
    params = {
        "method": "tag.gettoptracks",
        "tag": tag,
        "limit": limit,
        "api_key": LASTFM_API_KEY,
        "format": "json",
    }
    try:
        r = requests.get(LASTFM_BASE_URL, params=params, headers=_HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("tracks", {}).get("track", [])
    except Exception:
        return []


def build_tracklist(tags: list, track_count: int) -> list:
    seen, tracks = set(), []

    for tag in tags:
        for t in fetch_tracks_by_tag(tag, limit=20):
            title = t.get("name", "").strip()
            artist_info = t.get("artist", {})
            artist = (
                artist_info.get("name", "").strip()
                if isinstance(artist_info, dict)
                else str(artist_info)
            )
            url = t.get("url", "")

            if not title or not artist:
                continue
            key = (title.lower(), artist.lower())
            if key in seen:
                continue

            seen.add(key)
            tracks.append({"title": title, "artist": artist, "url": url})

            if len(tracks) >= track_count * 3:
                break
        if len(tracks) >= track_count * 2:
            break

    return tracks[:track_count]
