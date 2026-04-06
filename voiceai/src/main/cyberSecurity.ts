import { exec } from 'child_process';
import { promisify } from 'util';
import * as https from 'https';
import * as http from 'http';
import * as dns from 'dns';

const execAsync = promisify(exec);

export interface ThreatInfo {
  type: ThreatType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  recommendation: string;
  timestamp: Date;
}

export type ThreatType = 
  | 'malware'
  | 'phishing'
  | 'suspicious_process'
  | 'weak_password'
  | 'open_port'
  | 'outdated_software'
  | 'unencrypted_connection'
  | 'data_leak'
  | 'ransomware'
  | 'spyware'
  | 'trojan'
  | 'unauthorized_access';

export interface SecurityReport {
  overallScore: number;
  threats: ThreatInfo[];
  recommendations: string[];
  lastScan: Date;
}

export class CyberSecurityModule {
  private threats: ThreatInfo[] = [];
  private isMonitoring = false;
  private monitoringInterval: NodeJS.Timeout | null = null;

  async scanSystem(): Promise<SecurityReport> {
    this.threats = [];
    const recommendations: string[] = [];

    await Promise.all([
      this.checkRunningProcesses(),
      this.checkOpenPorts(),
      this.checkSystemUpdates(),
      this.checkFirewall(),
      this.checkSuspiciousStartupItems(),
      this.checkNetworkConnections(),
    ]);

    this.threats.forEach(t => recommendations.push(t.recommendation));

    const score = this.calculateSecurityScore();

    return {
      overallScore: score,
      threats: this.threats,
      recommendations,
      lastScan: new Date(),
    };
  }

  private calculateSecurityScore(): number {
    const criticalWeight = 25;
    const highWeight = 15;
    const mediumWeight = 8;
    const lowWeight = 3;

    let deductions = 0;
    this.threats.forEach(t => {
      switch (t.severity) {
        case 'critical': deductions += criticalWeight; break;
        case 'high': deductions += highWeight; break;
        case 'medium': deductions += mediumWeight; break;
        case 'low': deductions += lowWeight; break;
      }
    });

    return Math.max(0, 100 - deductions);
  }

  private addThreat(type: ThreatType, severity: ThreatInfo['severity'], description: string, recommendation: string) {
    this.threats.push({ type, severity, description, recommendation, timestamp: new Date() });
  }

  async checkRunningProcesses(): Promise<void> {
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync('tasklist /FO CSV /NH', { timeout: 10000 });
        const suspicious = ['mimikatz', 'pwdump', 'netcat', 'nc.exe', 'psexec', 'wce.exe', 'fgdump'];
        
        stdout.split('\n').forEach(line => {
          const process = line.toLowerCase();
          suspicious.forEach(s => {
            if (process.includes(s)) {
              this.addThreat(
                'malware',
                'critical',
                `Suspicious process detected: ${s}`,
                `ALERT: Potential malware tool "${s}" is running. Investigate immediately!`
              );
            }
          });
        });

        const { stdout: cpuUsage } = await execAsync('wmic process get Name,ProcessId,WorkingSetSize /format:csv', { timeout: 10000 });
        const processes = cpuUsage.split('\n').filter(line => line.trim());
        
        let highCpuCount = 0;
        processes.forEach(p => {
          const parts = p.split(',');
          if (parts.length >= 4 && parts[2] && !isNaN(parseInt(parts[2]))) {
            const cpu = parseInt(parts[2]);
            if (cpu > 80) highCpuCount++;
          }
        });

        if (highCpuCount > 3) {
          this.addThreat(
            'suspicious_process',
            'medium',
            'Multiple processes with high CPU usage detected',
            'Some processes are consuming excessive CPU. Could indicate cryptominer or malware.'
          );
        }
      }
    } catch (error) {
      console.error('Process scan error:', error);
    }
  }

  async checkOpenPorts(): Promise<void> {
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync('netstat -ano /TCP /TCP /UDP | findstr LISTENING', { timeout: 10000 });
        
        const dangerousPorts: Record<number, string> = {
          23: 'Telnet (unencrypted)',
          135: 'RPC Endpoint Mapper',
          139: 'NetBIOS',
          445: 'SMB (vulnerable to EternalBlue)',
          1433: 'MS SQL Server',
          3306: 'MySQL',
          3389: 'RDP (target for attackers)',
          5432: 'PostgreSQL',
          5900: 'VNC',
          8080: 'HTTP Proxy',
          4444: 'Metasploit default',
          5555: 'Android ADB',
          6667: 'IRC (botnets)',
          31337: 'Back Orifice default',
        };

        const lines = stdout.split('\n');
        lines.forEach(line => {
          const parts = line.trim().split(/\s+/);
          if (parts.length >= 4) {
            const localAddr = parts[1] || '';
            const portMatch = localAddr.match(/:(\d+)$/);
            if (portMatch) {
              const port = parseInt(portMatch[1]);
              if (dangerousPorts[port]) {
                const severity = [23, 445, 4444, 31337, 6667].includes(port) ? 'high' : 'medium';
                this.addThreat(
                  'open_port',
                  severity,
                  `Dangerous port open: ${port} - ${dangerousPorts[port]}`,
                  port === 3389 
                    ? 'CRITICAL: RDP is open! This is a primary attack vector. Close it if not needed.'
                    : `Port ${port} (${dangerousPorts[port]}) is listening. Ensure this is intentional.`
                );
              }
            }
          }
        });
      }
    } catch (error) {
      console.error('Port scan error:', error);
    }
  }

  async checkSystemUpdates(): Promise<void> {
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync('powershell -Command "Get-HotFix | Sort-Object -Property InstalledOn -Descending | Select-Object -First 5 | ConvertTo-Json"', { timeout: 15000 });
        
        if (stdout && stdout.trim()) {
          const hotfixes = JSON.parse(stdout);
          const recentDate = new Date(hotfixes[0]?.InstalledOn || Date.now() - 90 * 24 * 60 * 60 * 1000);
          const daysSinceUpdate = Math.floor((Date.now() - recentDate.getTime()) / (24 * 60 * 60 * 1000));
          
          if (daysSinceUpdate > 30) {
            this.addThreat(
              'outdated_software',
              'high',
              `System not updated in ${daysSinceUpdate} days`,
              'CRITICAL: Your system is missing security updates. Install updates immediately!'
            );
          } else if (daysSinceUpdate > 14) {
            this.addThreat(
              'outdated_software',
              'medium',
              `Last update was ${daysSinceUpdate} days ago`,
              'System updates are available. Install them soon.'
            );
          }
        }
      } else if (process.platform === 'darwin') {
        const { stdout } = await execAsync('softwareupdate -l 2>/dev/null | grep -c "recommended"', { timeout: 30000 });
        const pending = parseInt(stdout.trim() || '0');
        if (pending > 0) {
          this.addThreat(
            'outdated_software',
            'medium',
            `${pending} software updates available`,
            'Install pending software updates to patch security vulnerabilities.'
          );
        }
      }
    } catch (error) {
      console.error('Update check error:', error);
    }
  }

  async checkFirewall(): Promise<void> {
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync('netsh advfirewall show allprofiles state', { timeout: 10000 });
        
        if (stdout.includes('State                                 OFF')) {
          this.addThreat(
            'unauthorized_access',
            'critical',
            'Windows Firewall is DISABLED',
            'CRITICAL: Firewall is off! Enable immediately to protect against network attacks.'
          );
        }
      }
    } catch (error) {
      console.error('Firewall check error:', error);
    }
  }

  async checkSuspiciousStartupItems(): Promise<void> {
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync('wmic startup list full', { timeout: 10000 });
        const suspicious = ['temp', 'appdata\\local\\temp', 'downloads', 'registry'];
        
        stdout.split('\n').forEach(line => {
          suspicious.forEach(s => {
            if (line.toLowerCase().includes(s) && !line.includes('Microsoft')) {
              this.addThreat(
                'malware',
                'high',
                `Suspicious startup item: ${line.substring(0, 80)}`,
                'A program is set to start from an unusual location. Could be malware.'
              );
            }
          });
        });
      }
    } catch (error) {
      console.error('Startup check error:', error);
    }
  }

  async checkNetworkConnections(): Promise<void> {
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync('netstat -ano | findstr ESTABLISHED', { timeout: 10000 });
        
        const suspiciousCountries = ['CN', 'RU', 'KP', 'IR', 'UA', 'BY', 'PK'];
        const lines = stdout.split('\n');
        
        lines.forEach(line => {
          const parts = line.trim().split(/\s+/);
          if (parts.length >= 5) {
            const foreignAddr = parts[2] || '';
            suspiciousCountries.forEach(country => {
              if (foreignAddr.includes(country.toLowerCase()) || foreignAddr.includes('45.') || foreignAddr.includes('185.')) {
                this.addThreat(
                  'unauthorized_access',
                  'high',
                  `Suspicious connection to: ${foreignAddr}`,
                  'An established connection to a suspicious IP was detected. Investigate!'
                );
              }
            });
          }
        });
      }
    } catch (error) {
      console.error('Network check error:', error);
    }
  }

  async analyzeURL(url: string): Promise<{ safe: boolean; details: string }> {
    const details: string[] = [];
    let isSafe = true;

    try {
      const urlObj = new URL(url);
      const hostname = urlObj.hostname;

      const suspiciousPatterns = [
        { pattern: /\d+\.\d+\.\d+\.\d+/, reason: 'IP address instead of domain' },
        { pattern: /[a-z]{30,}/i, reason: 'Extremely long subdomain' },
        { pattern: /-(login|signin|account|secure|bank|paypal|apple|microsoft|google)/i, reason: 'Suspicious subdomain' },
        { pattern: /\.(xyz|tk|ml|ga|cf|gq|top|work)/i, reason: 'Suspicious TLD' },
      ];

      suspiciousPatterns.forEach(({ pattern, reason }) => {
        if (pattern.test(hostname)) {
          isSafe = false;
          details.push(`WARNING: ${reason} detected in hostname`);
        }
      });

      if (urlObj.protocol === 'http:') {
        isSafe = false;
        details.push('WARNING: Not using HTTPS (unencrypted connection)');
      }

      if (url.includes('@')) {
        isSafe = false;
        details.push('WARNING: URL contains @ symbol (possible phishing)');
      }

      if (url.includes('bit.ly') || url.includes('tinyurl') || url.includes('goo.gl')) {
        details.push('INFO: Shortened URL detected - destination hidden');
      }

      await this.checkDNS(hostname).catch(() => {
        isSafe = false;
        details.push('WARNING: DNS lookup failed - suspicious domain');
      });

    } catch (error) {
      return { safe: false, details: 'Invalid URL format' };
    }

    return {
      safe: isSafe,
      details: details.length > 0 ? details.join('\n') : 'No obvious threats detected. Proceed with caution.'
    };
  }

  private checkDNS(hostname: string): Promise<string> {
    return new Promise((resolve, reject) => {
      dns.lookup(hostname, (err, address) => {
        if (err) reject(err);
        else resolve(address);
      });
    });
  }

  async analyzeFileHash(hash: string): Promise<{ known: boolean; details: string }> {
    const details: string[] = [];
    
    const knownMalwareHashes: Record<string, string> = {
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855': 'SHA256 of empty file (testing hash)',
      '44d88612fea8a8f36de82e1278abb02f': 'EICAR Test Virus',
    };

    const lowerHash = hash.toLowerCase();
    if (knownMalwareHashes[lowerHash]) {
      return {
        known: true,
        details: `MALWARE DETECTED: ${knownMalwareHashes[lowerHash]}`
      };
    }

    return {
      known: false,
      details: 'Hash not found in local malware database. Submit to VirusTotal for analysis.'
    };
  }

  startContinuousMonitoring(intervalMs: number = 60000): void {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    this.monitoringInterval = setInterval(async () => {
      await this.quickThreatScan();
    }, intervalMs);

    console.log('Cyber Security: Continuous monitoring enabled');
  }

  stopContinuousMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
    console.log('Cyber Security: Monitoring stopped');
  }

  private async quickThreatScan(): Promise<ThreatInfo[]> {
    const quickThreats: ThreatInfo[] = [];
    
    try {
      if (process.platform === 'win32') {
        const { stdout } = await execAsync('netstat -ano | findstr ESTABLISHED', { timeout: 5000 });
        if (stdout.includes('4444') || stdout.includes('5555') || stdout.includes('31337')) {
          quickThreats.push({
            type: 'malware',
            severity: 'critical',
            description: 'Metasploit/Backdoor port activity detected',
            recommendation: 'IMMEDIATE ACTION: Possible backdoor connection detected!',
            timestamp: new Date(),
          });
        }
      }
    } catch (error) {
      console.error('Quick scan error:', error);
    }

    if (quickThreats.length > 0) {
      this.threats.push(...quickThreats);
    }

    return quickThreats;
  }

  getThreats(): ThreatInfo[] {
    return this.threats;
  }

  clearThreats(): void {
    this.threats = [];
  }

  generateThreatReport(): string {
    const report = this.threats.map((t, i) => 
      `[${i + 1}] ${t.severity.toUpperCase()}: ${t.type}\n   ${t.description}\n   ${t.recommendation}\n`
    ).join('\n');

    return `
═══════════════════════════════════════════════
           02 CYBER SECURITY REPORT           
═══════════════════════════════════════════════
Generated: ${new Date().toISOString()}
───────────────────────────────────────────────
THREATS DETECTED: ${this.threats.length}
OVERALL SECURITY SCORE: ${this.calculateSecurityScore()}/100

${report || 'No threats detected.'}
═══════════════════════════════════════════════
    `;
  }
}

export const cyberSecurity = new CyberSecurityModule();
