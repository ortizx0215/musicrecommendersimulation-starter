"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

try:
    from src.recommender import MAX_SCORE, load_songs, recommend_songs  # python -m src.main
except ImportError:
    from recommender import MAX_SCORE, load_songs, recommend_songs  # python src/main.py

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"
WIDTH = 60

# Distinct taste profiles used to test how the recommender behaves for different listeners.
PROFILES = {
    "High-Energy Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False,
    },
    "Late-Night R&B": {
        "genre": "r&b", "mood": "chill", "energy": 0.35, "likes_acoustic": True,
    },
}


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Prints the user profile and a numbered list of songs with scores and reasons."""
    profile = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print("=" * WIDTH)
    print(f"Profile: {name}")
    print(f"  {profile}")
    print("=" * WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} / {MAX_SCORE:.2f}   ({song['genre']}, {song['mood']})")
        for reason in explanation.split("; "):
            print(f"     - {reason}")

    print("\n" + "=" * WIDTH)


def main() -> None:
    """Loads the catalog, ranks songs for every profile in PROFILES, and prints each top 5."""
    songs = load_songs(str(DATA_PATH))
    print(f"Loaded songs: {len(songs)}\n")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)
        print()


if __name__ == "__main__":
    main()
