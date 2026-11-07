# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
