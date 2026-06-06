import re
import subprocess
from pathlib import Path


def bump_semver_patch() -> None:
    pyproject_path = Path("pyproject.toml")
    init_path = Path("src/hibp_downloader/__init__.py")

    if not pyproject_path.exists():
        raise FileNotFoundError(f"Could not find {pyproject_path}")
    if not init_path.exists():
        raise FileNotFoundError(f"Could not find {init_path}")

    # Read pyproject.toml
    pyproject_content = pyproject_path.read_text(encoding="utf-8")

    # Match project version line: version = "0.3.4"
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    old_version = match.group(1)
    parts = old_version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Version '{old_version}' is not semver X.Y.Z format")

    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    new_version = f"{major}.{minor}.{patch + 1}"
    print(f"Bumping version from {old_version} to {new_version}...")

    # Replace version in pyproject.toml (replaces both project and poetry versions if defined)
    pyproject_content = re.sub(
        r'^version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        pyproject_content,
        flags=re.MULTILINE,
    )
    pyproject_path.write_text(pyproject_content, encoding="utf-8")

    # Replace version in src/hibp_downloader/__init__.py: __version__ = "0.3.4"
    init_content = init_path.read_text(encoding="utf-8")
    init_content = re.sub(
        r'^__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
        init_content,
        flags=re.MULTILINE,
    )
    init_path.write_text(init_content, encoding="utf-8")

    # Run uv lock to synchronize uv.lock
    print("Running 'uv lock' to synchronize lock file...")
    try:
        subprocess.run(["uv", "lock"], check=True)
    except FileNotFoundError:
        print("Warning: 'uv' executable not found. Please run 'uv lock' manually.")


if __name__ == "__main__":
    bump_semver_patch()
