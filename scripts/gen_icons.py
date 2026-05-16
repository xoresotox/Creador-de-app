#!/usr/bin/env python3
"""Genera íconos PNG sin dependencias (zlib + struct).
Producir: web/icon-192.png, web/icon-512.png y los mipmap-* de Android.
Diseño: fondo gradiente oscuro + plato circular + tres barras de macros.
"""
import struct, zlib, os, math

def png_chunk(typ, data):
    chunk = typ + data
    crc = zlib.crc32(chunk) & 0xffffffff
    return struct.pack('>I', len(data)) + chunk + struct.pack('>I', crc)

def write_png(path, pixels, w, h):
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter: None
        for x in range(w):
            r,g,b,a = pixels[y*w + x]
            raw += bytes((r,g,b,a))
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    with open(path, 'wb') as f:
        f.write(sig)
        f.write(png_chunk(b'IHDR', ihdr))
        f.write(png_chunk(b'IDAT', idat))
        f.write(png_chunk(b'IEND', b''))

def lerp(a,b,t): return int(a + (b-a)*t)
def mix(c1, c2, t):
    return (lerp(c1[0],c2[0],t), lerp(c1[1],c2[1],t), lerp(c1[2],c2[2],t), 255)

def render(size):
    w = h = size
    pixels = [(0,0,0,0)] * (w*h)
    bg_top = (15, 18, 38)
    bg_bot = (28, 33, 72)
    accent = (108, 240, 194)
    accent2= (122, 162, 255)
    warn   = (255, 209, 102)
    plate  = (22, 26, 54)
    edge   = (38, 43, 86)

    cx = cy = w/2
    R_outer = w*0.46
    R_inner = w*0.34
    for y in range(h):
        t = y / max(1, h-1)
        bg = mix(bg_top, bg_bot, t)
        for x in range(w):
            dx = x - cx; dy = y - cy
            d  = math.sqrt(dx*dx + dy*dy)
            if d <= R_inner:
                pixels[y*w+x] = (plate[0], plate[1], plate[2], 255)
            elif d <= R_outer:
                # anillo: dividir en 3 sectores (proteína, carbohidratos, grasa)
                ang = math.atan2(dy, dx)            # -pi..pi
                ang = (ang + math.pi/2) % (2*math.pi)  # rotar inicio arriba
                third = 2*math.pi/3
                if   ang < third:        col = accent2
                elif ang < 2*third:      col = accent
                else:                    col = warn
                # bordes suaves
                e_outer = max(0.0, min(1.0, (R_outer - d)/2))
                e_inner = max(0.0, min(1.0, (d - R_inner)/2))
                a = int(255 * min(e_outer, e_inner))
                pixels[y*w+x] = (col[0], col[1], col[2], a) if a < 255 else (col[0], col[1], col[2], 255)
            else:
                pixels[y*w+x] = (bg[0], bg[1], bg[2], 255)

    # cuchara/tenedor estilizado: barra vertical en el centro inferior
    bar_w = max(2, w//40); bar_h = w//4
    bx0 = int(cx - bar_w/2); bx1 = int(cx + bar_w/2)
    by0 = int(cy - bar_h/2); by1 = int(cy + bar_h/2)
    for y in range(by0, by1):
        for x in range(bx0, bx1):
            if 0 <= x < w and 0 <= y < h:
                pixels[y*w+x] = (231, 233, 255, 255)
    return pixels, w, h

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets = [
        ('web/icon-192.png', 192),
        ('web/icon-512.png', 512),
        ('android/app/src/main/res/mipmap-mdpi/ic_launcher.png', 48),
        ('android/app/src/main/res/mipmap-hdpi/ic_launcher.png', 72),
        ('android/app/src/main/res/mipmap-xhdpi/ic_launcher.png', 96),
        ('android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png', 144),
        ('android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png', 192),
        ('android/app/src/main/res/mipmap-mdpi/ic_launcher_round.png', 48),
        ('android/app/src/main/res/mipmap-hdpi/ic_launcher_round.png', 72),
        ('android/app/src/main/res/mipmap-xhdpi/ic_launcher_round.png', 96),
        ('android/app/src/main/res/mipmap-xxhdpi/ic_launcher_round.png', 144),
        ('android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png', 192),
    ]
    for rel, size in targets:
        out = os.path.join(base, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pixels, w, h = render(size)
        write_png(out, pixels, w, h)
        print(f'Wrote {rel} ({size}x{size})')

if __name__ == '__main__':
    main()
