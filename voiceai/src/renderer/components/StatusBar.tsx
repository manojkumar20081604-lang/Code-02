import { useStore } from '../store/useStore';

function StatusBar() {
  const { connectionStatus, settings, isListening, isProcessing } = useStore();

  return (
    <footer className="h-8 glass-dark flex items-center justify-between px-4 text-xs text-text-secondary">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              connectionStatus === 'online'
                ? 'bg-green-400'
                : connectionStatus === 'connecting'
                ? 'bg-yellow-400 animate-pulse'
                : 'bg-red-400'
            }`}
          />
          <span className="capitalize">
            {connectionStatus === 'online' 
              ? `Connected (${settings.apiProvider})`
              : connectionStatus === 'connecting'
              ? 'Connecting...'
              : 'Offline'
            }
          </span>
        </div>

        {(isListening || isProcessing) && (
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isListening ? 'bg-red-400 animate-pulse' : 'bg-primary animate-pulse'}`} />
            <span>{isListening ? 'Listening' : 'Processing'}</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
          <span>Voice {settings.voiceSpeed}x</span>
        </div>

        <div className="flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
          </svg>
          <span>{settings.voiceLanguage}</span>
        </div>

        <div className="flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>{settings.model}</span>
        </div>
      </div>
    </footer>
  );
}

export default StatusBar;
