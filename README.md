# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube use hybrid recommenders. **Collaborative filtering** learns from other users' behavior: likes, skips, replays, and playlist adds. If people with similar listening habits enjoyed a song, you probably will too. **Content-based filtering** looks at the songs themselves, using attributes like tempo, energy, mood, and genre to find tracks that resemble what you already like. Large systems combine both, then rank the candidates with context such as time of day or device. My version is a **content-based** recommender, because it has no listening history from other users. It prioritizes the song's *vibe* over its label. Closeness in **energy** counts most, a matching **mood** counts next, a matching **genre** is a smaller bonus, and **acoustic** fit is a light tiebreaker. For numeric features, a song earns more points the *closer* it is to the user's target, not the higher or lower its value is.

### Features used

**`Song`**
- `genre`: scored (exact match bonus)
- `mood`: scored (exact match bonus)
- `energy`: scored (closeness to the user's target)
- `acousticness`: scored (fit with the user's acoustic preference)
- `id`, `title`, `artist`: identification and display
- `tempo_bpm`, `valence`, `danceability`: stored but not scored. Tempo and danceability are strongly correlated with energy in this dataset, so including them would double-count the same "intensity" signal.

**`UserProfile`**
- `favorite_genre`: compared to `Song.genre`
- `favorite_mood`: compared to `Song.mood`
- `target_energy` (0–1): the energy level the user wants
- `likes_acoustic` (True/False): whether to reward acoustic or non-acoustic songs

### Scoring Rule (one song)

```
score = 2.0 × (1 − |song.energy − target_energy|)
      + 1.5 × [song.mood  == favorite_mood]
      + 1.0 × [song.genre == favorite_genre]
      + 0.5 × (acousticness if likes_acoustic else 1 − acousticness)
```

The maximum score is 5.0. Each song also gets a list of reasons explaining where its points came from.

### Ranking Rule (list of songs)

Every song in the catalog is scored, then sorted from highest to lowest. Ties are broken by closeness to the target energy, then by title. The top `k` songs are returned as recommendations.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



