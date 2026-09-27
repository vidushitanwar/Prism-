"""
Run this to (re)seed the PRISM database from the command line:

    cd backend
    python -m scripts.seed          # seed only if empty
    python -m scripts.seed --force  # wipe and reseed

The backend also auto-seeds an empty database on startup, so this script
is mainly useful for forcing a fresh, reproducible dataset during
development.
"""
import sys
import json

from app.data.seed_generator import seed_all


def main():
    force = "--force" in sys.argv
    result = seed_all(force=force)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
