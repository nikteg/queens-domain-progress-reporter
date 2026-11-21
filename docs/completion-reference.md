# Queen's Domain — Completion Reference

Queen's Domain has 53 achievements. Every target below comes from the game's own challenge table
(`Blueprints/Challenges/FS_ChallengeData` in the .pak), not from guide sites, which mostly give no counts.

Progress is tracked in two files in `%LOCALAPPDATA%\QueensDomain\Saved\SaveGames\<SteamID>\`:

- `World0.sav` — the save slot. Its `NamedSaveData` holds the counters each achievement checks (e.g. `TotalChestsOpened`).
- `Challenges` — account-wide list of unlocked achievements, shared by all slots.

Run `python qd_progress.py` to see your own progress against these targets (`--all` lists every missing item).

## Achievements

The platinum (Queen's Domain) needs the other 52. *Counter* = the `NamedSaveData` key (or inventory item) the game
checks.

| Group | Achievement | Requirement | Target | Counter |
| --- | --- | --- | --- | --- |
| Platinum | Queen's Domain | Every other challenge | 52 | CompletedChallenges |
| Areas | Ocean Walk | Reach the Obmuer Temple | 1 | manual |
| Areas | Endless Pages | Reach the Tower of Knowledge | 1 | manual |
| Areas | Unsealed Tomb | Reach the Deimpo Mausoleum | 1 | manual |
| Areas | Genesis | Reach the Ancient World | 1 | manual |
| Areas | Halls of Hatred | Reach Siraatsu Castle | 1 | manual |
| Areas | Dark Silence | Reach the Forgotten Dungeon | 1 | manual |
| Areas | Sacred Groves | Reach the Verdant Hollow | 1 | manual |
| Areas | Deep Mire | Reach the Rotting Cavern | 1 | manual |
| Areas | Sin Keeper | Reach the Record of Sin | 1 | manual |
| Areas | Memorial Sculpture | Reach the Petrified Garden | 1 | manual |
| Quests | Fate of the Iryupe Raiders | Raider necklaces to Captain Aganmi | 4 | RaiderNeckacesTurnedIn |
| Quests | Sacred Waters | Orbewa Eggs to Erma | 50 | FishWifeTotalEggs |
| Quests | A Lifetime's Work | Wourha's bestiary to 100 % | 100 | LibrarianBestiaryCompletionPercent |
| Quests | Sparkling Clean | Destroy the 5 flesh walls in the Tower | 5 | NecroWall00–04Destroyed |
| Quests | I'm Not Paying the Late Fee | Tower + Record of Sin book puzzles | 2 | LibBookPuzzleComplete, ROSBookPuzzleComplete |
| Quests | Forgotten Rooms | Explore the 5 treasure vaults | 5 | SR_*_Acquired |
| Quests | Birds of a Feather | Meal Tickets to Chef Gagi | 60 | MealTicketsCollected |
| Quests | Wise Work | Data modules to Ossi | 10 | ScientistDataGiven |
| Quests | Let's Make a Deal | Spend coins at Umbada's | 1000 | ShopAmountSpent |
| Quests | Living Stone | Wake the Petrified Garden | 1 | StoneGardenPuzzleFinished |
| Quests | A Fine Collection | All 5 duck figurines to Umbada | 5 | ShopkeepUnlock1–4, ShopUnlockFinished |
| Quests | Oh the Places You'll Go | Own the Flying Mushroom Fossil (30 skulls) | 1 | item StrangeMushroom |
| Quests | The Call From Beyond | Skull ritual (69 skulls) | 1 | SkullRitualCompleted |
| Quests | Witchcraft | Inscribe in the Witch's Grimoire | 1 | HasEverInscribedGrimoire |
| Items | Flying Sword | Get Holy Sword Endu | 1 | FlyingSwordFirstgemAcquired |
| Items | Blade Bathed in Holy Light | Forge True Holy Sword Akunra | 1 | item SecretSword |
| Items | Most Spiritual Sword | Get Okbujo's Judgement | 1 | item SpectralSword_Item |
| Items | Raging Tempest | Recover the Storm Gem | 1 | HasUltraMove |
| Items | Feel the Wind | All Wind Gems | 5 | WindGemsAcquired |
| Items | Perfected Weaponry | Upgrade every main weapon | 63 | TotalWeaponsUpgraded |
| Items | Extensive Armaments | Every main weapon | 77 | TotalAchievementWeapons |
| Items | Versatile Volley | Every throwing weapon type | 22 | TotalAchievementThrowables |
| Items | Eclectic Accoutrements | Every accessory | 33 | TotalAchievementAccessories |
| Items | Glimmering Treasures | 93 treasures; every loot sack counts too | 93 | TotalAchievementTreasures |
| Items | Overflowing Energy | Full Energy Cells | 4 | FullEnergyCellsCount |
| Items | Magic Eyes | 4 lenses for the Mask of Second Sight | 4 | items RuneVisionUnlock1–4 |
| Items | Ancient Technology | Any energy weapon | 1 | tag EnergyWeapon |
| Exploration | Well Travelled | All Crystal Monuments + Wing Altars | 42 (32 + 10) | CheckpointUnlockCount, TeleporterUnlockCount |
| Exploration | Emptied Coffers | Open every chest | 108 | TotalChestsOpened |
| Exploration | Concealed Passages | Open every secret door | 89 | TotalSecretDoorsOpened |
| Bosses | Treacherous Baleen | Dagoom the Sea King | 1 | WhaleKingIsDead |
| Bosses | Hell Transcribed | The Necronomicon | 1 | NecronimiconDefeated |
| Bosses | Demonic Servitude | Poenir and Duenir | 1 | DemonBossesKilled |
| Bosses | Sworn Protector | Josami Lord Saijha | 1 | BridgeLordDead |
| Bosses | Dread Silver | Herald of Okbujo | 1 | ROSDragonDead |
| Bosses | Wake From Dreams | Usunha and Wujomiod | 1 | DragonLordDead |
| Bosses | Beneath Rotten Waters | The Gigantic Serf | 1 | GiantSwampFish_IsDead |
| Bosses | Fallen Angels | Blood Angel Lords Yuumed and Woyeki | 1 | RedLordsDead |
| Endings | Most Unfortunate | Ending 1 | 1 | Ending1Complete |
| Endings | A Kingdom Free From Darkness | Ending 2: beat the Queen with Akunra | 1 | Ending2Complete |
| Endings | God Slayer | Ending 3: 8 Mementos + Okbujo's Judgement, choose Banish | 1 | Ending3Complete |
| Endings | Eat | Ending 4: all 69 skulls, choose Eat | 1 | Ending4Complete |

## Collections and exploration

Item totals match the item tags in the game files exactly (77 items tagged `AchievementWeapon`, 33
`AchievementAccessory`, 22 `AchievementThrowables`). An item counts once it has been in your inventory, even if you
later sold it. Four of the 33 accessories are the skull-door fossils (see Silver Skulls), stored under `Artifacts/`
rather than `Items/` in the game files.

Treasures: there are 59 unique treasures, and every loot sack (Lizer treasure) you find also adds one to the
treasure counter. Loot sacks can be found more than once (some enemies drop them), so the 93 can be reached with
any mix of unique treasures and sacks.

| Collection | Total |
| --- | --- |
| Main weapons | 77 |
| Throwing weapons | 22 |
| Accessories | 33 |
| Treasures | 93 (59 unique, the rest loot sacks) |
| Crystal Monuments | 32 |
| Wing Altars | 10 |
| Chests | 108 |
| Secret doors | 89 |
| Treasure vaults | 5 |
| Wind Gems | 5 |
| Energy Cells (full) | 4 |
| Mask of Second Sight lenses | 4 |
| Meal Tickets | 60 |
| Orbewa Eggs | 50 |
| Data modules | 10 |
| Duck figurines | 5 |
| Weapon upgrades | 63 |
| Silver Skulls | 69 |

### Crystal Monuments and Wing Altars

| Region | Crystal Monuments | Wing Altar |
| --- | --- | --- |
| Isle of Neasied | Knight's Encampment, Cemetery Precipice | yes |
| Umbada's Islet | Familiar Location | — |
| Obmuer Temple | Cave Entrance, Sacred Cistern, Lift Room, Prison Corridor, Aganmi's Camp | yes |
| Tower of Knowledge | Foyer, Stairwell, Forbidden Archives | yes |
| Deimpo Mausoleum | Crumbling Stairwell, Lower Area, Puwema's Rest Room | yes |
| Ancient World | Overlook, Ossi's Lab, Scrap Yard, Ventilation Shaft | yes |
| Siraatsu Castle | Foyer, Lift Room, Halls of Disrepair | yes |
| Verdant Hollow | Cliff Edge, Lakeside | yes |
| Underworld | Halls Shrouded in Darkness, Crimson Grotto | — |
| Forgotten Dungeon | Pit of Despair | — |
| Rotting Cavern | Decaying Great Tree, Crumbling Fortress, Temple Entrance | yes |
| Petrified Garden | Stone Hut | yes |
| Record of Sin | Before Okbujo's Tree, Pinnacle Anteroom | yes |

## Silver Skulls

There are **69** Strange Silver Etched Skulls. You turn them in at the skull door, which pays out every 10 and starts
a ritual at 69. Rewards count skulls **turned in**, not carried.

Read from `NPCs/SecretSkullDoor/SecretSkullDoor_NPC_BP` (`RewardList`):

| Turned in | Reward | Effect (from the item's data) |
| --- | --- | --- |
| 10 | Ancient Stone Duck Figurine | The 5th duck for Umbada; completes A Fine Collection and opens his last shop tier |
| 20 | Fossilized Fish | Accessory: +15 % all status resistances, +25 Luck |
| 30 | Flying Mushroom Fossil | Accessory: launches you up to 20 m into the air, 34 s recharge; unlocks *Oh the Places You'll Go* |
| 40 | Fossilized Anemone | Accessory: pit immunity (saves you from deadly falls and water) |
| 50 | Sonic Crystal Fossil | Accessory: 2× movement speed |
| 69 | Ritual | *The Call From Beyond*; required for Ending 4 (Eat) |

The door's lines after each reward hint at them: "Quaaaack…", "still freshhhh…", "Boingggg… upppp youuuu gooooo…",
"Swimmm… freeee…", "gotttta goooo…. faaasssssstttt…".

The Skull Charm (Umbada, 20 coins) tracks skulls on the Mask of Second Sight. All four fossils are tagged
`AchievementAccessory`, so they count toward the 33 accessories (Eclectic Accoutrements). For per-skull locations use
[Queen's Domain Skull Finder](https://github.com/mesetamusic/queens-domain-skull-finder).

## Umbada's shop and the duck figurines

Each duck you bring Umbada opens one more shop tier; the Ancient Stone Duck opens the last, with six finder charms for
the Mask of Second Sight. Tiers and prices are from the shop config (`Blueprints/Shop/Shop`, `RequiredProgression`).

| Duck | Tier | New stock (price in Ancient Coins) |
| --- | --- | --- |
| Stone Duck Figurine | 0 (opens the shop) | Cures (3–9), Cestus, Silver Needle, Hand Axe, Morning Star (20 each), Sacred Necklace 14, Protection Charm 10, Strength Charm 12, throwing weapons once found (10–35), shop weapon replicas once the original is found (10) |
| Silver Duck Figurine | 1 | Elixer 4, Orda Bud 10, Radiant Fruit 6, Travel Crystal Fragment 8, Diamond Blade 25, Spiked Buckler 33, Warding Amulet 20, Brutal Amulet 24 |
| Golden Duck Figurine | 2 | Large Elixer 7, Steel Ale 10, Wing Stone Fragment 10, Occult Warhammer 30, Vampiric Scimitar 42, Lantern 22, Silver Bangle 35, Trident Key – Amethyst 15 |
| Mechanical Duck Figurine | 3 | Grand Elixer 13, Berserker's Brew 12, Plasma Sword 35, Heavy Rifle 40, Small Energy Cell 35 |
| Ancient Stone Duck Figurine | 4 | Rejuvenating Water 25, Spirit Oil 15, and 20 each: Treasure Charm (chests), Skull Charm, Egg Charm, Data Charm, Meal Charm, Star Charm (loot sacks) |

All six charms cost 120 coins together. Some appear only after meeting the matching NPC (Erma, Ossi, Chef Gagi) or
finding a loot sack.

After you have bought a lot (threshold not found in the files), Umbada mentions lost shipments in his signature
yellow chests that you may keep for free.

## Sources

- Game files from the local install (`QueensDomain-WindowsNoEditor.pak`): `FS_ChallengeData`, `Blueprints/Shop/Shop`,
  `NPCs/SecretSkullDoor/SecretSkullDoor_NPC_BP`, `Blueprints/Areas/*`, item assets, `StringTables/ImportedStringTable`.
- [Queen's Domain Skull Finder](https://github.com/mesetamusic/queens-domain-skull-finder) (pak reader and skull locations).
- Achievement lists: [Whisper of the House](https://www.whisperofthehouse.com/queens-domain/achievements),
  [GamerBlurb](https://gamerblurb.com/guides/queens-domain-achievements-guide),
  [Gaming Deputy](https://www.gamingdeputy.com/france/queens-domain-succes-liste-complete/),
  [WeMod](https://www.wemod.com/cheats/queens-domain-trainers/achievements).
