# 🎵 Music Recommender Simulation

## Project Summary

TuneScout 1.0 is a small music recommender that runs from the command line. You describe your taste with four settings: your favorite genre, a mood, how energetic you want the music to be (0 to 1), and whether you like acoustic music. It scores all 20 songs in the catalog against those settings and prints the top 5, along with a short list of reasons for every pick.

Along the way I tested it on four everyday listener profiles and ten "trick" profiles that were built to break it, fixed the bugs those trick profiles found, ran a weight shift experiment, and wrote up the biases I noticed. The full write-up is in the [Model Card](model_card.md).

---

## How The System Works

Real apps like Spotify and YouTube use a mix of two approaches. Collaborative filtering learns from what other people do, like their likes, skips, replays, and playlist adds, so if people with similar habits enjoyed a song, you probably will too. Content-based filtering looks at the songs themselves, using things like tempo, energy, mood, and genre to find tracks that sound like what you already like. Big systems combine both and then rank everything using context like the time of day or what device you're on.

My version is content-based, since it doesn't have any listening history from other users. Being close in energy counts the most, matching the genre comes next, matching the mood is a smaller bonus, and acoustic fit is more of a light tiebreaker. I put genre above mood because mood overlaps a lot with energy (chill songs are low energy and intense songs are high energy), so a big mood bonus would basically count the same thing twice. Near misses get half credit, so indie pop still counts for a pop fan and melancholy still counts for someone who wants sad music. For energy, a song earns more points the closer it is to what you asked for, not just for being higher or lower.

### Features used

Each `Song` has a genre, mood, energy, and acousticness, and those four are what get scored. Genre and mood get full credit for an exact match or half credit for something related, like indie pop for pop or melancholy for sad. Energy is scored on how close it is to the user's target, and acousticness is scored on how well it fits the user's acoustic preference. Songs also have an id, title, and artist, which are just used for display. Tempo, valence, and danceability are stored but not scored, because tempo and danceability follow energy really closely in this dataset, so including them would just double count the same "intensity."

The `UserProfile` has a favorite genre and favorite mood that get compared to each song's genre and mood, a target energy from 0 to 1 for how energetic they want the music, and a true or false setting for whether they like acoustic songs.

### Algorithm Recipe (finalized)

Here's how a single song gets scored:

```
score = 2.0 × max(0, 1 − |song.energy − target_energy| / 0.5)
      + 1.5 × genre_match      (1 exact, 0.5 related, 0 otherwise)
      + 1.0 × mood_match       (1 exact, 0.5 same mood family, 0 otherwise)
      + 0.5 × (acousticness if likes_acoustic else 1 − acousticness)
```

| Feature | Max points | Why |
|---|---|---|
| Energy | 2.0 | It's the strongest "vibe" signal. Points drop to 0 once a song is 0.5 or more away from the target, so a song that's way off can't coast on leftover points. |
| Genre | 1.5 | It captures long-term taste and doesn't depend on energy. |
| Mood | 1.0 | It matters, but it overlaps with energy, so I weighted it lower to avoid counting the same thing twice. |
| Acoustic | 0.5 | It's just a light tiebreaker. |

The mood families are {chill, relaxed, peaceful, focused}, {sad, melancholy, nostalgic, moody}, {happy, playful, uplifting, euphoric, romantic}, and {intense, angry, confident}.

The highest possible score is 5.0, and every song also gets a list of reasons showing where its points came from.

For ranking, every song in the catalog gets scored and then sorted from highest to lowest. If two songs tie, the one closer to the target energy wins, and if they're still tied it goes alphabetically by title. The top 5 are the recommendations.

To choose the weights, I started from a common baseline (+2.0 genre, +1.0 mood, plus energy similarity) and compared three different weightings across five test profiles. A mood-heavy version pushed the only R&B song out of an R&B fan's top 5, and a version with genre at 2.0 put that same song at #1 even though its energy was pretty far off. Genre at 1.5 and mood at 1.0 landed in between. I also changed the energy scoring from `1 − gap` to a curve that hits 0 at a gap of 0.5, which stopped low-energy chill songs from showing up for someone who wanted high energy.

### Expected Biases

Genre and vibe kind of pull against each other here. A genre match (+1.5) is worth less than matching both mood and energy (up to +3.0), so for an R&B, chill, 0.35 energy listener, Library Rain (lofi, chill, energy 0.35) scores 3.43 and beats Velvet Static, the only R&B song (romantic, energy 0.52), which scores 3.02. That means someone who names a genre can get songs from other genres first if their genre's songs don't match the vibe. Bumping the genre weight to about 1.9 flips that, but then a song in the right genre could win even with a bad energy match.

People who like a rare genre also get thin results. There are 17 genres across 20 songs, so a lofi fan gets three genre matches while a metal or classical fan gets one, and the rest of their top 5 gets filled with songs that just have a similar energy level (a rock fan ends up with EDM and pop, for example).

The mood families are my own judgment calls too. Putting "romantic" with "happy" or "moody" with "sad" is just how I see it, and other people would probably group them differently.

Valence isn't used at all, so a sad, low-energy listener can get calm but upbeat songs like Spacewalk Thoughts, since the system only looks at energy and the mood label and not how positive the song actually sounds.

Genre matching is based on whole words and is pretty literal. Two genres only count as related if they share their last word, so indie pop is related to pop but k-pop and pop punk aren't. An earlier version matched on parts of words, which wrongly connected k-pop to pop and "indie" to both indie pop and indie folk, but the edge case tests caught that and it's fixed now. It still can't tell that genres with different names are related, like hip hop and rap.

There's also nothing controlling variety. Nothing stops one artist or one sound from taking over the whole top 5, so it just recommends more of what you already like and never suggests anything new.

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

---

## Experiments You Tried

### Experiment 1: Weight shift (double energy, halve genre)

For this experiment I doubled `ENERGY_WEIGHT` from 2.0 to 4.0 and cut `GENRE_WEIGHT` in half from 1.5 to 0.75 in `src/recommender.py`. Mood (1.0) and acoustic (0.5) stayed the same, so the highest possible score went from 5.0 to 6.25.

Before running it, I had to make sure the math still worked. `MAX_SCORE` used to be hard-coded as 5.0 in `main.py`, which would have printed impossible scores like "6.18 / 5.00," so now it's calculated from the weights in `recommender.py`. I checked all 280 song and profile combinations (including the trick profiles in `src/evaluate.py`), and every score stayed between 0 and 6.25. A perfect match scored exactly 6.25, and half credit for related genres was still exactly half the genre weight.

Here's what changed in the top 5:

| Profile | Rank | Before (baseline) | After (experiment) |
|---|---|---|---|
| High-Energy Pop | #4 | Bassline Fever (edm, energy 0.95) | Fuego Lento (latin, energy 0.78) |
| High-Energy Pop | #5 | Fuego Lento (latin, energy 0.78) | Bassline Fever (edm, energy 0.95) |
| Chill Lofi | all | no change | no change |
| Deep Intense Rock | #5 | Concrete Verses (hip hop, confident) | Sunrise City (pop, happy) |
| Late-Night R&B | #4 | Velvet Static (r&b, romantic) | Coffee Shop Stories (jazz, relaxed) |
| Late-Night R&B | #5 | Coffee Shop Stories (jazz, relaxed) | Focus Flow (lofi, focused) |

Overall, the results were different but not more accurate. The top 3 didn't change for any profile, since songs that match on genre, mood, and energy all at once win no matter which weights you use. For High-Energy Pop, it was pretty neutral, since Fuego Lento's energy is a little closer to the target and either song works fine at #4. Deep Intense Rock got worse, because a happy pop song pushed out a confident hip hop track for an intense rock listener just because its energy was 0.1 closer. Late-Night R&B also got worse, because Velvet Static, the only R&B song in the catalog, fell out of the top 5 completely, so someone who asked for R&B didn't get any R&B at all.

With energy making up 64% of the max score, the recommender basically turned into an energy matcher that mostly ignores genre. That actually goes the wrong way for the Late-Night R&B problem, since Velvet Static would need `GENRE_WEIGHT` above about 1.9 to rank #1 for that profile. I switched the weights back to the original (energy 2.0, genre 1.5) but kept the calculated `MAX_SCORE`.

---

## Limitations and Risks

The catalog is really small. With 20 songs across 17 genres, most genres only have one song, so a lot of listeners get one match in their genre at most.

Energy also ends up deciding most of the rankings. In this catalog, mood and acousticness move almost exactly with energy (energy and acousticness have a correlation of −0.96), so people with mixed tastes, like "sad but high energy" or "upbeat but acoustic," get pretty bad matches.

It only sees labels and numbers, so it doesn't know anything about lyrics, language, an artist's style, or what a song is actually for. That's why Gym Hero, a workout song, still shows up at #3 for a happy pop fan.

It doesn't learn or add variety either. It never picks up on what you play or skip, and nothing stops the top 5 from all sounding the same.

And I labeled everything myself. I picked every song's mood and decided which moods go together, so the results carry my own judgment.

Sections 6 and 7 of the [Model Card](model_card.md) have the evidence behind all of this.

---

## Reflection

My full reflection is in the [Model Card](model_card.md).

A recommender turns data into predictions by turning "taste" into numbers and adding them up. TuneScout never actually knows whether you'll like a song. It just measures how close a song's labels are to your four settings, and the weights decide which kind of closeness matters most. That simple math still makes lists that feel personal, which surprised me. It also means every result depends on choices someone made, like which features to score, how much each one counts, and how the songs are labeled.

Bias showed up in places I didn't expect. Nothing in the code favors any group of listeners, but the catalog does. Calm songs are acoustic and loud songs are electric, so people whose tastes don't follow that pattern quietly get worse recommendations. Having only one song in a genre meant an R&B fan got mostly lofi. Real apps have millions of songs, but the same thing can happen on a bigger scale, where whatever is missing or poorly labeled in the data becomes a blind spot for the people who want it.
