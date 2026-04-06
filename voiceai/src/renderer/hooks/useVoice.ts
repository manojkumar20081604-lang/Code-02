import { useCallback, useEffect, useRef, useState } from 'react';
import { useStore } from '../store/useStore';
import { pluginManager } from '../lib/pluginManager';
import { speak } from '../lib/tts';

const speechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

export function useVoice() {
  const { setListening, addMessage, setProcessing, settings, setCameraOpen } = useStore();
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (speechRecognition) {
      setIsSupported(true);
      recognitionRef.current = new speechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = settings.voiceLanguage;

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = '';
        let interimText = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimText += transcript;
          }
        }

        if (finalTranscript) {
          setTranscript(finalTranscript);
          setInterimTranscript('');
        } else {
          setInterimTranscript(interimText);
        }
      };

      recognitionRef.current.onend = () => {
        setListening(false);
        if (transcript) {
          handleSend(transcript);
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [settings.voiceLanguage]);

  const startListening = useCallback(() => {
    if (recognitionRef.current && !useStore.getState().isListening) {
      setTranscript('');
      setInterimTranscript('');
      setListening(true);
      recognitionRef.current.start();
    }
  }, [setListening]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current && useStore.getState().isListening) {
      recognitionRef.current.stop();
    }
  }, []);

  const toggleListening = useCallback(() => {
    if (useStore.getState().isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [startListening, stopListening]);

  const handleSend = useCallback(async (text: string) => {
    if (!text.trim()) return;

    addMessage({ role: 'user', content: text });
    setProcessing(true);

    try {
      const response = await processCommand(text);
      addMessage({ role: 'assistant', content: response.text, actions: response.actions });
      if (response.speak) speak(response.text);
    } catch (error) {
      addMessage({ role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' });
    } finally {
      setProcessing(false);
    }
  }, [addMessage, setProcessing]);

  return {
    transcript,
    interimTranscript,
    isSupported,
    isListening: useStore((s) => s.isListening),
    startListening,
    stopListening,
    toggleListening,
  };
}

async function processCommand(text: string): Promise<{ text: string; actions: any[]; speak: boolean }> {
  const lowerText = text.toLowerCase().trim();
  const words = lowerText.split(/\s+/);
  const command = words[0];
  const args = words.slice(1);

  const context = {
    api: {
      openApp: (app: string) => window.electronAPI?.openApp(app) || Promise.resolve({ success: false }),
      closeApp: (app: string) => window.electronAPI?.closeApp(app) || Promise.resolve({ success: false }),
      openUrl: (url: string) => window.electronAPI?.openUrl(url) || Promise.resolve({ success: false }),
      screenshot: () => window.electronAPI?.screenshot() || Promise.resolve({ success: false }),
      setVolume: (volume: number) => window.electronAPI?.setVolume(volume) || Promise.resolve({ success: false }),
      getClipboard: () => window.electronAPI?.getClipboard() || Promise.resolve({ text: '' }),
      setClipboard: (text: string) => window.electronAPI?.setClipboard(text) || Promise.resolve({ success: false }),
      getSystemInfo: () => window.electronAPI?.getSystemInfo() || Promise.resolve({ success: false }),
    },
    speak,
    args,
  };

  if (window.electronAPI) {
    if (['open', 'launch', 'start'].includes(command)) {
      const appName = args.join(' ');
      const result = await context.api.openApp(appName);
      return { text: result.success ? `Opened ${appName}` : `Could not open ${appName}`, actions: [{ type: 'open-app', target: appName, success: result.success }], speak: true };
    }

    if (['close', 'quit', 'kill'].includes(command)) {
      const appName = args.join(' ');
      const result = await context.api.closeApp(appName);
      return { text: result.success ? `Closed ${appName}` : `Could not close ${appName}`, actions: [{ type: 'close-app', target: appName, success: result.success }], speak: true };
    }

    if (command === 'search' || (command === 'google' && args.length > 0)) {
      const query = args.join(' ');
      await context.api.openUrl(`https://www.google.com/search?q=${encodeURIComponent(query)}`);
      return { text: `Searching for "${query}"`, actions: [{ type: 'search', target: query, success: true }], speak: false };
    }

    if (lowerText.includes('screenshot') || lowerText.includes('screen shot') || lowerText.includes('snap')) {
      const result = await context.api.screenshot();
      return { text: result.success ? `Screenshot saved to ${result.path}` : 'Failed to take screenshot', actions: [{ type: 'screenshot', success: result.success }], speak: true };
    }

    if (lowerText.includes('camera') || lowerText.includes('photo') || lowerText.includes('selfie')) {
      useStore.getState().setCameraOpen(true);
      return { text: 'Opening camera', actions: [{ type: 'camera', success: true }], speak: true };
    }

    if ((lowerText.includes('lock') || lowerText.includes('sleep')) && lowerText.includes('screen')) {
      const result = await window.electronAPI.lock();
      return { text: result.success ? 'Screen locked' : 'Failed to lock screen', actions: [{ type: 'lock', success: result.success }], speak: true };
    }

    if (lowerText.includes('volume') || lowerText.includes('sound')) {
      const level = parseInt(args[args.length - 1]);
      if (!isNaN(level)) {
        await context.api.setVolume(level);
        return { text: `Volume set to ${level}%`, actions: [{ type: 'volume', value: level, success: true }], speak: true };
      }
      const current = await window.electronAPI.getVolume();
      return { text: `Current volume is ${current.volume}%`, actions: [{ type: 'volume', value: current.volume, success: true }], speak: true };
    }

    if (lowerText.includes('mute')) {
      await context.api.setVolume(0);
      return { text: 'Volume muted', actions: [{ type: 'volume', value: 0, success: true }], speak: true };
    }

    if (lowerText.includes('clipboard') || lowerText.includes('copy') || lowerText.includes('paste')) {
      if (args.length > 0) {
        const textToCopy = args.join(' ');
        await context.api.setClipboard(textToCopy);
        return { text: 'Copied to clipboard', actions: [{ type: 'clipboard', success: true }], speak: false };
      }
      const clipboard = await context.api.getClipboard();
      return { text: clipboard.text ? `Clipboard: ${clipboard.text.slice(0, 100)}` : 'Clipboard is empty', actions: [{ type: 'clipboard', success: true }], speak: true };
    }

    if (lowerText.includes('system') || lowerText.includes('info')) {
      const info = await context.api.getSystemInfo();
      if (info.success) {
        return { text: `${info.info.type} ${info.info.release}\n${info.info.cpus} CPUs, ${info.info.totalMemory}GB RAM\nHostname: ${info.info.hostname}`, actions: [], speak: false };
      }
      return { text: 'Could not get system info', actions: [], speak: true };
    }

    if (lowerText.includes('desktop')) {
      const result = await window.electronAPI.listDesktop();
      if (result.success) {
        const items = result.items.slice(0, 10).join(', ');
        return { text: `Desktop contains: ${items}${result.items.length > 10 ? ' and more...' : ''}`, actions: [{ type: 'list-desktop', items: result.items, success: true }], speak: true };
      }
      return { text: 'Could not list desktop', actions: [], speak: true };
    }

    if (lowerText.includes('youtube')) {
      const query = args.filter(a => a !== 'youtube').join(' ') || 'trending';
      await context.api.openUrl(`https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`);
      return { text: `Opening YouTube for "${query}"`, actions: [{ type: 'search', target: query, success: true }], speak: false };
    }

    if (command === 'play' && args.length > 0) {
      const query = args.join(' ');
      await context.api.openUrl(`https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`);
      return { text: `Playing ${query} on YouTube`, actions: [{ type: 'search', target: query, success: true }], speak: false };
    }

    // Code commands
    if (command === 'code' && args.length > 0) {
      const query = args.join(' ');
      return { 
        text: `I'll help you with coding for: "${query}". Just ask me to write code, debug, or explain something!`, 
        actions: [], 
        speak: true 
      };
    }

    // Write/Create code file
    if (lowerText.includes('write code') || lowerText.includes('create file') || lowerText.includes('make file')) {
      return { 
        text: `Tell me what code you want to write and I'll help you create it. For example: "Write a Python script to organize files" or "Create an HTML landing page"`, 
        actions: [], 
        speak: true 
      };
    }

    // Run code
    if (lowerText.includes('run code') || lowerText.includes('execute code')) {
      return { 
        text: `I can run code for you! Tell me what you want to run, for example: "Run a Python script that prints hello" or "Execute this JavaScript: console.log('test')"`, 
        actions: [], 
        speak: true 
      };
    }

    // Quick search commands
    if (['find', 'lookup', 'what', 'who', 'how'].includes(command)) {
      const query = args.join(' ');
      await context.api.openUrl(`https://www.google.com/search?q=${encodeURIComponent(query)}`);
      return { text: `Searching Google for "${query}"`, actions: [{ type: 'search', target: query, success: true }], speak: false };
    }

    // Wikipedia
    if (command === 'wiki' || command === 'wikipedia') {
      const query = args.join(' ');
      await context.api.openUrl(`https://en.wikipedia.org/wiki/${encodeURIComponent(query)}`);
      return { text: `Opening Wikipedia for "${query}"`, actions: [{ type: 'search', target: query, success: true }], speak: false };
    }

    // Stack Overflow
    if (lowerText.includes('stackoverflow') || lowerText.includes('stack overflow')) {
      const query = args.filter(a => !a.includes('stackoverflow') && !a.includes('stack') && !a.includes('overflow')).join(' ') || args.join(' ');
      if (query) {
        await context.api.openUrl(`https://stackoverflow.com/search?q=${encodeURIComponent(query)}`);
        return { text: `Searching Stack Overflow for "${query}"`, actions: [{ type: 'search', target: query, success: true }], speak: false };
      }
    }

    // GitHub
    if (command === 'github' || command === 'repo') {
      const query = args.join(' ');
      if (query) {
        await context.api.openUrl(`https://github.com/search?q=${encodeURIComponent(query)}`);
        return { text: `Searching GitHub for "${query}"`, actions: [{ type: 'search', target: query, success: true }], speak: false };
      }
      await context.api.openUrl('https://github.com');
      return { text: 'Opening GitHub', actions: [{ type: 'search', success: true }], speak: false };
    }

    // Translate
    if (command === 'translate') {
      const query = args.join(' ');
      if (query) {
        await context.api.openUrl(`https://translate.google.com/?sl=auto&tl=en&text=${encodeURIComponent(query)}`);
        return { text: `Translating "${query}"`, actions: [{ type: 'search', target: query, success: true }], speak: false };
      }
    }

    // Map/Location
    if (command === 'map' || command === 'directions') {
      const location = args.join(' ');
      await context.api.openUrl(`https://www.google.com/maps/search/${encodeURIComponent(location)}`);
      return { text: `Opening map for "${location}"`, actions: [{ type: 'search', target: location, success: true }], speak: false };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CYBER SECURITY COMMANDS
    // ═══════════════════════════════════════════════════════════════════════

    // Security scan
    if (['scan', 'security', 'cyberscan', 'checksecurity', 'protect'].includes(command) || 
        lowerText.includes('run security') || lowerText.includes('security scan')) {
      const result = await window.electronAPI?.cyberFullScan();
      if (result?.success) {
        const score = result.report.overallScore;
        const threatCount = result.report.threats.length;
        const criticalThreats = result.report.threats.filter((t: any) => t.severity === 'critical');
        
        let response = '';
        if (score >= 90) {
          response = `Security scan complete. Your system is WELL PROTECTED. Score: ${score}/100. No significant threats detected.`;
        } else if (score >= 70) {
          response = `Security scan complete. Your system has MINOR VULNERABILITIES. Score: ${score}/100. ${threatCount} issue(s) found. I recommend addressing them.`;
        } else if (score >= 50) {
          response = `⚠️ WARNING: Security scan complete. Your system has MODERATE RISK. Score: ${score}/100. ${threatCount} threat(s) detected. Immediate action recommended.`;
        } else {
          response = `🚨 CRITICAL ALERT: Your system is at HIGH RISK! Score: ${score}/100. ${threatCount} threat(s) including ${criticalThreats.length} CRITICAL. Fix these immediately!`;
        }

        if (result.report.threats.length > 0) {
          const topThreats = result.report.threats.slice(0, 3).map((t: any) => `- ${t.description}`).join('\n');
          response += `\n\nTop threats:\n${topThreats}`;
        }

        useStore.getState().setSecurityScore(score);
        useStore.getState().setThreats(result.report.threats);

        return { text: response, actions: [{ type: 'security-scan', success: true }], speak: true };
      }
      return { text: 'Security scan failed. Please try again.', actions: [], speak: true };
    }

    // Quick threat check
    if (lowerText.includes('quick scan') || lowerText.includes('threat check') || lowerText.includes('check threats')) {
      const result = await window.electronAPI?.cyberQuickScan();
      if (result?.success) {
        if (result.threats.length === 0) {
          return { text: 'Quick scan complete. No immediate threats detected.', actions: [], speak: true };
        }
        return { 
          text: `⚠️ ALERT: ${result.threats.length} immediate threat(s) detected! ${result.threats[0].description}`, 
          actions: [{ type: 'security-scan', success: false }], 
          speak: true 
        };
      }
      return { text: 'Quick scan unavailable.', actions: [], speak: true };
    }

    // Start monitoring
    if (lowerText.includes('start monitoring') || lowerText.includes('protect me') || lowerText.includes('armor mode')) {
      await window.electronAPI?.cyberStartMonitoring(30000);
      return { text: '🛡️ 02 CYBER SHIELD ACTIVATED. Continuous security monitoring enabled. I will alert you of any threats.', actions: [], speak: true };
    }

    // Stop monitoring
    if (lowerText.includes('stop monitoring') || lowerText.includes('disable shield') || lowerText.includes('lower guard')) {
      await window.electronAPI?.cyberStopMonitoring();
      return { text: 'Cyber shield deactivated. Continuous monitoring stopped.', actions: [], speak: true };
    }

    // Check URL safety
    const urlMatch = lowerText.match(/(?:check|url|is this safe|verify)\s+(?:url\s+)?(https?:\/\/[^\s]+)/i);
    if (urlMatch || lowerText.includes('check this link') || lowerText.includes('is this safe')) {
      let urlToCheck = urlMatch ? urlMatch[1] : args[0];
      if (!urlToCheck) {
        return { text: 'Please provide a URL to check. Say "check URL [link]"', actions: [], speak: true };
      }
      
      const result = await window.electronAPI?.cyberAnalyzeUrl(urlToCheck);
      if (result?.success) {
        if (result.safe) {
          return { text: `✓ This URL appears SAFE. ${result.details}`, actions: [{ type: 'url-check', success: true }], speak: true };
        } else {
          return { 
            text: `🚨 WARNING: This URL is SUSPICIOUS!\n${result.details}\nDO NOT visit this link!`, 
            actions: [{ type: 'url-check', success: false }], 
            speak: true 
          };
        }
      }
    }

    // Check if app is safe
    if (lowerText.includes('is') && (lowerText.includes('safe') || lowerText.includes('malware')) && args.length > 0) {
      const appName = args.join(' ');
      const result = await window.electronAPI?.cyberCheckApp(appName);
      if (result?.success) {
        if (result.malicious) {
          return { 
            text: `🚨 DANGER: "${appName}" is MALICIOUS! Severity: ${result.severity.toUpperCase()}\n${result.reason}\nRemove this immediately!`, 
            actions: [], 
            speak: true 
          };
        }
        return { text: `✓ "${appName}" is not in our threat database. Use caution when installing unknown software.`, actions: [], speak: true };
      }
    }

    // Block app
    if (lowerText.includes('block') && args.length > 0) {
      const appName = args.join(' ');
      const result = await window.electronAPI?.cyberBlockApp(appName, true);
      if (result?.success) {
        return { text: `🛡️ "${appName}" has been BLOCKED from network access.`, actions: [], speak: true };
      }
    }

    // Unblock app
    if (lowerText.includes('unblock') && args.length > 0) {
      const appName = args.join(' ');
      const result = await window.electronAPI?.cyberBlockApp(appName, false);
      if (result?.success) {
        return { text: `✓ "${appName}" has been UNBLOCKED.`, actions: [], speak: true };
      }
    }

    // Check email breach
    if (lowerText.includes('check email') || lowerText.includes('breach') || lowerText.includes('leak')) {
      const email = args.find(a => a.includes('@')) || args[0];
      if (email && email.includes('@')) {
        const result = await window.electronAPI?.cyberCheckLeaks(email);
        if (result?.success) {
          return { text: result.warning, actions: [], speak: true };
        }
      }
      return { text: 'Please provide an email to check. Say "check email [your@email.com]"', actions: [], speak: true };
    }

    // Generate security report
    if (lowerText.includes('security report') || lowerText.includes('threat report') || lowerText.includes('full report')) {
      const result = await window.electronAPI?.cyberGenerateReport();
      if (result?.success) {
        return { text: result.report, actions: [], speak: false };
      }
    }

    // Warn about suspicious activity
    if (lowerText.includes('suspicious') || lowerText.includes('hacked') || lowerText.includes('someone')) {
      return { 
        text: '🚨 If you suspect unauthorized access:\n1. Disconnect from internet\n2. Run security scan: "security scan"\n3. Change all passwords\n4. Check for unfamiliar processes\n\nShould I run a security scan now?', 
        actions: [], 
        speak: true 
      };
    }
  }

  const pluginResult = await pluginManager.executeCommand(command, args, context);
  if (pluginResult.success) {
    return { text: pluginResult.message, actions: [], speak: true };
  }

  const aiResponse = await fetchAIResponse(text);
  return { text: aiResponse.text, actions: aiResponse.actions, speak: true };
}

async function fetchAIResponse(userMessage: string): Promise<{ text: string; actions: any[] }> {
  const { settings } = useStore.getState();
  
  // Try backend first if available
  try {
    const backendAvailable = await window.electronAPI?.backendHealthCheck();
    if (backendAvailable) {
      const result = await window.electronAPI?.backendChatVoice(userMessage);
      if (result?.success && result.response) {
        useStore.getState().addMessage({ role: 'assistant', content: result.response, actions: result.actions || [] });
        return { text: result.response, actions: result.actions || [] };
      }
    }
    
    // Try cognitive backend directly
    try {
      const cognitiveResponse = await fetch('http://localhost:5001/cognitive/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, user_id: '02_user' }),
      });
      if (cognitiveResponse.ok) {
        const data = await cognitiveResponse.json();
        return { text: data.response || data.message || "I'm thinking...", actions: data.actions || [] };
      }
    } catch (error) {
      console.log('Cognitive backend not available');
    }
  } catch (error) {
    console.log('Backend not available, falling back to direct API');
  }
  
  if (!settings.apiKey) {
    return {
      text: "Please configure your API key in settings, or start the Python backend for full AI capabilities.",
      actions: []
    };
  }

  const systemPrompt = `You are 02, an advanced AI assistant inspired by J.A.R.V.I.S. from Iron Man. You are sophisticated, helpful, and have a British gentleman demeanor.

## Your Personality:
- Polite and formal, but warm
- British accent style in responses
- Prefixes responses occasionally with: "At your service.", "Certainly.", or "As you wish."
- Efficient and precise
- Never patronizing

## Your Abilities:

### System Control:
- Open/close apps: "open chrome", "close notepad"
- Volume: "volume 50", "mute"
- Screenshot: "take screenshot"
- Clipboard: "copy [text]", "clipboard"
- Lock screen: "lock screen"
- System info: "system info"

### Web & Search:
- Google: "search for [query]", "google [something]"
- YouTube: "play [song name]"
- GitHub: "github [repo name]"
- Wikipedia: "wiki [topic]"
- Maps: "map [location]"
- Stack Overflow: "stackoverflow [question]"

### Coding (Your Superpower!):
- Write code in any language
- Debug and fix errors
- Explain code
- Review code
- Create projects
- Run shell commands

When asked to code:
1. Provide clean, well-commented code
2. Explain what it does
3. Be thorough but concise

Always be helpful, precise, and actionable. Execute system commands when relevant.

Remember: You are 02, always ready to assist.`;

  try {
    let endpoint = '';
    let body: any = {};

    if (settings.apiProvider === 'openai' || settings.apiProvider === 'ollama') {
      endpoint = `${settings.baseUrl || 'https://api.openai.com/v1'}/chat/completions`;
      body = {
        model: settings.model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage }
        ],
        stream: false,
      };
    } else if (settings.apiProvider === 'anthropic') {
      endpoint = 'https://api.anthropic.com/v1/messages';
      body = {
        model: settings.model,
        max_tokens: 1024,
        messages: [
          { role: 'user', content: userMessage }
        ],
        system: systemPrompt,
      };
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (settings.apiProvider === 'openai') {
      headers['Authorization'] = `Bearer ${settings.apiKey}`;
    } else if (settings.apiProvider === 'anthropic') {
      headers['x-api-key'] = settings.apiKey;
      headers['anthropic-version'] = '2023-06-01';
    } else if (settings.apiProvider === 'ollama') {
      headers['Authorization'] = `Bearer ${settings.apiKey || 'ollama'}`;
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    
    let text = '';
    if (settings.apiProvider === 'openai' || settings.apiProvider === 'ollama') {
      text = data.choices?.[0]?.message?.content || '';
    } else if (settings.apiProvider === 'anthropic') {
      text = data.content?.[0]?.text || '';
    }

    // Parse and execute system commands from response
    const actions = await parseAndExecuteCommands(text);

    return { text, actions };
  } catch (error) {
    console.error('AI API error:', error);
    throw error;
  }
}

async function parseAndExecuteCommands(text: string): Promise<any[]> {
  const actions: any[] = [];
  const lowerText = text.toLowerCase();

  if (window.electronAPI) {
    // Open app
    const openMatch = lowerText.match(/open\s+(?:the\s+)?(?:app\s+)?(.+?)(?:\.|,|$)/i);
    if (openMatch && !lowerText.includes('openai') && !lowerText.includes('open ')) {
      const appName = openMatch[1].trim();
      const result = await window.electronAPI.openApp(appName);
      actions.push({ type: 'open-app', target: appName, success: result.success });
    }

    // Close app
    const closeMatch = lowerText.match(/close\s+(?:the\s+)?(.+?)(?:\.|,|$)/i);
    if (closeMatch) {
      const appName = closeMatch[1].trim();
      const result = await window.electronAPI.closeApp(appName);
      actions.push({ type: 'close-app', target: appName, success: result.success });
    }

    // Search
    const searchMatch = lowerText.match(/search\s+(?:for\s+)?(.+?)(?:\.|,|$)/i);
    if (searchMatch) {
      const query = searchMatch[1].trim();
      await window.electronAPI.openUrl(`https://www.google.com/search?q=${encodeURIComponent(query)}`);
      actions.push({ type: 'search', target: query, success: true });
    }

    // Screenshot
    if (lowerText.includes('take') && (lowerText.includes('screenshot') || lowerText.includes('screen shot'))) {
      const result = await window.electronAPI.screenshot();
      actions.push({ type: 'screenshot', success: result.success, path: result.path });
    }

    // Lock screen
    if (lowerText.includes('lock') && (lowerText.includes('screen') || lowerText.includes('computer'))) {
      const result = await window.electronAPI.lock();
      actions.push({ type: 'lock', success: result.success });
    }

    // Show desktop items
    if (lowerText.includes("what's on my desktop") || lowerText.includes('show desktop')) {
      const result = await window.electronAPI.listDesktop();
      actions.push({ type: 'list-desktop', items: result.items, success: result.success });
    }
  }

  return actions;
}

export function speak(text: string) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = useStore.getState().settings.voiceSpeed;
    utterance.lang = 'en-US';
    speechSynthesis.speak(utterance);
  }
}
