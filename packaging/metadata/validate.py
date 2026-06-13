#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError, SchemaError

BASE_DIR = Path(__file__).parent
SCHEMA_V2 = BASE_DIR / "schema.json"
SCHEMA_V1 = BASE_DIR / "schema_v1.json"  # optional fallback if you want it


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load {path}: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: validate.py <metadata.json>")
        sys.exit(1)

    metadata_path = Path(sys.argv[1])
    if not metadata_path.exists():
        print(f"ERROR: Metadata file not found: {metadata_path}")
        sys.exit(1)

    metadata = load_json(metadata_path)

    # Determine schema version
    meta_version = metadata.get("meta_version", 1)

    if meta_version == 2:
        schema_path = SCHEMA_V2
    else:
        # fallback for older metadata.json
        if SCHEMA_V1.exists():
            schema_path = SCHEMA_V1
        else:
            print("ERROR: metadata.json is v1 but schema_v1.json is missing.")
            sys.exit(1)

    schema = load_json(schema_path)

    try:
        validate(instance=metadata, schema=schema)
        print(f"metadata.json (v{meta_version}) is valid ✔")
        sys.exit(0)

    except ValidationError as e:
        print("ERROR: metadata.json validation failed ❌")
        print(f"Field: {'.'.join(str(x) for x in e.path)}")
        print(f"Message: {e.message}")
        sys.exit(2)

    except SchemaError as e:
        print("ERROR: schema.json is invalid ❌")
        print(e)
        sys.exit(3)


if __name__ == "__main__":
    main()
