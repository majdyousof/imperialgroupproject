"""Build the static dashboard: python -m heathrow.build_site."""

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

from heathrow.paths import ROOT

APP_FILES = (
    "Home.py",
    "pages/1_Proposed_Solutions.py",
    "pages/2_Link-to-Link_Assessment.py",
    "pages/3_Final_Proposal.py",
    "pages/4_Holistic_Assessment.py",
    "heathrow/*.py",
    "data/inputs/heathrow_flow.csv",
    "data/inputs/journeys_via_hubs.csv",
    "data/inputs/annual_factors.csv",
    "images/logo.jpg",
    "images/proposed-network.jpg",
    "images/proposed-trolleybus-routes.jpg",
    ".streamlit/config.toml",
)


def browser_config() -> dict:
    """Read the pinned browser runtime and app configuration."""
    config = json.loads((ROOT / "web/stlite.json").read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not isinstance(config.get("entrypoint"), str):
        raise ValueError("Stlite configuration needs a Python entrypoint.")
    for key in ("requirements", "prebuiltPackageNames"):
        values = config.get(key)
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise ValueError(f"{key} must be a list of package names.")
    if not isinstance(config.get("streamlitConfig"), dict):
        raise ValueError("streamlitConfig must be an object.")
    version = config.get("runtimeVersion")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Pin the Stlite runtime to an exact release.")
    pyodide_url = config.get("pyodideUrl")
    if not isinstance(pyodide_url, str) or not re.fullmatch(
        r"https://cdn\.jsdelivr\.net/pyodide/v\d+\.\d+\.\d+/full/pyodide\.mjs", pyodide_url
    ):
        raise ValueError("Pin Pyodide to an exact release on jsDelivr.")
    return config


def build(base_path: str) -> Path:
    """Validate and stage the site before replacing the last successful build."""
    if not re.fullmatch(r"/[A-Za-z0-9_./-]*", base_path) or ".." in base_path.split("/"):
        raise ValueError("Use a local URL path, such as /heathrow-surface-access/.")
    base_path = "/" + base_path.strip("/") + "/" if base_path.strip("/") else "/"
    config = browser_config()
    files: set[Path] = set()
    for pattern in APP_FILES:
        matches = set(ROOT.glob(pattern))
        if not matches:
            raise FileNotFoundError(f"Missing app files: {pattern}")
        files.update(matches)
    files.discard(ROOT / "heathrow/build_site.py")
    for file in files:
        if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(ROOT):
            raise ValueError(f"Expected a regular app file: {file.relative_to(ROOT)}")
        if file.suffix == ".py":
            compile(file.read_bytes(), str(file), "exec")
    if config["entrypoint"] not in {file.relative_to(ROOT).as_posix() for file in files}:
        raise ValueError("The configured entrypoint is not among the bundled app files.")
    fallback = (ROOT / "web/404.html").read_text(encoding="utf-8")
    if fallback.count("__BASE_PATH__") != 1:
        raise ValueError("The 404 template needs exactly one base-path placeholder.")
    output = ROOT / "dist"
    if output.is_symlink():
        raise ValueError("The build output must not be a symbolic link.")
    with tempfile.TemporaryDirectory(prefix=".site-build-", dir=ROOT) as temporary:
        staging = Path(temporary)
        site = staging / "site"
        site.mkdir()
        config["files"] = {}
        for file in sorted(files):
            relative = file.relative_to(ROOT)
            destination = site / "app" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, destination)
            config["files"][relative.as_posix()] = {"url": "./app/" + relative.as_posix()}
        (site / "stlite.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        for name in ("index.html", "app.js"):
            shutil.copyfile(ROOT / "web" / name, site / name)
        (site / "404.html").write_text(
            fallback.replace("__BASE_PATH__", json.dumps(base_path)), encoding="utf-8"
        )
        (site / ".nojekyll").touch()
        previous = staging / "previous"
        if output.exists():
            output.rename(previous)
        try:
            site.rename(output)
        except OSError:
            if previous.exists():
                previous.rename(output)
            raise
    total = sum(file.stat().st_size for file in files)
    print(f"Built {output}: {len(files)} app files, {total / 1e6:.2f} MB before HTTP compression.")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-path",
        default="/heathrow-surface-access/",
        help="Published URL path for subpage refreshes (use / for a local preview).",
    )
    build(parser.parse_args().base_path)


if __name__ == "__main__":
    main()
