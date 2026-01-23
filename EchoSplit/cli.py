"""Command-line interface for EchoSplit audio stem separation.

Allows separating one or more audio files into stems using the
Spleeter backend. Reuses the separation logic from
`04_src/00_core/spleeter_runner.py`.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Iterable


def _load_spleeter_runner():
    """Dynamically load the existing spleeter runner module.

    This keeps the CLI lightweight while reusing the logic already
    shipped with EchoSplit's source tree.
    """
    module_path = Path(__file__).resolve().parent / "04_src" / "00_core" / "spleeter_runner.py"
    spec = importlib.util.spec_from_file_location("spleeter_runner", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


spleeter_runner = _load_spleeter_runner()


def separate_files(files: Iterable[str], stems: int, output_dir: Path) -> None:
    """Separate given audio files into stems.

    Parameters
    ----------
    files:
        Iterable of paths to input audio files.
    stems:
        Number of stems to split into (2, 4, or 5).
    output_dir:
        Directory where separated stems will be written.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    separator = spleeter_runner.Separator(f"spleeter:{stems}stems")
    for input_path in files:
        in_file = Path(input_path)
        if not in_file.exists():
            print(f"[warn] File not found: {in_file}")
            continue
        separator.separate_to_file(str(in_file), str(output_dir))
        print(f"Separated {in_file} -> {output_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EchoSplit audio stem separation")
    parser.add_argument("inputs", nargs="+", help="Input audio file(s)")
    parser.add_argument(
        "--stems",
        type=int,
        choices=[2, 4, 5],
        default=2,
        help="Number of stems to separate (default: 2)",
    )
    parser.add_argument(
        "--output",
        default=str(Path("outputs") / "stems"),
        help="Directory to store separated stems (default: outputs/stems)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    separate_files(args.inputs, args.stems, Path(args.output))


if __name__ == "__main__":
    main()