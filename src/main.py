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
    from src.recommender import load_songs, recommend_songs  # python -m src.main
except ImportError:
    from recommender import load_songs, recommend_songs  # python src/main.py

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"
MAX_SCORE = 5.0
WIDTH = 60


def print_recommendations(user_prefs: dict, recommendations: list) -> None:
    """Prints the user profile and a numbered list of songs with scores and reasons."""
    profile = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print("=" * WIDTH)
    print(f"User profile: {profile}")
    print("=" * WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} / {MAX_SCORE:.2f}   ({song['genre']}, {song['mood']})")
        for reason in explanation.split("; "):
            print(f"     - {reason}")

    print("\n" + "=" * WIDTH)


def main() -> None:
    """Loads the catalog, ranks songs for the default profile, and prints the top 5."""
    songs = load_songs(str(DATA_PATH))
    print(f"Loaded songs: {len(songs)}\n")

    # Default taste profile: upbeat pop, happy mood, high energy, prefers non-acoustic.
    # Alternative to try: {"genre": "r&b", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(user_prefs, recommendations)


if __name__ == "__main__":
    main()
