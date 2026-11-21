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
| `TotalLizerTreasures` | Loot sacks found; no fixed total, each one also adds to `TotalAchievementTreasures` |
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
| `Items/**`, `Artifacts/**` | Item assets (`Artifacts/` has the skull-door fossils): `Name`, `Item Description`, `Category`, `ItemTags` (e.g. `ItemTags.AchievementWeapon`), `DataTags` (durations, cooldowns). |
| `Blueprints/Areas/*_Save`, `*_Teleporter` | Crystal Monuments (32) and Wing Altars (10) with their area names. |
| `StringTables/ImportedStringTable` | All English text, keyed (e.g. `guide_status_00_desc`). |
| `RuinsLevel/Maps/*.umap` | Levels; Skull Finder reads skull positions (`SkullKeyRelic_BP_C`) and landmarks here. |

Item category enum values: `NewEnumerator7` = treasure, `NewEnumerator2` = main weapon, `NewEnumerator3` = throwing
weapon, `NewEnumerator1` = accessory/artifact, `NewEnumerator0` = consumable, `NewEnumerator5` = key item.

## Coordinates and compass directions

Positions in the level files (`RelativeLocation` of an actor's root component) are Unreal units, **1 unit = 1 cm**.
Divide by 100 for metres.

The in-game compass (top right of the HUD) lines up with the world axes like this:

| Compass | World axis |
| --- | --- |
| North | +X |
| East | +Y |
| South | −X |
| West | −Y |
| Up | +Z |

This is Unreal's default: yaw 0° faces +X, and yaw grows clockwise when seen from above, so yaw 90° faces +Y.
The HUD (`UI/HUD/FS_PlayerHUD`) feeds the camera's yaw into `UI/HUD/Compass/MagicCompass_RWM`, which turns the 3D
compass model (`Compass_SM`) with a small spring (`SimYaw`, `YawSpringState`), so the needle swings briefly before
settling.

**How it was checked:** the mapping can't be read from the files, because which mark on the compass model means
north depends on the model's mesh and texture. It was confirmed in game instead. A food offering pedestal stands
40 m from the Verdant Hollow Wing Altar (`Teleporter_Forest` in `780_SZ_Depths`) at the same height, and it lies
almost exactly on the +X axis (Δx = +40 m, Δy = −2 m). In game that pedestal is directly north of the altar. A
second pedestal 85 m out on the same line agrees.

### Working out a direction

For two points A (where you stand) and B (the target):

```python
import math
dn = (B[0] - A[0]) / 100        # metres north (+X)
de = (B[1] - A[1]) / 100        # metres east  (+Y)
dz = (B[2] - A[2]) / 100        # metres up
distance = math.hypot(dn, de)   # horizontal distance
bearing = math.degrees(math.atan2(de, dn)) % 360   # 0 = N, 90 = E, 180 = S, 270 = W
```

Name the bearing with the 16-point compass (each point covers 22.5°):

| Bearing | Direction | Bearing | Direction |
| --- | --- | --- | --- |
| 0° | N | 180° | S |
| 22.5° | NNE | 202.5° | SSW |
| 45° | NE | 225° | SW |
| 67.5° | ENE | 247.5° | WSW |
| 90° | E | 270° | W |
| 112.5° | ESE | 292.5° | WNW |
| 135° | SE | 315° | NW |
| 157.5° | SSE | 337.5° | NNW |

Example: a skull at Δx = −71 m, Δy = −21 m, Δz = +45 m from the Verdant Hollow Wing Altar is 74 m away at bearing
196°, so it's south (slightly west) and 45 m up.

Side note for directions like "on your left": when facing along a bearing, a point is on your right if the 2D cross
product `dn_walk * de_point - de_walk * dn_point` is positive.

### Caveats

- **Only compare points from the same coordinate space.** Sub-levels of one region share coordinates (for example
  `400_MAUS_entrance`, `420_MAUS_mid` and `450_MAUS_darkmaze` in the Deimpo Mausoleum), so distances between them are
  real. Points in unrelated regions are not, even when a distance can be computed.
- **Nearest monument across sub-levels:** Skull Finder (`qdcore.describe`) prefers monuments in the skull's own
  level file, so it can name a monument that is further away than one in a sibling sub-level. For example, it
  pairs a Mausoleum skull with Lower Area (110 m) when Crumbling Stairwell is only 30 m away.
- **Height matters as much as direction:** many skulls are 20–100 m above or below the obvious floor, so always give
  Δz along with the bearing.
- The player's facing at the last save is stored in `World0.sav` (`SaveLocation.Rotation`, a quaternion). Its yaw
  uses the same convention, which gives a second way to check the mapping if a game update ever changes it.

## Caches

- `%LOCALAPPDATA%\QDProgress\gamedata.json` — items, monuments, altars, skulls (rebuilt when the .pak changes).
- `%LOCALAPPDATA%\QDSkullFinder\skull_data.json` — Skull Finder's skull cache.

Both are safe to delete.
