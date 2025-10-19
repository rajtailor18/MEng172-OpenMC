#!/usr/bin/env python3
import argparse
import os
import sys
import tarfile
import urllib.request
from pathlib import Path

URL = "https://zenodo.org/records/8410375/files/endfb80-lowtemp.tar.xz?download=1"

def human(n):
    for unit in ("B","KB","MB","GB","TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"

def download(url, dst):
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(f"==> Downloading {url}\n    -> {dst}")

    def hook(blocks, block_size, total_size):
        if total_size <= 0:
            return
        done = min(blocks * block_size, total_size)
        pct = done / total_size * 100
        bar_len = 30
        filled = int(bar_len * done / total_size)
        bar = "#" * filled + "-" * (bar_len - filled)
        end = "\r" if done < total_size else "\n"
        print(f"[{bar}] {pct:6.2f}%  {human(done)}/{human(total_size)}", end=end, flush=True)

    urllib.request.urlretrieve(url, dst, reporthook=hook)  # noqa: S310

def append_export_to_bashrc(line):
    bashrc = Path.home() / ".bashrc"
    existing = bashrc.read_text() if bashrc.exists() else ""
    if line not in existing:
        with bashrc.open("a") as f:
            f.write("\n" + line + "\n")

def main():
    p = argparse.ArgumentParser(description="Download and set OPENMC_CROSS_SECTIONS")
    p.add_argument("--outdir", default=str(Path.cwd() / "endfb80-lowtemp"),
                   help="Directory where the dataset folder should live (default: ./endfb80-lowtemp)")
    args = p.parse_args()

    outdir = Path(args.outdir).expanduser().resolve()
    tarball = Path(str(outdir) + ".tar.xz")
    parent = outdir.parent

    print(f"==> Target directory: {outdir}")
    if not outdir.exists():
        if not tarball.exists():
            print("==> Tarball not found locally; starting download (~3 GB).")
            download(URL, tarball)
        else:
            print(f"==> Using existing tarball: {tarball}")

        print("==> Extracting…")
        parent.mkdir(parents=True, exist_ok=True)
        try:
            with tarfile.open(tarball, mode="r:xz") as tf:
                tf.extractall(path=parent)
        except tarfile.ReadError as e:
            print(f"❌ Extract failed: {e}")
            sys.exit(1)

        # Normalize folder name if it extracted to ./endfb80-lowtemp
        extracted = parent / "endfb80-lowtemp"
        if extracted.exists() and extracted != outdir:
            try:
                extracted.rename(outdir)
            except Exception:
                # fallback: copy/replace
                print(f"==> Moving extracted data to {outdir}")
                os.replace(extracted, outdir)

    xs = outdir / "cross_sections.xml"
    if not xs.exists():
        print(f"❌ cross_sections.xml not found at {xs}")
        sys.exit(1)

    export_line = f'export OPENMC_CROSS_SECTIONS="{xs}"'
    append_export_to_bashrc(export_line)
    # Set for this process (note: cannot modify parent shell env)
    os.environ["OPENMC_CROSS_SECTIONS"] = str(xs)

    print("✅ Done.")
    print(f"OPENMC_CROSS_SECTIONS={xs}")
    print('Tip: run `source ~/.bashrc` (or open a new terminal) so future shells pick this up.')

if __name__ == "__main__":
    main()
