"""
Minimal read-only parser for Unreal Engine 4.27 GVAS save files (Queen's Domain).

parse(path) -> dict of top-level properties, values converted to plain Python:
  ints/floats/bools/strings, lists, dicts (maps), sets -> lists, structs -> dicts,
  Guid -> hex string, Vector/Rotator/Quat -> tuples, DateTime -> int ticks.
Anything it can't decode is skipped using the size in the property tag.
"""
import struct


class Reader:
    def __init__(self, data, pos=0):
        self.b, self.o = data, pos

    def take(self, n):
        v = self.b[self.o:self.o + n]
        if len(v) != n:
            raise EOFError
        self.o += n
        return v

    def i8(self): return self.take(1)[0]
    def i32(self): return struct.unpack("<i", self.take(4))[0]
    def u32(self): return struct.unpack("<I", self.take(4))[0]
    def i64(self): return struct.unpack("<q", self.take(8))[0]
    def f32(self): return struct.unpack("<f", self.take(4))[0]
    def f64(self): return struct.unpack("<d", self.take(8))[0]

    def fstr(self):
        n = self.i32()
        if n == 0:
            return ""
        if n < 0:
            if -n > 1 << 20:
                raise ValueError("bad string length")
            return self.take(-n * 2).decode("utf-16-le")[:-1]
        if n > 1 << 20:
            raise ValueError("bad string length")
        return self.take(n)[:-1].decode("latin-1")

    def looks_like_name(self):
        """Is the next thing a property name (short ASCII FString)?"""
        try:
            n = struct.unpack_from("<i", self.b, self.o)[0]
            if not 2 <= n <= 256:
                return False
            s = self.b[self.o + 4:self.o + 4 + n]
            return s[-1] == 0 and all(32 < c < 127 for c in s[:-1])
        except (struct.error, IndexError):
            return False


# structs with a fixed native layout (everything else is a tagged property list)
NATIVE = {
    "Vector": lambda r: struct.unpack("<3f", r.take(12)),
    "Rotator": lambda r: struct.unpack("<3f", r.take(12)),
    "Vector2D": lambda r: struct.unpack("<2f", r.take(8)),
    "Quat": lambda r: struct.unpack("<4f", r.take(16)),
    "LinearColor": lambda r: struct.unpack("<4f", r.take(16)),
    "Color": lambda r: tuple(r.take(4)),
    "IntPoint": lambda r: struct.unpack("<2i", r.take(8)),
    "Guid": lambda r: r.take(16).hex(),
    "DateTime": lambda r: r.i64(),
    "Timespan": lambda r: r.i64(),
}


def read_props(r, end=None):
    out = {}
    while end is None or r.o < end:
        name = r.fstr()
        if name == "None" or name == "":
            break
        typ = r.fstr()
        size = r.i64()
        val = read_tagged_value(r, typ, size)
        if name in out:  # static arrays repeat the name
            if not isinstance(out[name], _Multi):
                out[name] = _Multi([out[name]])
            out[name].append(val)
        else:
            out[name] = val
    return out


class _Multi(list):
    pass


def read_tagged_value(r, typ, size):
    if typ == "BoolProperty":
        v = bool(r.i8()); r.i8()
        return v
    if typ == "StructProperty":
        st = r.fstr(); r.take(16); r.i8()
        start = r.o
        try:
            return read_struct(r, st, start + size)
        finally:
            r.o = start + size
    if typ in ("ByteProperty", "EnumProperty"):
        enum = r.fstr(); r.i8()
        if typ == "ByteProperty" and enum == "None" and size == 1:
            return r.i8()
        start = r.o
        v = r.fstr()
        r.o = start + size
        return v
    if typ == "ArrayProperty":
        inner = r.fstr(); r.i8(); start = r.o
        try:
            return read_array(r, inner, start + size)
        except Exception:
            return None
        finally:
            r.o = start + size
    if typ == "SetProperty":
        inner = r.fstr(); r.i8(); start = r.o
        try:
            r.i32()  # removed
            return [read_value(r, inner, start + size) for _ in range(r.i32())]
        except Exception:
            return None
        finally:
            r.o = start + size
    if typ == "MapProperty":
        kt, vt = r.fstr(), r.fstr(); r.i8(); start = r.o
        try:
            r.i32()  # removed
            m = {}
            for _ in range(r.i32()):
                k = read_value(r, kt, start + size, key=True)
                m[_hashable(k)] = read_value(r, vt, start + size)
            return m
        except Exception:
            return None
        finally:
            r.o = start + size
    r.i8()  # no guid
    start = r.o
    try:
        return read_value(r, typ, start + size)
    except Exception:
        return None
    finally:
        r.o = start + size


def _hashable(v):
    if isinstance(v, dict):
        return tuple(sorted((k, _hashable(x)) for k, x in v.items()))
    if isinstance(v, list):
        return tuple(_hashable(x) for x in v)
    return v


def read_value(r, typ, end, key=False):
    """A bare value (inside arrays / sets / maps)."""
    if typ == "IntProperty": return r.i32()
    if typ == "UInt32Property": return r.u32()
    if typ == "Int64Property": return r.i64()
    if typ == "FloatProperty": return r.f32()
    if typ == "DoubleProperty": return r.f64()
    if typ == "BoolProperty": return bool(r.i8())
    if typ == "ByteProperty":
        return r.i8() if end - r.o == 1 else r.fstr()
    if typ in ("StrProperty", "NameProperty", "ObjectProperty", "EnumProperty"):
        return r.fstr()
    if typ == "SoftObjectProperty":
        v = r.fstr(); r.fstr()
        return v
    if typ == "TextProperty":
        return read_text(r)
    if typ == "StructProperty":
        # untyped struct: property list if it looks like one, else a Guid
        if r.looks_like_name():
            return read_props(r, end)
        return NATIVE["Guid"](r)
    if typ == "MulticastInlineDelegateProperty":
        out = []
        for _ in range(r.i32()):
            out.append((r.fstr(), r.fstr()))
        return out
    raise ValueError(f"unsupported {typ}")


def read_text(r):
    r.u32()  # flags
    ht = r.i8()
    if ht == 255:
        return r.fstr() if r.i32() else ""
    if ht == 0:
        r.fstr(); r.fstr()
        return r.fstr()
    raise ValueError("unsupported text")


def read_struct(r, st, end):
    if st in NATIVE:
        return NATIVE[st](r)
    return read_props(r, end)


def read_array(r, inner, end):
    n = r.i32()
    if inner == "StructProperty":
        r.fstr(); r.fstr(); r.i64()
        st = r.fstr(); r.take(16); r.i8()
        return [read_struct(r, st, end) for _ in range(n)]
    if inner == "ByteProperty" and end - r.o == n:
        return r.take(n)
    return [read_value(r, inner, end) for _ in range(n)]


def parse_bytes(data):
    if data[:4] != b"GVAS":
        raise ValueError("not a GVAS save file")
    r = Reader(data, 4)
    r.i32(); r.i32()                       # save game version, package version
    r.take(6); r.u32(); r.fstr()           # engine version + branch
    r.i32()                                # custom version format
    for _ in range(r.i32()):
        r.take(20)
    save_class = r.fstr()
    props = read_props(r)
    props["__class__"] = save_class
    return props


def parse(path):
    with open(path, "rb") as fh:
        return parse_bytes(fh.read())
