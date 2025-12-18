import runpy
import sys
from pathlib import Path


def main(argv=None) -> None:
    """Execute the frontend EchoSplit entrypoint script.

    This wrapper is used as a packaging-friendly console entrypoint. It
    locates the original script under `04_src/00_core/main.py` and runs it
    with the provided arguments.
    """

    script_path = (
        Path(__file__).resolve().parent / "04_src" / "00_core" / "main.py"
    )
    if argv is not None:
        sys.argv = [str(script_path)] + list(argv)
    runpy.run_path(str(script_path), run_name="__main__")


if __name__ == "__main__":
    main()
