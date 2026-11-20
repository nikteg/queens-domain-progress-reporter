# Queen's Domain — Consumables and Status Effects

Numbers come from the game's balance blueprint (`Player/Assets/Blueprints/PlayerBalance`) and the
item assets; descriptions are the in-game text.

## Healing: herbs vs elixirs

Elixirs heal 2.5× as much as the herb of the same tier; that's the only difference the files show
(`HealingHerbNHealAmount`, `HealingPotionNHealAmount`).

| Tier | Herb | Heals | Elixer | Heals |
| --- | --- | --- | --- | --- |
| 1 | Dried Herbs | 20 HP | Elixer | 50 HP |
| 2 | Freshly Dried Herbs | 40 HP | Large Elixer | 100 HP |
| 3 | Royal Dried Herbs | 80 HP | Grand Elixer | 200 HP |

- Healing items get stronger over time, up to **1.5× after 5 hours** (`HealItemIncreaseOverTime_*`). Probably play
  time; the files don't say which clock.
- Each **Pizza** upgrade adds +10 % healing (`Pizza_HealingEffectIncrease`).
- **Max HP** = 100 + 5 per level + 10 per Chicken upgrade — about 600 at level 72 with 15 Chickens.
- Wounds regenerate 1 % max HP/s after 2 s without being hit (`WoundRegenRate`, `WoundRegenDelay`); probably only
  recently lost HP.
- **Resting at a Crystal Monument** fully heals and clears all statuses, but respawns most enemies.

## Status effects

Panacea cures every status, and resting clears them all. Descriptions are from the in-game Status Effects guide.

| Status | What it does | Duration | Cure |
| --- | --- | --- | --- |
| Poison | Drains ~1 % of max HP per second | 60 s | Roasted Ojum Lizard |
| Heavy | Move speed ×0.5, slower power-meter refill, Wind Dash distance ×0.5 | 5 s | Badu Powder |
| Weaken | You take more damage (~+50 %) | 20 s | Roasted Cave Scorpion |
| Disease | You deal less damage (~half) | 60 s | Pungent Root |
| Sticky | Can't use throwing weapons | 20 s | Idinti Soap |
| Binding | Can't use magic abilities; drains weapon-ability and Ultra charge; energy-gun charge drains 4× faster | 30 s | Cleansing Flower |
| Paralysis | Can't move or attack | short | Panacea |
| Azure Flame (Burn) | Drains HP while it burns | ~6 s | Panacea or wait |
| Magic Rot | Builds up in rotten water; at the threshold (15) drains ~10 % HP per tick | until cleared | Orda Bud |
| Gem Curse | From the cursed-gem balloon enemies; likely +25 % damage taken | — | — |

- **Orda Bud** also gives 50 % Magic Rot resistance for 120 s — drink it *before* wading into the Rotting Cavern.
- Resistance charms (Poison Res Tiara, Disease Res Charm, Weaken Res Crown, …) make the matching status wear off faster.
- Enemies suffer the same statuses: Weaken and Disease work the same on them, and Heavy slows them to half speed.

## All consumables

### Healing

| Item | Effect |
| --- | --- |
| Dried Herbs | 20 HP |
| Freshly Dried Herbs | 40 HP |
| Royal Dried Herbs | 80 HP |
| Elixer | 50 HP |
| Large Elixer | 100 HP |
| Grand Elixer | 200 HP |

### Cures

| Item | Cures |
| --- | --- |
| Roasted Ojum Lizard | Poison |
| Badu Powder | Heavy |
| Roasted Cave Scorpion | Weaken |
| Pungent Root | Disease |
| Idinti Soap | Sticky |
| Cleansing Flower | Binding |
| Orda Bud | Magic Rot (+50 % rot resistance for 120 s) |
| Panacea | Everything |

### Buffs

The balance file and the item data disagree on durations; the balance file is probably what the game uses, but this
is untested.

| Item | Effect | Duration (balance / item data) |
| --- | --- | --- |
| Brawler's Berries | +4 damage | 30 s / 60 s |
| Berserker's Brew | +4 damage | 30 s / 60 s |
| Iron Pineapple | 25 % less damage taken | 30 s / 60 s |
| Steel Ale | 25 % less damage taken | 30 s / 60 s |
| Radiant Fruit | See in the dark (+1000 light radius) | 30 s / 120 s |
| Rejuvenating Water | Restores magical energy (magic-weapon charge) | instant |
| Spirit Oil | +200 weapon XP (100 XP per weapon level) | instant |

### Travel

| Item | Effect |
| --- | --- |
| Travel Crystal Fragment | Teleport to a Crystal Monument; used up |
| Travel Crystal | Same, never breaks |
| Wing Stone Fragment | Teleport to a Wing Altar; used up |
| Wing Stone | Same, never breaks |

### Special and joke items

- **Witch's Grimoire** — inscribe something in it; ink regenerates slowly. Doing it once unlocks *Witchcraft*.
- **Grimoire Ink Enhancer** — faster ink regeneration, so more inscriptions.
- **Memento Mirror** — reveals hidden details; tied to the 8 Mementos for Ending 3.
- **B33 Punch** — +5 % damage and +1.5 HP/s regen for 30 s, 60 s cooldown.
- **Ratpod** — 60 s effect; the description only asks "Why would you eat this?"

## Other balance values

| Value | Setting |
| --- | --- |
| Base damage | 10, +1 per level |
| Meat upgrade | +2 damage each |
| Charged attack | ×1.5 damage |
| Ultra attack | ×6 damage, needs 100 charge |
| Enemy weakness / resistance | ×1.5 / ×0.5 damage |
| Energy cell recharge | 30 s |
| Enemy respawn | 120 s (and on rest) |
| Run speed | ×1.5, drains the power meter |
| Death pit / crush damage | 10 % max HP |
| Low-health threshold | 20 % HP |
| Accessory / throwing / weapon slots | 2 / 3 / 3 |
| Luck | +5 % drop chance per point |

## Sources

- `Player/Assets/Blueprints/PlayerBalance` and the item assets under `Items/Consumables/` in
  `QueensDomain-WindowsNoEditor.pak`.
- In-game guide text from `StringTables/ImportedStringTable` (Status Effects, Crystal Monuments).
