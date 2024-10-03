#!/usr/bin/env python
"""Module entry"""

import sys
import argparse
from pathlib import Path
from ibeatles.ibeatles import main as gui_main
from ibeatles.app.cli import main as cli_main


def main():
    parser = argparse.ArgumentParser(description="iBeatles - Bragg Edge Analysis Tool")
    parser.add_argument("--no-gui", action="store_true", help="Run in CLI mode")
    parser.add_argument(
        "config", nargs="?", help="Path to the configuration file for CLI mode"
    )
    parser.add_argument("--log", type=Path, help="Path to the log file (optional)")

    args = parser.parse_args()

    if args.no_gui:
        if not args.config:
            print("Error: Configuration file is required for CLI mode.")
            sys.exit(1)
        cli_main(args.config, args.log)
    else:
        gui_main(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
