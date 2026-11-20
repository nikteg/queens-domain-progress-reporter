# Vendored from https://github.com/mesetamusic/queens-domain-skull-finder (src/qdcore.py), MIT License.
"""
Core logic for Queen's Domain Skull Finder.

 - finds the game install (Steam libraries) and the player's save
 - reads skull pickups and landmarks out of the game's .pak (UE4.27, v11, unencrypted)
 - checks which skulls the save has recorded as picked up
 - writes a plain-English "where is it" description for every skull

Read-only: nothing here writes to the game or the save.
"""
import glob, json, math, os, re, statistics, struct

APP_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "QDSkullFinder")
CACHE_FILE = os.path.join(APP_DIR, "skull_data.json")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
SAVE_ROOT = os.path.join(os.environ.get("LOCALAPPDATA", ""), "QueensDomain", "Saved", "SaveGames")
PAK_REL = os.path.join("steamapps", "common", "QueensDomain", "QueensDomain", "Content", "Paks",
                       "QueensDomain-WindowsNoEditor.pak")
MAP_DIR = "RuinsLevel/Maps/"
DATA_VERSION = 4
TOTAL_SKULLS = 69


class QDError(Exception):
    """Errors with a message that is safe to show to the user."""


# ------------------------------------------------------------------ settings
def load_settings():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_settings(s):
    os.makedirs(APP_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=1)


# ------------------------------------------------------------------ locating files
def steam_libraries():
    roots = []
    try:
        import winreg
        for hive, key, val in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                               (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
                               (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath")):
            try:
                with winreg.OpenKey(hive, key) as k:
                    roots.append(winreg.QueryValueEx(k, val)[0])
            except OSError:
                pass
    except ImportError:
        pass
    roots += [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam"]
    libs = []
    for r in roots:
        r = os.path.normpath(r)
        if r not in libs: libs.append(r)
        vdf = os.path.join(r, "steamapps", "libraryfolders.vdf")
        try:
            with open(vdf, encoding="utf-8", errors="ignore") as fh:
                for m in re.finditer(r'"path"\s+"(.+?)"', fh.read()):
                    p = os.path.normpath(m.group(1).replace("\\\\", "\\"))
                    if p not in libs: libs.append(p)
        except OSError:
            pass
    # common library locations on other drives
    for d in "CDEFGH":
        for sub in ("SteamLibrary", "Steam", r"Games\Steam", r"Games\SteamLibrary"):
            p = f"{d}:\\{sub}"
            if p not in libs: libs.append(p)
    return libs


def find_pak(settings=None):
    p = (settings or {}).get("pak")
    if p and os.path.isfile(p): return p
    for lib in steam_libraries():
        cand = os.path.join(lib, PAK_REL)
        if os.path.isfile(cand): return cand
    return None


def pak_from_folder(folder):
    """Accept the game folder, or any folder inside it, or the .pak itself."""
    if os.path.isfile(folder) and folder.lower().endswith(".pak"): return folder
    for _ in range(4):
        hits = glob.glob(os.path.join(folder, "**", "QueensDomain-WindowsNoEditor.pak"), recursive=True)
        if hits: return hits[0]
        folder = os.path.dirname(folder)
    return None


def find_saves():
    """All world saves, newest first (backups excluded)."""
    c = [p for p in glob.glob(os.path.join(SAVE_ROOT, "*", "World*.sav")) if "backup" not in os.path.basename(p).lower()]
    return sorted(c, key=os.path.getmtime, reverse=True)


# ------------------------------------------------------------------ binary helpers
class R:
    def __init__(s, b, o=0): s.b, s.o = b, o
    def i32(s): v = struct.unpack_from("<i", s.b, s.o)[0]; s.o += 4; return v
    def u32(s): v = struct.unpack_from("<I", s.b, s.o)[0]; s.o += 4; return v
    def u64(s): v = struct.unpack_from("<Q", s.b, s.o)[0]; s.o += 8; return v
    def raw(s, n): v = s.b[s.o:s.o + n]; s.o += n; return v
    def fstr(s):
        n = s.i32()
        if n == 0: return ""
        if n < 0: return s.raw(-n * 2).decode("utf-16-le")[:-1]
        return s.raw(n)[:-1].decode("latin-1")


class Pak:
    def __init__(s, path):
        s.f = f = open(path, "rb"); f.seek(0, 2); size = f.tell()
        f.seek(size - 300); tail = f.read(300)
        i = tail.find(struct.pack("<I", 0x5A6F12E1))
        if i < 0: raise QDError("The selected .pak file isn't an Unreal Engine pak.")
        if tail[i - 1]: raise QDError("The game's data is encrypted in this version - Skull Finder can't read it.")
        off, sz = struct.unpack_from("<qq", tail, i + 8)
        f.seek(off); r = R(f.read(sz))
        mount = r.fstr(); r.i32(); r.u64()
        if r.u32(): r.raw(36)
        if not r.u32(): raise QDError("Unsupported pak format (no directory index).")
        fdo, fds = struct.unpack("<qq", r.raw(16)); r.raw(20)
        s.enc = r.raw(r.i32())
        f.seek(fdo); d = R(f.read(fds)); s.files = {}
        for _ in range(d.i32()):
            dn = d.fstr()
            for _ in range(d.i32()):
                fn = d.fstr(); s.files[(mount + dn + fn).replace("../../../", "")] = d.i32()

    def read(s, name):
        e = R(s.enc, s.files[name]); v = e.u32()
        if (v & 0x3F) == 0x3F: e.u32()
        if (v >> 23) & 0x3F or (v >> 22) & 1:
            raise QDError("The game's data is compressed in this version - Skull Finder can't read it.")
        off = e.u32() if (v >> 31) & 1 else e.u64()
        size = e.u32() if (v >> 30) & 1 else e.u64()
        s.f.seek(off + 53); return s.f.read(size)

    def close(s): s.f.close()


class Pkg:
    def __init__(s, ua, ue):
        r = R(ua); s.ue = ue
        r.u32(); r.i32(); r.i32(); r.i32(); r.i32()
        for _ in range(r.i32()): r.raw(20)
        s.hdr = r.i32(); r.fstr(); flags = r.u32()
        nc, no = r.i32(), r.i32()
        if not flags & 0x80000000: r.fstr()
        r.i32(); r.i32()
        ec, eo, ic, io = r.i32(), r.i32(), r.i32(), r.i32()
        r = R(ua, no); s.names = []
        for _ in range(nc): s.names.append(r.fstr()); r.raw(4)
        r = R(ua, io); s.imports = []
        for _ in range(ic):
            s.fn(r); s.fn(r); r.i32(); s.imports.append(s.fn(r))
        r = R(ua, eo); s.exports = []
        for _ in range(ec):
            ci = r.i32(); r.i32(); r.i32(); oi = r.i32(); on = s.fn(r); r.u32()
            sz, off = struct.unpack("<qq", r.raw(16)); r.raw(60)
            s.exports.append((ci, oi, on, sz, off))

    def fn(s, r):
        i, n = r.i32(), r.i32()
        return s.names[i] if n == 0 else f"{s.names[i]}_{n - 1}"

    def objname(s, i):
        return s.imports[-i - 1] if i < 0 else s.exports[i - 1][2] if i > 0 else ""

    def props(s, idx):
        _, _, _, sz, off = s.exports[idx]
        b = s.ue[off - s.hdr: off - s.hdr + sz]; r = R(b); out = {}
        while r.o < len(b) - 8:
            name = s.fn(r)
            if name == "None": break
            typ = s.fn(r); size = r.i32(); r.i32()
            if typ == "StructProperty": s.fn(r); r.raw(16)
            elif typ == "BoolProperty": r.raw(1)
            elif typ in ("ByteProperty", "EnumProperty", "ArrayProperty", "SetProperty"): s.fn(r)
            elif typ == "MapProperty": s.fn(r); s.fn(r)
            if r.raw(1)[0]: r.raw(16)
            out[name] = r.raw(size)
        return out

    def location(s, pr):
        if "RootComponent" not in pr: return None
        ri = struct.unpack("<i", pr["RootComponent"])[0]
        if ri <= 0: return None
        rp = s.props(ri - 1)
        return list(struct.unpack("<3f", rp["RelativeLocation"])) if "RelativeLocation" in rp else None


# ------------------------------------------------------------------ landmarks
# (regex on class name, friendly name, kind). kind: "anchor" = worth naming from afar,
# "prop" = only mention when right next to the skull, "ground" = used to judge the floor height.
LANDMARKS = [
    (r"^FlyingSwordChargeRelic", "Wind Gem", "anchor"),
    (r"^Teleporter_C$", "Wing Altar", "anchor"),
    (r"SecretWall|ScienceRoomDoor", "secret wall", "anchor"),
    (r"^Chest_C$", "treasure chest", "anchor"),
    (r"^(\w+?)_Statue_BP", None, "anchor"),
    (r"GodParticleSphere", None, "anchor"),
    (r"Upgrade_?Pedestal", "food offering pedestal", "anchor"),
    (r"^EggPedestal", "egg pedestal", "anchor"),
    (r"KeyRecep", "key receptacle", "anchor"),
    (r"Lever", "lever", "anchor"),
    (r"SwordShrine", "sword shrine", "anchor"),
    (r"Lib_GargoyleBase", "gargoyle statue", "anchor"),
    (r"Lib_Basement_Statue", "statue", "anchor"),
    (r"SZ_Altar", "altar", "anchor"),
    (r"GiantBrazier", "giant brazier", "anchor"),
    (r"OW_BigPipe_", "huge pipe", "anchor"),
    (r"OW_MK_Tank", "large metal tank", "anchor"),
    (r"JailDoor", "cell door", "anchor"),
    (r"Waterfall", "waterfall", "anchor"),
    (r"OW_MK_Computer", "computer terminal", "prop"),
    (r"OW_MK_Generator", "generator", "prop"),
    (r"Table", "table", "prop"),
    (r"Stool|Chair", "stool", "prop"),
    (r"M_Grave", "grave", "prop"),
    (r"M_Kitchen", "kitchen utensils", "prop"),
    (r"Lib_Book|Lib_Pages", "books", "prop"),
    (r"BigCrate|^Crate_C|Barrel", "crates/barrels", "prop"),
    (r"Brazier", "brazier", "prop"),
    (r"Candle", "candles", "prop"),
    (r"Tree", "tree", "prop"),
    (r"Branch", "branch", "prop"),
    (r"Toilet", "toilet", "prop"),
    (r"Web", "cobwebs", "prop"),
    (r"Coin", "coins", "prop"),
    (r"Shackle", "shackles", "prop"),
    (r"LilyPads|seaweed|seashell", "water plants", "prop"),
    (r"Scrap", "scrap heap", "prop"),
    (r"Pipe", "pipes", "prop"),
    (r"Grass|Rubble|Deco_Rock|Pot|plant|Plant|Bush|Fern|Moss|moss|Mushroom|mushroom|FallenLeaves|Herb", None, "ground"),
]
_LM = [(re.compile(p), n, k) for p, n, k in LANDMARKS]


def classify(cls):
    for rx, name, kind in _LM:
        m = rx.search(cls)
        if m:
            if name is None and kind == "anchor":
                if "GodParticle" in cls:
                    name = cls.split("GodParticle")[0] + " seal"
                else:
                    base = re.sub(r"^(FS|OW|SG|SZ)_", "", m.group(1))
                    name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", base).replace("_", " ") + " statue"
            return name, kind
    return None, None


def read_strings(pak):
    try:
        d = pak.read("QueensDomain/Content/StringTables/ImportedStringTable.uexp")
        r = R(d, 12); r.fstr(); tab = {}
        for _ in range(r.i32()):
            k = r.fstr(); tab[k.lower()] = r.fstr()
        return tab
    except Exception:
        return {}


def text_key(blob):
    """Pull the string-table key out of a serialized FText (string-table reference)."""
    m = re.findall(rb"([A-Za-z0-9_]{3,})\x00", blob)
    return m[-1].decode().lower() if m else None


def scan_game(pak_path, progress=None):
    pak = Pak(pak_path)
    try:
        strings = read_strings(pak)
        loc_names = {}  # LocationData asset name -> (monument name, area name)
        for k in pak.files:
            if k.startswith("QueensDomain/Content/Blueprints/Areas/") and k.endswith(".uasset") and "_Icon" not in k:
                try:
                    p = Pkg(pak.read(k), pak.read(k[:-7] + ".uexp")); pr = p.props(len(p.exports) - 1)
                    mon = strings.get(text_key(pr.get("AreaName", b"")) or "")
                    area = strings.get(text_key(pr.get("Name", b"")) or "")
                    if mon: loc_names[os.path.basename(k)[:-7]] = (mon, area)
                except Exception:
                    pass

        levels = sorted(k for k in pak.files if MAP_DIR in k and k.endswith(".umap"))
        skulls, monuments, per_map = [], [], {}
        for n, path in enumerate(levels, 1):
            ua = pak.read(path)
            has_skull = b"SkullKeyRelic" in ua
            if not has_skull and b"Checkpoint_C" not in ua and b"Teleporter_C" not in ua: continue
            mapname = path.rsplit("/", 1)[1][:-5]
            if progress: progress(n, len(levels), mapname)
            p = Pkg(ua, pak.read(path[:-5] + ".uexp"))
            things = []
            for i, (ci, oi, on, _, _) in enumerate(p.exports):
                cls = p.objname(ci)
                if oi == 0 or not cls.endswith("_C"): continue
                if not has_skull and cls not in ("Checkpoint_C", "Teleporter_C"): continue
                try:
                    pr = p.props(i); loc = p.location(pr)
                except Exception:
                    continue
                if loc is None: continue
                if cls == "SkullKeyRelic_BP_C" and "GUIDs" in pr:
                    skulls.append(dict(map=mapname, actor=on, guid=pr["GUIDs"][-16:].hex(), loc=loc))
                elif cls == "Checkpoint_C":
                    ld = struct.unpack("<i", pr["LocationData"])[0] if "LocationData" in pr else 0
                    raw = p.objname(ld)
                    mon, area = loc_names.get(raw, (raw.replace("_Save", "").replace("_", " "), ""))
                    monuments.append(dict(name=mon, area=area, loc=loc, map=mapname))
                else:
                    name, kind = classify(cls)
                    if kind: things.append((name, kind, loc))
            per_map[mapname] = things
        for sk in skulls:
            sk.update(describe(sk, monuments, per_map.get(sk["map"], [])))
        if len(skulls) < 10:
            raise QDError(f"Only found {len(skulls)} skulls in the game files - this game version may not be supported.")
        return skulls
    finally:
        pak.close()


def _m(units): return max(1, round(units / 100))


def _a(noun): return ("an " if noun[0].lower() in "aeiou" else "a ") + noun


def _height(dz):
    m = round(dz / 100)
    if m >= 4: return f"{m} m higher than it"
    if m <= -4: return f"{-m} m lower than it"
    return "about the same height"


def describe(sk, monuments, things):
    loc = sk["loc"]
    region = sk["map"][0]
    # nearest monument: prefer same level, else same region (sub-levels share coordinates)
    same = [m for m in monuments if m["map"] == sk["map"]] or [m for m in monuments if m["map"][0] == region]
    mon = min(same, key=lambda m: math.dist(m["loc"], loc)) if same else None
    area = (mon or {}).get("area") or ""
    if not area.strip("? "):  # the game hides some area names as "???"
        area = FALLBACK_AREAS.get(sk["map"], "Underworld")
    lines, tags = [], []

    if mon:
        d = math.dist(mon["loc"], loc)
        lines.append(f"Nearest Crystal Monument: {mon['name']} - {_m(d)} m away, skull is {_height(loc[2] - mon['loc'][2])}.")

    # anchors (named landmarks) within 60 m, closest of each kind
    anchors, seen = [], set()
    for name, kind, l in sorted(things, key=lambda t: math.dist(t[2], loc)):
        d = math.dist(l, loc)
        if d > 6000: break
        if kind == "anchor" and name not in seen:
            seen.add(name); anchors.append((name, d, loc[2] - l[2]))
    for name, d, dz in anchors[:3]:
        if name == "secret wall" and d < 800:
            lines.append(f"There's a secret wall {_m(d)} m away - the skull may be in the room behind it.")
            tags.append("secret wall")
        else:
            lines.append(f"Close to {_a(name)}: {_m(d)} m away, skull is {_height(dz)}.")
        if name == "Wind Gem": tags.append("near Wind Gem")

    # props right next to it
    props = []
    for name, kind, l in sorted(things, key=lambda t: math.dist(t[2], loc)):
        if math.dist(l, loc) > 600: break
        if kind == "prop" and name not in props: props.append(name)
    if props:
        lines.append("Right beside: " + ", ".join(props[:4]) + ".")

    # Is it up high? Look at floor clutter (grass, rubble, pots...) close by horizontally and
    # within 30 m vertically, so other floors of multi-level areas don't skew it.
    near = [l[2] for n, k, l in things
            if k in ("ground", "prop") and math.dist(l[:2], loc[:2]) < 2000 and abs(l[2] - loc[2]) < 3000]
    below = [z for z in near if z <= loc[2] + 100]
    if len(near) >= 4 and below:
        gap = (loc[2] - max(below)) / 100            # drop to the nearest thing underneath/around it
        floor = statistics.median(near)
        if gap >= 6 and (loc[2] - floor) / 100 >= 6:
            lines.append(f"It's up high - about {round((loc[2] - floor) / 100)} m above the floor around it. "
                         f"Look up for a roof, ledge, pillar or treetop; you'll likely need dashes, Cestus jumps or flight.")
            tags.append("high up")
        elif (floor - loc[2]) / 100 >= 8:
            lines.append(f"It's down low - about {round((floor - loc[2]) / 100)} m below the area around it "
                         f"(pit, shaft or lower floor).")
            tags.append("down low")

    short = f"near {mon['name']}" if mon else area
    if anchors and anchors[0][1] < 4000:
        short += f", by {_a(anchors[0][0])}"
    if "high up" in tags: short += " (high up)"
    return dict(area=area, monument=mon["name"] if mon else None, short=short, details=lines, tags=tags)


FALLBACK_AREAS = {
    "100_GR": "Isle of Neasied", "130_GR_outerisles": "Isle of Neasied", "140_GR_ShopIsleOnly": "Umbada's Islet",
    "200_AQ": "Obmuer Temple", "210_AQ_underground": "Obmuer Temple", "310_LIB_exterior": "Tower of Knowledge",
    "320_LIB_basement": "Tower of Knowledge", "400_MAUS_entrance": "Deimpo Mausoleum", "420_MAUS_mid": "Deimpo Mausoleum",
    "450_MAUS_darkmaze": "Deimpo Mausoleum", "500_AUT": "Ancient World", "510_AUT_droptunnel": "Ancient World",
    "600_Castle": "Siraatsu Castle", "610_Castle_Ext": "Siraatsu Castle", "740_SZ_Prison": "Forgotten Dungeon",
    "760_SZ_AUT": "Record of Sin", "770_SZ_Swamp": "Rotting Cavern", "790_SG": "Petrified Garden", "800_FinalZone": "Final Zone",
}


def load_skulls(pak_path, progress=None):
    st = os.stat(pak_path); key = f"{DATA_VERSION}:{st.st_size}:{int(st.st_mtime)}"
    try:
        with open(CACHE_FILE, encoding="utf-8") as fh:
            c = json.load(fh)
        if c.get("key") == key: return c["skulls"]
    except (OSError, ValueError):
        pass
    skulls = scan_game(pak_path, progress)
    os.makedirs(APP_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as fh:
        json.dump({"key": key, "skulls": skulls}, fh)
    return skulls


# ------------------------------------------------------------------ save file
def read_save(path):
    with open(path, "rb") as fh:
        sv = fh.read()
    if sv[:4] != b"GVAS": raise QDError("That file isn't a Queen's Domain save.")
    key = b"SavableActorStates\0"; o = sv.find(key)
    if o < 0: raise QDError("Couldn't find pickup data in this save (the save format may have changed).")
    r = R(sv, o + len(key)); r.fstr(); r.raw(8); r.fstr(); r.fstr(); r.raw(1); r.i32()
    picked = set()
    for _ in range(r.i32()):
        picked.add(r.raw(16).hex()); r.i32()

    def named_int(name):
        k = name.encode() + b"\0"; i = sv.find(struct.pack("<i", len(k)) + k)
        return struct.unpack_from("<i", sv, i + 4 + len(k))[0] if i >= 0 else None

    k = b"SkullKeyRelic_Data.SkullKeyRelic_Data\0"; i = sv.find(k)
    held = struct.unpack_from("<i", sv, i + len(k))[0] if i >= 0 else 0
    return dict(picked=picked, turned_in=named_int("SkullsTurnedIn"), held=held)


def check(skulls, save):
    for s in skulls: s["have"] = s["guid"] in save["picked"]
    return [s for s in skulls if not s["have"]]
