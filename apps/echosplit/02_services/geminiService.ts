
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { SongData, GeminiSongResponse, ChordProgression, SongLine } from '../types';

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.warn(
    "⚠️ Missing API_KEY environment variable. Set it to your Google Gemini API key to enable AI features."
  );
}

const ai = new GoogleGenAI({ apiKey: API_KEY || "fallback_or_error_key" });
const model = "gemini-2.5-flash-preview-04-17";

const constructPrompt = (description: string, genre?: string, mood?: string, instruments?: string): string => {
  let userInputs = `User's core song idea: "${description}"\n`;
  if (genre && genre.trim() !== "") userInputs += `Preferred Genre: "${genre}"\n`;
  if (mood && mood.trim() !== "") userInputs += `Desired Mood: "${mood}"\n`;
  if (instruments && instruments.trim() !== "") userInputs += `Key Instruments: "${instruments}"\n`;

  return `
You are an expert songwriter and music theorist AI. A user will provide a theme, mood, genre, or specific ideas for a song.
Your task is to generate a complete song concept, including a creative title, structured lyrics, and detailed musical suggestions.
The lyrics should be broken down into conventional song parts like Intro, Verse 1, Chorus, Verse 2, Bridge, Outro, etc.
Please return your response *only* as a JSON object adhering strictly to the following format:
{
  "title": "The Song Title Here",
  "genre": "Suggested Genre (e.g., Indie Folk, Synthwave, Power Ballad)",
  "mood": "Overall Mood (e.g., Melancholic, Uplifting, Energetic, Reflective)",
  "suggestedKey": "Suggested Musical Key (e.g., C Major, A minor, E♭ Major)",
  "suggestedBPM": "Suggested Tempo in BPM (e.g., 120 BPM, 75 BPM)",
  "instrumentationIdeas": [
    "Description of instruments for verse (e.g., Gentle acoustic guitar and soft piano)",
    "Description of instruments for chorus (e.g., Full drums, driving bass, layered synths)",
    "Notes on other sections or overall sound (e.g., String section swells in the bridge)"
  ],
  "vocalStyle": "Suggested Vocal Style (e.g., Soaring male tenor, husky female alto, spoken word)",
  "chordProgressions": [
    { "section": "Intro", "chords": "Am - G - C - F (repeat)" },
    { "section": "Verse 1", "chords": "C - G - Am - Em" },
    { "section": "Chorus", "chords": "F - C - G - Am" },
    { "section": "Bridge", "chords": "Dm - Am - E - Am" }
  ],
  "lyrics": [
    { "type": "Intro", "lines": ["Line 1 of intro", "Line 2 of intro"] },
    { "type": "Verse 1", "lines": ["Line 1 of verse 1", "Line 2 of verse 1", "Line 3 of verse 1"] },
    { "type": "Chorus", "lines": ["Line 1 of chorus", "Line 2 of chorus"] }
  ]
}
Ensure each "lines" array in lyrics contains strings representing individual lines of that song part.
Ensure "instrumentationIdeas" is an array of strings.
Ensure "chordProgressions" is an array of objects, each with "section" and "chords" string properties.
The "genre" and "mood" fields should reflect the user's input if provided, or your creative suggestion if not. If the user provides genre/mood/instruments, use that as strong guidance.
Do not include any other text, explanations, or markdown formatting outside of the JSON object itself.

${userInputs}
`;
};

const isValidSongData = (data: any): data is SongData => {
  if (!data || typeof data.title !== 'string' || !Array.isArray(data.lyrics)) {
    return false;
  }
  if (data.genre !== undefined && typeof data.genre !== 'string') return false;
  if (data.mood !== undefined && typeof data.mood !== 'string') return false;
  if (data.suggestedKey !== undefined && typeof data.suggestedKey !== 'string') return false;
  if (data.suggestedBPM !== undefined && typeof data.suggestedBPM !== 'string') return false;
  if (data.vocalStyle !== undefined && typeof data.vocalStyle !== 'string') return false;

  if (data.instrumentationIdeas !== undefined) {
    if (!Array.isArray(data.instrumentationIdeas) || !data.instrumentationIdeas.every((item: any) => typeof item === 'string')) {
      return false;
    }
  }

  if (data.chordProgressions !== undefined) {
    if (!Array.isArray(data.chordProgressions) || !data.chordProgressions.every((cp: any) =>
      typeof cp === 'object' && cp !== null && typeof cp.section === 'string' && typeof cp.chords === 'string'
    )) {
      return false;
    }
  }

  return data.lyrics.every((part: any) =>
    typeof part === 'object' && part !== null && typeof part.type === 'string' &&
    Array.isArray(part.lines) && part.lines.every((line: any) => typeof line === 'string')
  );
};


export const generateSong = async (description: string, genre?: string, mood?: string, instruments?: string): Promise<SongData> => {
  if (!API_KEY) {
    throw new Error(
      "Google Gemini API key not found. Set the API_KEY environment variable to use song generation."
    );
  }

  const prompt = constructPrompt(description, genre, mood, instruments);

  try {
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: model,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      },
    });

    let jsonStr = response.text.trim();

    const fenceRegex = /^```(\w*)?\s*\n?(.*?)\n?\s*```$/s;
    const match = jsonStr.match(fenceRegex);
    if (match && match[2]) {
      jsonStr = match[2].trim();
    }

    const parsedData: GeminiSongResponse = JSON.parse(jsonStr);
    const songData = Array.isArray(parsedData) ? parsedData[0] : parsedData;

    if (!isValidSongData(songData)) {
      console.error("Invalid song data structure received:", songData);
      throw new Error("AI returned an unexpected song format. Please try again.");
    }

    return songData as SongData;

  } catch (error) {
    console.error("Error generating song with Gemini:", error);
    if (error instanceof Error) {
        if (error.message.includes("API Key not valid")) {
             throw new Error("The configured API Key for Gemini is invalid. Please check your API_KEY environment variable.");
        }
         throw new Error(`Failed to generate song: ${error.message}`);
    }
    throw new Error("An unknown error occurred while generating the song.");
  }
};
