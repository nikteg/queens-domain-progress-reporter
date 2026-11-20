# Queen's Domain — Save File and Game Data Notes

Technical notes behind `qd_progress.py`, as of 2026-11-20 (Unreal Engine 4.27 build).

## Save files

Location: `%LOCALAPPDATA%\QueensDomain\Saved\SaveGames\<SteamID>\`. All are UE4 GVAS files (parsed by `gvas.py`).

| File | Class | Contents |
| --- | --- | --- |
| `World0.sav` | `FS_SaveSlot_C` | The save slot (see keys below). `World0_backup*.sav` are the game's backups. |
| `Challenges` | `FS_ChallengeSaveGame` | Account-wide: `CompletedChallenges` (set of challenge IDs) and `ChallengeStats` (ID → best progress). |
| `System0.sav` | `FS_SystemSave_C` | Settings: volumes, mouse sensitivity, key bindings, language. |

### Useful `World0.sav` properties

| Property | Meaning |
| --- | --- |
| `NamedSaveData` | Map of name → int; every quest flag and counter (see next table). |
| `InventoryContents` | Item path → count. Items you sold or used stay with count 0, which is how "ever owned" is tracked. |
| `SavableActorStates` | GUID → state for world actors already used: chests, pickups, Silver Skulls. Skull Finder matches skull GUIDs here. |
| `SavePointsVisited` / `UnlockedTeleporters` | Crystal Monuments and Wing Altars activated (asset paths). |
| `KilledEnemyCounts` | Enemy data asset → kill count. |
| `WeaponLevels`, `WeaponXP`, `WeaponUpgrades` | Per-weapon level, XP and upgrade state. |
| `ShopPurchases` / `ShopSales` | Umbada stock key → amount bought / item → amount sold. |
| `SavedPlayerLevel`, `XPAmount`, `PlayTime_Seconds` | Level, XP, play time. |
| `CollectedNotes`, `NPCsInJournal` | Journal entries. |

### `NamedSaveData` counters used by achievements

| Key | Meaning |
| --- | --- |
| `TotalAchievementWeapons` / `…Throwables` / `…Accessories` / `…Treasures` | Collection counts (targets 77 / 22 / 33 / 93) |
| `TotalChestsOpened`, `TotalSecretDoorsOpened` | Targets 108 and 89 |
| `CheckpointUnlockCount`, `TeleporterUnlockCount` | Crystal Monuments (32) and Wing Altars (10) |
| `TotalWeaponsUpgraded` | Target 63 |
| `FullEnergyCellsCount`, `WindGemsAcquired`, `HasUltraMove` | Energy Cells (4), Wind Gems (5), Storm Gem |
| `MealTicketsCollected`, `FishWifeTotalEggs`, `ScientistDataGiven` | Chef (60), Erma (50), Ossi (10) |
| `LibrarianBestiaryCompletionPercent` | Wourha's bestiary (100) |
| `RaiderNeckacesTurnedIn` | Aganmi (4) — note the game's spelling |
| `ShopkeepUnlock1–4`, `ShopUnlockFinished` | Duck figurines given to Umbada |
| `ShopAmountSpent` | Coins spent at Umbada (1000) |
| `SkullsTurnedIn`, `SkullDoorRewardCount` | Silver Skulls handed in at the skull door |
| `TotalLizerTreasures` | Loot sacks found (34 total) |
| `NecroWall00–04Destroyed` | Tower flesh walls |
| `SR_*_Acquired` | Treasure vaults (5) |
| `*Dead`, `*IsDead`, `*Defeated`, `DemonBossesKilled` | Boss kills |
| `Ending1–4Complete` | Endings seen |
| `ReadNote_*` | Notes and books read |

## Game data in the .pak

`steamapps\common\QueensDomain\QueensDomain\Content\Paks\QueensDomain-WindowsNoEditor.pak` — UE 4.27, pak v11,
unencrypted, uncompressed. `qdcore.py` (from Skull Finder) reads it.

| Asset | What's in it |
| --- | --- |
| `Blueprints/Challenges/FS_ChallengeData` | `ChallengeDefinitions`: every achievement's ID, name, description, condition mode (`Manual`, `Stat_AutoNSD`, `Stat_AutoInventory`, `Stat_AutoItemTag`), required counters and `StatMax`. |
| `Blueprints/Shop/Shop` | `Stock`: Umbada's items with `Price`, `RequiredProgression` (duck tier), `UnlockItem`, `RequiredNSD`. |
| `NPCs/SecretSkullDoor/SecretSkullDoor_NPC_BP` | `RewardList`: skull-door rewards at 10/20/30/40/50/69. |
| `Player/Assets/Blueprints/PlayerBalance` | Balance values: heal amounts, status durations, damage, XP curve. |
| `Items/**` | Item assets: `Name`, `Item Description`, `Category`, `ItemTags` (e.g. `ItemTags.AchievementWeapon`), `DataTags` (durations, cooldowns). |
| `Blueprints/Areas/*_Save`, `*_Teleporter` | Crystal Monuments (32) and Wing Altars (10) with their area names. |
| `StringTables/ImportedStringTable` | All English text, keyed (e.g. `guide_status_00_desc`). |
| `RuinsLevel/Maps/*.umap` | Levels; Skull Finder reads skull positions (`SkullKeyRelic_BP_C`) and landmarks here. |

Item category enum values: `NewEnumerator7` = treasure, `NewEnumerator2` = main weapon, `NewEnumerator3` = throwing
weapon, `NewEnumerator1` = accessory/artifact, `NewEnumerator0` = consumable, `NewEnumerator5` = key item.

## Caches

- `%LOCALAPPDATA%\QDProgress\gamedata.json` — items, monuments, altars, skulls (rebuilt when the .pak changes).
- `%LOCALAPPDATA%\QDSkullFinder\skull_data.json` — Skull Finder's skull cache.

Both are safe to delete.
