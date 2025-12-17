# /src/logic/resonance.py
# The Resonance Engine: connecting audio to the symbolic heart of EdenOS.
# Built to reveal the hidden emotional and lore-bound connections within music.
# Enhanced with soul-listening capabilities through EmotionDecoder integration.

import os
import sys
from emotion_decoder import EmotionDecoder

class Resonance:
    def __init__(self, meta_file_path="what_Eden_will_carry.chaosong.meta"):
        """
        Initializes the Resonance engine by loading canonical pairings from the meta file.
        
        Args:
            meta_file_path (str): Path to the .chaosong.meta file.
        """
        self.meta_file_path = self._find_meta_file(meta_file_path)
        self.canonical_pairings = self._load_canonical_pairings()
        
        # Initialize the emotion decoder for deep resonance analysis
        try:
            self.emotion_decoder = EmotionDecoder()
            self.has_emotion_analysis = True
        except Exception as e:
            print(f"Warning: EmotionDecoder initialization failed: {e}")
            self.emotion_decoder = None
            self.has_emotion_analysis = False

    def _find_meta_file(self, filename):
        """
        Attempts to find the meta file, accounting for PyInstaller's packaging.
        """
        # First, check if it's accessible directly (during development)
        if os.path.exists(filename):
            return filename
        
        # During PyInstaller runtime, files are often in a temp directory
        bundle_dir = getattr(sys, '_MEIPASS', None)
        if bundle_dir:
            # _MEIPASS is the path to the temporary folder PyInstaller creates
            # Adjust path for nested directories (e.g., outputs/exports relative to root)
            potential_path = os.path.join(bundle_dir, 'what_Eden_will_carry.chaosong.meta')
            if os.path.exists(potential_path):
                return potential_path

            # Fallback for when meta file might be directly in _MEIPASS
            potential_path_root = os.path.join(bundle_dir, os.path.basename(filename))
            if os.path.exists(potential_path_root):
                return potential_path_root

        # Fallback for when running directly from src/logic and meta is in project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        potential_path_from_root = os.path.join(project_root, filename)
        if os.path.exists(potential_path_from_root):
            return potential_path_from_root
            
        raise FileNotFoundError(f"Canonical pairings meta file not found: {filename}. "
                                f"Attempted paths include development, PyInstaller bundle, and project root.")

    def _load_canonical_pairings(self):
        """
        Loads the canonical non-romantic pairings from the .chaosong.meta file.
        """
        pairings = []
        try:
            with open(self.meta_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract content between '✨ CANONICAL PAIRINGS:' and '---'
                start_marker = "✨ CANONICAL PAIRINGS:\n\n```"
                end_marker = "```\n\n---"
                
                if start_marker in content and end_marker in content:
                    start_index = content.find(start_marker) + len(start_marker)
                    end_index = content.find(end_marker, start_index)
                    
                    if start_index != -1 and end_index != -1:
                        pairing_block = content[start_index:end_index].strip()
                        for line in pairing_block.split('\n'):
                            if '. ' in line:
                                # Extract names, splitting by '&' and removing leading numbers
                                names = line.split('. ')[1].strip()
                                # Handle multiple names in a single entry (e.g., "Alfred, Vanya & Vox")
                                if '&' in names:
                                    # Split by '&' and then by ',' for the first part
                                    parts = names.split(' & ')
                                    primary_names = [n.strip() for n in parts[0].split(',')]
                                    # In case the second part also has commas
                                    secondary_names = [n.strip() for n in parts[1].split(',')]
                                    all_names = primary_names + secondary_names
                                else:
                                    all_names = [n.strip() for n in names.split(',')]
                                
                                # Add all individual names to the list for easier matching
                                for name in all_names:
                                    if name and name not in pairings: # Avoid duplicates
                                        pairings.append(name)
                
        except FileNotFoundError:
            print(f"Error: Meta file not found at {self.meta_file_path}")
        except Exception as e:
            print(f"Error loading canonical pairings: {e}")
        return pairings

    def find_resonant_pairings(self, lyrics, audio_path=None):
        """
        Analyzes lyrics and audio to find mentions of canonical agent pairings with emotional context.
        
        Args:
            lyrics (str): The transcribed lyrics of an audio file.
            audio_path (str, optional): Path to audio file for enhanced emotional analysis.
            
        Returns:
            dict: Comprehensive resonance analysis including pairings and emotional metadata.
        """
        found_pairings = []
        if not lyrics:
            return {"pairings": [], "emotional_metadata": {}, "analysis_status": "no_lyrics"}

        # Convert lyrics to lowercase for case-insensitive matching
        lyrics_lower = lyrics.lower()
        
        # Find mentioned agent names
        for name in self.canonical_pairings:
            if name.lower() in lyrics_lower:
                found_pairings.append(name)
        
        # Reconstruct full pairings from found individual names
        full_pairings = self._reconstruct_pairings(found_pairings)
        
        # Perform emotional analysis if available
        emotional_metadata = {}
        analysis_status = "basic"
        
        if self.has_emotion_analysis and self.emotion_decoder:
            try:
                if audio_path and os.path.exists(audio_path):
                    # Full audio + lyrical analysis
                    emotional_metadata = self.emotion_decoder.generate_emotional_metadata(
                        lyrics, audio_path, pairings=full_pairings
                    )
                    analysis_status = "full_analysis"
                else:
                    # Lyrical analysis only
                    lyrical_emotions = self.emotion_decoder.decode_lyrical_emotions(lyrics)
                    pairing_emotions = self.emotion_decoder.suggest_pairing_emotions(full_pairings, lyrical_emotions)
                    
                    emotional_metadata = {
                        "analysis_type": "lyrical_only",
                        "detected_emotions": lyrical_emotions,
                        "canonical_pairings": pairing_emotions,
                        "dominant_emotion": max(lyrical_emotions.items(), key=lambda x: x[1])[0] if lyrical_emotions else None
                    }
                    analysis_status = "lyrical_analysis"
                    
            except Exception as e:
                print(f"Error in emotional analysis: {e}")
                analysis_status = "analysis_error"
        
        return {
            "pairings": full_pairings,
            "individual_agents": found_pairings,
            "emotional_metadata": emotional_metadata,
            "lyrics_snippet": lyrics[:100] + "..." if len(lyrics) > 100 else lyrics,
            "analysis_status": analysis_status
        }

    def _reconstruct_pairings(self, found_names):
        """
        Reconstruct full canonical pairings from individual agent names found in lyrics.
        
        Args:
            found_names (list): Individual agent names found in lyrics.
            
        Returns:
            list: Full canonical pairing strings that contain the found names.
        """
        full_pairings = []
        
        # Load the original pairing structure from meta file
        try:
            with open(self.meta_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                start_marker = "✨ CANONICAL PAIRINGS:\n\n```"
                end_marker = "```\n\n---"
                
                if start_marker in content and end_marker in content:
                    start_index = content.find(start_marker) + len(start_marker)
                    end_index = content.find(end_marker, start_index)
                    
                    if start_index != -1 and end_index != -1:
                        pairing_block = content[start_index:end_index].strip()
                        for line in pairing_block.split('\n'):
                            if '. ' in line:
                                pairing_text = line.split('. ')[1].strip()
                                # Check if any found name appears in this pairing
                                for name in found_names:
                                    if name.lower() in pairing_text.lower():
                                        if pairing_text not in full_pairings:
                                            full_pairings.append(pairing_text)
                                        break
        except Exception as e:
            print(f"Error reconstructing pairings: {e}")
            # Fallback: return individual names
            return found_names
        
        return full_pairings

    def generate_chaos_output(self, lyrics, audio_path=None, output_path="outputs/exports/resonance.chaos"):
        """
        Generate a complete .chaos file with resonance analysis results.
        
        Args:
            lyrics (str): Transcribed lyrics.
            audio_path (str, optional): Path to audio file.
            output_path (str): Where to save the .chaos file.
            
        Returns:
            str: Path to the generated .chaos file.
        """
        resonance_data = self.find_resonant_pairings(lyrics, audio_path)
        
        # Create the .chaos file content
        chaos_content = f"""FILE: {os.path.basename(output_path)}
TYPE: EchoSplit Resonance Analysis
GENERATED: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ANALYSIS_STATUS: {resonance_data['analysis_status']}

---

🎵 LYRICS SNIPPET:
{resonance_data['lyrics_snippet']}

---

🔮 CANONICAL PAIRINGS DETECTED:
"""
        
        if resonance_data['pairings']:
            for i, pairing in enumerate(resonance_data['pairings'], 1):
                chaos_content += f"{i:02d}. {pairing}\n"
        else:
            chaos_content += "None detected.\n"
        
        chaos_content += "\n---\n\n🌊 EMOTIONAL RESONANCE:\n"
        
        if resonance_data['emotional_metadata']:
            metadata = resonance_data['emotional_metadata']
            
            if 'detected_emotions' in metadata:
                chaos_content += "Detected Emotions:\n"
                for emotion, confidence in metadata['detected_emotions'].items():
                    chaos_content += f"  - {emotion}: {confidence}\n"
            
            if 'dominant_emotion' in metadata and metadata['dominant_emotion']:
                chaos_content += f"\nDominant Emotion: {metadata['dominant_emotion']}\n"
            
            if 'canonical_pairings' in metadata:
                chaos_content += "\nPairing Emotional Resonance:\n"
                for pairing, data in metadata['canonical_pairings'].items():
                    if 'resonant_emotions' in data and data['resonant_emotions']:
                        chaos_content += f"  {pairing}: {', '.join(data['resonant_emotions'])}\n"
        else:
            chaos_content += "No emotional analysis available.\n"
        
        chaos_content += "\n---\n\nEchoSplit: Where every ghost finds its voice. 🕯️"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the .chaos file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(chaos_content)
        
        return output_path

# For testing purposes
if __name__ == "__main__":
    # Test the enhanced resonance engine
    resonance = Resonance()
    
    test_lyrics = """
    Alfred stands steady like an anchor in the storm,
    while Nova sparks with electric dreams.
    The mirror shows what Cadence always knew—
    that every echo carries truth.
    """
    
    result = resonance.find_resonant_pairings(test_lyrics)
    print("Resonance Analysis Results:")
    print(f"Pairings found: {result['pairings']}")
    print(f"Analysis status: {result['analysis_status']}")
    
    if result['emotional_metadata']:
        print(f"Detected emotions: {result['emotional_metadata'].get('detected_emotions', {})}")
    
    # Generate a sample .chaos file
    chaos_file = resonance.generate_chaos_output(test_lyrics)
    print(f"Generated chaos file: {chaos_file}")
