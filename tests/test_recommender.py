from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Edge-case / adversarial regression tests (see src/evaluate.py) ---

import pytest

from src.recommender import (
    normalize_prefs, score_song, recommend_songs, _genres_related,
    ENERGY_WEIGHT, GENRE_WEIGHT, MOOD_WEIGHT,
)


def song_dict(**overrides) -> dict:
    base = {
        "id": 1, "title": "T", "artist": "A", "genre": "pop", "mood": "happy",
        "energy": 0.8, "tempo_bpm": 120.0, "valence": 0.8,
        "danceability": 0.8, "acousticness": 0.2,
    }
    base.update(overrides)
    return base


def test_padded_and_capitalized_genre_still_exact_match():
    clean, _ = score_song({"genre": "pop", "mood": "happy"}, song_dict())
    messy, _ = score_song({"genre": " Pop ", "mood": " HAPPY"}, song_dict())
    assert messy == clean == GENRE_WEIGHT + MOOD_WEIGHT


def test_string_false_means_dislikes_acoustic():
    prefs = normalize_prefs({"likes_acoustic": "False"})
    assert prefs["likes_acoustic"] is False


def test_unparseable_acoustic_raises():
    with pytest.raises(ValueError):
        normalize_prefs({"likes_acoustic": "maybe"})


def test_string_energy_is_converted_not_crash():
    score, _ = score_song({"energy": "0.8"}, song_dict(energy=0.8))
    assert score == ENERGY_WEIGHT


def test_non_numeric_energy_raises_value_error():
    with pytest.raises(ValueError):
        normalize_prefs({"energy": "loud"})


def test_out_of_range_energy_is_clamped():
    assert normalize_prefs({"energy": 1.5})["energy"] == 1.0
    assert normalize_prefs({"energy": -0.3})["energy"] == 0.0
    score, _ = score_song({"energy": 1.5}, song_dict(energy=0.97))
    assert score > 0  # energy points no longer zeroed for every song


@pytest.mark.parametrize("a, b, related", [
    ("indie pop", "pop", True),     # subgenre of pop
    ("pop", "indie pop", True),
    ("k-pop", "pop", False),        # substring, not a word match
    ("indie", "indie pop", False),  # modifier, not the genre itself
    ("indie pop", "indie folk", False),
    ("rock", "rock", True),
])
def test_genre_relation_uses_head_word(a, b, related):
    assert _genres_related(a, b) is related


def test_empty_profile_does_not_crash():
    results = recommend_songs({}, [song_dict(id=1), song_dict(id=2, title="U")], k=2)
    assert len(results) == 2
    assert all(score == 0 for _, score, _ in results)


def test_normalize_does_not_mutate_input():
    raw = {"genre": " Pop ", "energy": "0.8"}
    normalize_prefs(raw)
    assert raw == {"genre": " Pop ", "energy": "0.8"}
