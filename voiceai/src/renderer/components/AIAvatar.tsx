import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';

interface AIAvatarProps {
  isProcessing: boolean;
}

function AIAvatar({ isProcessing }: AIAvatarProps) {
  const { isListening } = useStore();
  const [waveHeights, setWaveHeights] = useState([0.3, 0.3, 0.3, 0.3, 0.3]);

  useEffect(() => {
    if (isListening) {
      const interval = setInterval(() => {
        setWaveHeights([
          Math.random() * 0.7 + 0.3,
          Math.random() * 0.7 + 0.3,
          Math.random() * 0.7 + 0.3,
          Math.random() * 0.7 + 0.3,
          Math.random() * 0.7 + 0.3,
        ]);
      }, 150);
      return () => clearInterval(interval);
    } else {
      setWaveHeights([0.3, 0.3, 0.3, 0.3, 0.3]);
    }
  }, [isListening]);

  return (
    <div className="relative">
      {/* Pulse ring when listening */}
      {isListening && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-24 h-24 rounded-full border-2 border-accent/50 animate-pulse-ring" />
        </div>
      )}

      {/* Avatar container */}
      <div
        className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
          isProcessing
            ? 'bg-primary/20 glow-primary'
            : isListening
            ? 'bg-accent/20 glow-accent'
            : 'bg-white/5'
        }`}
      >
        {/* Animated face */}
        <svg
          className={`w-12 h-12 transition-all ${isProcessing ? 'animate-spin text-primary' : isListening ? 'text-accent' : 'text-text-primary'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          {/* Robot face */}
          <circle cx="12" cy="12" r="10" strokeWidth="1.5" />
          {/* Eyes */}
          <circle cx="8" cy="10" r="1.5" fill="currentColor" className={isListening ? 'animate-pulse' : ''} />
          <circle cx="16" cy="10" r="1.5" fill="currentColor" className={isListening ? 'animate-pulse' : ''} />
          {/* Mouth */}
          <path
            strokeWidth="1.5"
            strokeLinecap="round"
            d={isProcessing ? 'M8 15h8' : isListening ? 'M7 14c1-2 2.5-3 5-3s4 1 5 3' : 'M8 15c1-1 2-2 4-2s3 1 4 2'}
          />
          {/* Antenna */}
          <line x1="12" y1="2" x2="12" y2="4" strokeWidth="1.5" />
          <circle cx="12" cy="2" r="1" fill="currentColor" className={isListening ? 'animate-pulse' : ''} />
        </svg>
      </div>

      {/* Voice wave visualization */}
      {isListening && (
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 flex items-end gap-1 h-8">
          {waveHeights.map((height, i) => (
            <div
              key={i}
              className="w-1 bg-accent rounded-full transition-all duration-100"
              style={{ height: `${height * 24}px` }}
            />
          ))}
        </div>
      )}

      {/* Status text */}
      <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 text-xs text-text-secondary whitespace-nowrap">
        {isProcessing ? 'Thinking...' : isListening ? 'Listening...' : 'Ready'}
      </div>
    </div>
  );
}

export default AIAvatar;
