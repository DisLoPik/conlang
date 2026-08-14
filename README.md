```
 a88888b.                   dP                            
d8'   `88                   88                            
88        .d8888b. 88d888b. 88 .d8888b. 88d888b. .d8888b. 
88        88'  `88 88'  `88 88 88'  `88 88'  `88 88'  `88 
Y8.   .88 88.  .88 88    88 88 88.  .88 88    88 88.  .88 
 Y88888P' `88888P' dP    dP dP `88888P8 dP    dP `8888P88 
oooooooooooooooooooooooooooooooooooooooooooooooooo~~~~.88~
                                                  d8888P  
```

# conlang

A command-line tool for building a **typed-only constructed language** — a secret language with its own vocabulary, designed to be written and read but never spoken.

You bring a list of random roots. It validates them, fills the gaps, assigns them to meanings, builds a working encoder and decoder, and generates an offline searchable dictionary you can open on your phone.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Offline](https://img.shields.io/badge/network-never-lightgrey)

---

> [!WARNING]
> **This is obfuscation, not cryptography.**
>
> It defeats a casual reader, someone glancing at your screen, or a moderately determined person with a few pages of your messages. It does **not** defeat anyone with real resources or time. Don't put anything in it that would genuinely hurt you if it were read. For actual private messaging, use Signal.

---

## Why not just use a cipher?

A cipher swaps letters, so word frequencies survive the swap. The most common short word in your text is `the`, the second is `of`, and someone unravels the rest from there. A word-for-word substitution language ("relex") has the same problem one level up.

This tool keeps English word order — so the language is learnable in weeks rather than months — while deleting the specific features that leak:

| Attack | Countermeasure |
|---|---|
| Frequency analysis on common words | Every high-frequency word has 2–3 interchangeable roots, chosen at random per use |
| `the` / `is` / `of` as anchors | Those words don't exist in the grammar |
| Word-length statistics | No spaces; capitals mark word boundaries; all roots are the same length |
| Structural fingerprints | No question inversion, no verb conjugation, no possessive `'s` |
| Names as cribs | Names are marked and reversed; frequent ones get dedicated roots |
| Recognisable vocabulary | Roots are generated randomly and assigned to meanings randomly |

## Quick start

```bash
git clone https://github.com/DisLoPik/conlang.git
cd conlang
python3 conlang.py
```

On first run it walks you through eight questions, builds everything, and opens the dictionary in your browser.

If you don't have a `roots.txt`, it offers to generate one. If you do, put it beside the script — one root per line.

## Setup options

The wizard asks about each of these. Press enter to take the default.

| Question | Options | Default |
|---|---|---|
| Root length | 3 or 4 letters | 3 |
| Reject near-identical roots | on / off | on |
| Rotation depth | 3-way / 2-way / none | 3-way |
| Word boundaries | capitals, no spaces / normal spaces | capitals |
| Marker letters | `Ä Ö Ü Ñ` / `Qq Xx Zz Vv` / none | accented |
| Grammar deletions | articles, copula, `of`, infinitive `to` | all four |
| Minimum root count | any | 250 |

A few of these have real trade-offs worth understanding:

- **The similarity rule** rejects any root within one letter of another, so a typo can't silently turn one word into another. At 3 letters it's expensive — expect to lose a third or more of a randomly generated batch. At 4 letters it's nearly free.
- **Rotation depth** is the main thing standing between you and a cracked language. Dropping to 1 makes it much easier to learn and much easier to break.
- **Marker letters**: the accented set is more visually distinct, but needs a long-press on phone keyboards. The ASCII set types instantly anywhere.

## How the language works

| Rule | Effect |
|---|---|
| No spaces | A capital starts each word — `ZimKerBoshNeld` is four words |
| No articles | No `the`, `a`, `an` |
| No copula | "He tall", not "he is tall" |
| No `of` | Possessor comes first |
| No conjugation | A time marker at the start of the sentence, held until changed |
| Questions | Question particle first; word order never inverts |
| Negation | Particle immediately before the verb |
| Plurals | Suffix on the root, skipped when a number is already present |
| Rotation | Pick freely between A/B/C; never repeat one inside a sentence |

Example round trip:

```
$ python3 conlang.py --encode "I am going to the store tomorrow."
ZhbKhdIpaWhaNrtPic.

$ python3 conlang.py --decode "ZhbKhdIpaWhaNrtPic."
[future] I go to store tomorrow.
```

Note what happened: `the` and `am` are gone, tense moved to a leading marker, and the whole sentence became one unbroken string.

## Command reference

```
python3 conlang.py                  first run: setup wizard, build, open browser
python3 conlang.py --reconfigure    change the rules, then rebuild
python3 conlang.py --rebuild        rebuild from saved settings, no prompts
python3 conlang.py --encode "..."   English -> language
python3 conlang.py --decode "..."   language -> English
python3 conlang.py --shell          interactive translation
python3 conlang.py --no-open        skip opening the browser
```

`--encode` and `--decode` print nothing but their result, so they pipe cleanly.

## Files

| File | What it is |
|---|---|
| `roots.txt` | Your roots, one per line. Rewritten with the cleaned list. |
| `roots.txt.bak` | Backup of the original, written once. |
| `rejected.txt` | Every rejected root with the reason. |
| `language.json` | Settings plus the full dictionary. **This is the key.** |
| `dictionary.md` | Readable vocabulary tables. **Also the key.** |
| `lookup.html` | Offline searchable dictionary. **Also the key.** |

`lookup.html` is fully self-contained — no CDN links, no fetch calls, nothing external. It works on a plane. Search runs in both directions at once: type an English word or type a root, same box. Tapping a root copies it.

## Keeping it secret

The tool is only as strong as how you handle what it produces.

1. **Never commit your generated files.** Add `roots.txt`, `language.json`, `dictionary.md`, and `lookup.html` to `.gitignore` before your first push. Publishing the tool is fine; publishing your dictionary defeats the entire point.
2. **Hand the dictionary over in person**, or on paper. Not through the channel you use the language on.
3. **Never send a message and its translation together.** That's a known-plaintext pair, and it's how systems like this die.
4. **Don't translate anything an outsider already has** — no song lyrics, no famous quotes, no copy-pasted memes. If someone recognises the source, they have the plaintext.
5. **Keep the group small.** Every member is a complete copy of the key.
6. **Don't teach it in writing over the internet.** Explaining "this root means tomorrow" in a DM undoes the work.
7. **Plan for v2.** Generate a replacement root set at the same time as your first, and agree in advance how you'd switch.

Rebuilding reassigns every root, which means every message ever written in the old version stops decoding. The tool warns before it does this.

## A note on generating roots

Generate them yourself, offline. The tool uses Python's `secrets` module, seeded by the OS, and never touches the network.

Roots produced anywhere else — an online generator, a chat with an AI, a shared document — are roots someone else could reproduce. Assignment is random too, so no root ever resembles the word it stands for.

## Requirements

Python 3.8 or newer. Standard library only. No install step, no virtualenv, no `pip`.

## License
MIT
