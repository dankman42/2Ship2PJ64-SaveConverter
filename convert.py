"""Convert a 2Ship2Harkinian JSON save (file1.json) into an N64 Majora's Mask (US) FlashRAM image.

Usage:
  python convert.py <input.json> [<output.fla>] [--file 1|2]

Without an output path, "ZELDA MAJORA'S MASK.fla" is written next to the input file.
The slot defaults to the number in the file name (file2.json -> slot 2), otherwise slot 1.
The 2ship-to-pj64 app (gui.py) uses the same code and can also merge into an existing save file.
Writes the image in Project64's word-swapped byte order (and a big-endian copy next to it).
"""
import json, os, re, shutil, struct, sys, time

def u8(v): return struct.pack('>B', v & 0xFF)
def s8(v): return struct.pack('>b', v)
def u16(v): return struct.pack('>H', v & 0xFFFF)
def s16(v): return struct.pack('>h', v)
def u32(v): return struct.pack('>I', v & 0xFFFFFFFF)
def s32(v): return struct.pack('>i', v)
def u64(v): return struct.pack('>Q', v & 0xFFFFFFFFFFFFFFFF)
def chars(lst): return bytes(c & 0xFF for c in lst)


def player_data(p):
    b = chars(p['newf']) + u16(p['threeDayResetCount']) + chars(p['playerName'])
    b += s16(p['healthCapacity']) + s16(p['health']) + s8(p['magicLevel']) + s8(p['magic'])
    b += s16(p['rupees']) + u16(p['swordHealth']) + u16(p['tatlTimer'])
    b += u8(p['isMagicAcquired']) + u8(p['isDoubleMagicAcquired']) + u8(p['doubleDefense']) + u8(p['unk_1F'])
    b += u8(p['unk_20']) + b'\0' + u16(p['owlActivationFlags']) + u8(p['unk_24']) + b'\0' + s16(p['savedSceneId'])
    assert len(b) == 0x28
    return b


def equips(e):
    b = b''.join(chars(r) for r in e['buttonItems']) + b''.join(chars(r) for r in e['cButtonSlots'])
    b += u16(e['equipment'])
    assert len(b) == 0x22
    return b


def inventory(i):
    b = chars(i['items']) + b''.join(s8(a) for a in i['ammo'])
    b += u32(i['upgrades']) + u32(i['questItems']) + chars(i['dungeonItems'])
    b += b''.join(s8(k) for k in i['dungeonKeys']) + s8(i['defenseHearts'])
    b += b''.join(s8(f) for f in i['strayFairies'])
    b += b''.join(chars(n) for n in i['dekuPlaygroundPlayerName'])
    b += b'\0\0'  # pad to 0x88
    assert len(b) == 0x88, hex(len(b))
    return b


def save_info(s):
    b = player_data(s['playerData'])
    b += equips(s['equips']) + b'\0\0'  # 0x22 bytes + pad so Inventory starts at 0x4C
    b += inventory(s['inventory'])
    assert len(b) == 0xD4
    for f in s['permanentSceneFlags']:
        for k in ('chest', 'switch0', 'switch1', 'clearedRoom', 'collectible', 'unk_14', 'rooms'):
            b += u32(f[k])
    assert len(b) == 0xDF4
    b += chars(s['unk_DF4'])
    b += b''.join(u32(x) for x in s['dekuPlaygroundHighScores'])
    b += u32(s['pictoFlags0']) + u32(s['pictoFlags1']) + u32(s['unk_E5C']) + u32(s['unk_E60'])
    b += b''.join(u32(x) for x in s['unk_E64'])
    b += b''.join(u32(x) for x in s['scenesVisible'])
    b += u32(s['skullTokenCount']) + u32(s['unk_EA0']) + u32(s['unk_EA4'])
    b += b''.join(u32(x) for x in s['unk_EA8'])
    b += u32(s['stolenItems']) + u32(s['unk_EB4'])
    b += b''.join(u32(x) for x in s['highScores'])
    assert len(b) == 0xED4, hex(len(b))
    b += chars(s['weekEventReg'])
    b += u32(s['regionsVisited']) + u32(s['worldMapCloudVisibility'])
    assert len(b) == 0xF40
    b += u8(s['unk_F40']) + u8(s['scarecrowSpawnSongSet']) + chars(s['scarecrowSpawnSong'])
    b += s8(s['bombersCaughtNum']) + b''.join(s8(x) for x in s['bombersCaughtOrder'])
    b += b''.join(b''.join(s8(x) for x in row) for row in s['lotteryCodes'])
    b += b''.join(s8(x) for x in s['spiderHouseMaskOrder'])
    b += b''.join(s8(x) for x in s['bomberCode'])
    assert len(b) == 0xFDC
    h = s['horseData']
    b += s16(h['sceneId']) + s16(int(h['pos']['x'])) + s16(int(h['pos']['y'])) + s16(int(h['pos']['z'])) + s16(h['yaw'])
    b += u16(0)  # checksum placeholder
    assert len(b) == 0xFE8
    return b


def save(sv):
    b = s32(sv['entrance']) + u8(sv['equippedMask']) + u8(sv['isFirstCycle']) + u8(sv['unk_06']) + u8(sv['linkAge'])
    b += s32(sv['cutsceneIndex']) + u16(sv['time']) + u16(sv['owlSaveLocation'])
    b += s32(sv['isNight']) + s32(sv['timeSpeedOffset']) + s32(sv['day']) + s32(sv['eventDayCount'])
    b += u8(sv['playerForm']) + u8(sv['snowheadCleared']) + u8(sv['hasTatl']) + u8(sv['isOwlSave'])
    assert len(b) == 0x24
    b += save_info(sv['saveInfo'])
    assert len(b) == 0x100C
    return bytearray(b)


def owl_context(o):
    b = save(o['save'])
    b += chars(o['eventInf']) + u8(o['unk_1014']) + u8(o['bButtonStatus']) + u16(o['jinxTimer'])
    b += s16(o['rupeeAccumulator']) + chars(o['bottleTimerStates'])
    assert len(b) == 0x1020
    for k in ('bottleTimerStartOsTimes', 'bottleTimerTimeLimits', 'bottleTimerCurTimes', 'bottleTimerPausedOsTimes'):
        b += b''.join(u64(x) for x in o[k])
    assert len(b) == 0x10E0
    b += chars(o['pictoPhotoI5'])
    assert len(b) == 0x3CA0, hex(len(b))
    return b


CHECKSUM_OFS = 0x24 + 0xFE6
FLASH_SIZE = 0x20000
OUT_NAME = "ZELDA MAJORA'S MASK.fla"
OPTIONS_OFS = (0x18000, 0x1C000)
OPTIONS_ID = b'\xA5\x1D'
# Per slot: the Song of Time save (main + backup copy, 0x4000 bytes) and the owl save (main + backup, 0x8000 bytes)
NEW_CYCLE_OFS = {1: 0x0000, 2: 0x4000}
OWL_OFS = {1: 0x8000, 2: 0x10000}


def finalize(buf):
    """Write the game's checksum (16-bit byte sum, computed with the field zeroed). Returns it."""
    buf[CHECKSUM_OFS:CHECKSUM_OFS + 2] = b'\0\0'
    c = sum(buf) & 0xFFFF
    buf[CHECKSUM_OFS:CHECKSUM_OFS + 2] = u16(c)
    return c


def word_swap(data):
    """Reverse every 4-byte word. Converts between cartridge order and Project64's order (both directions)."""
    out = bytearray(len(data))
    for i in range(0, len(data) - len(data) % 4, 4):
        out[i:i + 4] = data[i:i + 4][::-1]
    return out


def load_save(path):
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    if not isinstance(d, dict) or d.get('type') != '2S2H_SAVE':
        raise ValueError('this is not a 2Ship2Harkinian save file')
    return d


def slot_from_filename(path):
    """file2.json / file2backup.json -> 2, anything else -> 1."""
    m = re.match(r'file([12])', os.path.basename(path), re.I)
    return int(m.group(1)) if m else 1


# ---- reading names and stats, for showing what's in a save ----

def decode_name(raw):
    s = ''
    for c in raw:
        if c <= 0x09: s += chr(ord('0') + c)
        elif c <= 0x23: s += chr(ord('A') + c - 0x0A)
        elif c <= 0x3D: s += chr(ord('a') + c - 0x24)
        elif c == 0x3E: s += ' '
        elif c == 0x40: s += '.'
        elif c == 0x3F: s += '-'
        else: s += '?'
    return s.strip() or '(no name)'


def describe_json(d):
    """Short facts about a 2Ship save, for the preview panel."""
    owl = d.get('owlSave')
    has_owl = bool(owl and owl['save'].get('isOwlSave'))
    # Describe the save the player will actually load: the owl save if there is one.
    cur = owl['save'] if has_owl else d['newCycleSave']['save']
    p = cur['saveInfo']['playerData']
    inv = cur['saveInfo']['inventory']
    info = {
        'name': decode_name(p['playerName']),
        'hearts': p['healthCapacity'] / 16,
        'masks': sum(1 for x in inv['items'][24:48] if x != 255),
        'rupees': p['rupees'],
        'cycles': p['threeDayResetCount'],
        'owl': has_owl,
    }
    if has_owl:
        s = owl['save']
        mins = s['time'] * 24 * 60 // 0x10000
        info['owl_day'] = s['day']
        info['owl_time'] = f'{mins // 60:02d}:{mins % 60:02d}'
    return info


def to_native(raw, assume_pj64=True):
    """Return (cartridge-order flash image, detected format) for an existing .fla file."""
    data = bytearray(raw[:FLASH_SIZE]) + bytearray(max(0, FLASH_SIZE - len(raw)))
    swapped = word_swap(data)
    for ofs in OPTIONS_OFS + (0x24, 0x4024, 0x8024, 0x10024):
        if data[ofs:ofs + 2] == OPTIONS_ID or data[ofs:ofs + 6] == b'ZELDA3':
            return data, 'big-endian'
        if swapped[ofs:ofs + 2] == OPTIONS_ID or swapped[ofs:ofs + 6] == b'ZELDA3':
            return swapped, 'project64'
    return (swapped, 'project64') if assume_pj64 else (data, 'big-endian')


def describe_flash(native):
    """What each slot of a cartridge-order flash image holds: {1: str, 2: str}."""
    out = {}
    for slot in (1, 2):
        parts = []
        for ofs, kind in ((NEW_CYCLE_OFS[slot], ''), (OWL_OFS[slot], 'owl')):
            for copy in (0, 0x2000 if not kind else 0x4000):
                base = ofs + copy
                if native[base + 0x24:base + 0x2A] == b'ZELDA3':
                    name = decode_name(native[base + 0x2C:base + 0x34])
                    parts.append(f'{name}, owl save' if kind else name)
                    break
        if not parts:
            out[slot] = 'empty'
        elif len(parts) == 2 and parts[1].startswith(parts[0]):
            out[slot] = parts[1]
        else:
            out[slot] = parts[0]
    return out


# ---- building and writing ----

def build_slot(d, flash, slot):
    """Write save `d` into `flash` (cartridge order) at `slot`, replacing whatever was there. Returns checksums."""
    if slot not in (1, 2):
        raise ValueError('file slot must be 1 or 2')
    nc_ofs, owl_ofs = NEW_CYCLE_OFS[slot], OWL_OFS[slot]
    flash[nc_ofs:nc_ofs + 0x4000] = bytes(0x4000)
    flash[owl_ofs:owl_ofs + 0x8000] = bytes(0x8000)

    nc = d['newCycleSave']['save']
    ncb = save(nc)
    sums = {'new-cycle save': (finalize(ncb), nc['saveInfo']['checksum'])}
    flash[nc_ofs:nc_ofs + len(ncb)] = ncb
    flash[nc_ofs + 0x2000:nc_ofs + 0x2000 + len(ncb)] = ncb

    o = d.get('owlSave')
    if o and o['save'].get('isOwlSave'):
        ob = owl_context(o)
        sums['owl save'] = (finalize(ob), o['save']['saveInfo']['checksum'])
        flash[owl_ofs:owl_ofs + len(ob)] = ob
        flash[owl_ofs + 0x4000:owl_ofs + 0x4000 + len(ob)] = ob

    for ofs in OPTIONS_OFS:
        if flash[ofs:ofs + 2] != OPTIONS_ID:
            flash[ofs:ofs + 6] = OPTIONS_ID + u8(1) + u8(0) + u8(0) + u8(0)
    return sums


def write_flash(d, dst, slot, pj64=True, merge=True, backup=True, bigendian_copy=False):
    """Convert save `d` into slot `slot` of `dst`. Returns a dict describing what happened."""
    result = {'path': dst, 'backup': None, 'merged': False, 'extra': None}
    flash = bytearray(FLASH_SIZE)
    if os.path.exists(dst):
        with open(dst, 'rb') as f:
            raw = f.read()
        if backup:
            stamp = time.strftime('%Y-%m-%d_%H%M%S')
            result['backup'] = f'{dst}.{stamp}.bak'
            n = 2
            while os.path.exists(result['backup']):
                result['backup'] = f'{dst}.{stamp}-{n}.bak'
                n += 1
            shutil.copy2(dst, result['backup'])
        if merge:
            flash, _ = to_native(raw, assume_pj64=pj64)
            result['merged'] = True
    result['checksums'] = build_slot(d, flash, slot)
    with open(dst, 'wb') as f:
        f.write(word_swap(flash) if pj64 else flash)
    if bigendian_copy:
        result['extra'] = dst.rsplit('.', 1)[0] + '.bigendian.fla'
        with open(result['extra'], 'wb') as f:
            f.write(flash)
    result['slots'] = describe_flash(flash)
    return result


def main():
    """Command line: python convert.py <input.json> [<output.fla>] [--file 1|2]"""
    args = sys.argv[1:]
    slot = None
    if '--file' in args:
        i = args.index('--file'); slot = int(args[i + 1]); del args[i:i + 2]
    if not args:
        print(__doc__)
        sys.exit(2)
    src = args[0]
    dst = args[1] if len(args) > 1 else os.path.join(os.path.dirname(os.path.abspath(src)), OUT_NAME)
    slot = slot or slot_from_filename(src)
    try:
        d = load_save(src)
        print(f'Converting {src}  ->  file slot {slot}')
        r = write_flash(d, dst, slot, merge=False, backup=False, bigendian_copy=True)
    except Exception as e:
        print(f'Conversion failed: {e!r}')
        sys.exit(1)
    for label, (mine, theirs) in r['checksums'].items():
        print(f'{label}: checksum {mine} (2Ship stored {theirs})')
    print('Wrote', r['path'])
    print('  and', r['extra'])


if __name__ == '__main__':
    main()
