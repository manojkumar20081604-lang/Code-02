import { app, BrowserWindow, ipcMain, Tray, Menu, globalShortcut, nativeImage, dialog, Notification } from 'electron';
import * as path from 'path';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import Store from 'electron-store';
import { cyberSecurity, SecurityReport, ThreatInfo } from './cyberSecurity';

const execAsync = promisify(exec);
const store = new Store();

const API_URL = 'http://localhost:5000';
let pythonServer: any = null;

async function checkPythonServer(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

async function startPythonServer(): Promise<void> {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const serverPath = path.join(__dirname, '../../cyber-assistant/api_server.py');
  
  try {
    pythonServer = spawn(pythonPath, [serverPath], {
      cwd: path.join(__dirname, '../../cyber-assistant'),
      detached: true,
      stdio: 'ignore'
    });
    pythonServer.unref();
    
    for (let i = 0; i < 10; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (await checkPythonServer()) {
        console.log('Python backend server started successfully');
        return;
      }
    }
    console.warn('Python server may not have started - some features may be unavailable');
  } catch (error) {
    console.error('Failed to start Python server:', error);
  }
}

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;

const isDev = process.env.NODE_ENV !== 'production' || !app.isPackaged;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    minWidth: 600,
    minHeight: 500,
    frame: false,
    transparent: false,
    backgroundColor: '#0a0a0f',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, '../../public/icon.png'),
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('close', (event) => {
    if (store.get('minimizeToTray', true)) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createTray() {
  const iconPath = path.join(__dirname, '../../public/icon.png');
  let trayIcon: Electron.NativeImage;
  
  try {
    trayIcon = nativeImage.createFromPath(iconPath);
    if (trayIcon.isEmpty()) {
      trayIcon = nativeImage.createEmpty();
    }
  } catch {
    trayIcon = nativeImage.createEmpty();
  }

  tray = new Tray(trayIcon.resize({ width: 16, height: 16 }));

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show VoiceAI', click: () => mainWindow?.show() },
    { label: 'Start Voice', click: () => mainWindow?.webContents.send('voice:toggle') },
    { type: 'separator' },
    { label: 'Settings', click: () => mainWindow?.webContents.send('open-settings') },
    { type: 'separator' },
    { label: 'Quit', click: () => { 
      store.set('minimizeToTray', false);
      app.quit(); 
    }},
  ]);

  tray.setToolTip('VoiceAI Assistant');
  tray.setContextMenu(contextMenu);
  tray.on('click', () => mainWindow?.show());
}

function registerShortcuts() {
  globalShortcut.register('CommandOrControl+Shift+Space', () => {
    mainWindow?.webContents.send('voice:toggle');
  });
}

function setupIPC() {
  // Window controls
  ipcMain.on('window:minimize', () => mainWindow?.minimize());
  ipcMain.on('window:maximize', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow?.maximize();
    }
  });
  ipcMain.on('window:close', () => mainWindow?.hide());

  // System control - Open application
  ipcMain.handle('system:open-app', async (_, appName: string) => {
    try {
      if (process.platform === 'win32') {
        await execAsync(`start ${appName}`);
      } else if (process.platform === 'darwin') {
        await execAsync(`open -a "${appName}"`);
      } else {
        await execAsync(`xdg-open ${appName}`);
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Close application
  ipcMain.handle('system:close-app', async (_, appName: string) => {
    try {
      if (process.platform === 'win32') {
        await execAsync(`taskkill /IM ${appName}.exe /F`);
      } else if (process.platform === 'darwin') {
        await execAsync(`pkill "${appName}"`);
      } else {
        await execAsync(`pkill ${appName}`);
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Get running apps
  ipcMain.handle('system:get-running-apps', async () => {
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync('tasklist /FO CSV /NH');
        const apps = stdout.split('\n')
          .map(line => {
            const match = line.match(/"([^"]+)"/);
            return match ? match[1].replace('.exe', '') : null;
          })
          .filter(Boolean);
        return { success: true, apps: [...new Set(apps)] };
      } else if (process.platform === 'darwin') {
        const { stdout } = await execAsync('osascript -e \'tell application "System Events" to name of processes where background only is false\'');
        return { success: true, apps: stdout.trim().split(', ') };
      }
      return { success: true, apps: [] };
    } catch (error) {
      return { success: false, error: String(error), apps: [] };
    }
  });

  // System control - Open URL in browser
  ipcMain.handle('system:open-url', async (_, url: string) => {
    try {
      if (process.platform === 'win32') {
        await execAsync(`start ${url}`);
      } else if (process.platform === 'darwin') {
        await execAsync(`open ${url}`);
      } else {
        await execAsync(`xdg-open ${url}`);
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Search web
  ipcMain.handle('system:search', async (_, query: string) => {
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    return ipcMain.emit('system:open-url', _, searchUrl);
  });

  // System control - Take screenshot
  ipcMain.handle('system:screenshot', async () => {
    if (!mainWindow) return { success: false, error: 'No window' };
    const screenshot = await mainWindow.webContents.capturePage();
    const filePath = path.join(app.getPath('pictures'), `screenshot-${Date.now()}.png`);
    const { filePath: savedPath } = await dialog.showSaveDialog({
      defaultPath: filePath,
      filters: [{ name: 'Images', extensions: ['png'] }]
    });
    if (savedPath) {
      require('fs').writeFileSync(savedPath, screenshot.toPNG());
      return { success: true, path: savedPath };
    }
    return { success: false, error: 'Cancelled' };
  });

  // System control - Lock screen
  ipcMain.handle('system:lock', async () => {
    try {
      if (process.platform === 'win32') {
        await execAsync('rundll32.exe user32.dll,LockWorkStation');
      } else if (process.platform === 'darwin') {
        await execAsync('pmset displaysleepnow');
      } else {
        await execAsync('loginctl lock-session');
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Shutdown
  ipcMain.handle('system:shutdown', async () => {
    try {
      if (process.platform === 'win32') {
        await execAsync('shutdown /s /t 0');
      } else if (process.platform === 'darwin') {
        await execAsync('sudo shutdown -h now');
      } else {
        await execAsync('sudo shutdown -h now');
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Open folder
  ipcMain.handle('system:open-folder', async (_, folderPath: string) => {
    try {
      if (process.platform === 'win32') {
        await execAsync(`explorer ${folderPath}`);
      } else if (process.platform === 'darwin') {
        await execAsync(`open ${folderPath}`);
      } else {
        await execAsync(`xdg-open ${folderPath}`);
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Volume control
  ipcMain.handle('system:set-volume', async (_, volume: number) => {
    try {
      const clampedVolume = Math.max(0, Math.min(100, volume));
      if (process.platform === 'win32') {
        await execAsync(`powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)")`);
        // Set volume via PowerShell
        await execAsync(`powershell -Command "(Get-AudioDevice -Playback -Index 0).Volume = ${clampedVolume}"`);
      } else if (process.platform === 'darwin') {
        await execAsync(`osascript -e 'set volume output volume ${clampedVolume}'`);
      } else {
        await execAsync(`amixer -D pulse sset Master ${clampedVolume}%`);
      }
      return { success: true, volume: clampedVolume };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  ipcMain.handle('system:get-volume', async () => {
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync(`powershell -Command "(Get-AudioDevice -Playback -Index 0).Volume"`);
        return { success: true, volume: parseInt(stdout.trim()) || 50 };
      } else if (process.platform === 'darwin') {
        const { stdout } = await execAsync(`osascript -e 'output volume of (get volume settings)'`);
        return { success: true, volume: parseInt(stdout.trim()) || 50 };
      }
      return { success: true, volume: 50 };
    } catch {
      return { success: true, volume: 50 };
    }
  });

  // System control - Brightness control (Windows/Mac only)
  ipcMain.handle('system:set-brightness', async (_, brightness: number) => {
    try {
      const clampedBrightness = Math.max(0, Math.min(100, brightness));
      if (process.platform === 'win32') {
        await execAsync(`powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,${clampedBrightness})"`);
      } else if (process.platform === 'darwin') {
        await execAsync(`osascript -e 'set brightness of (do shell script "system_profiler SPDisplaysDataType -json" as JSON) to ${clampedBrightness / 100}'`);
      }
      return { success: true, brightness: clampedBrightness };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Clipboard
  ipcMain.handle('system:get-clipboard', async () => {
    try {
      let text = '';
      if (process.platform === 'win32') {
        const { stdout } = await execAsync(`powershell -Command "Get-Clipboard"`);
        text = stdout.trim();
      } else if (process.platform === 'darwin') {
        const { stdout } = await execAsync(`pbpaste`);
        text = stdout.trim();
      } else {
        const { stdout } = await execAsync(`xclip -selection clipboard -o`);
        text = stdout.trim();
      }
      return { success: true, text };
    } catch (error) {
      return { success: false, error: String(error), text: '' };
    }
  });

  ipcMain.handle('system:set-clipboard', async (_, text: string) => {
    try {
      if (process.platform === 'win32') {
        await execAsync(`powershell -Command "Set-Clipboard -Value '${text.replace(/'/g, "''")}'"`);
      } else if (process.platform === 'darwin') {
        await execAsync(`echo '${text.replace(/'/g, "'\\''")}' | pbcopy`);
      } else {
        await execAsync(`echo '${text.replace(/'/g, "'\\''")}' | xclip -selection clipboard`);
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Screenshot with camera
  ipcMain.handle('system:camera-capture', async () => {
    try {
      const filePath = path.join(app.getPath('pictures'), `camera-${Date.now()}.png`);
      // Camera capture requires renderer-side handling
      return { success: true, path: filePath };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Get system info
  ipcMain.handle('system:get-info', async () => {
    try {
      const os = require('os');
      return {
        success: true,
        info: {
          platform: process.platform,
          hostname: os.hostname(),
          type: os.type(),
          release: os.release(),
          cpus: os.cpus().length,
          totalMemory: Math.round(os.totalmem() / (1024 * 1024 * 1024)),
          freeMemory: Math.round(os.freemem() / (1024 * 1024 * 1024)),
          uptime: os.uptime(),
        }
      };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Execute custom command
  ipcMain.handle('system:execute', async (_, command: string) => {
    try {
      if (process.platform === 'win32') {
        await execAsync(command, { shell: 'cmd.exe' });
      } else {
        await execAsync(command, { shell: '/bin/bash' });
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Run code snippet
  ipcMain.handle('system:run-code', async (_, code: string, language: string) => {
    try {
      const fs = require('fs');
      const os = require('os');
      const tempDir = os.tmpdir();
      let filePath = '';
      let command = '';

      switch (language.toLowerCase()) {
        case 'python':
        case 'py':
          filePath = path.join(tempDir, `temp_${Date.now()}.py`);
          fs.writeFileSync(filePath, code);
          command = `python "${filePath}"`;
          break;
        case 'javascript':
        case 'js':
          filePath = path.join(tempDir, `temp_${Date.now()}.js`);
          fs.writeFileSync(filePath, code);
          command = `node "${filePath}"`;
          break;
        case 'bash':
        case 'shell':
          filePath = path.join(tempDir, `temp_${Date.now()}.sh`);
          fs.writeFileSync(filePath, code);
          command = `bash "${filePath}"`;
          break;
        case 'powershell':
        case 'ps1':
          filePath = path.join(tempDir, `temp_${Date.now()}.ps1`);
          fs.writeFileSync(filePath, code);
          command = `powershell "${filePath}"`;
          break;
        default:
          return { success: false, error: `Unsupported language: ${language}` };
      }

      const { stdout, stderr } = await execAsync(command, { timeout: 30000 });
      fs.unlinkSync(filePath);

      return {
        success: true,
        output: stdout || '(no output)',
        errors: stderr || null
      };
    } catch (error: any) {
      return { success: false, error: String(error.message || error) };
    }
  });

  // System control - Read file
  ipcMain.handle('system:read-file', async (_, filePath: string) => {
    try {
      const fs = require('fs');
      const content = fs.readFileSync(filePath, 'utf-8');
      return { success: true, content };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // System control - Write file
  ipcMain.handle('system:write-file', async (_, filePath: string, content: string) => {
    try {
      const fs = require('fs');
      fs.writeFileSync(filePath, content, 'utf-8');
      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // ═══════════════════════════════════════════════════════════════════════
  // CYBER SECURITY MODULE
  // ═══════════════════════════════════════════════════════════════════════

  // Full security scan
  ipcMain.handle('cyber:full-scan', async () => {
    try {
      const report = await cyberSecurity.scanSystem();
      return { success: true, report };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // Quick threat scan
  ipcMain.handle('cyber:quick-scan', async () => {
    try {
      const threats = await cyberSecurity.quickThreatScan();
      return { success: true, threats };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // Start continuous monitoring
  ipcMain.handle('cyber:start-monitoring', async (_, intervalMs?: number) => {
    cyberSecurity.startContinuousMonitoring(intervalMs);
    return { success: true };
  });

  // Stop monitoring
  ipcMain.handle('cyber:stop-monitoring', async () => {
    cyberSecurity.stopContinuousMonitoring();
    return { success: true };
  });

  // Get current threats
  ipcMain.handle('cyber:get-threats', async () => {
    return { success: true, threats: cyberSecurity.getThreats() };
  });

  // Analyze URL for phishing/malware
  ipcMain.handle('cyber:analyze-url', async (_, url: string) => {
    try {
      const result = await cyberSecurity.analyzeURL(url);
      return { success: true, ...result };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // Analyze file hash
  ipcMain.handle('cyber:analyze-hash', async (_, hash: string) => {
    try {
      const result = await cyberSecurity.analyzeFileHash(hash);
      return { success: true, ...result };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // Generate text report
  ipcMain.handle('cyber:generate-report', async () => {
    return { success: true, report: cyberSecurity.generateThreatReport() };
  });

  // Check if suspicious app
  ipcMain.handle('cyber:check-app', async (_, appName: string) => {
    const knownMalicious: Record<string, { severity: string; reason: string }> = {
      'mimikatz': { severity: 'critical', reason: 'Password extraction tool - often used in attacks' },
      'pwdump': { severity: 'critical', reason: 'Password hash dumper - malicious' },
      'netcat': { severity: 'high', reason: 'Network瑞士军刀 - can create backdoors' },
      'nc.exe': { severity: 'high', reason: 'Netcat - known backdoor tool' },
      'psexec': { severity: 'medium', reason: 'Remote execution tool - use with caution' },
      'wce.exe': { severity: 'critical', reason: 'Windows Credential Editor - malicious' },
      'fgdump': { severity: 'critical', reason: 'Password dumper - malicious' },
      'john': { severity: 'high', reason: 'Password cracker - security tool' },
      'hashcat': { severity: 'high', reason: 'Password cracker - security tool' },
      'hydra': { severity: 'high', reason: 'Password brute forcer - security tool' },
      'nmap': { severity: 'low', reason: 'Network scanner - security tool (if used legitimately)' },
    };

    const lowerName = appName.toLowerCase();
    const result = knownMalicious[lowerName];

    if (result) {
      return {
        success: true,
        malicious: true,
        severity: result.severity,
        reason: result.reason,
        warning: `⚠️ WARNING: "${appName}" is flagged as potentially dangerous!`,
      };
    }

    return {
      success: true,
      malicious: false,
      warning: null,
    };
  });

  // Show desktop notification for threats
  ipcMain.handle('cyber:alert', async (_, title: string, body: string) => {
    if (Notification.isSupported()) {
      new Notification({ title, body }).show();
    }
    return { success: true };
  });

  // Block/unblock internet for app
  ipcMain.handle('cyber:block-app', async (_, appName: string, block: boolean) => {
    try {
      if (process.platform === 'win32') {
        const ruleName = `02_BLOCK_${appName.toUpperCase()}`;
        if (block) {
          await execAsync(`netsh advfirewall firewall add rule name="${ruleName}" dir=out action=block program="%ProgramFiles%\\${appName}\\*.exe"`);
          await execAsync(`netsh advfirewall firewall add rule name="${ruleName}_in" dir=in action=block program="%ProgramFiles%\\${appName}\\*.exe"`);
        } else {
          await execAsync(`netsh advfirewall firewall delete rule name="${ruleName}"`);
          await execAsync(`netsh advfirewall firewall delete rule name="${ruleName}_in"`);
        }
      }
      return { success: true, blocked: block };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  });

  // Check for data leaks
  ipcMain.handle('cyber:check-leaks', async (_, email: string) => {
    try {
      const response = await fetch(`https://haveibeenpwned.com/api/v3/breachcheck/${encodeURIComponent(email)}?truncateResponse=false`, {
        headers: { 'User-Agent': '02-CyberSec-AI' },
      });

      if (response.status === 200) {
        const breaches = await response.json();
        const breachNames = breaches.map((b: any) => b.Name).join(', ');
        return {
          success: true,
          leaked: true,
          breachCount: breaches.length,
          breaches: breachNames,
          warning: `⚠️ ${email} found in ${breaches.length} data breach(es): ${breachNames}`,
        };
      } else if (response.status === 404) {
        return {
          success: true,
          leaked: false,
          warning: `✓ ${email} not found in known breaches`,
        };
      }

      return { success: true, leaked: null, warning: 'Could not check breach database' };
    } catch (error) {
      return { success: true, leaked: null, warning: 'Breach check unavailable - try again later' };
    }
  });

  // System control - List desktop items
  ipcMain.handle('system:list-desktop', async () => {
    try {
      const desktopPath = app.getPath('desktop');
      const fs = require('fs');
      const items = fs.readdirSync(desktopPath);
      return { success: true, items };
    } catch (error) {
      return { success: false, error: String(error), items: [] };
    }
  });

  // Settings
  ipcMain.handle('settings:get', (_, key: string) => store.get(key));
  ipcMain.handle('settings:set', (_, key: string, value: unknown) => store.set(key, value));
  ipcMain.handle('settings:getAll', () => store.store);

  // ═══════════════════════════════════════════════════════════════════════
  // PYTHON BACKEND INTEGRATION
  // ═══════════════════════════════════════════════════════════════════════

  ipcMain.handle('backend:chat', async (_, message: string) => {
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Backend chat error:', error);
      return { success: false, error: 'Backend unavailable', response: 'The AI backend is not running. Please start the Python server.' };
    }
  });

  ipcMain.handle('backend:chat-voice', async (_, message: string) => {
    try {
      const response = await fetch(`${API_URL}/chat/voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Backend voice chat error:', error);
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:status', async () => {
    try {
      const response = await fetch(`${API_URL}/status`);
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:scan-system', async () => {
    try {
      const response = await fetch(`${API_URL}/scan/system`, { method: 'POST' });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:scan-url', async (_, url: string) => {
    try {
      const response = await fetch(`${API_URL}/scan/url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:scan-file', async (_, filepath: string) => {
    try {
      const response = await fetch(`${API_URL}/scan/file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filepath })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:scan-network', async (_, target: string) => {
    try {
      const response = await fetch(`${API_URL}/scan/network`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target || 'localhost' })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:analyze-email', async (_, content: string) => {
    try {
      const response = await fetch(`${API_URL}/analyze/email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:autonomous-start', async () => {
    try {
      const response = await fetch(`${API_URL}/autonomous/start`, { method: 'POST' });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:autonomous-stop', async () => {
    try {
      const response = await fetch(`${API_URL}/autonomous/stop`, { method: 'POST' });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:agent-status', async () => {
    try {
      const response = await fetch(`${API_URL}/agent/status`);
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:memory-store', async (_, key: string, value: any, category: string) => {
    try {
      const response = await fetch(`${API_URL}/memory/store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, value, category })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:memory-recall', async (_, key: string) => {
    try {
      const response = await fetch(`${API_URL}/memory/recall?key=${encodeURIComponent(key)}`);
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:generate-report', async () => {
    try {
      const response = await fetch(`${API_URL}/report/generate`, { method: 'POST' });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:health-check', async () => {
    return await checkPythonServer();
  });

  // ML Phishing Detection
  ipcMain.handle('backend:ml-phishing', async (_, url?: string, subject?: string, body?: string) => {
    try {
      const response = await fetch(`${API_URL}/ml/detect-phishing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, subject, body })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  // Monitoring
  ipcMain.handle('backend:monitor-start', async (_, interval?: number) => {
    try {
      const response = await fetch(`${API_URL}/monitor/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interval: interval || 60 })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:monitor-stop', async () => {
    try {
      const response = await fetch(`${API_URL}/monitor/stop`, { method: 'POST' });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:monitor-status', async () => {
    try {
      const response = await fetch(`${API_URL}/monitor/status`);
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });

  ipcMain.handle('backend:monitor-alerts', async () => {
    try {
      const response = await fetch(`${API_URL}/monitor/alerts`);
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Backend unavailable' };
    }
  });
}

app.whenReady().then(async () => {
  createWindow();
  createTray();
  registerShortcuts();
  setupIPC();
  
  const serverRunning = await checkPythonServer();
  if (!serverRunning) {
    console.log('Starting Python backend server...');
    await startPythonServer();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});
