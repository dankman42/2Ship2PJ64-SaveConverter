"""Draws the app icon (a low, cratered moon on a night-purple disc) as moon.png and moon.ico. Standard library only."""
import struct, zlib


def render(size, ss=4):
    n = size * ss
    px = []
    R = n / 2
    moon_c, moon_r = (n * 0.5, n * 0.5), n * 0.36
    craters = [(-0.35, -0.2, 0.17), (0.25, -0.38, 0.11), (0.28, 0.22, 0.2), (-0.12, 0.45, 0.12)]
    out = bytearray()
    for y in range(size):
        out.append(0)  # PNG filter byte
        for x in range(size):
            acc = [0, 0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    X, Y = x * ss + sx + 0.5, y * ss + sy + 0.5
                    dx, dy = X - R, Y - R
                    if dx * dx + dy * dy > (R - 0.5) ** 2:
                        continue
                    col = (0x1d, 0x0f, 0x33)
                    if dx * dx + dy * dy > (R * 0.9) ** 2:
                        col = (0xe9, 0xc4, 0x6a)  # gold rim
                    mx, my = X - moon_c[0], Y - moon_c[1]
                    d2 = mx * mx + my * my
                    if d2 < (moon_r * 1.18) ** 2 and col != (0xe9, 0xc4, 0x6a):
                        col = (0x4a, 0x21, 0x55)  # halo
                    if d2 < moon_r ** 2:
                        t = min(1, max(0, 0.5 - (mx + my) / (moon_r * 2.6)))
                        col = tuple(round(a + (b - a) * t) for a, b in zip((0xb0, 0x63, 0x2c), (0xf2, 0xb4, 0x65)))
                        for cx, cy, cr in craters:
                            ex, ey = mx - cx * moon_r, my - cy * moon_r
                            if ex * ex + ey * ey < (cr * moon_r) ** 2:
                                col = (0xc0, 0x72, 0x35)
                    acc[0] += col[0]; acc[1] += col[1]; acc[2] += col[2]; acc[3] += 255
            k = ss * ss
            a = acc[3] // k
            if a:
                out += bytes((acc[0] * 255 // acc[3], acc[1] * 255 // acc[3], acc[2] * 255 // acc[3], a))
            else:
                out += b'\0\0\0\0'
    return out


def png(size):
    raw = render(size)
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def main():
    sizes = [16, 24, 32, 48, 64, 256]
    imgs = {s: png(s) for s in sizes}
    with open('moon.png', 'wb') as f:
        f.write(imgs[64])
    head = struct.pack('<HHH', 0, 1, len(sizes))
    ofs = 6 + 16 * len(sizes)
    entries, data = b'', b''
    for s in sizes:
        d = imgs[s]
        entries += struct.pack('<BBBBHHII', s % 256, s % 256, 0, 0, 1, 32, len(d), ofs + len(data))
        data += d
    with open('moon.ico', 'wb') as f:
        f.write(head + entries + data)


if __name__ == '__main__':
    main()
