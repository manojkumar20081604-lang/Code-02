import { useStore } from '../store/useStore';

export function speak(text: string) {
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const { settings } = useStore.getState();
    
    // J.A.R.V.I.S. mode - British, slightly slower, formal
    if (settings.jarvisMode) {
      utterance.rate = 0.9; // Slightly slower
      utterance.pitch = 0.95; // Slightly deeper
      utterance.lang = 'en-GB'; // British accent
      
      // Add JARVIS-style phrases
      const prefixes = [
        "At your service.",
        "Certainly.",
        "Understood.",
        "As you wish.",
        "Right away."
      ];
      const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    }
    
    // Normal mode settings
    if (!settings.jarvisMode) {
      utterance.rate = settings.voiceSpeed;
      utterance.lang = settings.voiceLanguage;
    }
    
    const voices = speechSynthesis.getVoices();
    
    // Try to find a British voice for J.A.R.V.I.S. mode
    if (settings.jarvisMode) {
      const britishVoice = voices.find(v => 
        v.lang.startsWith('en-GB') || 
        v.name.toLowerCase().includes('british') ||
        v.name.toLowerCase().includes('daniel') ||
        v.name.toLowerCase().includes('fred') ||
        v.name.toLowerCase().includes('harry')
      );
      if (britishVoice) {
        utterance.voice = britishVoice;
      }
    } else {
      const preferredVoice = voices.find(v => 
        v.name.toLowerCase().includes(settings.voice.toLowerCase()) ||
        v.lang.startsWith(settings.voiceLanguage.split('-')[0])
      );
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
    }
    
    speechSynthesis.speak(utterance);
  }
}

export function stopSpeaking() {
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel();
  }
}
