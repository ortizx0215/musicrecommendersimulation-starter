# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

TuneScout 1.0. I picked the name because it basically scouts through a small song catalog looking for tracks that fit your vibe.

---

## 2. Goal and Intended Use

### Goal / Task

TuneScout tries to suggest songs you'd like. You give it four things: your favorite genre, the mood you're in, how energetic you want the music to be (from 0 to 1), and whether you like acoustic sound. It scores every song based on those answers and shows you the top 5, along with a short list of reasons for each pick so you can see why it got chosen. It doesn't learn from you or know what you've listened to before, and it has no idea what other people like. It just compares your four answers to the info about each song.

### Intended use

I built this as a classroom project to learn how recommenders work. It's good for messing around with the weights to see how the results change, and for walking through why a certain song got picked.

### Non-intended use

I wouldn't use this for real users on an actual music app, since the catalog only has 20 songs. It also shouldn't be used to decide what music is "good," because the scores only measure how well a song fits four settings. It definitely shouldn't be used for anything that really matters to someone, like ads or hiring, since it has known biases (I go into those in section 6). It also doesn't do a great job for people with mixed tastes, like someone who wants sad music that's also high energy.

---

## 3. How the Model Works

### Algorithm summary

The easiest way to think about it is a judge handing out points, where every song can earn up to 5. Energy is worth the most, up to 2 points, and the closer a song's energy is to what you asked for, the more points it gets. If it's 0.5 or more away, it gets nothing for energy. Genre is worth up to 1.5 points, with full points if it's your genre and half points if it's a close cousin, like indie pop for a pop fan. Mood works the same way and is worth up to 1 point, so "relaxed" still gets half credit if you asked for "chill." Last is acoustic sound, worth up to 0.5 points. If you like acoustic music, more acoustic songs get more points, and if you don't, the less acoustic ones do. TuneScout adds everything up, sorts the songs from highest to lowest, and if two songs tie, the one closer to your energy level wins.

### Changes from the starter

I picked the weights by testing a few different versions on real profiles, and I made energy count the most since it's the strongest "vibe" signal. I added the half credit for related genres and moods so near misses still count. I also made TuneScout clean up messy input, so extra spaces, capital letters, numbers typed as text, and energy values outside 0 to 1 don't mess it up anymore. And the highest possible score is now calculated from the weights instead of being typed in, so it stays correct if I change them.

---

## 4. Data

### Data used

The catalog has 20 songs. The starter had 10 and I added 10 more. There are 17 genres and 16 moods, but most genres only have one song, and lofi has the most with 3. Each song has a title, artist, genre, mood, energy, tempo, valence (how positive it sounds), danceability, and acousticness. TuneScout only scores genre, mood, energy, and acousticness, though. I left tempo and danceability out because they mostly follow energy, so scoring them would just count the same thing twice. Valence isn't used at all.

### Limits of the data

20 songs is really small, so fans of most genres get one genre match at best. Energy and acousticness are also almost perfect opposites in this catalog, meaning loud songs are electric and quiet songs are acoustic, and there aren't any loud acoustic songs or high-energy sad songs. I made up the songs and their labels myself, so they reflect my own idea of what "chill" or "intense" means. There's also no data on lyrics, language, era, or listening history.

---

## 5. Strengths

TuneScout works really well when someone's taste is clear-cut and their genre, mood, and energy all point the same way. In those cases the #1 pick is spot on, like Library Rain for the Chill Lofi profile (4.93 out of 5) and Storm Runner for Deep Intense Rock (4.91). Opposite listeners also get opposite lists, which is what you'd expect. The pop and lofi lists don't share a single song, and neither do the rock and lofi lists. I also like that every pick shows where its points came from, which made it easy to spot weird results like Gym Hero showing up for a pop fan. Near misses still count too, so a pop fan still gets indie pop and a chill fan still gets relaxed and focused songs. And after the fixes, it doesn't break on messy input like " Pop " or an energy of 1.5.

---

## 6. Limitations and Bias

Energy ends up deciding most of the rankings, because in this catalog two of the other features are basically energy in disguise. Acousticness and energy are almost exact opposites across the 20 songs (a correlation of −0.96). On top of that, every "chill" type song has an energy of 0.42 or less and every "intense" type song is 0.72 or more, so the mood and acoustic checks mostly reward the same songs energy already does. That creates a filter bubble for people whose tastes don't follow that pattern. My "Sad Raver" test profile (edm, sad, energy 0.9) didn't get a single sad song in its top 3. There's also no song that's both energetic (above 0.7) and acoustic (above 0.5), so someone who likes upbeat acoustic music can never get a strong match. And since a song gets zero energy points once it's 0.5 away from the target, your energy setting rules out a big chunk of the catalog before genre or mood even come into play. So it works well for "typical" listeners whose genre, mood, and energy line up, and pretty poorly for people with mixed tastes, even though nothing in the code is aimed at them.

---

## 7. Evaluation

### Profiles tested

I ran four everyday listener profiles through the recommender and looked at the top 5 for each one:

| Profile | Genre | Mood | Energy | Acoustic? |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.85 | no |
| Chill Lofi | lofi | chill | 0.35 | yes |
| Deep Intense Rock | rock | intense | 0.92 | no |
| Late-Night R&B | r&b | chill | 0.35 | yes |

I also ran 10 "trick" profiles (in `src/evaluate.py`) that were built to try to break the scoring. Some had conflicting tastes, like a sad listener who wants high energy, and others had messy input like " Pop " with extra spaces or an energy of 1.5. Those actually found real bugs, which I fixed and added tests for. For each list, I checked whether the #1 song was something a real fan of that profile would pick, and whether the rest of the list still matched the feel of what they asked for.

### Comparing the profiles, pair by pair

High-Energy Pop and Chill Lofi don't have a single song in common. The pop list is all loud, electric songs (energy 0.76 to 0.95) and the lofi list is all quiet, acoustic-leaning ones (energy 0.28 to 0.42). That makes sense since the two profiles disagree on every setting, so they should end up at opposite ends of the catalog.

High-Energy Pop and Deep Intense Rock both want loud, non-acoustic music, so they share two songs, Gym Hero and Bassline Fever. The difference comes down to mood. The pop list fills up with happy and playful songs like Sunrise City, Rooftop Lights, and Fuego Lento, while the rock list fills up with intense and angry ones like Storm Runner and Iron Cathedral. So when energy is about the same, mood decides which loud songs you get.

High-Energy Pop and Late-Night R&B have no overlap at all. The R&B listener asked for calm, chill, acoustic music, which is the opposite of the pop listener on pretty much everything, so it makes sense that one list is quiet songs and the other is party songs.

Chill Lofi and Deep Intense Rock also have no overlap. These are the two most opposite profiles, since one wants quiet, relaxed, acoustic songs and the other wants the loudest, most aggressive ones. Both of their #1 songs are near-perfect matches too, with Library Rain at 4.93 and Storm Runner at 4.91 out of 5.

Chill Lofi and Late-Night R&B was the most interesting pair. The two profiles are exactly the same except for genre, and their lists share 4 out of 5 songs, with Library Rain (a lofi song) at #1 for both. The only R&B song in the catalog, Velvet Static, shows up at #4 for the R&B listener. This showed me that genre is only one part of the score, and when the only song in your genre doesn't match your mood or energy, songs that match the vibe win instead.

Deep Intense Rock and Late-Night R&B don't overlap either. One listener wants music to work out to and the other wants music to wind down to, so it makes sense the lists have nothing in common.

### Why does Gym Hero show up for someone who wants Happy Pop?

Gym Hero is #3 on the High-Energy Pop list even though it's a workout song with an "intense" mood, not a happy one. The thing is, the recommender doesn't actually understand what a song feels like. It just checks a few boxes and adds up the points. Gym Hero is pop, so it gets the full 1.50 for genre. Its energy is 0.93, which is really close to the 0.85 the user asked for, so it gets 1.68 there. It's almost completely non-acoustic, which earns another 0.47. The only box it misses is mood, since it isn't happy, and that only costs it 1 point out of 5. Songs that are happy but not pop, like Bassline Fever (edm, euphoric), only get half credit for a related mood and no genre points, so they end up ranked below it. To the recommender, being pop, loud, and electric counts for more than being happy. A person would notice right away that a workout anthem isn't the same vibe, but the scoring just has no way of seeing that.

### What surprised me

The biggest surprise was Library Rain winning the R&B profile. I expected the R&B song to come first, but the lofi song beat it because it matched the mood, the energy, and the acoustic preference all at once. The R&B song would need the genre weight bumped from 1.5 to about 1.9 to win. I was also surprised that Gym Hero landed on two really different lists, #3 for the pop fan because it's pop and #2 for the rock fan because it's intense, so one song can satisfy two listeners for totally different reasons. Doubling the energy weight barely changed the top songs either. In that experiment (it's in the README), the top 3 stayed the same for every profile, and only the bottom of each list moved, mostly for the worse. And before the fixes, messy input could fool it pretty easily. Typing "False" as text for the acoustic setting made the system think you liked acoustic music, and an energy of 1.5 wiped out the energy score for every single song.

### Tests and checks I ran

I have 16 automated tests (run with `pytest`), including one for each of the tricky input bugs. I also checked that every score stays between 0 and the max score across all 280 song and profile combinations, including after changing the weights, and I compared all four top 5 lists before and after the weight shift experiment.

---

## 8. Future Work

If I kept working on this, I'd start by adding more songs, especially the combos that are missing right now, like loud acoustic songs, high-energy sad songs, and a few more songs for each genre. That alone would probably fix the Late-Night R&B problem without touching any weights. I'd also add some kind of variety rule so one artist or one sound can't take over the whole top 5, maybe by saving a spot for a "wild card" that's a little outside your usual taste. And I'd want to let users decide what matters most to them, since some people care about genre above everything and others only care about the vibe. Letting each person set their own weights would really help people with mixed tastes.

---

## 9. Personal Reflection

My biggest learning moment was the Late-Night R&B profile. I expected the R&B song to win, but a lofi song came first because it matched the mood, the energy, and the acoustic setting all at once. Working out the points by hand showed me the R&B song would need a genre weight of about 1.9 to win. That's when I realized every weight is a trade-off, and fixing one person's list can make someone else's worse. I saw that happen when I doubled the energy weight and the R&B song got pushed out of the top 5 completely.

Using AI tools sped things up a lot. The AI suggested "trick" profiles I wouldn't have thought of, like typing "False" as text, and that one actually exposed a real bug. It also ran the math checks and before and after comparisons really quickly. I still had to double-check its work, though. Some of the tests it wrote had the old weights hard-coded, so they broke as soon as I changed the weights, and the score display was stuck at "/ 5.00" until we caught it. I learned to ask the AI to show me the actual numbers by running the code instead of just explaining them.

What surprised me most is how real the results feel from just four checks and some addition. The lists for clear-cut tastes honestly look like something a friend would put together. But it also showed me how easy it is to be fooled. Gym Hero feels like a fine pick for a pop fan, even though the system has no idea it's a workout song. The scores look really precise, but they only measure what I chose to measure.

If I kept going, I'd grow the catalog first, since a lot of the problems came from missing songs and not bad math. After that, I'd add a variety rule and try mixing in "people who liked this also liked..." data. I'm curious how much that would help people with mixed tastes.
