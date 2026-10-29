#!/usr/bin/env python3
"""Control de escritorio con pocos tokens: win | find T | click T | shot [escala]."""
import json, os, shutil, subprocess as sp, sys

D = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
PKG = {"grim": "grim", "hyprctl": "hyprland", "tesseract": "tesseract tesseract-data-spa",
       "ydotool": "ydotool"}


def die(msg):
    print(msg)
    sys.exit(1)


def run(*cmd):
    if not shutil.which(cmd[0]):
        die(f"falta {cmd[0]}: sudo pacman -S {PKG.get(cmd[0], cmd[0])}")
    r = sp.run(cmd, capture_output=True, text=True)
    if r.returncode:
        die(f"{cmd[0]} falló: " + (r.stderr.strip().split("\n")[0] or f"código {r.returncode}"))
    return r.stdout


def win():
    try:
        w = json.loads(run("hyprctl", "-j", "activewindow"))
    except ValueError:
        die("sin ventana activa")
    if not w.get("size"):
        die("sin ventana activa")
    return w


def geom(w):
    return f"{w['at'][0]},{w['at'][1]} {w['size'][0]}x{w['size'][1]}"


def grab(scale, w, path):
    if os.path.exists(path):
        os.remove(path)
    run("grim", "-s", str(scale), "-g", geom(w), path)


def norm(s):
    return s.strip(".,:;()!?\"'").lower()


def find(text):
    w = win()
    img = os.path.join(D, "pc_ocr.png")
    grab(2, w, img)
    rows = [l.split("\t") for l in run("tesseract", img, "-", "-l", "spa+eng", "tsv").split("\n")[1:]]
    rows = [r for r in rows if len(r) == 12 and r[11].strip()]
    words, out = [norm(x) for x in text.split()], []
    for i, r in enumerate(rows):
        seq = rows[i:i + len(words)]
        if len(seq) == len(words) and all(s[2:5] == r[2:5] and x in norm(s[11])
                                          for s, x in zip(seq, words)):
            e = seq[-1]
            l, t, h = int(r[6]) / 2, int(r[7]) / 2, int(r[9]) / 2
            wd = (int(e[6]) + int(e[8])) / 2 - l
            exact = all(x == norm(s[11]) for s, x in zip(seq, words))
            out.append((not exact, round(w["at"][0] + l + wd / 2), round(w["at"][1] + t + h / 2)))
    if not out:
        die("no encontrado")
    return [(x, y) for _, x, y in sorted(out, key=lambda o: o[0])][:3]


def main():
    a = sys.argv[1:]
    if not a or a[0] not in ("win", "find", "click", "shot"):
        die('uso: pc.py win | find "texto" | click "texto" | shot [escala]')
    if a[0] in ("find", "click") and (len(a) < 2 or not a[1].strip()):
        die("texto vacío")
    if a[0] == "win":
        w = win()
        print(f"{w['class']} | {w['title']} | {w['at'][0]},{w['at'][1]} {w['size'][0]}x{w['size'][1]}")
    elif a[0] == "find":
        print("\n".join(f"{x},{y}" for x, y in find(a[1])))
    elif a[0] == "click":
        x, y = find(a[1])[0]
        run("hyprctl", "dispatch", "movecursor", str(x), str(y))
        run("ydotool", "click", "0xC0")
        print(f"ok {x},{y}")
    else:
        p = os.path.join(D, "pc_shot.png")
        grab(a[1] if len(a) > 1 else "0.5", win(), p)
        print(p)


main()
