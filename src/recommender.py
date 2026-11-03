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
MOOD_WEIGHT = 1.5
GENRE_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5

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


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences (the Scoring Rule).
    Required by recommend_songs() and src/main.py

    user_prefs keys: "genre", "mood", "energy" (0-1), optional "likes_acoustic" (bool).
    Returns (score, reasons).
    """
    score = 0.0
    reasons: List[str] = []

    # Energy: reward closeness to the target, not higher/lower values.
    if "energy" in user_prefs:
        similarity = 1 - abs(song["energy"] - user_prefs["energy"])
        points = ENERGY_WEIGHT * similarity
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{points:.2f})"
        )

    if song["mood"].lower() == str(user_prefs.get("mood", "")).lower():
        score += MOOD_WEIGHT
        reasons.append(f"mood matches '{song['mood']}' (+{MOOD_WEIGHT:.2f})")

    if song["genre"].lower() == str(user_prefs.get("genre", "")).lower():
        score += GENRE_WEIGHT
        reasons.append(f"genre matches '{song['genre']}' (+{GENRE_WEIGHT:.2f})")

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
    target_energy = user_prefs.get("energy", 0.5)
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    scored.sort(
        key=lambda item: (
            -item[1],
            abs(item[0]["energy"] - target_energy),
            item[0]["title"],
        )
    )
    return scored[:k]
