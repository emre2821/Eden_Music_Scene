"""Command-line interface for EchoSplit audio stem separation.

This CLI reuses the separation logic from `04_src/00_core/spleeter_runner.py`
to split one or more audio files into vocal and instrumental stems.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Iterable


def _load_spleeter_runner():
    """Dynamically import the existing spleeter runner module."""
    module_path = (
        Path(__file__).resolve().parent / "04_src" / "00_core" / "spleeter_runner.py"
    )
    spec = importlib.util.spec_from_file_location("spleeter_runner", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


spleeter_runner = _load_spleeter_runner()


def separate_files(files: Iterable[str], output_dir: Path) -> None:
    """Separate vocals from the given audio files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for input_path in files:
        try:
            spleeter_runner.separate_vocals(str(input_path), str(output_dir))
            print(f"Separated {input_path} -> {output_dir}")
        except FileNotFoundError:
            print(f"[warn] File not found: {input_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EchoSplit audio stem separation")
    parser.add_argument("inputs", nargs="+", help="Input audio file(s)")
    parser.add_argument(
        "--output",
        default=str(Path("outputs") / "stems"),
        help="Directory to store separated stems (default: outputs/stems)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    separate_files(args.inputs, Path(args.output))


if __name__ == "__main__":
    main()
