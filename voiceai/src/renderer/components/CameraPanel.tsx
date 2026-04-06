import { useEffect, useRef } from 'react';
import { useCamera } from '../hooks/useCamera';
import { useStore } from '../store/useStore';

function CameraPanel() {
  const { cameraOpen, setCameraOpen, addMessage } = useStore();
  const { isActive, error, startCamera, stopCamera, captureAndSave, setVideoRef, isSupported } = useCamera();
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (cameraOpen && isSupported && !isActive) {
      startCamera();
    }
    if (videoRef.current) {
      setVideoRef(videoRef.current);
    }
  }, [cameraOpen, isSupported, isActive, startCamera, setVideoRef]);

  useEffect(() => {
    if (videoRef.current && isActive) {
      videoRef.current.srcObject = useCamera.getState?.()?.stream || null;
    }
  }, [isActive]);

  const handleCapture = async () => {
    const result = await captureAndSave();
    if (result.success) {
      addMessage({ role: 'system', content: `Photo saved: ${result.path}` });
      setCameraOpen(false);
      stopCamera();
    }
  };

  const handleClose = () => {
    setCameraOpen(false);
    stopCamera();
  };

  if (!cameraOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="glass rounded-xl overflow-hidden max-w-2xl w-full mx-4">
        <div className="p-4 flex items-center justify-between border-b border-white/10">
          <h3 className="text-lg font-semibold text-text-primary">Camera</h3>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="aspect-video bg-black flex items-center justify-center">
          {error ? (
            <div className="text-center p-8">
              <svg className="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-red-400">{error}</p>
              <p className="text-text-secondary text-sm mt-2">Please allow camera access in your browser settings</p>
            </div>
          ) : (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
          )}
        </div>

        <div className="p-4 flex items-center justify-center gap-4">
          <button
            onClick={handleClose}
            className="px-6 py-2 glass rounded-lg text-text-secondary hover:bg-white/10 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleCapture}
            disabled={!isActive}
            className="px-8 py-2 bg-primary rounded-lg text-white font-medium hover:bg-primary/80 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Capture
          </button>
        </div>
      </div>
    </div>
  );
}

export default CameraPanel;
