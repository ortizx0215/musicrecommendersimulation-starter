"""
System Evaluation: adversarial / edge-case profiles for the Music Recommender.

Each profile is designed to "trick" the scoring logic or expose an unexpected
result. Run with:  python -m src.evaluate
"""

from pathlib import Path

try:
    from src.recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"

# name -> (profile, what it is probing)
ADVERSARIAL_PROFILES = {
    "Sad Raver (conflicting energy + mood)": (
        {"genre": "edm", "mood": "sad", "energy": 0.9, "likes_acoustic": False},
        "Every sad/melancholy song has energy <= 0.30. Which signal wins?",
    ),
    "Acoustic Headbanger (conflicting acoustic + genre)": (
        {"genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": True},
        "The only metal song has acousticness 0.03. Does acoustic pref matter at all?",
    ),
    "Genre Loyalist vs. Energy (genre dominates?)": (
        {"genre": "classical", "mood": "peaceful", "energy": 0.9, "likes_acoustic": False},
        "Wants high energy but a genre/mood whose only song is energy 0.18.",
    ),
    "K-Pop Fan (substring genre trick)": (
        {"genre": "k-pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        "'pop' is a substring of 'k-pop' -> partial credit for a genre not in catalog?",
    ),
    "Indie Anything (substring over-match)": (
        {"genre": "indie", "mood": "happy", "energy": 0.5, "likes_acoustic": True},
        "'indie' matches both 'indie pop' and 'indie folk' -- two unrelated genres.",
    ),
    "Unknown Mood (no mood family)": (
        {"genre": "pop", "mood": "anxious", "energy": 0.7, "likes_acoustic": False},
        "Mood outside every MOOD_FAMILY silently contributes nothing.",
    ),
    "Out-of-Range Energy (1.5)": (
        {"genre": "rock", "mood": "intense", "energy": 1.5, "likes_acoustic": False},
        "No clamping: every song is >0.5 away, so energy (40% of max score) is zeroed.",
    ),
    "Stringly-Typed Acoustic ('False' as str)": (
        {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": "False"},
        "Non-empty string 'False' is truthy -> treated as LIKES acoustic.",
    ),
    "Whitespace / Case Genre (' Pop ')": (
        {"genre": " Pop ", "mood": "Happy", "energy": 0.85, "likes_acoustic": False},
        "Lowercased but not stripped -- does the padded genre still match?",
    ),
    "Empty Profile ({})": (
        {},
        "No preferences at all: every score is 0, order is pure tie-break.",
    ),
}


def main() -> None:
    songs = load_songs(str(DATA_PATH))
    for name, (prefs, probe) in ADVERSARIAL_PROFILES.items():
        print("=" * 70)
        print(f"{name}\n  prefs: {prefs}\n  probe: {probe}")
        print("-" * 70)
        try:
            for rank, (song, score, why) in enumerate(recommend_songs(prefs, songs, k=3), 1):
                print(f"  {rank}. {song['title']:<22} {score:4.2f}  "
                      f"({song['genre']}, {song['mood']}, e={song['energy']:.2f}, "
                      f"ac={song['acousticness']:.2f})")
                print(f"       {why}")
        except Exception as exc:  # surface crashes as findings, not tracebacks
            print(f"  CRASH: {type(exc).__name__}: {exc}")
    print("=" * 70)

    # Crash probe: energy given as a string (e.g. read from a form/CSV).
    print("Crash probe: energy='0.8' (string)")
    try:
        recommend_songs({"genre": "pop", "energy": "0.8"}, songs, k=1)
        print("  no crash")
    except Exception as exc:
        print(f"  CRASH: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
