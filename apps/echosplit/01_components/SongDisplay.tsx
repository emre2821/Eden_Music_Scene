
import React from 'react';
import { SongData, SongLine, ChordProgression } from '../types';

interface SongDisplayProps {
  song: SongData;
}

const DetailItem: React.FC<{ label: string; value?: string | string[] | ChordProgression[] }> = ({ label, value }) => {
  if (!value || (Array.isArray(value) && value.length === 0)) return null;

  let content;
  if (label === "Instrumentation Ideas" && Array.isArray(value)) {
    content = (
      <ul className="list-disc list-inside pl-4">
        {(value as string[]).map((item, idx) => <li key={idx}>{item}</li>)}
      </ul>
    );
  } else if (label === "Chord Progressions" && Array.isArray(value)) {
    content = (
      <div className="space-y-1">
        {(value as ChordProgression[]).map((cp, idx) => (
          <div key={idx}>
            <span className="font-semibold text-purple-300">{cp.section}:</span> {cp.chords}
          </div>
        ))}
      </div>
    );
  } else {
    content = <>{value}</>;
  }

  return (
    <div>
      <h4 className="text-md font-semibold text-purple-300">{label}:</h4>
      <p className="text-slate-300 text-sm leading-relaxed">{content}</p>
    </div>
  );
};


const SongDisplay: React.FC<SongDisplayProps> = ({ song }) => {
  return (
    <div className="mt-8 p-6 bg-slate-800 rounded-lg shadow-xl w-full max-w-2xl mx-auto">
      <h2 className="text-3xl font-bold text-purple-400 mb-6 text-center">{song.title}</h2>

      <div className="mb-6 p-4 bg-slate-700/70 rounded-md space-y-3">
        <h3 className="text-xl font-bold text-purple-300 mb-3 border-b border-slate-600 pb-2">Musical Blueprint</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <DetailItem label="Genre" value={song.genre} />
          <DetailItem label="Mood" value={song.mood} />
          <DetailItem label="Suggested Key" value={song.suggestedKey} />
          <DetailItem label="Suggested BPM" value={song.suggestedBPM} />
        </div>
        <DetailItem label="Vocal Style" value={song.vocalStyle} />
        <DetailItem label="Instrumentation Ideas" value={song.instrumentationIdeas} />
        <DetailItem label="Chord Progressions" value={song.chordProgressions} />
      </div>

      <div className="space-y-6 text-slate-200">
        {song.lyrics.map((part: SongLine, index: number) => (
          <div key={`${part.type}-${index}`} className="p-4 bg-slate-700/50 rounded-md shadow">
            <h3 className="text-xl font-semibold text-purple-300 mb-2">{part.type}</h3>
            {part.lines.map((line: string, lineIndex: number) => (
              <p key={lineIndex} className="text-base leading-relaxed whitespace-pre-line">
                {line}
              </p>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SongDisplay;
