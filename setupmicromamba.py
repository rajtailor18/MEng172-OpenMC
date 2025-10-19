#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

MICROMAMBA_URL = "https://micro.mamba.pm/api/micromamba/linux-64/latest"
LOCAL_BIN = Path.home() / ".local" / "bin"
MAMBA_EXE = LOCAL_BIN / "micromamba"
BASHRC = Path.home() / ".bashrc"
ENV_NAME = "openmc"
CHANNELS = ["-c", "conda-forge"]
ENV_PKGS = [
    "python=3.11", "openmc", "jupyterlab", "ipykernel",
    "numpy", "pandas", "scipy", "h5py", "matplotlib",
    "mpi", "mpi4py"
]

def run(cmd, check=True, capture=False, env=None):
    if capture:
        return subprocess.run(cmd, check=check, text=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, env=env).stdout
    subprocess.run(cmd, check=check, env=env)

def is_micromamba_installed():
    """Check if micromamba is already installed and works."""
    try:
        out = run(["micromamba", "--version"], capture=True)
        print(f"✅ micromamba already installed: {out.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def ensure_local_bin_on_path():
    LOCAL_BIN.mkdir(parents=True, exist_ok=True)
    line = 'export PATH="$HOME/.local/bin:$PATH"'
    existing = BASHRC.read_text() if BASHRC.exists() else ""
    if line not in existing:
        with BASHRC.open("a") as f:
            f.write("\n" + line + "\n")
    os.environ["PATH"] = f"{LOCAL_BIN}:{os.environ.get('PATH','')}"

def download_micromamba():
    print("==> Downloading micromamba …")
    tmp_tar = Path("/tmp/micromamba.tar.bz2")
    with urllib.request.urlopen(MICROMAMBA_URL) as r, open(tmp_tar, "wb") as f:
        shutil.copyfileobj(r, f)
    print("==> Extracting micromamba …")
    with tarfile.open(tmp_tar, "r:bz2") as tf:
        member = next(m for m in tf.getmembers() if m.name.endswith("bin/micromamba"))
        tf.extract(member, path="/tmp")
    extracted = Path("/tmp/bin/micromamba")
    LOCAL_BIN.mkdir(parents=True, exist_ok=True)
    shutil.move(str(extracted), str(MAMBA_EXE))
    shutil.rmtree("/tmp/bin", ignore_errors=True)
    tmp_tar.unlink(missing_ok=True)
    MAMBA_EXE.chmod(0o755)

def remove_stale_tmp_hooks():
    if not BASHRC.exists():
        return
    txt = BASHRC.read_text()
    new = re.sub(r".*\/tmp\/bin\/micromamba.*\n?", "", txt)
    if new != txt:
        BASHRC.write_text(new)

def init_shell_hook():
    print("==> Initializing micromamba shell hook …")
    run([str(MAMBA_EXE), "shell", "init", "-s", "bash", "-r", str(Path.home() / "mamba")], check=False)

def env_exists(name: str) -> bool:
    out = run([str(MAMBA_EXE), "env", "list"], capture=True)
    return any(line.split()[0] == name for line in out.splitlines() if line and not line.startswith("#"))

def create_env(name: str):
    print(f"==> Creating environment '{name}' …")
    run([str(MAMBA_EXE), "create", "-y", "-n", name, *CHANNELS, *ENV_PKGS])

def ensure_openmc_importable(name: str):
    code = "import openmc, sys; print('OpenMC:', openmc.__version__)"
    try:
        out = run([str(MAMBA_EXE), "run", "-n", name, "python", "-c", code], capture=True)
        print(out.strip())
    except subprocess.CalledProcessError:
        print("   OpenMC not importable — installing via pip …")
        run([str(MAMBA_EXE), "run", "-n", name, "python", "-m", "pip", "install", "--upgrade", "pip"])
        run([str(MAMBA_EXE), "run", "-n", name, "python", "-m", "pip", "install", "openmc"])
        out = run([str(MAMBA_EXE), "run", "-n", name, "python", "-c", code], capture=True)
        print(out.strip())

def register_jupyter_kernel(name: str):
    print("==> Registering Jupyter kernel …")
    run([str(MAMBA_EXE), "run", "-n", name, "python", "-m", "ipykernel", "install", "--user", f"--name={name}", "-y"])

def main():
    print("🚀 Micromamba + OpenMC setup starting...")

    ensure_local_bin_on_path()
    remove_stale_tmp_hooks()

    # ✅ Pre-check: if micromamba already works, skip installation
    if not is_micromamba_installed():
        print("⚠️ micromamba not found — installing now")
        download_micromamba()
    else:
        print("✅ Skipping installation — already available")

    init_shell_hook()

    if not env_exists(ENV_NAME):
        create_env(ENV_NAME)
    else:
        print(f"✅ Environment '{ENV_NAME}' already exists")

    ensure_openmc_importable(ENV_NAME)
    register_jupyter_kernel(ENV_NAME)

    print("\n🎉 Setup complete!")
    print(f"👉 To activate: micromamba activate {ENV_NAME}")
    print("👉 If needed:  source ~/.bashrc")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed: {' '.join(e.cmd) if isinstance(e.cmd, list) else e.cmd}")
        sys.exit(e.returncode)
