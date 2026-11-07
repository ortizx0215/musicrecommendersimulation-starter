import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

# --- Algorithm Recipe weights (max total = 5.0) ---
ENERGY_WEIGHT = 2.0
GENRE_WEIGHT = 1.5
MOOD_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5

# A "related" genre or mood earns this fraction of the full match points.
PARTIAL_CREDIT = 0.5

# Energy gap at which a song earns zero energy points.
ENERGY_TOLERANCE = 0.5

# Moods that feel alike; a song in the same family as the user's mood is "related".
MOOD_FAMILIES = [
    {"chill", "relaxed", "peaceful", "focused"},
    {"sad", "melancholy", "nostalgic", "moody"},
    {"happy", "playful", "uplifting", "euphoric", "romantic"},
    {"intense", "angry", "confident"},
]

NUMERIC_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile into the dict format used by score_song()."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Stores the song catalog this recommender will rank."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k Song objects for the user, best match first."""
        prefs = _profile_to_prefs(user)
        ranked = recommend_songs(prefs, [vars(song) for song in self.songs], k)
        by_id = {song.id: song for song in self.songs}
        return [by_id[song_dict["id"]] for song_dict, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song was scored as it was."""
        score, reasons = score_song(_profile_to_prefs(user), vars(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for field in NUMERIC_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs


_TRUE_STRINGS = {"true", "yes", "y", "1"}
_FALSE_STRINGS = {"false", "no", "n", "0", ""}


def _to_bool(value) -> bool:
    """Parses a bool, rejecting ambiguous strings (plain bool('False') would be True)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in _TRUE_STRINGS:
            return True
        if text in _FALSE_STRINGS:
            return False
    raise ValueError(f"likes_acoustic must be true/false, got {value!r}")


def normalize_prefs(user_prefs: Dict) -> Dict:
    """
    Cleans raw user preferences so scoring can't be tricked by messy input.

    - genre/mood: stripped and lowercased (' Pop ' -> 'pop')
    - energy: converted to float and clamped to 0.0-1.0 ('0.8' -> 0.8, 1.5 -> 1.0)
    - likes_acoustic: parsed to a real bool ('False' -> False)
    Keys the user didn't provide stay absent. Raises ValueError on unparseable values.
    """
    prefs: Dict = {}
    for key in ("genre", "mood"):
        if key in user_prefs and user_prefs[key] is not None:
            prefs[key] = str(user_prefs[key]).strip().lower()
    if user_prefs.get("energy") is not None:
        try:
            energy = float(user_prefs["energy"])
        except (TypeError, ValueError):
            raise ValueError(f"energy must be a number, got {user_prefs['energy']!r}") from None
        prefs["energy"] = min(1.0, max(0.0, energy))
    if user_prefs.get("likes_acoustic") is not None:
        prefs["likes_acoustic"] = _to_bool(user_prefs["likes_acoustic"])
    return prefs


def _genres_related(a: str, b: str) -> bool:
    """
    True when two genres share a head word (the last word), e.g. 'indie pop' and 'pop'.

    Whole-word matching avoids substring accidents: 'k-pop' is not 'pop', and
    'indie' alone is not a kind of 'indie pop' or 'indie folk'.
    """
    a_words, b_words = a.split(), b.split()
    return bool(a_words and b_words) and a_words[-1] == b_words[-1]


def _moods_related(a: str, b: str) -> bool:
    """True when both moods belong to the same mood family."""
    return any(a in family and b in family for family in MOOD_FAMILIES)


def _match_points(song_value: str, user_value: str, weight: float, related) -> Tuple[float, str]:
    """Returns (points, kind) for an exact, related, or missing categorical match."""
    song_value, user_value = song_value.lower(), user_value.lower()
    if not user_value:
        return 0.0, ""
    if song_value == user_value:
        return weight, "matches"
    if related(song_value, user_value):
        return weight * PARTIAL_CREDIT, f"is related to '{user_value}'"
    return 0.0, ""


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences (the Scoring Rule).
    Required by recommend_songs() and src/main.py

    user_prefs keys: "genre", "mood", "energy" (0-1), optional "likes_acoustic" (bool).
    Returns (score, reasons).
    """
    user_prefs = normalize_prefs(user_prefs)
    score = 0.0
    reasons: List[str] = []

    # Energy: reward closeness to the target, not higher/lower values.
    # Points fall off linearly and hit zero at ENERGY_TOLERANCE away.
    if "energy" in user_prefs:
        gap = abs(song["energy"] - user_prefs["energy"])
        similarity = max(0.0, 1 - gap / ENERGY_TOLERANCE)
        points = ENERGY_WEIGHT * similarity
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{points:.2f})"
        )

    points, kind = _match_points(
        song["genre"], str(user_prefs.get("genre", "")), GENRE_WEIGHT, _genres_related
    )
    if points:
        score += points
        reasons.append(f"genre '{song['genre']}' {kind} (+{points:.2f})")

    points, kind = _match_points(
        song["mood"], str(user_prefs.get("mood", "")), MOOD_WEIGHT, _moods_related
    )
    if points:
        score += points
        reasons.append(f"mood '{song['mood']}' {kind} (+{points:.2f})")

    # Acoustic fit: only applied when the user stated a preference.
    if "likes_acoustic" in user_prefs:
        acousticness = song["acousticness"]
        fit = acousticness if user_prefs["likes_acoustic"] else 1 - acousticness
        points = ACOUSTIC_WEIGHT * fit
        score += points
        label = "acoustic" if user_prefs["likes_acoustic"] else "non-acoustic"
        reasons.append(f"{label} fit (+{points:.2f})")

    return round(score, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Ranks all songs and returns the top k (the Ranking Rule).
    Required by src/main.py

    Sorts by score (descending), breaks ties by energy closeness, then title.
    Returns a list of (song_dict, score, explanation).
    """
    user_prefs = normalize_prefs(user_prefs)
    target_energy = user_prefs.get("energy", 0.5)

    # Judge every song: score_song returns (score, reasons) for each one.
    judged = [(song, *score_song(user_prefs, song)) for song in songs]

    # sorted() returns a new ranked list and leaves the caller's catalog untouched.
    ranked = sorted(
        judged,
        key=lambda item: (
            -item[1],                                   # highest score first
            abs(item[0]["energy"] - target_energy),     # tie: closer energy wins
            item[0]["title"],                           # tie: alphabetical
        ),
    )
    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
