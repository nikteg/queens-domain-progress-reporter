"""
Queen's Domain progress analyzer.

Reads your save (World*.sav + the account-wide Challenges file) and prints how far you
are through the game's 53 achievements/challenges, the item collections, Crystal
Monuments / Wing Altars and the 69 Silver Skulls - including what is still missing.

Item, location and skull names are read from your own game install (the .pak), using
the reader from Queen's Domain Skull Finder (qdcore.py). Without the game installed it
still reports all counts, just without the "missing" lists.

Usage:
  python qd_progress.py                      # newest save in %LOCALAPPDATA%\\QueensDomain
  python qd_progress.py "path\\to\\save dir"   # or a World0.sav inside it
  python qd_progress.py --game "D:\\SteamLibrary\\steamapps\\common\\QueensDomain"
  python qd_progress.py --all                # also list every missing item / skull in full

Read-only: never writes to the save or the game.
"""
import argparse, glob, json, os, struct, sys
from collections import defaultdict

import gvas
import qdcore

CACHE_FILE = os.path.join(qdcore.APP_DIR.replace("QDSkullFinder", "QDProgress"), "gamedata.json")
CACHE_VERSION = 2

# ------------------------------------------------------------------ challenges
# Taken from the game's own definition table (Blueprints/Challenges/FS_ChallengeData).
# kind: "nsd"  -> counters in the world save's NamedSaveData {key: target}
#       "inv"  -> items that must be in the inventory
#       "tag"  -> own N items with a gameplay tag
#       "manual" -> flagged by the game when it happens (areas reached)
#       "all"  -> count of the other challenges completed
CHALLENGES = [
    ("Platinum", "cha_All_Complete", "Queen's Domain", "Overcome every challenge on the Isle of Neasied.", "all", 52),
    ("Areas", "cha_Area_Aqr", "Ocean Walk", "Reach the Obmuer Temple.", "manual", None),
    ("Areas", "cha_Area_Lib", "Endless Pages", "Reach the Tower of Knowledge.", "manual", None),
    ("Areas", "cha_Area_Maus", "Unsealed Tomb", "Reach the Deimpo Mausoleum.", "manual", None),
    ("Areas", "cha_Area_Aut", "Genesis", "Reach the Ancient World.", "manual", None),
    ("Areas", "cha_Area_Castle", "Halls of Hatred", "Reach Siraatsu Castle.", "manual", None),
    ("Areas", "cha_Area_Prison", "Dark Silence", "Reach the Forgotten Dungeon.", "manual", None),
    ("Areas", "cha_Area_Forest", "Sacred Groves", "Reach the Verdant Hollow.", "manual", None),
    ("Areas", "cha_Area_Swamp", "Deep Mire", "Reach the Rotting Cavern.", "manual", None),
    ("Areas", "cha_Area_ROS", "Sin Keeper", "Reach the Record of Sin.", "manual", None),
    ("Areas", "cha_Area_SG", "Memorial Sculpture", "Reach the Petrified Garden.", "manual", None),
    ("Quests", "cha_Quest_Raider", "Fate of the Iryupe Raiders", "Tell Captain Aganmi about the fate of his crew (necklaces).", "nsd", {"RaiderNeckacesTurnedIn": 4}),
    ("Quests", "cha_Quest_Fish", "Sacred Waters", "Bring every Orbewa Egg to Erma, Matron of the Deep.", "nsd", {"FishWifeTotalEggs": 50}),
    ("Quests", "cha_Quest_Lib", "A Lifetime's Work", "Help Knowledge Keeper Wourha complete her research (bestiary %).", "nsd", {"LibrarianBestiaryCompletionPercent": 100}),
    ("Quests", "cha_Quest_Meat", "Sparkling Clean", "Clean up the Tower of Knowledge (flesh walls).", "nsd", {f"NecroWall0{i}Destroyed": 1 for i in range(5)}),
    ("Quests", "cha_Quest_Books", "I'm Not Paying the Late Fee", "Return all of the lost books (Tower + Record of Sin puzzles).", "nsd", {"LibBookPuzzleComplete": 1, "ROSBookPuzzleComplete": 1}),
    ("Quests", "cha_Quest_Vaults", "Forgotten Rooms", "Explore every treasure vault.", "nsd", {"SR_GMS_Acquired": 1, "SR_GreenKey_Acquired": 1, "SR_RustedLeafBlade_Acquired": 1, "SR_Key_Blue_Acquired": 1, "SR_Rusted_Greatsword_Acquired": 1}),
    ("Quests", "cha_Quest_Chef", "Birds of a Feather", "Bring sixty Meal Tickets to Chef Gagi.", "nsd", {"MealTicketsCollected": 60}),
    ("Quests", "cha_Quest_Science", "Wise Work", "Witness the result of Mechanical Engineer Ossi's experiment (data modules).", "nsd", {"ScientistDataGiven": 10}),
    ("Quests", "cha_Quest_Shop_Spend", "Let's Make a Deal", "Spend one thousand Ancient Coins at Umbada's Trading Outpost.", "nsd", {"ShopAmountSpent": 1000}),
    ("Quests", "cha_Quest_PG_Puzzle", "Living Stone", "Wake the Petrified Garden.", "nsd", {"StoneGardenPuzzleFinished": 1}),
    ("Quests", "cha_Quest_Shop_Unlocks", "A Fine Collection", "Bring every duck figurine to Umbada.", "nsd", {"ShopkeepUnlock1": 1, "ShopkeepUnlock2": 1, "ShopkeepUnlock3": 1, "ShopkeepUnlock4": 1, "ShopUnlockFinished": 1}),
    ("Quests", "cha_Quest_Mushroom", "Oh the Places You'll Go", "Receive a strange reward.", "inv", ["StrangeMushroom"]),
    ("Quests", "cha_Quest_Skulls", "The Call From Beyond", "Complete a mysterious ritual (all 69 Silver Skulls).", "nsd", {"SkullRitualCompleted": 1}),
    ("Quests", "cha_Quest_Grimoire", "Witchcraft", "Inscribe something in the grimoire.", "nsd", {"HasEverInscribedGrimoire": 1}),
    ("Items", "cha_Item_FlyingSword", "Flying Sword", "Collect the Holy Sword Endu.", "nsd", {"FlyingSwordFirstgemAcquired": 1}),
    ("Items", "cha_Item_SecretSword", "Blade Bathed in Holy Light", "Forge the True Holy Sword Akunra.", "inv", ["SecretSword"]),
    ("Items", "cha_Item_SpecSword", "Most Spiritual Sword", "Collect Okbujo's Judgement.", "inv", ["SpectralSword_Item"]),
    ("Items", "cha_Item_UltraGem", "Raging Tempest", "Recover the Storm Gem.", "nsd", {"HasUltraMove": 1}),
    ("Items", "cha_Item_AllDashGems", "Feel the Wind", "Recover all five Wind Gems.", "nsd", {"WindGemsAcquired": 5}),
    ("Items", "cha_Item_UpgradeAllWeps", "Perfected Weaponry", "Upgrade every Main Weapon.", "nsd", {"TotalWeaponsUpgraded": 63}),
    ("Items", "cha_Item_GotAllWeps", "Extensive Armaments", "Collect every Main Weapon.", "nsd", {"TotalAchievementWeapons": 77}),
    ("Items", "cha_Item_GotAllThrowables", "Versatile Volley", "Collect every type of Throwing Weapon.", "nsd", {"TotalAchievementThrowables": 22}),
    ("Items", "cha_Item_GotAllAcc", "Eclectic Accoutrements", "Collect every Accessory.", "nsd", {"TotalAchievementAccessories": 33}),
    ("Items", "cha_Item_GotAllTreasures", "Glimmering Treasures", "Collect every Treasure.", "nsd", {"TotalAchievementTreasures": 93}),
    ("Items", "cha_Item_GotAllCells", "Overflowing Energy", "Collect four Energy Cells.", "nsd", {"FullEnergyCellsCount": 4}),
    ("Items", "cha_Item_GotAllLenses", "Magic Eyes", "Collect all four lenses for the Mask of Second Sight.", "inv", ["RuneVisionUnlock1", "RuneVisionUnlock2", "RuneVisionUnlock3", "RuneVisionUnlock4"]),
    ("Items", "cha_Item_EnergyWep", "Ancient Technology", "Find a very different type of main weapon.", "tag", ("ItemTags.EnergyWeapon", 1)),
    ("Exploration", "cha_Challenge_AllTeleporters", "Well Travelled", "Activate every Crystal Monument (32) and Wing Altar (10).", "nsd", {"CheckpointUnlockCount": 32, "TeleporterUnlockCount": 10}),
    ("Exploration", "cha_Challenge_AllChests", "Emptied Coffers", "Open every chest.", "nsd", {"TotalChestsOpened": 108}),
    ("Exploration", "cha_Challenge_AllSecretDoors", "Concealed Passages", "Open every secret door.", "nsd", {"TotalSecretDoorsOpened": 89}),
    ("Bosses", "cha_Bosses_Whale", "Treacherous Baleen", "Defeat Dagoom the Sea King.", "nsd", {"WhaleKingIsDead": 1}),
    ("Bosses", "cha_Bosses_Necro", "Hell Transcribed", "Defeat The Necronomicon.", "nsd", {"NecronimiconDefeated": 1}),
    ("Bosses", "cha_Bosses_Demons", "Demonic Servitude", "Defeat Poenir and Duenir, Malformed Demonic Aberrations.", "nsd", {"DemonBossesKilled": 1}),
    ("Bosses", "cha_Bosses_BridgeLord", "Sworn Protector", "Defeat Josami Lord Saijha.", "nsd", {"BridgeLordDead": 1}),
    ("Bosses", "cha_Bosses_RoSDragon", "Dread Silver", "Defeat Herald of Okbujo.", "nsd", {"ROSDragonDead": 1}),
    ("Bosses", "cha_Bosses_DragonLord", "Wake From Dreams", "Defeat Usunha and Wujomiod, Shrine of Puwema Gatekeepers.", "nsd", {"DragonLordDead": 1}),
    ("Bosses", "cha_Bosses_GiantFish", "Beneath Rotten Waters", "Defeat the Gigantic Serf.", "nsd", {"GiantSwampFish_IsDead": 1}),
    ("Bosses", "cha_Bosses_RedLords", "Fallen Angels", "Defeat Blood Angel Lords Yuumed and Woyeki.", "nsd", {"RedLordsDead": 1}),
    ("Endings", "cha_Endings_1", "Most Unfortunate", "Saw Ending 1.", "nsd", {"Ending1Complete": 1}),
    ("Endings", "cha_Endings_2", "A Kingdom Free From Darkness", "Saw Ending 2 (defeat the Queen with True Holy Sword Akunra).", "nsd", {"Ending2Complete": 1}),
    ("Endings", "cha_Endings_3", "God Slayer", "Saw Ending 3 (8 Mementos + Okbujo's Judgement, choose Banish).", "nsd", {"Ending3Complete": 1}),
    ("Endings", "cha_Endings_4", "Eat", "Saw Ending 4 (all 69 Silver Skulls, choose Eat).", "nsd", {"Ending4Complete": 1}),
]
TOTAL_SKULLS = qdcore.TOTAL_SKULLS

TAG_WEAPON, TAG_ACC, TAG_THROW = "ItemTags.AchievementWeapon", "ItemTags.AchievementAccessory", "ItemTags.AchievementThrowables"
TREASURE_CAT = "ItemCategory::NewEnumerator7"

# Lost books for "I'm Not Paying the Late Fee": (asset id, shelf, name, where the pickup is).
# Shelves are LIB_BookRecepticle_BP actors in 300_LIB (10 slots) and 760_SZ_AUT (4 slots). Six Tower slots name
# their book; the other four don't, and the four books left over are assumed to go there.
LOST_BOOKS = [
    ("Alchemy", "Tower", "The Great Work IV - Rubedo", "Isle of Neasied, Cube Hall: 26 m ENE of Cemetery Precipice, 13 m down"),
    ("Dragons", "Tower", "The History of Dragons", "Tower of Knowledge (not a placed pickup)"),
    ("DamsAndWeirs", "Tower", "Dams and Weirs", "Tower of Knowledge: 21 m SE of the Wing Altar, same height"),
    ("FairyTales", "Tower", "Upim's Fairy Tales", "level 710_SZ_AQ"),
    ("Eldritch", "Tower", "The Old Ones Beyond", "Tower of Knowledge (not a placed pickup)"),
    ("QueerRomance", "Tower", "Koko's Sapphic Adventure", "Tower of Knowledge: 32 m ENE of the Wing Altar, same height"),
    ("WarHistory", "Tower", "The End of Epha", "Tower of Knowledge"),
    ("RattyBugs", "Tower", "Ratty Bug Compendium", "Isle of Neasied"),
    ("BoneMachines", "Tower", "Bone Machines", "Deimpo Mausoleum, dark maze"),
    ("CookBook", "Tower", "How to Serve Humans", "Deimpo Mausoleum, dark maze"),
    ("Wodaso", "Record of Sin", "Wodaso's Embrace", "Tower of Knowledge: 26 m WSW of Forbidden Archives, 46 m down"),
    ("Jigeki", "Record of Sin", "The Rotting God", "level 210_AQ_underground"),
    ("Puwema", "Record of Sin", "The Green Goddess", "level 750_SZ_MAUS2"),
    ("Sipeha", "Record of Sin", "Monarch of the Void", "level 720_SZ_LIB"),
]


# ------------------------------------------------------------------ game data (from the .pak)
def scan_items(pak, strings):
    items = []
    for k in pak.files:
        # Artifacts/ holds the skull-door fossils, which are accessories too
        if not (k.startswith(("QueensDomain/Content/Items/", "QueensDomain/Content/Artifacts/"))
                and k.endswith(".uasset")): continue
        ua = pak.read(k)
        if b"Item Description" not in ua: continue
        try:
            p = qdcore.Pkg(ua, pak.read(k[:-7] + ".uexp")); pr = p.props(len(p.exports) - 1)
        except Exception:
            continue
        if "Name" not in pr: continue
        tags = []
        if "ItemTags" in pr:
            r = qdcore.R(pr["ItemTags"]); tags = [p.fn(r) for _ in range(r.i32())]
        key = qdcore.text_key(pr["Name"])
        items.append(dict(path="/Game/" + k[len("QueensDomain/Content/"):-7],
                          name=strings.get(key or "", key or os.path.basename(k)[:-7]),
                          cat=p.fn(qdcore.R(pr["Category"])) if "Category" in pr else None, tags=tags))
    return items


def scan_places(pak, strings):
    """Crystal Monuments (*_Save) and Wing Altars (*_Teleporter) -> asset path: name."""
    monuments, altars = {}, {}
    for k in pak.files:
        if not (k.startswith("QueensDomain/Content/Blueprints/Areas/") and k.endswith(".uasset")): continue
        base = os.path.basename(k)[:-7]
        is_mon, is_tp = base.lower().endswith("_save"), base.endswith("_Teleporter")
        if not (is_mon or is_tp): continue
        try:
            p = qdcore.Pkg(pak.read(k), pak.read(k[:-7] + ".uexp")); pr = p.props(len(p.exports) - 1)
        except Exception:
            continue
        area = strings.get(qdcore.text_key(pr.get("Name", b"")) or "", "")
        mon = strings.get(qdcore.text_key(pr.get("AreaName", b"")) or "", "")
        path = "/Game/" + k[len("QueensDomain/Content/"):-7]
        if is_mon:
            monuments[path] = f"{mon} ({area})" if area.strip("? ") else mon
        else:
            altars[path] = area
    return monuments, altars


def load_gamedata(pak_path):
    st = os.stat(pak_path); key = f"{CACHE_VERSION}:{st.st_size}:{int(st.st_mtime)}"
    try:
        with open(CACHE_FILE, encoding="utf-8") as fh:
            c = json.load(fh)
        if c.get("key") == key: return c
    except (OSError, ValueError):
        pass
    print("Reading game data from the .pak (first run only, takes a minute)...", file=sys.stderr)
    pak = qdcore.Pak(pak_path)
    try:
        strings = qdcore.read_strings(pak)
        items = scan_items(pak, strings)
        monuments, altars = scan_places(pak, strings)
    finally:
        pak.close()
    skulls = qdcore.load_skulls(pak_path, lambda n, t, m: print(f"  scanning levels {n}/{t}", end="\r", file=sys.stderr))
    print(" " * 40, end="\r", file=sys.stderr)
    data = dict(key=key, items=items, monuments=monuments, altars=altars, skulls=skulls)
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    return data


# ------------------------------------------------------------------ save
def find_save(arg):
    if arg:
        if os.path.isfile(arg): return arg
        c = [p for p in glob.glob(os.path.join(arg, "World*.sav")) if "backup" not in p.lower()]
        if not c: sys.exit(f"No World*.sav found in {arg}")
        return max(c, key=os.path.getmtime)
    c = qdcore.find_saves()
    if not c: sys.exit(f"No saves found under {qdcore.SAVE_ROOT}. Pass the save folder as an argument.")
    return c[0]


def strip_obj(path):
    """'/Game/A/B.B' -> '/Game/A/B'"""
    return path.split(".")[0]


# ------------------------------------------------------------------ report helpers
def bar(have, total, width=24):
    frac = 0 if not total else min(1, have / total)
    n = round(frac * width)
    return "█" * n + "░" * (width - n)


def line(label, have, total, extra=""):
    pct = 100 * have / total if total else 0
    return f"  {label:<34} {bar(have, total)} {have:>5}/{total:<5} {pct:5.1f}%{('  ' + extra) if extra else ''}"


def header(title):
    print(); print(title); print("─" * len(title))


def show_list(names, show_all, limit=12, indent="      "):
    names = sorted(names)
    shown = names if show_all else names[:limit]
    for n in shown:
        print(f"{indent}- {n}")
    if len(names) > len(shown):
        print(f"{indent}  ...and {len(names) - len(shown)} more (use --all)")


def fmt_time(sec):
    h, m = divmod(int(sec) // 60, 60)
    return f"{h}h {m:02d}m"


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="Show your Queen's Domain completion progress.")
    ap.add_argument("save", nargs="?", help="save folder or World*.sav (default: newest save)")
    ap.add_argument("--game", help="game folder or .pak (default: found via Steam)")
    ap.add_argument("--all", action="store_true", help="list every missing item/skull instead of a sample")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    save_path = find_save(args.save)
    world = gvas.parse(save_path)
    nsd = world.get("NamedSaveData") or {}
    inv = {strip_obj(k): v for k, v in (world.get("InventoryContents") or {}).items()}
    inv_names = {p.rsplit("/", 1)[-1] for p in inv}

    chal_path = os.path.join(os.path.dirname(save_path), "Challenges")
    completed = set()
    if os.path.isfile(chal_path):
        completed = set(gvas.parse(chal_path).get("CompletedChallenges") or [])

    pak = qdcore.pak_from_folder(args.game) if args.game else qdcore.find_pak()
    game = None
    if pak:
        try:
            game = load_gamedata(pak)
        except Exception as e:
            print(f"(Couldn't read game data: {e}. Showing counts only.)", file=sys.stderr)
    else:
        print("(Game install not found - showing counts only. Use --game to point at it.)", file=sys.stderr)

    items_by_tag = defaultdict(list)
    if game:
        for it in game["items"]:
            for t in it["tags"]: items_by_tag[t].append(it)

    # ---------------------------------------------------------- overview
    print(f"Queen's Domain progress — {save_path}")
    print(f"  Level {world.get('SavedPlayerLevel', '?')}   XP {world.get('XPAmount', 0):,}   "
          f"Play time {fmt_time(world.get('PlayTime_Seconds') or world.get('LastSavePlaytime') or 0)}   "
          f"Saved at: {os.path.basename(strip_obj(world.get('SavedArea', '?')))}")

    # ---------------------------------------------------------- challenges
    results = []
    for group, cid, name, desc, kind, cond in CHALLENGES:
        if kind == "nsd":
            have = sum(min(int(nsd.get(k, 0)), v) for k, v in cond.items()); total = sum(cond.values())
        elif kind == "inv":
            have = sum(1 for n in cond if n in inv_names); total = len(cond)
        elif kind == "tag":
            tag, total = cond
            have = min(total, sum(1 for it in items_by_tag[tag] if it["path"] in inv)) if game else 0
        elif kind == "all":
            total = cond; have = len(completed - {cid})
        else:
            have, total = (1 if (cid in completed or nsd.get(cid)) else 0), 1
        done = cid in completed or have >= total
        results.append((group, cid, name, desc, have, total, done))

    n_done = sum(r[6] for r in results)
    header(f"Achievements / Challenges: {n_done}/{len(results)} complete")
    print(line("Overall", n_done, len(results)))
    for group in dict.fromkeys(r[0] for r in results):
        rows = [r for r in results if r[0] == group]
        print(f"\n  {group} ({sum(r[6] for r in rows)}/{len(rows)})")
        for _, cid, name, desc, have, total, done in rows:
            mark = "✔" if done else "✘"
            prog = "" if total == 1 else f"  [{have}/{total}]"
            print(f"    {mark} {name:<30}{prog}" + ("" if done else f"  — {desc}"))

    # ---------------------------------------------------------- collections
    header("Collections")

    def collection(label, tag, stat, total):
        have = int(nsd.get(stat, 0))
        print(line(label, have, total))
        if game and have < total:
            missing = [it["name"] for it in items_by_tag[tag] if it["path"] not in inv]
            if missing:
                print(f"      missing {len(missing)}:")
                show_list(missing, args.all)

    collection("Main weapons", TAG_WEAPON, "TotalAchievementWeapons", 77)
    collection("Throwing weapons", TAG_THROW, "TotalAchievementThrowables", 22)
    collection("Accessories", TAG_ACC, "TotalAchievementAccessories", 33)

    have_t = int(nsd.get("TotalAchievementTreasures", 0))
    print(line("Treasures (incl. loot sacks)", have_t, 93))
    if game:
        uniq = [it for it in game["items"] if it["cat"] == TREASURE_CAT and not it["tags"]
                and not it["path"].endswith("/Coin")]
        got = [it for it in uniq if it["path"] in inv]
        print(line("  unique treasures", len(got), len(uniq)))
        # every loot sack counts toward the 93, and they can drop repeatedly, so there's no fixed total
        print(f"    loot sacks found: {int(nsd.get('TotalLizerTreasures', 0))} (each one counts toward the 93)")
        missing = [it["name"] for it in uniq if it["path"] not in inv]
        if missing:
            if have_t >= 93:
                note = "not needed, the achievement is complete"
            else:
                note = f"any {93 - have_t} more treasures or sacks finish it"
            print(f"      missing {len(missing)} unique treasures ({note}):")
            show_list(missing, args.all)

    print(line("Weapons upgraded", int(nsd.get("TotalWeaponsUpgraded", 0)), 63))
    print(line("Energy cells (full)", int(nsd.get("FullEnergyCellsCount", 0)), 4))
    print(line("Wind Gems", int(nsd.get("WindGemsAcquired", 0)), 5))
    lenses = sum(1 for i in range(1, 5) if f"RuneVisionUnlock{i}" in inv_names)
    print(line("Mask of Second Sight lenses", lenses, 4))
    print(line("Meal Tickets (Chef Gagi)", int(nsd.get("MealTicketsCollected", 0)), 60))
    print(line("Orbewa Eggs (Erma)", int(nsd.get("FishWifeTotalEggs", 0)), 50))
    print(line("Data modules (Ossi)", int(nsd.get("ScientistDataGiven", 0)), 10))
    print(line("Duck figurines (Umbada)", sum(int(nsd.get(k, 0) > 0) for k in
               ("ShopkeepUnlock1", "ShopkeepUnlock2", "ShopkeepUnlock3", "ShopkeepUnlock4", "ShopUnlockFinished")), 5))
    print(line("Raider necklaces (Aganmi)", int(nsd.get("RaiderNeckacesTurnedIn", 0)), 4))
    print(line("Bestiary % (Wourha)", int(nsd.get("LibrarianBestiaryCompletionPercent", 0)), 100))
    print(line("Coins spent at Umbada", min(1000, int(nsd.get("ShopAmountSpent", 0))), 1000,
               f"(total spent {int(nsd.get('ShopAmountSpent', 0)):,})"))

    for shelf, done_key in (("Tower", "LibBookPuzzleComplete"), ("Record of Sin", "ROSBookPuzzleComplete")):
        books = [b for b in LOST_BOOKS if b[1] == shelf]
        done = nsd.get(done_key, 0) > 0
        got = [b for b in books if done or f"BookKey_00_{b[0]}_Item" in inv_names]
        print(line(f"Lost books: {shelf} shelf", len(got), len(books), "(shelf done)" if done else ""))
        missing = [f"{b[2]} — {b[3]}" for b in books if b not in got]
        if missing: show_list(missing, True)

    # ---------------------------------------------------------- exploration
    header("Exploration")
    visited = {strip_obj(p) for p in world.get("SavePointsVisited") or []}
    altars = {strip_obj(p) for p in world.get("UnlockedTeleporters") or []}
    print(line("Crystal Monuments", int(nsd.get("CheckpointUnlockCount", len(visited))), 32))
    if game:
        miss = [n for p, n in game["monuments"].items() if p not in visited]
        if miss: show_list(miss, True)
    print(line("Wing Altars", int(nsd.get("TeleporterUnlockCount", len(altars))), 10))
    if game:
        miss = [n for p, n in game["altars"].items() if p not in altars]
        if miss: show_list(miss, True)
    print(line("Chests opened", int(nsd.get("TotalChestsOpened", 0)), 108))
    print(line("Secret doors opened", int(nsd.get("TotalSecretDoorsOpened", 0)), 89))
    print(line("Treasure vaults", sum(int(nsd.get(k, 0) > 0) for k in CHALLENGES_BY_ID["cha_Quest_Vaults"][5]), 5))
    print(line("Tower flesh walls cleaned", sum(int(nsd.get(f"NecroWall0{i}Destroyed", 0) > 0) for i in range(5)), 5))

    # ---------------------------------------------------------- skulls
    header("Silver Skulls")
    held = next((int(v) for k, v in inv.items() if k.endswith("/SkullKeyRelic_Data")), 0)
    turned_in = int(nsd.get("SkullsTurnedIn", 0))
    if game:
        save = qdcore.read_save(save_path)
        missing = qdcore.check([dict(s) for s in game["skulls"]], save)
        found = len(game["skulls"]) - len(missing)
        print(line("Found", found, TOTAL_SKULLS))
        print(line("Turned in at the skull door", turned_in, TOTAL_SKULLS, f"({held} carried)"))
        if missing:
            by_area = defaultdict(list)
            for s in missing: by_area[s["area"]].append(s)
            print(f"      missing {len(missing)}, by area:")
            for area, ss in sorted(by_area.items(), key=lambda x: -len(x[1])):
                print(f"      {area} ({len(ss)})")
                if args.all:
                    for s in ss: print(f"          - {s['short']}")
            if not args.all:
                print("      (use --all for a hint per skull, or run Skull Finder for full directions)")
    else:
        print(line("Turned in at the skull door", turned_in, TOTAL_SKULLS, f"({held} carried)"))

    # ---------------------------------------------------------- stats
    header("Stats")
    kills = world.get("KilledEnemyCounts") or {}
    notes = sum(1 for k in nsd if k.startswith("ReadNote_") and k != "ReadNote_")
    print(f"  Enemies killed       {sum(kills.values()):,} ({len(kills)} kinds)")
    print(f"  Pots broken          {int(nsd.get('TotalPotBreaks', 0)):,}")
    print(f"  Consumables used     {int(world.get('ConsumablesUsedCount', 0)):,}")
    print(f"  Notes/books read     {notes}")
    print(f"  Grimoire inks        {int(nsd.get('GrimoireInksAcquired', 0))}")
    print(f"  Sipeha seals removed {int(nsd.get('SipehaRunesActivated', 0))}")
    print(f"  Knight ghosts found  {int(nsd.get('KnightGhostsActive', 0))}")
    print(f"  Ancient Coins        {int(inv.get('/Game/Items/Treasure/Coins/Coin', 0) or 0):,}")
    levels = world.get("WeaponLevels") or {}
    if levels:
        top = sorted(levels.items(), key=lambda kv: -kv[1])[:5]
        names = {it["path"]: it["name"] for it in game["items"]} if game else {}
        print("  Highest weapon levels: " + ", ".join(
            f"{names.get(strip_obj(p), os.path.basename(strip_obj(p)))} {lv}" for p, lv in top))


CHALLENGES_BY_ID = {c[1]: c for c in CHALLENGES}

if __name__ == "__main__":
    try:
        main()
    except qdcore.QDError as e:
        sys.exit(str(e))
