# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  
**TuneScout 1.0**

TuneScout scouts a small song catalog for tracks that fit your vibe.

---

## 2. Goal and Intended Use  
### Goal / Task

TuneScout suggests songs you might like. You tell it four things: a favorite genre, a mood, how energetic you want the music to be (0 to 1), and whether you like acoustic sound. It gives every song a score and shows you the top 5. Each pick comes with a list of reasons, so you can see why it was chosen.

It does not learn from you. It does not know what you played before or what other people like. It only compares your four answers to the facts about each song.

### Intended use

- A classroom project for learning how recommenders work.
- Exploring how small changes to weights change the results.
- Showing why a song was picked, step by step.

### Non-intended use

- Real users on a real music app. The catalog has only 20 songs.
- Judging what music is "good." The scores only measure fit with four settings.
- Any decision that matters to a person, like ads or hiring. The system has known biases (see section 6).
- Users with mixed tastes, like "sad but high energy." It handles them poorly.

---

## 3. How the Model Works  
### Algorithm summary

Think of it like a judge giving points. Every song can earn up to 5 points:

- **Energy (up to 2 points).** The closer the song's energy is to what you asked for, the more points. A song that is way off (0.5 or more away) gets nothing here.
- **Genre (up to 1.5 points).** Full points if it's your genre. Half points if it's a close cousin, like "indie pop" for a pop fan.
- **Mood (up to 1 point).** Full points if it's your mood. Half points if it's a similar mood, like "relaxed" for someone who wants "chill."
- **Acoustic sound (up to 0.5 points).** If you like acoustic music, more acoustic songs get more points. If you don't, less acoustic songs get more.

TuneScout adds up the points for every song and sorts them from highest to lowest. If two songs tie, the one closer to your energy level wins.

### Changes from the starter

- I picked the weights by testing a few versions on real profiles. Energy counts most because it's the strongest "vibe" signal.
- I added "close cousin" half credit for related genres and moods.
- I made TuneScout clean up messy input. Extra spaces, capital letters, numbers typed as text, and energy values outside 0 to 1 are now handled.
- The highest possible score is now calculated from the weights, so it stays correct if the weights change.

---

## 4. Data  
### Data used

- **Size:** 20 songs. I grew the starter catalog from 10 to 20.
- **Variety:** 17 genres and 16 moods. Most genres have only one song. Lofi has the most, with 3.
- **Features per song:** title, artist, genre, mood, energy, tempo, valence (how positive it sounds), danceability, and acousticness.
- **Features actually scored:** genre, mood, energy, and acousticness. Tempo and danceability mostly follow energy, so scoring them would count the same thing twice. Valence is not used.

### Limits of the data

- 20 songs is tiny. Fans of most genres get one genre match at best.
- Energy and acousticness are almost perfect opposites in this catalog. Loud songs are electric and quiet songs are acoustic.
- There are no loud acoustic songs and no high-energy sad songs.
- I made up the songs and labels myself. They reflect my own sense of what "chill" or "intense" means.
- There is no lyrics, language, era, or listening-history data.

---

## 5. Strengths  
- **Clear-cut tastes work great.** When genre, mood, and energy all point the same way, the #1 pick is spot on. Chill Lofi gets Library Rain (4.93 out of 5). Deep Intense Rock gets Storm Runner (4.91).
- **Opposite users get opposite lists.** The pop and lofi lists share zero songs, and so do the rock and lofi lists. That is what you'd expect.
- **The reasons are easy to check.** Every pick lists where its points came from. That made it easy to spot problems, like why Gym Hero shows up for a pop fan.
- **Near misses still count.** A pop fan still gets indie pop. A chill fan still gets "relaxed" and "focused" songs.
- **It doesn't break on messy input.** After the fixes, odd input like `" Pop "` or an energy of 1.5 still gives sensible results.

---

## 6. Limitations and Bias 

Energy quietly decides most rankings, because in this catalog two of the other features are really energy in disguise. Acousticness and energy are almost exact opposites across the 20 songs (correlation −0.96), every "chill"-type song has energy of 0.42 or less, and every "intense"-type song has energy of 0.72 or more, so the mood and acoustic checks mostly reward the same songs the energy gap already rewards. This creates a filter bubble for listeners whose tastes cut across that pattern: the "Sad Raver" test profile (edm, sad, energy 0.9) got no sad songs at all in its top 3, and no song in the catalog is both energetic (above 0.7) and acoustic (above 0.5), so a fan of upbeat acoustic music can never get a strong match. Because a song earns zero energy points once it is 0.5 away from the target, a user's energy setting also walls off a large part of the catalog before genre or mood are even considered. The result is a system that works well for "typical" listeners whose genre, mood and energy line up, and poorly for people with mixed tastes, even though nothing in the code singles them out.

---

## 7. Evaluation  

### Profiles tested

I ran four everyday listener profiles through the recommender and looked at each top 5:

| Profile | Genre | Mood | Energy | Acoustic? |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.85 | no |
| Chill Lofi | lofi | chill | 0.35 | yes |
| Deep Intense Rock | rock | intense | 0.92 | no |
| Late-Night R&B | r&b | chill | 0.35 | yes |

I also ran 10 "trick" profiles (in `src/evaluate.py`) built to break the scoring. They included conflicting tastes like a sad listener who wants high energy, and messy input like `" Pop "` with extra spaces or an energy of 1.5. Those runs found real bugs, which are fixed and covered by tests.

For each list I checked whether the #1 song is what a real fan of that profile would pick, and whether the rest of the list still matches the "feel" of the request.

### Comparing the profiles, pair by pair

**High-Energy Pop vs. Chill Lofi.** These two lists have no songs in common. The pop list is all loud, electric songs (energy 0.76 to 0.95), and the lofi list is all quiet, acoustic-leaning songs (energy 0.28 to 0.42). That makes sense because the two profiles disagree on every setting, so they should land at opposite ends of the catalog.

**High-Energy Pop vs. Deep Intense Rock.** Both want loud, non-acoustic music, so they share two songs: Gym Hero and Bassline Fever. The difference is mood. The pop list fills up with happy and playful songs (Sunrise City, Rooftop Lights, Fuego Lento), while the rock list fills up with intense and angry ones (Storm Runner, Iron Cathedral). When energy is the same, mood decides which loud songs you get.

**High-Energy Pop vs. Late-Night R&B.** There is no overlap. The R&B listener asked for calm, chill, acoustic music, which is the opposite of the pop listener on everything except "I like a specific genre." The R&B list is quiet songs and the pop list is party songs, which is what you would expect.

**Chill Lofi vs. Deep Intense Rock.** Again, no overlap. These are the two most opposite profiles: one wants quiet, relaxed, acoustic songs and the other wants the loudest, most aggressive ones. Each #1 song is a near-perfect match for its listener (Library Rain 4.93, Storm Runner 4.91 out of 5).

**Chill Lofi vs. Late-Night R&B.** This was the most revealing pair. The two profiles are identical except for genre, and their lists share 4 of 5 songs, with Library Rain (a lofi song) at #1 for both. The only R&B song in the catalog, Velvet Static, shows up at #4 for the R&B listener. This shows that genre is only one part of the score: when the only song in your genre doesn't match your mood or energy, songs that match the "vibe" win instead.

**Deep Intense Rock vs. Late-Night R&B.** No overlap. One listener wants music to work out to and the other wants music to wind down to, so the lists have nothing in common.

### Why does "Gym Hero" show up for someone who wants Happy Pop?

Gym Hero is #3 on the High-Energy Pop list even though it is a workout song with an "intense" mood, not a happy one. The recommender doesn't understand what a song feels like. It only checks a few boxes and adds up points:

- **Is it pop?** Yes, so it gets the full genre points (+1.50).
- **Is it about as energetic as you asked for?** Very close: 0.93 vs. your 0.85 (+1.68).
- **Is it non-acoustic, like you wanted?** Almost completely (+0.47).
- **Is it happy?** No, so it misses the mood points (+0.00).

Gym Hero passes three of the four checks, and missing the mood only costs it 1 point out of 5. Songs that are happy but not pop, like Bassline Fever (edm, euphoric), get just half credit for a "related" mood (+0.50) and no genre points at all, so they rank below it. To the recommender, "pop, loud and electric" counts for more than "happy." A person would notice that a workout anthem isn't the same vibe, but the scoring has no way to see that.

### What surprised me

- **Library Rain wins the R&B profile.** I expected the R&B song to come first. Instead, a lofi song beat it because it matched the mood, the energy and the acoustic preference all at once. The R&B song would need the genre weight raised from 1.5 to about 1.9 to win.
- **Gym Hero lands on two very different lists:** #3 for the pop fan (because it's pop) and #2 for the rock fan (because it's intense). One song can satisfy two listeners for completely different reasons.
- **Doubling energy barely changed the top songs.** In the weight-shift experiment (see the README), the top 3 stayed the same for every profile. Only the bottom of each list moved, and mostly for the worse.
- **Messy input could fool it.** Before the fixes, typing `"False"` (as text) for the acoustic preference made the system think you *liked* acoustic music, and an energy of 1.5 wiped out the energy score for every song.

### Tests and checks I ran

- 16 automated tests (`pytest`), including one for each tricky-input bug.
- A check that every score stays between 0 and the maximum score for all 280 song × profile combinations, including after changing the weights.
- A before/after comparison of all four top 5 lists for the weight-shift experiment.

---

## 8. Future Work  
1. **Add more songs, especially the missing combos.** Add loud acoustic songs, high-energy sad songs, and a few more songs per genre. This would fix the Late-Night R&B problem without touching any weights.
2. **Add a variety rule.** Don't let one artist or one sound take over the top 5. Save one slot for a "wild card" that is a little outside your usual taste.
3. **Let users say what matters most to them.** Some people care about genre above all, others only care about the vibe. Letting each user set their own weights would help people with mixed tastes.

---

## 9. Personal Reflection  
**My biggest learning moment** was the Late-Night R&B profile. I expected the R&B song to win. Instead, a lofi song came first because it matched the mood, the energy, and the acoustic setting all at once. Working out the points by hand showed me the R&B song needed a genre weight of about 1.9 to win. Every weight is a trade-off. Fixing one user's list can make another user's list worse, like when doubling energy pushed the R&B song out of the top 5 completely.

**Using AI tools** sped things up a lot. The AI suggested "trick" profiles I would not have thought of, like typing `"False"` as text. That one exposed a real bug. It also ran the math checks and before/after comparisons quickly. But I still had to double-check its work. Some of the tests it wrote had the old weights hard-coded, so they broke when I changed the weights. The score display was also stuck at "/ 5.00" until we caught it. I learned to ask the AI to *show* the numbers by running the code, not just to explain them.

**What surprised me** is how real the results feel from just four checks and some addition. The lists for clear-cut tastes look like something a friend would make. But it also showed me how easy it is to be fooled. Gym Hero "feels" like a fine pick for a pop fan, even though the system has no idea it's a workout song. The scores look precise, but they only measure what I chose to measure.

**If I kept going,** I would grow the catalog first, since many problems came from missing songs, not bad math. Then I would add a variety rule and try mixing in "people who liked this also liked..." data. I'm curious how much that would help people with mixed tastes.
