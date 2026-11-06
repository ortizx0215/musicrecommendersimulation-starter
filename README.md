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

Real-world platforms like Spotify and YouTube use hybrid recommenders. **Collaborative filtering** learns from other users' behavior: likes, skips, replays, and playlist adds. If people with similar listening habits enjoyed a song, you probably will too. **Content-based filtering** looks at the songs themselves, using attributes like tempo, energy, mood, and genre to find tracks that resemble what you already like. Large systems combine both, then rank the candidates with context such as time of day or device. My version is a **content-based** recommender, because it has no listening history from other users. Closeness in **energy** counts most, a matching **genre** counts next, a matching **mood** is a smaller bonus, and **acoustic** fit is a light tiebreaker. Genre outranks mood because mood overlaps heavily with energy (chill songs are low-energy, intense songs are high-energy), so a big mood bonus would double-count the same signal. Near-misses earn half credit, so "indie pop" still counts for a pop fan and "melancholy" still counts for a sad mood. For numeric features, a song earns more points the *closer* it is to the user's target, not the higher or lower its value is.

### Features used

**`Song`**
- `genre`: scored (exact match, or half credit for a related genre like "indie pop" vs "pop")
- `mood`: scored (exact match, or half credit for a mood in the same family, e.g. "sad" and "melancholy")
- `energy`: scored (closeness to the user's target)
- `acousticness`: scored (fit with the user's acoustic preference)
- `id`, `title`, `artist`: identification and display
- `tempo_bpm`, `valence`, `danceability`: stored but not scored. Tempo and danceability are strongly correlated with energy in this dataset, so including them would double-count the same "intensity" signal.

**`UserProfile`**
- `favorite_genre`: compared to `Song.genre`
- `favorite_mood`: compared to `Song.mood`
- `target_energy` (0–1): the energy level the user wants
- `likes_acoustic` (True/False): whether to reward acoustic or non-acoustic songs

### Algorithm Recipe (finalized)

**Scoring Rule (one song):**

```
score = 2.0 × max(0, 1 − |song.energy − target_energy| / 0.5)
      + 1.5 × genre_match      (1 exact, 0.5 related, 0 otherwise)
      + 1.0 × mood_match       (1 exact, 0.5 same mood family, 0 otherwise)
      + 0.5 × (acousticness if likes_acoustic else 1 − acousticness)
```

| Feature | Max points | Why |
|---|---|---|
| Energy | 2.0 | The strongest "vibe" signal. Points drop to 0 once a song is 0.5 or more away from the target, so a far-off song can't coast on a generous floor. |
| Genre | 1.5 | Captures long-term taste and is independent of energy. |
| Mood | 1.0 | Matters, but overlaps with energy, so it is weighted lower to avoid double-counting. |
| Acoustic | 0.5 | Light tiebreaker. |

Mood families: {chill, relaxed, peaceful, focused}, {sad, melancholy, nostalgic, moody}, {happy, playful, uplifting, euphoric, romantic}, {intense, angry, confident}.

The maximum score is 5.0. Each song also gets a list of reasons explaining where its points came from.

**Ranking Rule (list of songs):** Every song in the catalog is scored, then sorted from highest to lowest. Ties are broken by closeness to the target energy, then by title. The top `k` songs are returned as recommendations.

**How I chose the weights:** I started from a common baseline (+2.0 genre, +1.0 mood, energy similarity) and compared three weightings across five test profiles. A mood-heavy version pushed the only r&b song out of an r&b fan's top 5. A genre-at-2.0 version ranked that same song #1 even though its energy was well off the target. Genre 1.5 / mood 1.0 sat between the two. Switching energy from `1 − gap` to a curve that reaches 0 at a gap of 0.5 stopped low-energy "chill" songs from showing up for a user who wanted high energy.

### Expected Biases

- **Genre can outweigh a better overall fit.** A genre match (+1.5) makes up for a large energy miss. For an r&b/chill/0.35 user, Velvet Static (r&b, energy 0.52) scores 2.82, close to Library Rain's 3.00, which matches energy and mood exactly. A great song that matches the user's mood and energy but not their genre can still lose to a weaker song in the right genre.
- **Users with a rare genre get thin results.** The catalog has 17 genres across 20 songs. A lofi fan gets three genre matches, but a metal or classical fan gets one, and the rest of their top 5 is filled by songs that only share an energy level (e.g. a rock fan gets EDM and pop).
- **Mood families are my own judgment calls.** Grouping "romantic" with "happy" or "moody" with "sad" reflects my own interpretation, not a universal truth, and other listeners would group them differently.
- **Valence is ignored.** A sad, low-energy listener can be recommended calm but upbeat songs (e.g. Spacewalk Thoughts) because the system only checks energy and the mood label, not how positive the song sounds.
- **Substring genre matching can produce false matches.** "pop" counts as related to "indie pop" as intended, but it would also count "k-pop" or "pop punk" as related, even though those are quite different styles.
- **No variety control.** Nothing stops one artist or one sound from filling the whole top 5. The system recommends more of what the user already likes and never suggests something new.

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

Output of `python -m src.main` for the default pop/happy profile:

```
Loaded songs: 20

============================================================
User profile: genre=pop, mood=happy, energy=0.8, likes_acoustic=False
============================================================

1. Sunrise City by Neon Echo
   Score: 4.83 / 5.00   (pop, happy)
     - energy 0.82 vs target 0.80 (+1.92)
     - genre 'pop' matches (+1.50)
     - mood 'happy' matches (+1.00)
     - non-acoustic fit (+0.41)

2. Rooftop Lights by Indigo Parade
   Score: 3.92 / 5.00   (indie pop, happy)
     - energy 0.76 vs target 0.80 (+1.84)
     - genre 'indie pop' is related to 'pop' (+0.75)
     - mood 'happy' matches (+1.00)
     - non-acoustic fit (+0.33)

3. Gym Hero by Max Pulse
   Score: 3.46 / 5.00   (pop, intense)
     - energy 0.93 vs target 0.80 (+1.48)
     - genre 'pop' matches (+1.50)
     - non-acoustic fit (+0.47)

4. Fuego Lento by Los Brisas
   Score: 2.77 / 5.00   (latin, playful)
     - energy 0.78 vs target 0.80 (+1.92)
     - mood 'playful' is related to 'happy' (+0.50)
     - non-acoustic fit (+0.35)

5. Bassline Fever by Kilowatt Kids
   Score: 2.39 / 5.00   (edm, euphoric)
     - energy 0.95 vs target 0.80 (+1.40)
     - mood 'euphoric' is related to 'happy' (+0.50)
     - non-acoustic fit (+0.49)

============================================================
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



