import os
import argparse
from pathlib import Path
from typing import List, Tuple

import fitz  # PyMuPDF
from PIL import Image
from tqdm import tqdm


IMG_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".jfif", ".heic"}
PDF_EXTS = {".pdf"}

def list_files(folder: Path) -> List[Path]:
    files = []
    for p in folder.rglob("*"):
        if p.is_file():
            ext = p.suffix.lower()
            if ext in IMG_EXTS or ext in PDF_EXTS:
                files.append(p)
    return sorted(files)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
    

def convert_pdf_to_pngs(pdf_path: Path, out_dir: Path, dpi: int=300) -> List[Path]:
    """
    Convert PDF pages to PNG images using PyMuPDF.
    """
    ensure_dir(out_dir)
    doc = fitz.open(str(pdf_path))
    outputs = []
    
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    
    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path = out_dir / f"{pdf_path.stem}_p{page_index+1:02d}.png"
        pix.save(str(out_path))
        outputs.append(out_path)

    doc.close()
    return outputs

def convert_image_to_png(img_path: Path, out_path: Path) -> Path:
    ensure_dir(out_path.parent)
    img = Image.open(img_path).convert("RGB")
    img.save(out_path, format="PNG", optimize=True)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_root", type=str, default="idu_data/raw", help="raw root with invoice/contract/form")
    ap.add_argument("--out_root", type=str, default="idu_data/images", help="output root for PNG images")
    ap.add_argument("--dpi", type=int, default=300, help="PDF render DPI")
    args = ap.parse_args()

    raw_root = Path(args.raw_root)
    out_root = Path(args.out_root)
    dpi = args.dpi

    classes = ["invoice", "contract", "form"]

    for cls in classes:
        in_dir = raw_root / cls
        if not in_dir.exists():
            print(f"[WARN] Missing folder: {in_dir}")
            continue

        files = list_files(in_dir)
        if not files:
            print(f"[WARN] No files found in: {in_dir}")
            continue

        out_dir = out_root / cls
        ensure_dir(out_dir)

        print(f"\n[INFO] Converting {cls}: {len(files)} files")
        for f in tqdm(files):
            ext = f.suffix.lower()
            if ext in PDF_EXTS:
                # Each PDF becomes multiple page images
                convert_pdf_to_pngs(f, out_dir, dpi=dpi)
            else:
                # Image → PNG
                out_path = out_dir / f"{f.stem}.png"
                convert_image_to_png(f, out_path)

    print("\n[DONE] Conversion finished.")
    print(f"Output: {out_root}")


if __name__ == "__main__":
    main()