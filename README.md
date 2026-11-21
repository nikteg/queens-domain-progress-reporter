# Queen's Domain progress analyzer

Reads a Queen's Domain save and prints your completion: all 53 achievements/challenges,
item collections (with what's missing), lost books, Crystal Monuments / Wing Altars, Silver Skulls and some stats.

```
python qd_progress.py                      # newest save in %LOCALAPPDATA%\QueensDomain\Saved\SaveGames
python qd_progress.py "path\to\save dir"   # a specific save folder (or World0.sav)
python qd_progress.py --all                # full missing lists + a hint per missing skull
python qd_progress.py --game "D:\SteamLibrary\steamapps\common\QueensDomain"
```

Python 3.10+, no dependencies. It never writes to your save or the game.

## Example output

From a save about 23 hours in (default output; `--all` expands every list):

<details>
<summary>Show example</summary>

```text
Queen's Domain progress — C:\Users\<you>\AppData\Local\QueensDomain\Saved\SaveGames\<SteamID>\World0.sav
  Level 72   XP 1,266,990   Play time 23h 12m   Saved at: GR_Camp_Save

Achievements / Challenges: 26/53 complete
─────────────────────────────────────────
  Overall                            ████████████░░░░░░░░░░░░    26/53     49.1%

  Platinum (0/1)
    ✘ Queen's Domain                  [26/52]  — Overcome every challenge on the Isle of Neasied.

  Areas (10/10)
    ✔ Ocean Walk
    ✔ Endless Pages
    ✔ Unsealed Tomb
    ✔ Genesis
    ✔ Halls of Hatred
    ✔ Dark Silence
    ✔ Sacred Groves
    ✔ Deep Mire
    ✔ Sin Keeper
    ✔ Memorial Sculpture

  Quests (4/14)
    ✔ Fate of the Iryupe Raiders      [4/4]
    ✘ Sacred Waters                   [32/50]  — Bring every Orbewa Egg to Erma, Matron of the Deep.
    ✘ A Lifetime's Work               [82/100]  — Help Knowledge Keeper Wourha complete her research (bestiary %).
    ✔ Sparkling Clean                 [5/5]
    ✘ I'm Not Paying the Late Fee     [0/2]  — Return all of the lost books (Tower + Record of Sin puzzles).
    ✘ Forgotten Rooms                 [3/5]  — Explore every treasure vault.
    ✘ Birds of a Feather              [50/60]  — Bring sixty Meal Tickets to Chef Gagi.
    ✘ Wise Work                       [8/10]  — Witness the result of Mechanical Engineer Ossi's experiment (data modules).
    ✔ Let's Make a Deal               [1000/1000]
    ✔ Living Stone
    ✘ A Fine Collection               [4/5]  — Bring every duck figurine to Umbada.
    ✘ Oh the Places You'll Go         — Receive a strange reward.
    ✘ The Call From Beyond            — Complete a mysterious ritual (all 69 Silver Skulls).
    ✘ Witchcraft                      — Inscribe something in the grimoire.

  Items (5/13)
    ✔ Flying Sword
    ✘ Blade Bathed in Holy Light      — Forge the True Holy Sword Akunra.
    ✘ Most Spiritual Sword            — Collect Okbujo's Judgement.
    ✔ Raging Tempest
    ✔ Feel the Wind                   [5/5]
    ✘ Perfected Weaponry              [2/63]  — Upgrade every Main Weapon.
    ✘ Extensive Armaments             [44/77]  — Collect every Main Weapon.
    ✘ Versatile Volley                [18/22]  — Collect every type of Throwing Weapon.
    ✘ Eclectic Accoutrements          [22/33]  — Collect every Accessory.
    ✘ Glimmering Treasures            [67/93]  — Collect every Treasure.
    ✘ Overflowing Energy              [3/4]  — Collect four Energy Cells.
    ✔ Magic Eyes                      [4/4]
    ✔ Ancient Technology

  Exploration (0/3)
    ✘ Well Travelled                  [37/42]  — Activate every Crystal Monument (32) and Wing Altar (10).
    ✘ Emptied Coffers                 [77/108]  — Open every chest.
    ✘ Concealed Passages              [45/89]  — Open every secret door.

  Bosses (7/8)
    ✔ Treacherous Baleen
    ✔ Hell Transcribed
    ✔ Demonic Servitude
    ✔ Sworn Protector
    ✔ Dread Silver
    ✘ Wake From Dreams                — Defeat Usunha and Wujomiod, Shrine of Puwema Gatekeepers.
    ✔ Beneath Rotten Waters
    ✔ Fallen Angels

  Endings (0/4)
    ✘ Most Unfortunate                — Saw Ending 1.
    ✘ A Kingdom Free From Darkness    — Saw Ending 2 (defeat the Queen with True Holy Sword Akunra).
    ✘ God Slayer                      — Saw Ending 3 (8 Mementos + Okbujo's Judgement, choose Banish).
    ✘ Eat                             — Saw Ending 4 (all 69 Silver Skulls, choose Eat).

Collections
───────────
  Main weapons                       ██████████████░░░░░░░░░░    44/77     57.1%
      missing 33:
      - Ancient Short Sword
      - Black Diamond Claw
      - Black Steel Greataxe
      - Bronze Great Morning Star
      - Common Spear
      - Crushing Lance
      - Daji the Grasping
      - Explorer's Cudgel
      - Gagi's Magic Pot
      - Gilded Leaf Blade
      - Golem Arm Crusher
      - Hard Wooden Club
        ...and 21 more (use --all)
  Throwing weapons                   ████████████████████░░░░    18/22     81.8%
      missing 4:
      - Mystical Nut of the White Tree
      - Okbujo's Gaze
      - Paralytic Needle
      - Spiked Ball
  Accessories                        ████████████████░░░░░░░░    22/33     66.7%
      missing 11:
      - Agate Link Charm
      - Crown of the Sea King
      - Extravagant Hourglass
      - Flying Mushroom Fossil
      - Fossilized Anemone
      - Fossilized Fish
      - Growth Apparatus
      - Orbewa Holy Amulet
      - Quick Charger
      - Sonic Crystal Fossil
      - White Quartz Charm
  Treasures (incl. loot sacks)       █████████████████░░░░░░░    67/93     72.0%
    unique treasures                 ████████████████░░░░░░░░    40/59     67.8%
    loot sacks found: 27 (each one counts toward the 93)
      missing 19 unique treasures (any 26 more treasures or sacks finish it):
      - Ancient Green Bottle
      - Ancient Yellow Bottle
      - Cell Phone
      - Demonic Ritual Skull
      - Distinguished Monocle
      - Elegant Compass
      - Fortune Lamp
      - Gold Crown
      - Gold Jigeki Statuette
      - Gold Nautilus Crown
      - Gold Puwema Statuette
      - Gold Sipeha Statuette
        ...and 7 more (use --all)
  Weapons upgraded                   █░░░░░░░░░░░░░░░░░░░░░░░     2/63      3.2%
  Energy cells (full)                ██████████████████░░░░░░     3/4      75.0%
  Wind Gems                          ████████████████████████     5/5     100.0%
  Mask of Second Sight lenses        ████████████████████████     4/4     100.0%
  Meal Tickets (Chef Gagi)           ████████████████████░░░░    50/60     83.3%
  Orbewa Eggs (Erma)                 ███████████████░░░░░░░░░    32/50     64.0%
  Data modules (Ossi)                ███████████████████░░░░░     8/10     80.0%
  Duck figurines (Umbada)            ███████████████████░░░░░     4/5      80.0%
  Raider necklaces (Aganmi)          ████████████████████████     4/4     100.0%
  Bestiary % (Wourha)                ████████████████████░░░░    82/100    82.0%
  Coins spent at Umbada              ████████████████████████  1000/1000  100.0%  (total spent 1,381)
  Lost books: Tower shelf            ████░░░░░░░░░░░░░░░░░░░░     1/6      16.7%
      - Dams and Weirs — bottom of the bookcase next to the Tower of Knowledge Wing Altar
      - Koko's Sapphic Adventure — upper Tower room near Wourha; 32 m ENE of the Wing Altar
      - The Great Work IV - Rubedo — cave below the Cemetery (entrance with an egg), altar right of the cube pedestal; 26 m ENE of Cemetery Precipice, 13 m down
      - The Old Ones Beyond — hidden passage above an upper library room door (Archivist Inha's bones)
      - Upim's Fairy Tales — hidden cave on the Obmuer Temple side; drop toward the giant tree, Wind Dash to the ledge with a skeleton
  Lost books: Record of Sin shelf    ██████████████████░░░░░░     3/4      75.0%
      - Wodaso's Embrace — Tower of Knowledge: 26 m WSW of Forbidden Archives, 46 m down

Exploration
───────────
  Crystal Monuments                  █████████████████████░░░    28/32     87.5%
      - Halls Shrouded in Darkness (Underworld)
      - Halls of Disrepair (Siraatsu Castle)
      - Lift Room (Siraatsu Castle)
      - Ventilation Shaft
  Wing Altars                        ██████████████████████░░     9/10     90.0%
      - Siraatsu Castle
  Chests opened                      █████████████████░░░░░░░    77/108    71.3%
  Secret doors opened                ████████████░░░░░░░░░░░░    45/89     50.6%
  Treasure vaults                    ██████████████░░░░░░░░░░     3/5      60.0%
  Tower flesh walls cleaned          ████████████████████████     5/5     100.0%

Silver Skulls
─────────────
  Found                              ██░░░░░░░░░░░░░░░░░░░░░░     7/69     10.1%
  Turned in at the skull door        ██░░░░░░░░░░░░░░░░░░░░░░     6/69      8.7%  (1 carried)
      missing 62, by area:
      Ancient World (14)
      Isle of Neasied (7)
      Siraatsu Castle (6)
      Verdant Hollow (6)
      Tower of Knowledge (5)
      Deimpo Mausoleum (5)
      Rotting Cavern (5)
      Record of Sin (4)
      Obmuer Temple (3)
      Underworld (3)
      Forgotten Dungeon (2)
      Petrified Garden (1)
      Final Zone (1)
      (use --all for a hint per skull, or run Skull Finder for full directions)

Stats
─────
  Enemies killed       2,494 (157 kinds)
  Pots broken          515
  Consumables used     470
  Notes/books read     34
  Grimoire inks        10
  Sipeha seals removed 3
  Knight ghosts found  8
  Ancient Coins        126
  Highest weapon levels: Holy Sword Endu 9, Azure Torch 9, Soul Bound Endu 9, Heavy Rifle 9, Grave Reaper 7
```

</details>

## Where the numbers come from

- **Targets** (77 weapons, 22 throwables, 33 accessories, 93 treasures, 108 chests, 89 secret doors,
  32 Crystal Monuments + 10 Wing Altars, 60 meal tickets, 50 eggs, ...) are from the game's own
  challenge table `Blueprints/Challenges/FS_ChallengeData`.
- **Your progress** comes from `World*.sav` (the counters the game uses for those challenges) and the
  account-wide `Challenges` file (which achievements are already unlocked).
- **Item, place and skull names** are read from your game install's `.pak` on the first run and cached in
  `%LOCALAPPDATA%\QDProgress` (skulls in `%LOCALAPPDATA%\QDSkullFinder`). Without the game it still shows all counts.

## Docs

- [Completion reference](docs/completion-reference.md) — all 53 achievements, collection totals, Silver Skull rewards, lost books, Umbada's shop tiers
- [Consumables and status effects](docs/consumables-and-status-effects.md) — heal amounts, buffs, status debuffs and cures
- [Save file and game data notes](docs/save-and-game-data-notes.md) — save keys and .pak assets the analyzer reads, plus how level coordinates map to the in-game compass

## Files

| File | What it is |
| --- | --- |
| `qd_progress.py` | The report |
| `gvas.py` | Reader for UE4.27 `.sav` (GVAS) files |
| `qdcore.py` | Pak reader + skull data, vendored from [Queen's Domain Skull Finder](https://github.com/mesetamusic/queens-domain-skull-finder) (MIT, see `LICENSE-skull-finder`) |
