#!/usr/bin/env python3
"""Rebuild assets/logo-hsabli.png and assets/logo-icon.png from assets/source-logo.png (remove checkerboard)."""
from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "source-logo.png"
OUT_FULL = ROOT / "assets" / "logo-hsabli.png"


def walkable_edge(r: int, g: int, b: int) -> bool:
    mx, mn = max(r, g, b), min(r, g, b)
    if mx < 85 and (mx - mn) < 18:
        return True
    if mn >= 188 and (mx - mn) <= 14:
        return True
    return False


def achromatic(r: int, g: int, b: int, tol: int = 20) -> bool:
    return max(r, g, b) - min(r, g, b) <= tol


def bright_achromatic(r: int, g: int, b: int) -> bool:
    if not achromatic(r, g, b, tol=20):
        return False
    return min(r, g, b) >= 165


def achromatic_neighbors(px, w: int, h: int, x: int, y: int) -> int:
    c = 0
    for nx in range(max(0, x - 1), min(w, x + 2)):
        for ny in range(max(0, y - 1), min(h, y + 2)):
            if nx == x and ny == y:
                continue
            r, g, b = px[nx, ny]
            if bright_achromatic(r, g, b):
                c += 1
    return c


def main() -> None:
    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    px = im.load()

    seen = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            r, g, b = px[x, y]
            if walkable_edge(r, g, b) and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            r, g, b = px[x, y]
            if walkable_edge(r, g, b) and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                r, g, b = px[nx, ny]
                if walkable_edge(r, g, b):
                    seen[ny][nx] = True
                    q.append((nx, ny))

    out = Image.new("RGBA", (w, h))
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if seen[y][x]:
                opx[x, y] = (0, 0, 0, 0)
                continue
            if bright_achromatic(r, g, b) and achromatic_neighbors(px, w, h, x, y) >= 4:
                opx[x, y] = (0, 0, 0, 0)
                continue
            opx[x, y] = (r, g, b, 255)

    OUT_FULL.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT_FULL, optimize=True)

    y2 = int(h * 0.55)
    sub = out.crop((0, 0, w, y2))
    bbox = sub.split()[-1].getbbox()
    if bbox:
        icon = sub.crop(bbox)
        icon.save(ROOT / "assets" / "logo-icon.png", optimize=True)
    print("Wrote", OUT_FULL, "and logo-icon.png")


if __name__ == "__main__":
    main()
