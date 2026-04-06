import { useCallback, useEffect, useRef, useState } from 'react';

interface CameraState {
  isSupported: boolean;
  isActive: boolean;
  error: string | null;
  stream: MediaStream | null;
}

export function useCamera() {
  const [state, setState] = useState<CameraState>({
    isSupported: false,
    isActive: false,
    error: null,
    stream: null,
  });
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    const isSupported = 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices;
    setState(prev => ({ ...prev, isSupported }));
  }, []);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
        audio: false,
      });
      streamRef.current = stream;
      setState({ isSupported: true, isActive: true, error: null, stream });
      return stream;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Camera access denied';
      setState(prev => ({ ...prev, isActive: false, error: message }));
      return null;
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setState({ isSupported: true, isActive: false, error: null, stream: null });
  }, []);

  const capturePhoto = useCallback(async (): Promise<string | null> => {
    if (!videoRef.current || !streamRef.current) {
      await startCamera();
      if (!videoRef.current) return null;
    }

    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    
    ctx.drawImage(video, 0, 0);
    return canvas.toDataURL('image/png');
  }, [startCamera]);

  const captureAndSave = useCallback(async (): Promise<{ success: boolean; path?: string; error?: string }> => {
    const dataUrl = await capturePhoto();
    if (!dataUrl) {
      return { success: false, error: 'Failed to capture photo' };
    }

    if (window.electronAPI) {
      const result = await window.electronAPI.cameraCapture();
      if (result.success && result.path) {
        const link = document.createElement('a');
        link.download = result.path.split(/[\\/]/).pop() || `photo-${Date.now()}.png`;
        link.href = dataUrl;
        link.click();
        return { success: true, path: result.path };
      }
    }
    return { success: true, path: dataUrl };
  }, [capturePhoto]);

  const setVideoRef = useCallback((video: HTMLVideoElement | null) => {
    videoRef.current = video;
    if (video && streamRef.current) {
      video.srcObject = streamRef.current;
    }
  }, []);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return {
    ...state,
    videoRef,
    setVideoRef,
    startCamera,
    stopCamera,
    capturePhoto,
    captureAndSave,
  };
}
