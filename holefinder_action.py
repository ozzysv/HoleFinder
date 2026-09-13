from pathlib import Path
import sys

PLUGIN_DIR = Path(__file__).resolve().parent

if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))


def main():
    from holefinder_core import run
    run()


if __name__ == "__main__":
    main()
