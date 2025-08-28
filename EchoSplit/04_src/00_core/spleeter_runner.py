# /src/logic/spleeter_runner.py
# A module to divide sound into voice and harmony, built with trust and precision.
# Separates vocals using Spleeter, honoring the next dev with clarity.

import os
import argparse
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
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(input_path, output_dir)

def main():
    """Parse command-line arguments and execute the separation."""
    parser = argparse.ArgumentParser(description="Separate vocals from audio using Spleeter.")
    parser.add_argument('--input', required=True, help='Path to the input audio file')
    args = parser.parse_args()

    output_dir = os.path.join('outputs', 'stems')
    try:
        separate_vocals(args.input, output_dir)
        print(f"Separation complete. Outputs saved to {output_dir}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()