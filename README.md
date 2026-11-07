# 🎵 Music Recommender Simulation

## Project Summary

**TuneScout 1.0** is a small content-based music recommender that runs from the command line. You describe your taste with four settings: a favorite genre, a mood, a target energy level (0 to 1), and whether you like acoustic music. TuneScout scores all 20 songs in its catalog against those settings and prints the top 5, with a list of reasons for every pick.

Along the way I tested it on four everyday listener profiles and ten "trick" profiles built to break it, fixed the bugs those profiles exposed, ran a weight-shift experiment, and documented its biases. The full write-up is in the [Model Card](model_card.md).

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

- **Genre and "vibe" pull against each other.** A genre match (+1.5) is worth less than matching mood and energy together (up to +3.0). For an r&b/chill/0.35 user, Library Rain (lofi, chill, energy 0.35) scores 3.43 and beats Velvet Static, the only r&b song (romantic, energy 0.52), at 3.02. A listener who names a genre can get songs from other genres first when their genre's songs don't match the vibe. Raising the genre weight to about 1.9 flips this result, but then a song in the right genre can win despite a poor energy match.
- **Users with a rare genre get thin results.** The catalog has 17 genres across 20 songs. A lofi fan gets three genre matches, but a metal or classical fan gets one, and the rest of their top 5 is filled by songs that only share an energy level (e.g. a rock fan gets EDM and pop).
- **Mood families are my own judgment calls.** Grouping "romantic" with "happy" or "moody" with "sad" reflects my own interpretation, not a universal truth, and other listeners would group them differently.
- **Valence is ignored.** A sad, low-energy listener can be recommended calm but upbeat songs (e.g. Spacewalk Thoughts) because the system only checks energy and the mood label, not how positive the song sounds.
- **Genre matching is word-based and literal.** Genres count as related only when they share their last word, so "indie pop" is related to "pop" but "k-pop" and "pop punk" are not. (An earlier substring version wrongly matched "k-pop" to "pop" and "indie" to both "indie pop" and "indie folk". The edge-case tests caught this, and it is fixed.) The rule still can't recognize related genres with different names, like "hip hop" and "rap."
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

Run the tests with:

```bash
pytest
```

The tests in `tests/test_recommender.py` cover ranking, explanations, and every edge-case bug found during evaluation (padded text, `"False"` as a string, out-of-range or text energy values, and genre matching).

To run the adversarial "trick" profiles and see how the scoring handles them:

```bash
python -m src.evaluate
```

---

## Sample Recommendation Output

Output of `python -m src.main`, which loads 20 songs and prints the top 5 recommendations for each of four taste profiles.

### High-Energy Pop

```
============================================================
Profile: High-Energy Pop
  genre=pop, mood=happy, energy=0.85, likes_acoustic=False
============================================================

1. Sunrise City by Neon Echo
   Score: 4.79 / 5.00   (pop, happy)
     - energy 0.82 vs target 0.85 (+1.88)
     - genre 'pop' matches (+1.50)
     - mood 'happy' matches (+1.00)
     - non-acoustic fit (+0.41)

2. Rooftop Lights by Indigo Parade
   Score: 3.71 / 5.00   (indie pop, happy)
     - energy 0.76 vs target 0.85 (+1.64)
     - genre 'indie pop' is related to 'pop' (+0.75)
     - mood 'happy' matches (+1.00)
     - non-acoustic fit (+0.33)

3. Gym Hero by Max Pulse
   Score: 3.65 / 5.00   (pop, intense)
     - energy 0.93 vs target 0.85 (+1.68)
     - genre 'pop' matches (+1.50)
     - non-acoustic fit (+0.47)

4. Bassline Fever by Kilowatt Kids
   Score: 2.59 / 5.00   (edm, euphoric)
     - energy 0.95 vs target 0.85 (+1.60)
     - mood 'euphoric' is related to 'happy' (+0.50)
     - non-acoustic fit (+0.49)

5. Fuego Lento by Los Brisas
   Score: 2.57 / 5.00   (latin, playful)
     - energy 0.78 vs target 0.85 (+1.72)
     - mood 'playful' is related to 'happy' (+0.50)
     - non-acoustic fit (+0.35)

============================================================
```

### Chill Lofi

```
============================================================
Profile: Chill Lofi
  genre=lofi, mood=chill, energy=0.35, likes_acoustic=True
============================================================

1. Library Rain by Paper Lanterns
   Score: 4.93 / 5.00   (lofi, chill)
     - energy 0.35 vs target 0.35 (+2.00)
     - genre 'lofi' matches (+1.50)
     - mood 'chill' matches (+1.00)
     - acoustic fit (+0.43)

2. Midnight Coding by LoRoom
   Score: 4.58 / 5.00   (lofi, chill)
     - energy 0.42 vs target 0.35 (+1.72)
     - genre 'lofi' matches (+1.50)
     - mood 'chill' matches (+1.00)
     - acoustic fit (+0.35)

3. Focus Flow by LoRoom
   Score: 4.19 / 5.00   (lofi, focused)
     - energy 0.40 vs target 0.35 (+1.80)
     - genre 'lofi' matches (+1.50)
     - mood 'focused' is related to 'chill' (+0.50)
     - acoustic fit (+0.39)

4. Spacewalk Thoughts by Orbit Bloom
   Score: 3.18 / 5.00   (ambient, chill)
     - energy 0.28 vs target 0.35 (+1.72)
     - mood 'chill' matches (+1.00)
     - acoustic fit (+0.46)

5. Coffee Shop Stories by Slow Stereo
   Score: 2.87 / 5.00   (jazz, relaxed)
     - energy 0.37 vs target 0.35 (+1.92)
     - mood 'relaxed' is related to 'chill' (+0.50)
     - acoustic fit (+0.45)

============================================================
```

### Deep Intense Rock

```
============================================================
Profile: Deep Intense Rock
  genre=rock, mood=intense, energy=0.92, likes_acoustic=False
============================================================

1. Storm Runner by Voltline
   Score: 4.91 / 5.00   (rock, intense)
     - energy 0.91 vs target 0.92 (+1.96)
     - genre 'rock' matches (+1.50)
     - mood 'intense' matches (+1.00)
     - non-acoustic fit (+0.45)

2. Gym Hero by Max Pulse
   Score: 3.44 / 5.00   (pop, intense)
     - energy 0.93 vs target 0.92 (+1.96)
     - mood 'intense' matches (+1.00)
     - non-acoustic fit (+0.47)

3. Iron Cathedral by Graveborne
   Score: 2.79 / 5.00   (metal, angry)
     - energy 0.97 vs target 0.92 (+1.80)
     - mood 'angry' is related to 'intense' (+0.50)
     - non-acoustic fit (+0.48)

4. Bassline Fever by Kilowatt Kids
   Score: 2.37 / 5.00   (edm, euphoric)
     - energy 0.95 vs target 0.92 (+1.88)
     - non-acoustic fit (+0.49)

5. Concrete Verses by Blockline
   Score: 2.14 / 5.00   (hip hop, confident)
     - energy 0.72 vs target 0.92 (+1.20)
     - mood 'confident' is related to 'intense' (+0.50)
     - non-acoustic fit (+0.44)

============================================================
```

### Late-Night R&B

```
============================================================
Profile: Late-Night R&B
  genre=r&b, mood=chill, energy=0.35, likes_acoustic=True
============================================================

1. Library Rain by Paper Lanterns
   Score: 3.43 / 5.00   (lofi, chill)
     - energy 0.35 vs target 0.35 (+2.00)
     - mood 'chill' matches (+1.00)
     - acoustic fit (+0.43)

2. Spacewalk Thoughts by Orbit Bloom
   Score: 3.18 / 5.00   (ambient, chill)
     - energy 0.28 vs target 0.35 (+1.72)
     - mood 'chill' matches (+1.00)
     - acoustic fit (+0.46)

3. Midnight Coding by LoRoom
   Score: 3.08 / 5.00   (lofi, chill)
     - energy 0.42 vs target 0.35 (+1.72)
     - mood 'chill' matches (+1.00)
     - acoustic fit (+0.35)

4. Velvet Static by Mara Lune
   Score: 3.02 / 5.00   (r&b, romantic)
     - energy 0.52 vs target 0.35 (+1.32)
     - genre 'r&b' matches (+1.50)
     - acoustic fit (+0.20)

5. Coffee Shop Stories by Slow Stereo
   Score: 2.87 / 5.00   (jazz, relaxed)
     - energy 0.37 vs target 0.35 (+1.92)
     - mood 'relaxed' is related to 'chill' (+0.50)
     - acoustic fit (+0.45)

============================================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Experiment 1: Weight shift (double energy, halve genre)

**Change:** `ENERGY_WEIGHT` 2.0 → 4.0 and `GENRE_WEIGHT` 1.5 → 0.75 in `src/recommender.py`. Mood (1.0) and acoustic (0.5) stayed the same, so the maximum score went from 5.0 to 6.25.

**Checking the math:** `MAX_SCORE` used to be hard-coded as 5.0 in `main.py`, which would have printed impossible scores like "6.18 / 5.00". It is now computed from the weights in `recommender.py`. Across all 280 song × profile pairs (including the adversarial profiles in `src/evaluate.py`), every score stayed between 0 and 6.25, a perfect match scored exactly 6.25, and related-genre partial credit stayed at exactly half the genre weight.

**Top 5 before → after:**

| Profile | Rank | Before (baseline) | After (experiment) |
|---|---|---|---|
| High-Energy Pop | #4 | Bassline Fever (edm, energy 0.95) | Fuego Lento (latin, energy 0.78) |
| High-Energy Pop | #5 | Fuego Lento (latin, energy 0.78) | Bassline Fever (edm, energy 0.95) |
| Chill Lofi | all | no change | no change |
| Deep Intense Rock | #5 | Concrete Verses (hip hop, confident) | Sunrise City (pop, happy) |
| Late-Night R&B | #4 | Velvet Static (r&b, romantic) | Coffee Shop Stories (jazz, relaxed) |
| Late-Night R&B | #5 | Coffee Shop Stories (jazz, relaxed) | Focus Flow (lofi, focused) |

**Result: different, not more accurate.**

- The top 3 did not change for any profile. Songs that match on genre, mood and energy at once win under either set of weights.
- High-Energy Pop: neutral. Fuego Lento's energy is slightly closer to the target, and either song works at #4.
- Deep Intense Rock: worse. A happy pop song pushed out a confident hip-hop track for an intense rock listener, only because its energy was 0.1 closer.
- Late-Night R&B: worse. Velvet Static, the only R&B song in the catalog, dropped out of the top 5. The user named a genre and got no songs from it.

With energy at 64% of the maximum score, the recommender became an energy matcher that mostly ignores genre. That goes the wrong way for the Late-Night R&B problem: Velvet Static would need `GENRE_WEIGHT` above about 1.9 to rank #1 for that profile. The weights were reverted to the baseline (energy 2.0, genre 1.5). The computed `MAX_SCORE` was kept.

---

## Limitations and Risks

- **Tiny catalog.** 20 songs across 17 genres means most genres have exactly one song, so many listeners get at most one match in their genre.
- **Energy decides most rankings.** In this catalog, mood and acousticness both move almost in lockstep with energy (energy vs. acousticness correlation is −0.96). Listeners with mixed tastes, like "sad but high energy" or "upbeat but acoustic," get poor matches.
- **It only sees labels and numbers.** It knows nothing about lyrics, language, artists' style, or what a song is *for*. Gym Hero, a workout song, still ranks #3 for a happy pop fan.
- **No learning and no variety.** It never learns from what you play or skip, and nothing stops the top 5 from all sounding the same.
- **Hand-made labels.** I chose every song's mood and the mood families myself, so the results carry my own judgment.

See sections 6 and 7 of the [Model Card](model_card.md) for the evidence behind these.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

A recommender turns data into predictions by turning "taste" into numbers and adding them up. TuneScout never knows whether you'll like a song. It only measures how close a song's labels are to your four settings, and the weights decide which kind of closeness matters most. That simple math still produces lists that feel personal, which surprised me. It also means every result depends on choices someone made: which features to score, how much each one counts, and how songs are labeled.

Bias showed up in places I didn't expect. Nothing in the code favors any group of listeners, but the catalog does. Calm songs are acoustic and loud songs are electric, so people whose tastes don't follow that pattern quietly get worse recommendations. One genre with a single song meant an R&B fan got mostly lofi. Real apps have millions of songs, but the same thing can happen at a larger scale: whatever is missing or under-labeled in the data becomes a blind spot for the users who want it.



