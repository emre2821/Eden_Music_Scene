
export interface SongLine {
  type: string; // e.g., "Verse 1", "Chorus", "Bridge", "Intro", "Outro"
  lines: string[];
}

export interface ChordProgression {
  section: string; // e.g., "Verse 1", "Chorus"
  chords: string;  // e.g., "Am - G - C - F"
}

export interface SongData {
  title: string;
  genre?: string;
  mood?: string;
  suggestedKey?: string;
  suggestedBPM?: string;
  instrumentationIdeas?: string[];
  vocalStyle?: string;
  chordProgressions?: ChordProgression[];
  lyrics: SongLine[];
}

// This type is for the raw response from Gemini.
export type GeminiSongResponse = SongData | SongData[];
