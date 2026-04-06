import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';

interface ThreatInfo {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  recommendation: string;
}

function SecurityPanel() {
  const { securityScanOpen, setSecurityScanOpen, securityScore, setSecurityScore, threats, setThreats, isScanning, setIsScanning, isMonitoring, setIsMonitoring } = useStore();

  const runFullScan = async () => {
    setIsScanning(true);
    try {
      const result = await window.electronAPI?.cyberFullScan();
      if (result?.success) {
        setSecurityScore(result.report.overallScore);
        setThreats(result.report.threats);
      }
    } catch (error) {
      console.error('Scan error:', error);
    } finally {
      setIsScanning(false);
    }
  };

  const toggleMonitoring = async () => {
    if (isMonitoring) {
      await window.electronAPI?.cyberStopMonitoring();
      setIsMonitoring(false);
    } else {
      await window.electronAPI?.cyberStartMonitoring(30000);
      setIsMonitoring(true);
    }
  };

  if (!securityScanOpen) return null;

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 border-red-500 text-red-400';
      case 'high': return 'bg-orange-500/20 border-orange-500 text-orange-400';
      case 'medium': return 'bg-yellow-500/20 border-yellow-500 text-yellow-400';
      case 'low': return 'bg-blue-500/20 border-blue-500 text-blue-400';
      default: return 'bg-gray-500/20 border-gray-500 text-gray-400';
    }
  };

  const getThreatIcon = (type: string) => {
    switch (type) {
      case 'malware': return '🦠';
      case 'phishing': return '🎣';
      case 'open_port': return '🚪';
      case 'unauthorized_access': return '🔓';
      case 'outdated_software': return '📅';
      default: return '⚠️';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="w-full max-w-2xl glass rounded-xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between bg-gradient-to-r from-red-900/20 to-orange-900/20">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🛡️</div>
            <div>
              <h2 className="text-xl font-bold text-text-primary">02 CYBER SHIELD</h2>
              <p className="text-xs text-text-secondary">Advanced Threat Protection</p>
            </div>
          </div>
          <button
            onClick={() => setSecurityScanOpen(false)}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Security Score */}
          <div className="glass rounded-xl p-6 text-center">
            <div className="relative w-32 h-32 mx-auto mb-4">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="64" cy="64" r="56"
                  fill="none"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="12"
                />
                <circle
                  cx="64" cy="64" r="56"
                  fill="none"
                  stroke={securityScore >= 70 ? '#22c55e' : securityScore >= 50 ? '#f59e0b' : '#ef4444'}
                  strokeWidth="12"
                  strokeDasharray={`${(securityScore / 100) * 352} 352`}
                  strokeLinecap="round"
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-4xl font-bold ${getScoreColor(securityScore)}`}>
                  {securityScore}
                </span>
                <span className="text-xs text-text-secondary">/100</span>
              </div>
            </div>
            <h3 className={`text-lg font-semibold ${securityScore >= 70 ? 'text-green-400' : securityScore >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
              {securityScore >= 90 ? '🟢 EXCELLENT' : securityScore >= 70 ? '🟡 GOOD' : securityScore >= 50 ? '🟠 MODERATE RISK' : '🔴 HIGH RISK'}
            </h3>
          </div>

          {/* Actions */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={runFullScan}
              disabled={isScanning}
              className="flex items-center justify-center gap-2 p-3 glass rounded-xl hover:bg-white/10 transition-colors disabled:opacity-50"
            >
              {isScanning ? (
                <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              ) : (
                <span className="text-xl">🔍</span>
              )}
              <span className="text-sm">Full Scan</span>
            </button>

            <button
              onClick={toggleMonitoring}
              className={`flex items-center justify-center gap-2 p-3 glass rounded-xl hover:bg-white/10 transition-colors ${isMonitoring ? 'bg-green-500/20 border border-green-500' : ''}`}
            >
              <span className={`text-xl ${isMonitoring ? 'animate-pulse' : ''}`}>🛡️</span>
              <span className="text-sm">{isMonitoring ? 'Monitoring ON' : 'Start Monitor'}</span>
            </button>
          </div>

          {/* Threats List */}
          {threats.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-text-secondary flex items-center gap-2">
                <span>⚠️</span> Threats Detected ({threats.length})
              </h3>
              {threats.map((threat: ThreatInfo, index: number) => (
                <div
                  key={index}
                  className={`p-4 rounded-xl border ${getSeverityColor(threat.severity)}`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-xl">{getThreatIcon(threat.type)}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-sm uppercase">{threat.severity}</span>
                        <span className="text-xs opacity-60">{threat.type}</span>
                      </div>
                      <p className="text-sm mb-2">{threat.description}</p>
                      <p className="text-xs opacity-80">{threat.recommendation}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {threats.length === 0 && !isScanning && (
            <div className="text-center py-8 text-text-secondary">
              <div className="text-4xl mb-2">✓</div>
              <p>No threats detected. Your system is protected.</p>
            </div>
          )}

          {/* Quick Actions */}
          <div className="glass rounded-xl p-4">
            <h3 className="text-sm font-medium text-text-secondary mb-3">Quick Actions</h3>
            <div className="grid grid-cols-3 gap-2">
              <button className="p-3 rounded-lg bg-white/5 hover:bg-white/10 text-sm flex flex-col items-center gap-1">
                <span>🔐</span>
                <span>Check Password</span>
              </button>
              <button className="p-3 rounded-lg bg-white/5 hover:bg-white/10 text-sm flex flex-col items-center gap-1">
                <span>📧</span>
                <span>Check Email</span>
              </button>
              <button className="p-3 rounded-lg bg-white/5 hover:bg-white/10 text-sm flex flex-col items-center gap-1">
                <span>🔗</span>
                <span>Check URL</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-white/10 flex items-center justify-between text-xs text-text-secondary">
          <span>Last scan: {new Date().toLocaleTimeString()}</span>
          <span>02 Cyber Shield v1.0</span>
        </div>
      </div>
    </div>
  );
}

export default SecurityPanel;
