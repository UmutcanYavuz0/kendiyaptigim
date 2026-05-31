from dataclasses import dataclass, field
from typing import List


@dataclass
class Track:
    title: str
    artist: str
    url: str = ""


@dataclass
class AlbumModel:
    album_name: str = ""
    artist_name: str = ""
    year: str = ""
    label: str = ""
    mood_description: str = ""
    cover_prompt: str = ""
    lastfm_tags: List[str] = field(default_factory=list)
    tracklist: List[dict] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict) -> "AlbumModel":
        return AlbumModel(
            album_name=data.get("album_name", ""),
            artist_name=data.get("artist_name", ""),
            year=data.get("year", ""),
            label=data.get("label", ""),
            mood_description=data.get("mood_description", ""),
            cover_prompt=data.get("cover_prompt", ""),
            lastfm_tags=data.get("lastfm_tags", []),
            tracklist=data.get("tracklist", []),
        )

    def to_dict(self) -> dict:
        return {
            "album_name": self.album_name,
            "artist_name": self.artist_name,
            "year": self.year,
            "label": self.label,
            "mood_description": self.mood_description,
            "cover_prompt": self.cover_prompt,
            "lastfm_tags": self.lastfm_tags,
            "tracklist": self.tracklist,
        }
