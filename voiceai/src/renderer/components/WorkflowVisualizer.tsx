import { useState, useEffect, useRef } from 'react';

interface WorkflowStep {
  id: number;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  icon: string;
  duration?: number;
}

interface WorkflowVisualizerProps {
  steps: WorkflowStep[];
  title?: string;
  autoPlay?: boolean;
  onComplete?: () => void;
}

export default function WorkflowVisualizer({ 
  steps: initialSteps, 
  title = 'Workflow',
  autoPlay = false,
  onComplete 
}: WorkflowVisualizerProps) {
  const [steps, setSteps] = useState<WorkflowStep[]>(initialSteps);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setSteps(initialSteps);
    setCurrentStep(0);
  }, [initialSteps]);

  useEffect(() => {
    if (isPlaying && currentStep < steps.length) {
      intervalRef.current = setInterval(() => {
        setCurrentStep(prev => {
          if (prev >= steps.length - 1) {
            setIsPlaying(false);
            onComplete?.();
            return prev;
          }
          
          setSteps(s => s.map((step, i) => {
            if (i < prev) return { ...step, status: 'completed' as const };
            if (i === prev + 1) return { ...step, status: 'running' as const };
            return step;
          }));
          
          return prev + 1;
        });
      }, 1000);
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPlaying, currentStep, steps.length]);

  const play = () => {
    setIsPlaying(true);
    if (currentStep === 0) {
      setSteps(s => s.map((step, i) => i === 0 ? { ...step, status: 'running' as const } : step));
    }
  };

  const pause = () => setIsPlaying(false);

  const reset = () => {
    setIsPlaying(false);
    setCurrentStep(0);
    setSteps(initialSteps.map(s => ({ ...s, status: 'pending' as const })));
  };

  const getStatusColor = (status: WorkflowStep['status']) => {
    switch (status) {
      case 'completed': return 'bg-green-500 text-white';
      case 'running': return 'bg-primary text-black animate-pulse';
      case 'error': return 'bg-red-500 text-white';
      default: return 'bg-surface text-gray-400';
    }
  };

  const getStatusIcon = (status: WorkflowStep['status']) => {
    switch (status) {
      case 'completed': return '✓';
      case 'running': return '◐';
      case 'error': return '✗';
      default: return '○';
    }
  };

  const progress = (steps.filter(s => s.status === 'completed').length / steps.length) * 100;

  return (
    <div className="bg-surface/50 rounded-xl border border-border p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-medium flex items-center gap-2">
          <span>⚙️</span> {title}
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={reset}
            className="px-2 py-1 text-xs bg-surface hover:bg-surface/80 rounded transition-all"
          >
            ↺ Reset
          </button>
          {isPlaying ? (
            <button
              onClick={pause}
              className="px-3 py-1 text-xs bg-orange-500 hover:bg-orange-600 rounded transition-all flex items-center gap-1"
            >
              ⏸ Pause
            </button>
          ) : (
            <button
              onClick={play}
              disabled={currentStep >= steps.length}
              className="px-3 py-1 text-xs bg-primary hover:bg-primary/80 rounded transition-all flex items-center gap-1 disabled:opacity-50"
            >
              ▶ Play
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-surface rounded-full mb-6 overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-primary to-green-500 transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Steps */}
      <div className="relative">
        {/* Connection lines */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border" />
        
        {/* Step items */}
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={step.id} className="relative flex items-start gap-4">
              {/* Node */}
              <div 
                className={`relative z-10 w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold transition-all duration-300 ${getStatusColor(step.status)}`}
              >
                {getStatusIcon(step.status)}
              </div>
              
              {/* Content */}
              <div className="flex-1 pt-2">
                <div className="flex items-center gap-2">
                  <span className={`font-medium ${step.status === 'pending' ? 'text-gray-400' : 'text-white'}`}>
                    {step.name}
                  </span>
                  {step.status === 'running' && (
                    <span className="text-xs text-primary animate-pulse">Running...</span>
                  )}
                  {step.duration && (
                    <span className="text-xs text-gray-500">{step.duration}ms</span>
                  )}
                </div>
                
                {/* Expandable details for running step */}
                {step.status === 'running' && index === currentStep && (
                  <div className="mt-2 p-3 bg-surface/80 rounded-lg border border-border">
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <div className="w-2 h-2 rounded-full bg-primary animate-ping"></div>
                      Executing step {index + 1} of {steps.length}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-border flex items-center justify-between text-sm">
        <span className="text-gray-400">
          Progress: {steps.filter(s => s.status === 'completed').length} / {steps.length} steps
        </span>
        <span className={`font-medium ${
          progress === 100 ? 'text-green-400' : 
          progress > 0 ? 'text-primary' : 'text-gray-400'
        }`}>
          {Math.round(progress)}% Complete
        </span>
      </div>
    </div>
  );
}
