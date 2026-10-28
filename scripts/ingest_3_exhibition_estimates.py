# -*- coding: utf-8 -*-
"""
3대 실제 전시 견적서 인제스트 & 최적화 스크립트
1. 2026 WIS 완료견적서 (200평 이상)
2. 2026 8월 갤럭시 스튜디오 견적서 (100평 규모)
3. 2025 KES 한국전자전 견적서 (300평 이상)
"""

import os
import sys
import io
import shutil
import zipfile
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
IMAGES_DIR = DATA_DIR / "learned_images"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

SRC_DIR = Path(r"C:\Users\ws081\OneDrive\Desktop\정승우\AX대회관련")

TARGETS = [
    {
        "src_name": "(송부) 2026 WIS 완료견적서 수정_260624_청구 fin.xlsx",
        "dst_name": "2026_WIS_전시제작_완료견적서.xlsx",
        "max_img_dim": 800,
        "quality": 65
    },
    {
        "src_name": "01. 8월 갤럭시스튜디오_0829_견적서.xlsx",
        "dst_name": "2026_8월_갤럭시스튜디오_완료견적서.xlsx",
        "max_img_dim": 800,
        "quality": 65
    },
    {
        "src_name": "251117_2025 KES 한국전자전_전시 제작 견적서.xlsx",
        "dst_name": "2025_KES_한국전자전_전시제작견적서.xlsx",
        "max_img_dim": 800,
        "quality": 60
    }
]

def optimize_and_copy_xlsx(src_path: Path, dst_path: Path, max_dim: int = 800, quality: int = 65):
    print(f"Processing {src_path.name} ({src_path.stat().st_size / 1024 / 1024:.2f} MB)...")
    out_buf = io.BytesIO()

    with zipfile.ZipFile(src_path, 'r') as zin:
        with zipfile.ZipFile(out_buf, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                fname_lower = item.filename.lower()
                
                # Check if it's an embedded image in xl/media
                if 'media/' in fname_lower and any(fname_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    try:
                        img = Image.open(io.BytesIO(data))
                        img.thumbnail((max_dim, max_dim))
                        c_buf = io.BytesIO()
                        if img.mode in ('RGBA', 'P') and fname_lower.endswith('.png'):
                            img.save(c_buf, format='PNG', optimize=True)
                        else:
                            img = img.convert('RGB')
                            img.save(c_buf, format='JPEG', quality=quality, optimize=True)
                        c_data = c_buf.getvalue()
                        zout.writestr(item, c_data)
                    except Exception as e:
                        zout.writestr(item, data)
                else:
                    zout.writestr(item, data)

    final_bytes = out_buf.getvalue()
    dst_path.write_bytes(final_bytes)
    print(f"  -> Saved {dst_path.name}: {len(final_bytes) / 1024 / 1024:.2f} MB")

def main():
    for t in TARGETS:
        src = SRC_DIR / t["src_name"]
        if not src.exists():
            print(f"ERROR: {src} does not exist!")
            continue

        dst_data = DATA_DIR / t["dst_name"]
        dst_sample = SAMPLES_DIR / t["dst_name"]

        optimize_and_copy_xlsx(src, dst_sample, t["max_img_dim"], t["quality"])
        shutil.copy2(dst_sample, dst_data)
        print(f"  -> Synced to data/ and data/samples/")

    # Copy real images if present
    img_kes = SRC_DIR / "2025 KES.png"
    if img_kes.exists():
        target_kes_img = IMAGES_DIR / "2025_KES_MEGA.png"
        shutil.copy2(img_kes, target_kes_img)
        print(f"Copied KES image: {target_kes_img} ({target_kes_img.stat().st_size / 1024:.1f} KB)")

    img_hyundai = SRC_DIR / "더현대.jpg"
    if img_hyundai.exists():
        target_hyundai_img = IMAGES_DIR / "GALAXY_AUG_HYUNDAI.jpg"
        shutil.copy2(img_hyundai, target_hyundai_img)
        print(f"Copied Hyundai image: {target_hyundai_img} ({target_hyundai_img.stat().st_size / 1024:.1f} KB)")

    # Extract an image for WIS from its media if available
    wis_sample = SAMPLES_DIR / "2026_WIS_전시제작_완료견적서.xlsx"
    target_wis_img = IMAGES_DIR / "2026_WIS_COEX.png"
    if wis_sample.exists() and not target_wis_img.exists():
        with zipfile.ZipFile(wis_sample, 'r') as z:
            media_pngs = [m for m in z.infolist() if m.filename.startswith("xl/media/") and m.filename.endswith(".png")]
            if media_pngs:
                # pick a decent sized one
                media_pngs.sort(key=lambda x: x.file_size, reverse=True)
                target_wis_img.write_bytes(z.read(media_pngs[0].filename))
                print(f"Extracted WIS image: {target_wis_img} ({target_wis_img.stat().st_size / 1024:.1f} KB)")

    print("All 3 files processed successfully!")

if __name__ == "__main__":
    main()
