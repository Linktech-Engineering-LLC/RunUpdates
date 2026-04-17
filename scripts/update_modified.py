#!/usr/bin/env python3
# System Libraries
import os
import sys
from datetime import date, datetime
from pathlib import Path
# RunUpdates Libraries
from RunUpdates.logging.factory import LoggerFactory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = PROJECT_ROOT / "RunUpdates"
IGNORE_FILE = PROJECT_ROOT / "ignore-list.txt"


# Maintenance logs go to RunUpdates/Logs/<script>.log
# Script name
script_name = Path(sys.argv[0]).stem

# Maintenance logs go to <Project Root>/Logs/<script>.log
LOG_DIR = PROJECT_ROOT / "Logs"
LOG_DIR.mkdir(exist_ok=True)

log_cfg = {
    "enabled": True,
    "path": LOG_DIR / f"{script_name}.log",
    "rotate_logs": True,
    "max_bytes": 50_000_000,
    "max_age_days": 30,
    "console_enabled": True,
    "custom_levels": {
        "AUDIT": 25,
        "LIFECYCLE": 26,
        "TRACE": 5,
    },
}

factory = LoggerFactory(log_cfg, project_name=script_name)
logger = factory.get_logger("update_modified")

def build_summary(updated_files: list[str], preview: bool) -> str:
    mode = "PREVIEW" if preview else "UPDATE"
    today = date.today()
    lines = [f"{mode} summary for {today}"]
    if updated_files:
        lines.append("\n=== Files updated ===")
        lines.extend(f" - {f}" for f in updated_files)
    else:
        lines.append("\nNo files updated today")
    return "\n".join(lines)

def get_new_files_today() -> list[Path]:
    today = date.today()
    new_files = []
    for root, _, files in os.walk(PACKAGE_DIR):
        for f in files:
            if f.endswith(".py"):
                path = Path(root) / f
                # Use mtime as a proxy for creation time
                mtime = datetime.fromtimestamp(path.stat().st_mtime).date()
                if mtime == today:
                    new_files.append(path)
    return new_files

def update_file(path: Path) -> str | None:
    """Update the Modified header in a file. Return relative path if updated."""
    updated = False
    today = date.today().isoformat()
    lines = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("Modified:"):
                lines.append(f" Modified: {today}\n")
                updated = True
            else:
                lines.append(line)

    if updated:
        with path.open("w", encoding="utf-8") as f:
            f.writelines(lines)
        return str(path.relative_to(PROJECT_ROOT.parent))
    else:
        logger.debug(f"Skipped {path} (no header found)")
        return None
def walk_package(preview: bool) -> list[str]:
    """Walk package and update headers, return list of updated files."""
    fs_files = get_new_files_today()
    updated_files: list[str] = []
    for path in fs_files:
        if preview:
            updated_files.append(str(path.relative_to(PROJECT_ROOT.parent)))
        else:
            result = update_file(path)
            if result:
                updated_files.append(result)
    return updated_files

def main():
    preview = "--preview" in sys.argv
    updated_files = walk_package(preview)
    summary = build_summary(updated_files, preview)
    logger.info(summary)

if __name__ == "__main__":
    main()

