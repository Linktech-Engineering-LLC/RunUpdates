#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import tomllib  # Python 3.11+

# ------------------------------------------------------------
# Colors
# ------------------------------------------------------------
class Color:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"

def ctext(color, msg):
    return f"{color}{msg}{Color.RESET}"

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------
def setup_logging(script_name: str, project_path: Path) -> Path:
    logs_root = project_path / "logs"
    logs_root.mkdir(exist_ok=True)
    return logs_root / f"{script_name}_{project_path.name}.log"

def log(msg: str, log_file: Path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(ctext(Color.BLUE, line))
    with log_file.open("a") as f:
        f.write(line + "\n")

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def rm(path: Path):
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

def check_pyinstaller():
    return shutil.which("pyinstaller") is not None

def check_upx():
    return shutil.which("upx") is not None

def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)

# ------------------------------------------------------------
# Config loading
# ------------------------------------------------------------
def load_project_metadata(project_path: Path, log_file: Path) -> dict:
    config = {}

    build_toml = project_path / "build.toml"
    pyproject_toml = project_path / "pyproject.toml"

    # 1) Load build.toml if present
    if build_toml.exists():
        log(f"Using build configuration from {build_toml}", log_file)
        config = load_toml(build_toml)

    # 2) Load pyproject.toml if present
    pyproject_data = {}
    if pyproject_toml.exists():
        pyproject_data = load_toml(pyproject_toml)

        # Prefer [tool.build] if present
        tool_build = pyproject_data.get("tool", {}).get("build", {})
        if tool_build:
            log("Merging [tool.build] from pyproject.toml", log_file)
            config = {**tool_build, **config}  # build.toml overrides tool.build
        else:
            # Fall back to [project] metadata
            project_meta = pyproject_data.get("project", {})
            log("Merging [project] metadata from pyproject.toml", log_file)
            config = {
                **project_meta,
                **config
            }

    # 3) Final merged config with defaults
    return {
        "name": config.get("name", project_path.name),
        "version": config.get("version", "0.0.0"),
        "entry": config.get("entry", "__main__.py"),
        "pyinstaller_args": config.get("pyinstaller_args", []),
        "include": config.get("include", []),
        "prebuild": config.get("prebuild", None),
        "postbuild": config.get("postbuild", None),
        "release_sign": config.get("release_sign", None),
        "release_compress": bool(config.get("release_compress", False)),
    }

# ------------------------------------------------------------
# Versioning
# ------------------------------------------------------------
def write_version_file(project_path: Path, version: str, log_file: Path):
    version_file = project_path / "version.py"
    version_file.write_text(f'VERSION = "{version}"\n')
    log(f"Injected version into {version_file}", log_file)

def bump_version_in_pyproject(project_path: Path, bump: str, log_file: Path):
    pyproject_toml = project_path / "pyproject.toml"
    if not pyproject_toml.exists():
        log("No pyproject.toml found; cannot bump version.", log_file)
        return None

    text = pyproject_toml.read_text()
    data = load_toml(pyproject_toml)
    old_version = data.get("project", {}).get("version")

    if not old_version:
        log("No [project].version found; cannot bump.", log_file)
        return None

    parts = old_version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        log(f"Version '{old_version}' not x.y.z; cannot bump.", log_file)
        return None

    major, minor, patch = map(int, parts)
    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1 
        patch = 0
    elif bump == "patch":
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    log(f"Bumping version: {old_version} → {new_version}", log_file)

    new_text = text.replace(f'version = "{old_version}"', f'version = "{new_version}"')
    pyproject_toml.write_text(new_text)
    return new_version

# ------------------------------------------------------------
# Hooks
# ------------------------------------------------------------
def run_hook(project_path: Path, hook_path: str | None, default_names: list[str], label: str, log_file: Path):
    hook = None

    if hook_path:
        hook = (project_path / hook_path).resolve()
    else:
        for name in default_names:
            candidate = project_path / name
            if candidate.exists():
                hook = candidate
                break

    if not hook or not hook.exists():
        return

    log(f"Running {label} hook: {hook}", log_file)

    cmd = [sys.executable, str(hook)] if hook.suffix == ".py" else ["bash", str(hook)]

    cwd = os.getcwd()
    os.chdir(project_path)
    try:
        result = subprocess.run(cmd)
    finally:
        os.chdir(cwd)

    if result.returncode != 0:
        log(f"{label} hook failed with exit code {result.returncode}", log_file)

# ------------------------------------------------------------
# Entry Point Resolver
# ------------------------------------------------------------
def resolve_entry_point(project_path: Path, meta: dict, log_file: Path) -> Path:
    package_name = meta["name"]
    entry = meta["entry"]

    # 1) Package layout: ProjectRoot/PackageName/entry
    package_dir = project_path / package_name
    package_entry = package_dir / entry
    if package_dir.exists() and package_entry.exists():
        log(f"Detected package layout. Entry point: {package_entry}", log_file)
        return package_entry

    # 2) Flat layout: ProjectRoot/entry
    flat_entry = project_path / entry
    if flat_entry.exists():
        log(f"Detected flat project layout. Entry point: {flat_entry}", log_file)
        return flat_entry

    # 3) Single-file layout: ProjectRoot/PackageName.py
    single_file = project_path / f"{package_name}.py"
    if single_file.exists():
        log(f"Detected single-file project layout. Entry point: {single_file}", log_file)
        return single_file

    # 4) Nothing found
    log("ERROR: Could not locate entry point.", log_file)
    log("Checked:", log_file)
    log(f" - {package_entry}", log_file)
    log(f" - {flat_entry}", log_file)
    log(f" - {single_file}", log_file)
    raise FileNotFoundError("Entry point not found in any expected location.")

# ------------------------------------------------------------
# Granular Build Steps
# ------------------------------------------------------------
def clean_directories(dist_dir: Path, build_dir: Path, release_dir: Path, log_file: Path):
    log("Cleaning old build directories...", log_file)
    rm(dist_dir)
    rm(build_dir)

def build_pyinstaller_command(project_path: Path, meta: dict, args, log_file: Path) -> list[str]:
    entry_path = resolve_entry_point(project_path, meta, log_file)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", meta["name"],
        str(entry_path),
    ]
    python_tools_path = project_path.parent / "PythonTools"
    if python_tools_path.exists():
        cmd += ["--paths", str(python_tools_path)]
        log(f"Including PythonTools from {python_tools_path}", log_file)

    cmd.extend(meta["pyinstaller_args"])

    if args.include_toml:
        toml_path = project_path / "pyproject.toml"
        if toml_path.exists():
            cmd += ["--add-data", f"{toml_path}:."]
            log("Including pyproject.toml", log_file)

    for inc in meta["include"]:
        src = project_path / inc
        if src.exists():
            cmd += ["--add-data", f"{src}:{inc}"]
            log(f"Including data: {src}", log_file)

    if args.release and meta["release_compress"] and check_upx():
        log("UPX compression enabled.", log_file)

    return cmd

def run_pyinstaller(cmd: list[str], args, project_path: Path, log_file: Path) -> bool:
    if args.dry_run:
        log("Dry-run mode:", log_file)
        log(" ".join(cmd), log_file)
        print(ctext(Color.YELLOW, "Dry-run complete"))
        return False

    log(f"Running PyInstaller in {project_path}", log_file)

    cwd = os.getcwd()
    os.chdir(project_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        os.chdir(cwd)

    log(result.stdout, log_file)
    log(result.stderr, log_file)

    return result.returncode == 0

def copy_binary(project_path: Path, meta: dict, log_file: Path):
    dist_dir = project_path / "dist"
    release_dir = project_path / "release"
    release_dir.mkdir(exist_ok=True)
    binary = dist_dir / (meta["name"] + (".exe" if os.name == "nt" else ""))
    final = release_dir / binary.name
    shutil.copy2(binary, final)
    log(f"Copied binary to {final}", log_file)

def finalize_release(project_path: Path, meta: dict, args, log_file: Path):
    if args.release and meta["release_sign"]:
        log(f"Signing with: {meta['release_sign']}", log_file)
        subprocess.run(meta["release_sign"], shell=True)

# ------------------------------------------------------------
# Argument Parser
# ------------------------------------------------------------
def get_arguments():
    parser = argparse.ArgumentParser(description="Reusable build script for Python projects.")
    parser.add_argument("project_path")
    parser.add_argument("--clean-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-toml", action="store_true")
    parser.add_argument("--bump", choices=["major", "minor", "patch"])
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--spec", help="Use an explicit PyInstaller spec file")
    parser.add_argument("--keep-spec", action="store_true",
                        help="Keep and auto-use an existing .spec file")
    return parser.parse_args()

# ------------------------------------------------------------
# Orchestrator
# ------------------------------------------------------------
def main():
    args = get_arguments()

    project_path = Path(args.project_path).resolve()
    script_name = Path(sys.argv[0]).stem
    log_file = setup_logging(script_name, project_path)

    meta = load_project_metadata(project_path, log_file)
    version = meta["version"]

    if args.bump:
        bumped = bump_version_in_pyproject(project_path, args.bump, log_file)
        if bumped:
            version = bumped

    dist_dir = project_path / "dist"
    build_dir = project_path / "build"
    release_dir = project_path / "release"

    clean_directories(dist_dir, build_dir, release_dir, log_file)

    if args.clean_only:
        print(ctext(Color.YELLOW, "Clean-only mode complete"))
        return

    if not check_pyinstaller():
        log("PyInstaller not found.", log_file)
        return

    run_hook(project_path, meta["prebuild"], ["prebuild.sh", "prebuild.py"], "pre-build", log_file)
    write_version_file(project_path, version, log_file)

    # Determine if we should use a spec file
    spec_file = None

    if args.spec:
        # Explicit spec file provided
        spec_file = Path(args.spec).resolve()

    elif args.keep_spec:
        # Auto-use project spec if it exists
        candidate = project_path / f"{meta['name']}.spec"
        if candidate.exists():
            spec_file = candidate

    if spec_file:
        log(f"Using spec file: {spec_file}", log_file)
        cmd = ["pyinstaller", str(spec_file)]
    else:
        cmd = build_pyinstaller_command(project_path, meta, args, log_file)

    if not run_pyinstaller(cmd, args, project_path, log_file):
        log("PyInstaller failed.", log_file)
        return

    copy_binary(project_path, meta, log_file)
    run_hook(project_path, meta["postbuild"], ["postbuild.sh", "postbuild.py"], "post-build", log_file)
    finalize_release(project_path, meta, args, log_file)
    clean_directories(dist_dir, build_dir, release_dir, log_file)
    spec_file = project_path / f"{meta['name']}.spec"
    if not args.keep_spec and not args.spec:
        rm(spec_file)

    print(ctext(Color.GREEN, f"Build complete: {meta['name']} v{version}"))

# ------------------------------------------------------------
if __name__ == "__main__":
    main()
