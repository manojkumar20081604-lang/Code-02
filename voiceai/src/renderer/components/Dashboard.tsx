import { useState, useEffect } from 'react';

interface ModuleCard {
  name: string;
  icon: string;
  description: string;
  status: 'active' | 'inactive';
  action: () => void;
}

interface QuickAction {
  name: string;
  icon: string;
  command: string;
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    securityScore: 95,
    tasksCompleted: 12,
    filesManaged: 45,
    apiCalls: 128
  });

  const modules: ModuleCard[] = [
    { name: 'Security', icon: '🛡️', description: 'Scan, monitor, protect', status: 'active', action: () => {} },
    { name: 'Voice AI', icon: '🎤', description: 'Voice commands & TTS', status: 'active', action: () => {} },
    { name: 'Data Science', icon: '📊', description: 'Analyze & visualize', status: 'active', action: () => {} },
    { name: 'Developer', icon: '💻', description: 'Code help & tools', status: 'active', action: () => {} },
    { name: 'Personal', icon: '📝', description: 'Tasks & planning', status: 'active', action: () => {} },
    { name: 'Content', icon: '✍️', description: 'Posts & articles', status: 'active', action: () => {} },
    { name: 'Files', icon: '📁', description: 'Manage files', status: 'active', action: () => {} },
    { name: 'Web', icon: '🌐', description: 'Search & extract', status: 'active', action: () => {} },
    { name: 'Pentest', icon: '🔍', description: 'Recon & testing', status: 'active', action: () => {} },
    { name: 'Memory', icon: '🧠', description: 'Learn & remember', status: 'active', action: () => {} },
  ];

  const quickActions: QuickAction[] = [
    { name: 'Security Scan', icon: '🔍', command: 'Run security scan' },
    { name: 'Plan Day', icon: '📅', command: 'Plan my day' },
    { name: 'Analyze Data', icon: '📊', command: 'Analyze dataset' },
    { name: 'Write Code', icon: '💻', command: 'Help with code' },
    { name: 'Create Post', icon: '✍️', command: 'Generate post' },
    { name: 'Search Web', icon: '🌐', command: 'Search for info' },
  ];

  const recentActivity = [
    { time: '2 min ago', action: 'Security scan completed', type: 'security' },
    { time: '15 min ago', action: 'Code reviewed', type: 'dev' },
    { time: '1 hour ago', action: 'Files organized', type: 'files' },
    { time: '2 hours ago', action: 'Content generated', type: 'content' },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">02 Dashboard</h1>
        <p className="text-gray-400">Your Universal AI Assistant — At your service.</p>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">⚡ Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {quickActions.map((action) => (
            <button
              key={action.name}
              className="bg-surface hover:bg-surface/80 border border-border rounded-xl p-4 transition-all hover:scale-105 flex flex-col items-center gap-2"
              onClick={() => {
                // Send command to chat
                const input = document.querySelector('input[type="text"]') as HTMLInputElement;
                if (input) {
                  input.value = action.command;
                  input.dispatchEvent(new Event('input', { bubbles: true }));
                }
              }}
            >
              <span className="text-3xl">{action.icon}</span>
              <span className="text-sm text-gray-300">{action.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 rounded-xl p-4">
          <div className="text-3xl font-bold text-green-400">{stats.securityScore}</div>
          <div className="text-sm text-gray-400">Security Score</div>
          <div className="text-xs text-green-400 mt-1">🛡️ Protected</div>
        </div>
        <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 border border-blue-500/30 rounded-xl p-4">
          <div className="text-3xl font-bold text-blue-400">{stats.tasksCompleted}</div>
          <div className="text-sm text-gray-400">Tasks Done</div>
          <div className="text-xs text-blue-400 mt-1">📝 This week</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 rounded-xl p-4">
          <div className="text-3xl font-bold text-purple-400">{stats.filesManaged}</div>
          <div className="text-sm text-gray-400">Files Managed</div>
          <div className="text-xs text-purple-400 mt-1">📁 Organized</div>
        </div>
        <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 rounded-xl p-4">
          <div className="text-3xl font-bold text-orange-400">{stats.apiCalls}</div>
          <div className="text-sm text-gray-400">AI Requests</div>
          <div className="text-xs text-orange-400 mt-1">🤖 Processed</div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Modules Grid */}
        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold text-white mb-4">🚀 Active Modules</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {modules.map((module) => (
              <div
                key={module.name}
                className="bg-surface border border-border rounded-xl p-4 hover:border-primary/50 transition-all cursor-pointer group"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl">{module.icon}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${module.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {module.status === 'active' ? '● Active' : '○ Inactive'}
                  </span>
                </div>
                <h3 className="font-semibold text-white group-hover:text-primary transition-colors">{module.name}</h3>
                <p className="text-xs text-gray-400 mt-1">{module.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Recent Activity */}
          <div className="bg-surface border border-border rounded-xl p-4">
            <h3 className="font-semibold text-white mb-4">📜 Recent Activity</h3>
            <div className="space-y-3">
              {recentActivity.map((item, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    item.type === 'security' ? 'bg-green-400' :
                    item.type === 'dev' ? 'bg-blue-400' :
                    item.type === 'files' ? 'bg-purple-400' : 'bg-orange-400'
                  }`}></div>
                  <div>
                    <p className="text-sm text-gray-300">{item.action}</p>
                    <p className="text-xs text-gray-500">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* System Status */}
          <div className="bg-surface border border-border rounded-xl p-4">
            <h3 className="font-semibold text-white mb-4">💻 System Status</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">CPU</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-400 rounded-full" style={{ width: '35%' }}></div>
                  </div>
                  <span className="text-xs text-gray-400">35%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Memory</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-green-400 rounded-full" style={{ width: '62%' }}></div>
                  </div>
                  <span className="text-xs text-gray-400">62%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Disk</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-orange-400 rounded-full" style={{ width: '45%' }}></div>
                  </div>
                  <span className="text-xs text-gray-400">45%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Commands */}
          <div className="bg-surface border border-border rounded-xl p-4">
            <h3 className="font-semibold text-white mb-4">⌨️ Voice Commands</h3>
            <div className="space-y-2 text-sm">
              <p className="text-gray-400"><span className="text-primary">"02 scan my system"</span></p>
              <p className="text-gray-400"><span className="text-primary">"02 plan my day"</span></p>
              <p className="text-gray-400"><span className="text-primary">"02 analyze this data"</span></p>
              <p className="text-gray-400"><span className="text-primary">"02 create a post"</span></p>
              <p className="text-gray-400"><span className="text-primary">"02 help with code"</span></p>
            </div>
          </div>
        </div>
      </div>

      {/* Capabilities */}
      <div className="mt-8 bg-gradient-to-r from-primary/20 to-purple-500/20 border border-primary/30 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-4">🎯 02 Capabilities</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-primary font-medium mb-2">🧠 Intelligence</h3>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• LLM-powered conversations</li>
              <li>• Context awareness</li>
              <li>• Multi-step reasoning</li>
              <li>• Code generation</li>
            </ul>
          </div>
          <div>
            <h3 className="text-primary font-medium mb-2">⚙️ Automation</h3>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• System control</li>
              <li>• File management</li>
              <li>• Task automation</li>
              <li>• Scheduled actions</li>
            </ul>
          </div>
          <div>
            <h3 className="text-primary font-medium mb-2">🛡️ Security</h3>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Threat detection</li>
              <li>• URL analysis</li>
              <li>• Security scanning</li>
              <li>• Privacy protection</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
