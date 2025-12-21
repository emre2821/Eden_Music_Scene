# /src/logic/spleeter_runner.py
# A module to divide sound into voice and harmony, built with trust and precision.
# Separates vocals using Spleeter, honoring the next dev with clarity.

"""Simple CLI wrapper around Spleeter.

The input audio path is supplied via ``--input`` or the ``ECHO_INPUT``
environment variable. Output stems are written to the directory given by
``--output-dir`` or ``ECHO_OUTPUT_DIR``. Paths are validated before processing.
"""

import argparse
import os

from spleeter.separator import Separator


def separate_vocals(input_path, output_dir):
    """
    Separate vocals from an audio file using Spleeter’s 2-stem model.

    Args:
        input_path (str): Path to the input audio file (.mp3 or .wav).
        output_dir (str): Directory to save vocals.wav and instrumental.wav.

    Raises:
        FileNotFoundError: If the input file doesn’t exist.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create output directory if it’s not there

    # Initialize Spleeter with 2-stem separation (vocals + instrumental)
    separator = Separator("spleeter:2stems")
    separator.separate_to_file(input_path, output_dir)


def main():
    """Parse command-line arguments and execute the separation."""

    parser = argparse.ArgumentParser(
        description="Separate vocals from audio using Spleeter."
    )
    parser.add_argument(
        "--input",
        "-i",
        default=os.getenv("ECHO_INPUT"),
        help="Path to the input audio file. Can also be set via ECHO_INPUT.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=os.getenv("ECHO_OUTPUT_DIR"),
        help="Directory to save output stems. Can also be set via ECHO_OUTPUT_DIR.",
    )
    args = parser.parse_args()

    if not args.input:
        parser.error("Input file required via --input or ECHO_INPUT")
    if not os.path.exists(args.input):
        parser.error(f"Input file not found: {args.input}")

    output_dir = args.output_dir
    if not output_dir:
        parser.error("Output directory required via --output-dir or ECHO_OUTPUT_DIR")

    try:
        separate_vocals(args.input, output_dir)
        print(f"Separation complete. Outputs saved to {output_dir}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
