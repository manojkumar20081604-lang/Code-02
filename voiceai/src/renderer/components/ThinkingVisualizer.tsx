import { useState, useEffect, useRef } from 'react';

interface ThinkingState {
  step: number;
  total: number;
  label: string;
  sublabel?: string;
}

interface ThinkingVisualizerProps {
  isThinking: boolean;
  intent?: string;
  confidence?: number;
}

const thinkingSteps = [
  { label: 'Understanding request', sublabel: 'Analyzing input...' },
  { label: 'Classifying intent', sublabel: 'Identifying goal...' },
  { label: 'Extracting entities', sublabel: 'Finding key information...' },
  { label: 'Planning execution', sublabel: 'Creating action steps...' },
  { label: 'Executing plan', sublabel: 'Running tasks...' },
  { label: 'Generating response', sublabel: 'Preparing answer...' },
];

export default function ThinkingVisualizer({ isThinking, intent, confidence }: ThinkingVisualizerProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [visible, setVisible] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isThinking) {
      setVisible(true);
      setCurrentStep(0);
      
      const cycleSteps = () => {
        timeoutRef.current = setTimeout(() => {
          setCurrentStep(prev => {
            if (prev >= thinkingSteps.length - 1) {
              return 0;
            }
            return prev + 1;
          });
          cycleSteps();
        }, 800);
      };
      
      cycleSteps();
    } else {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      setTimeout(() => setVisible(false), 300);
    }

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [isThinking]);

  if (!visible) return null;

  return (
    <div className="bg-surface/80 backdrop-blur-sm rounded-xl border border-border p-6 transition-all duration-300">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <span className="text-xl">🧠</span>
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-primary rounded-full animate-ping"></div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-primary rounded-full"></div>
          </div>
          <div>
            <h3 className="text-white font-medium">02 is thinking...</h3>
            <p className="text-xs text-gray-400">
              {intent && `Intent: ${intent}`}
              {confidence && ` (${Math.round(confidence * 100)}% confidence)`}
            </p>
          </div>
        </div>
        
        {/* Thinking animation */}
        <div className="flex gap-1">
          {[0, 1, 2, 3].map(i => (
            <div
              key={i}
              className="w-2 h-8 bg-primary rounded-full"
              style={{
                animation: `bounce 1.4s ease-in-out infinite`,
                animationDelay: `${i * 0.2}s`
              }}
            />
          ))}
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-surface rounded-full mb-6 overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-primary to-purple-500 transition-all duration-500"
          style={{ width: `${((currentStep + 1) / thinkingSteps.length) * 100}%` }}
        />
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {thinkingSteps.map((step, index) => (
          <div 
            key={index}
            className={`flex items-center gap-3 transition-all duration-300 ${
              index === currentStep 
                ? 'opacity-100 translate-x-0' 
                : index < currentStep 
                  ? 'opacity-40 translate-x-2' 
                  : 'opacity-20'
            }`}
          >
            {/* Status indicator */}
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
              index === currentStep 
                ? 'bg-primary text-black' 
                : index < currentStep 
                  ? 'bg-green-500 text-white' 
                  : 'bg-surface text-gray-500'
            }`}>
              {index < currentStep ? '✓' : index + 1}
            </div>
            
            {/* Label */}
            <div className="flex-1">
              <p className={`text-sm ${
                index === currentStep ? 'text-white font-medium' : 'text-gray-400'
              }`}>
                {step.label}
              </p>
              {index === currentStep && step.sublabel && (
                <p className="text-xs text-primary animate-pulse">{step.sublabel}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Current action highlight */}
      <div className="mt-6 p-4 bg-primary/10 rounded-lg border border-primary/30">
        <p className="text-xs text-primary mb-1">Current Action</p>
        <p className="text-white font-medium">
          {thinkingSteps[currentStep].label}
        </p>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: scaleY(0.4); }
          40% { transform: scaleY(1); }
        }
      `}</style>
    </div>
  );
}
