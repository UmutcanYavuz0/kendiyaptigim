from google import genai as google_genai

from config import GEMINI_API_KEY, GENRE_VISUAL_STYLES
from utils.json_cleaner import clean_and_parse

_client = google_genai.Client(api_key=GEMINI_API_KEY)

REQUIRED_KEYS = [
    "album_name", "artist_name", "year", "label",
    "mood_description", "cover_prompt", "lastfm_tags",
]


def generate_album_metadata(journal_text: str, genre: str, era: str, track_count: int) -> dict:
    visual_style = GENRE_VISUAL_STYLES.get(genre, "artistic, creative, unique")
    prompt = f"""You are a creative music AI. Based on the journal entry / mood description below,
generate a FICTIONAL album concept. Return ONLY a single valid JSON object — no explanations,
no markdown fences, no extra text.

JSON schema (all fields required):
{{
  "album_name": "string",
  "artist_name": "string",
  "year": "string — a plausible year within the {era} era",
  "label": "string — fictional record label name",
  "mood_description": "string — 1-2 sentence poetic mood summary",
  "cover_prompt": "string — detailed visual image generation prompt incorporating: {visual_style}",
  "lastfm_tags": ["5-7 lowercase Last.fm tag strings matching the mood and genre"]
}}

Journal / Mood: \"\"\"{journal_text}\"\"\"
Genre: {genre}
Era: {era}
Track count: {track_count}

Return ONLY the JSON object.
"""
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    data = clean_and_parse(response.text)

    for key in REQUIRED_KEYS:
        if key not in data:
            raise ValueError(f"Missing field in Gemini response: '{key}'")

    return data
