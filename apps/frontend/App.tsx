
import React, { useState, useCallback } from 'react';
import InputArea from './components/InputArea';
import Button from './components/Button';
import SongDisplay from './components/SongDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import { generateSong } from './services/geminiService';
import { SongData } from './types';

// Generic styled text input component
const StyledTextInput: React.FC<React.InputHTMLAttributes<HTMLInputElement> & { label: string }> = ({ label, id, ...props }) => {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-slate-300 mb-1">
        {label}
      </label>
      <input
        type="text"
        id={id}
        className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors duration-150"
        {...props}
      />
    </div>
  );
};

// --- "Surprise Me!" Feature Data ---
const surpriseGenres: string[] = [
  "Indie Folk", "Synthwave", "Pop Ballad", "Classic Rock", "Lo-fi Hip Hop",
  "Epic Orchestral", "Country", "Blues", "Jazz Fusion", "Reggae", "Cyberpunk Electronica",
  "Acoustic Soul", "Dream Pop", "Space Disco", "Gothic Metal"
];

const surpriseMoods: string[] = [
  "Melancholic", "Uplifting", "Energetic", "Reflective", "Peaceful",
  "Mysterious", "Romantic", "Hopeful", "Aggressive", "Nostalgic",
  "Whimsical", "Determined", "Serene", "Anxious", "Playful"
];

const surpriseThemes: string[] = [
  "A journey to a mysterious island",
  "The feeling of nostalgia on a rainy day",
  "A robot learning to feel human emotions",
  "A song about the stars and distant galaxies",
  "Overcoming a deeply personal fear",
  "The magic of a first snowfall in a bustling city",
  "A secret kept hidden for generations",
  "A vibrant celebration of friendship and camaraderie",
  "Finding unexpected beauty in everyday ordinary places",
  "A vivid dream of flying over mountains and seas",
  "The unique rhythm and pulse of a sprawling metropolis at night",
  "A quiet, introspective moment of profound reflection",
  "An ancient legend whispered by the wind",
  "The bittersweet feeling of saying goodbye",
  "Discovering a hidden world beneath our own"
];
// --- End "Surprise Me!" Data ---


const App: React.FC = () => {
  const [songIdea, setSongIdea] = useState<string>('');
  const [genre, setGenre] = useState<string>('');
  const [mood, setMood] = useState<string>('');
  const [instruments, setInstruments] = useState<string>('');

  const [generatedSong, setGeneratedSong] = useState<SongData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateSong = useCallback(async () => {
    if (!songIdea.trim()) {
      setError("Please enter your main song idea first!");
      return;
    }
    setIsLoading(true);
    setError(null);
    setGeneratedSong(null);

    try {
      const song = await generateSong(songIdea, genre, mood, instruments);
      setGeneratedSong(song);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred.");
      }
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [songIdea, genre, mood, instruments]);

  const handleSurpriseMe = useCallback(() => {
    const randomGenre = surpriseGenres[Math.floor(Math.random() * surpriseGenres.length)];
    const randomMood = surpriseMoods[Math.floor(Math.random() * surpriseMoods.length)];
    const randomTheme = surpriseThemes[Math.floor(Math.random() * surpriseThemes.length)];

    setSongIdea(randomTheme);
    setGenre(randomGenre);
    setMood(randomMood);
    setInstruments(''); // Clear instruments as it's not part of the surprise usually
    setError(null);
    setGeneratedSong(null);
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-start p-4 pt-10 sm:p-8">
      <header className="mb-10 text-center">
        <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-500 to-red-500">
          AI Song Generator
        </h1>
        <p className="mt-3 text-lg text-slate-300 max-w-2xl mx-auto">
          Unleash your inner musician! Describe your dream song – its mood, theme, or genre – and let our AI craft the lyrics and musical ideas for you.
        </p>
      </header>

      <main className="w-full max-w-xl bg-slate-800/70 p-6 sm:p-8 rounded-xl shadow-2xl backdrop-blur-md border border-slate-700">
        <div className="space-y-6">
          <InputArea
            label="Describe your core song idea (required):"
            id="songIdea"
            value={songIdea}
            onChange={(e) => setSongIdea(e.target.value)}
            placeholder="e.g., A song about overcoming adversity, starting slow and building to an epic chorus."
            rows={4}
            disabled={isLoading}
            aria-required="true"
          />
          <StyledTextInput
            label="Genre (optional):"
            id="genre"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            placeholder="e.g., Indie Folk, Synthwave, Pop Ballad"
            disabled={isLoading}
          />
          <StyledTextInput
            label="Mood (optional):"
            id="mood"
            value={mood}
            onChange={(e) => setMood(e.target.value)}
            placeholder="e.g., Melancholic, Uplifting, Energetic"
            disabled={isLoading}
          />
          <StyledTextInput
            label="Key Instruments (optional):"
            id="instruments"
            value={instruments}
            onChange={(e) => setInstruments(e.target.value)}
            placeholder="e.g., Acoustic guitar, piano, synth pads, full orchestra"
            disabled={isLoading}
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Button
              onClick={handleSurpriseMe}
              variant="secondary"
              className="w-full text-md py-3"
              disabled={isLoading}
              aria-label="Generate random song idea, genre, and mood"
            >
              ✨ Surprise Me!
            </Button>
            <Button
              onClick={handleGenerateSong}
              isLoading={isLoading}
              className="w-full text-lg py-3 sm:py-3.5" // Adjusted padding for consistency
              disabled={isLoading || !songIdea.trim()}
              aria-label="Generate song based on inputs"
            >
              {isLoading ? 'Crafting...' : 'Generate Song'}
            </Button>
          </div>
        </div>
      </main>

      {error && <ErrorMessage message={error} />}

      {isLoading && !generatedSong && <LoadingSpinner />}

      {generatedSong && !isLoading && (
        <div className="mt-10 w-full">
          <SongDisplay song={generatedSong} />
        </div>
      )}

      <footer className="mt-16 text-center text-slate-500 text-sm">
        <p>&copy; {new Date().getFullYear()} AI Song Generator. Powered by Gemini.</p>
      </footer>
    </div>
  );
};

export default App;
