# tools/convert_to_webp.py
from PIL import Image
from pathlib import Path

# === CONFIG ===
CANDIDATES = [
    "imghome1.jpg",
    "imghome2.jpg",
    "landmarks.jpg",
    "static/imgfront.jpg",
    "static/anniversary13.jpg",
    # adicione mais caminhos se quiser...
]

GENERATE_SCALES = [1280, 768]   # [] para desativar tamanhos extras
PHOTO_QUALITY   = 82            # 75–85 é um bom intervalo
WEBP_METHOD     = 6             # 0=rápido, 6=melhor compressão

def has_alpha(img: Image.Image) -> bool:
    return img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

def to_webp(src: Path, dst: Path | None = None, max_width: int | None = None):
    if not src.exists():
        print(f"[skip] não encontrado: {src}")
        return
    if src.suffix.lower() == ".svg":
        print(f"[skip] svg não é suportado pelo Pillow: {src.name}")
        return

    img = Image.open(src)
    alpha = has_alpha(img)

    # resize opcional
    if max_width and img.width > max_width:
        img.thumbnail((max_width, 10_000), Image.LANCZOS)

    if dst is None:
        dst = src.with_suffix(".webp")

    # já atualizado?
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        print(f"[ok] já atualizado: {dst.name}")
        return

    save_args = {"method": WEBP_METHOD}
    if alpha or src.suffix.lower() == ".png":
        img = img.convert("RGBA")
        save_args["lossless"] = True
    else:
        img = img.convert("RGB")
        save_args["quality"] = PHOTO_QUALITY

    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "WEBP", **save_args)
    print(f"[ok] {src.name} -> {dst.name} ({img.width}x{img.height})")

def main():
    root = Path(__file__).resolve().parent.parent
    for rel in CANDIDATES:
        p = (root / rel).resolve()
        if not p.exists():
            print(f"[warn] não encontrado: {rel}")
            continue
        to_webp(p)
        for w in GENERATE_SCALES:
            to_webp(p, dst=p.with_name(f"{p.stem}-{w}.webp"), max_width=w)

if __name__ == "__main__":
    main()
