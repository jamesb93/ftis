#! /Users/james/.virtualenvs/ftis/bin/python3

import argparse
from pathlib import Path
from ftis.process import FTISProcess
from ftis.generate import new_analyser


parser = argparse.ArgumentParser(description="The entry point to ftis.")
subparsers = parser.add_subparsers(help="New or Run commands", dest="subcmd")

new_parser = subparsers.add_parser("new")
run_parser = subparsers.add_parser("run")
dry_parser = subparsers.add_parser("dry")

new_parser.add_argument(
    "-n", "--name", type=str, required=True, help="Name for the analyser."
)

run_parser.add_argument(
    "-c", "--config", type=str, required=True, help="A YAML configuration."
)

dry_parser.add_argument(
    "-c", "--config", type=str, required=True, help="A YAML configuration."
)

args = parser.parse_args()

if __name__ == "__main__":
    if parser.parse_args().subcmd == "new":
        new_analyser(args.name)
    if parser.parse_args().subcmd == "run":
        process = FTISProcess(args.config)
        process.run_process()
    if parser.parse_args().subcmd == "dry":
        process = FTISProcess(args.config)
        process.dry()
        print(process.source)
