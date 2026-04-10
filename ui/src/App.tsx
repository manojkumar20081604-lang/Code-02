import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain, MessageSquare, Database, Shield, Terminal, Settings,
  Mic, MicOff, Send, ChevronRight, Zap, Activity, Cpu,
  Layers, Workflow, Eye, Lightbulb, TrendingUp, Clock,
  FileCode, BarChart3, Lock, Play, Pause, RotateCcw
} from 'lucide-react';

// Types
interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: Date;
  type?: 'text' | 'plan' | 'code' | 'analysis' | 'error';
}

interface WorkflowStep {
  step: number;
  name: string;
  status: 'pending' | 'active' | 'completed';
  icon: string;
}

interface SystemStatus {
  status: string;
  thinking: boolean;
  memory: number;
  uptime: string;
}

// API Functions
const api = {
  async chat(message: string) {
    const res = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return res.json();
  },
  
  async think(prompt: string) {
    const res = await fetch('http://localhost:5000/api/think', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    return res.json();
  },
  
  async getStatus() {
    const res = await fetch('http://localhost:5000/api/status');
    return res.json();
  },
  
  async speak(text: string) {
    await fetch('http://localhost:5000/api/voice/speak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
  }
};

// Components
const NeuralAnimation: React.FC = () => (
  <div className="relative w-full h-full">
    {[...Array(20)].map((_, i) => (
      <motion.div
        key={i}
        className="absolute w-1 h-1 bg-cyber-cyan rounded-full"
        style={{
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`
        }}
        animate={{
          opacity: [0, 1, 0],
          scale: [0, 1.5, 0],
          x: [0, Math.random() * 100 - 50],
          y: [0, Math.random() * 100 - 50]
        }}
        transition={{
          duration: 2 + Math.random() * 2,
          repeat: Infinity,
          delay: Math.random() * 2
        }}
      />
    ))}
  </div>
);

const WorkflowVisualizer: React.FC<{ steps: WorkflowStep[] }> = ({ steps }) => (
  <div className="flex items-center justify-between gap-2 p-4 bg-cyber-dark/50 rounded-lg">
    {steps.map((step, index) => (
      <React.Fragment key={step.step}>
        <motion.div
          className={`flex flex-col items-center gap-1 ${
            step.status === 'completed' ? 'text-cyber-green' :
            step.status === 'active' ? 'text-cyber-blue' : 'text-gray-500'
          }`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
            step.status === 'completed' ? 'border-cyber-green bg-cyber-green/20' :
            step.status === 'active' ? 'border-cyber-blue bg-cyber-blue/20 animate-pulse-glow' :
            'border-gray-600'
          }`}>
            {step.status === 'completed' ? (
              <Layers size={18} />
            ) : step.status === 'active' ? (
              <Zap size={18} />
            ) : (
              <span className="text-xs">{step.step}</span>
            )}
          </div>
          <span className="text-xs">{step.name}</span>
        </motion.div>
        {index < steps.length - 1 && (
          <ChevronRight className={`${step.status === 'completed' ? 'text-cyber-green' : 'text-gray-600'}`} size={16} />
        )}
      </React.Fragment>
    ))}
  </div>
);

const ChatMessage: React.FC<{ message: Message }> = ({ message }) => (
  <motion.div
    initial={{ opacity: 0, x: message.role === 'user' ? 50 : -50 }}
    animate={{ opacity: 1, x: 0 }}
    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
  >
    <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${
      message.role === 'user'
        ? 'bg-gradient-to-r from-cyber-purple to-cyber-pink text-white'
        : 'bg-cyber-dark border border-cyber-blue/30 text-gray-200'
    }`}>
      <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
      <span className="text-xs opacity-60 mt-1 block">
        {message.timestamp.toLocaleTimeString()}
      </span>
    </div>
  </motion.div>
);

const MemoryVisualizer: React.FC<{ data: any }> = ({ data }) => (
  <div className="space-y-2">
    <div className="flex justify-between text-xs">
      <span className="text-gray-400">Short-term Memory</span>
      <span className="text-cyber-blue">{data.short_term?.size || 0} items</span>
    </div>
    <div className="h-2 bg-cyber-dark rounded-full overflow-hidden">
      <motion.div
        className="h-full bg-gradient-to-r from-cyber-blue to-cyber-cyan"
        initial={{ width: 0 }}
        animate={{ width: `${Math.min((data.short_term?.size || 0) / 50 * 100, 100)}%` }}
      />
    </div>
    <div className="flex justify-between text-xs">
      <span className="text-gray-400">Long-term Memory</span>
      <span className="text-cyber-green">{data.long_term_size || 0} interactions</span>
    </div>
  </div>
);

const Sidebar: React.FC<{
  activeTab: string;
  setActiveTab: (tab: string) => void;
}> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'chat', icon: MessageSquare, label: 'AI Chat', color: 'cyan' },
    { id: 'thinking', icon: Brain, label: 'Deep Think', color: 'purple' },
    { id: 'workflow', icon: Workflow, label: 'Workflow', color: 'pink' },
    { id: 'memory', icon: Database, label: 'Memory', color: 'green' },
    { id: 'data', icon: BarChart3, label: 'Data', color: 'yellow' },
    { id: 'security', icon: Shield, label: 'Security', color: 'red' },
    { id: 'terminal', icon: Terminal, label: 'Terminal', color: 'blue' },
    { id: 'settings', icon: Settings, label: 'Settings', color: 'gray' },
  ];

  return (
    <div className="w-16 hover:w-56 bg-cyber-dark/80 backdrop-blur-xl border-r border-cyber-blue/20 
                    flex flex-col py-4 transition-all duration-300 group overflow-hidden">
      <div className="px-3 mb-6">
        <motion.div
          className="flex items-center gap-3"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyber-pink to-cyber-purple 
                        flex items-center justify-center text-white font-bold text-lg">
            02
          </div>
          <div className="whitespace-nowrap overflow-hidden opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="font-bold text-white">CODE: 02</div>
            <div className="text-xs text-cyber-green">ACTIVE</div>
          </div>
        </motion.div>
      </div>

      <div className="flex-1 flex flex-col gap-1 px-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
              activeTab === tab.id
                ? `bg-${tab.color === 'cyan' ? 'cyber-cyan' : tab.color === 'purple' ? 'cyber-purple' : 
                   tab.color === 'pink' ? 'cyber-pink' : tab.color === 'green' ? 'cyber-green' :
                   tab.color === 'yellow' ? 'cyber-yellow' : tab.color === 'red' ? 'cyber-red' :
                   tab.color === 'blue' ? 'cyber-blue' : 'gray'}-/20 text-white`
                : 'hover:bg-white/5 text-gray-400 hover:text-white'
            }`}
          >
            <tab.icon size={20} className={activeTab === tab.id ? `text-cyber-${tab.color}` : ''} />
            <span className="whitespace-nowrap overflow-hidden opacity-0 group-hover:opacity-100 transition-opacity text-sm">
              {tab.label}
            </span>
          </button>
        ))}
      </div>

      <div className="px-3 mt-auto">
        <div className="p-3 rounded-lg bg-cyber-black/50 border border-cyber-blue/20">
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Activity size={12} className="text-cyber-green animate-pulse" />
            <span>System Online</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const MainPanel: React.FC<{
  activeTab: string;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  workflowSteps: WorkflowStep[];
  isProcessing: boolean;
}> = ({ activeTab, messages, setMessages, workflowSteps, isProcessing }) => {
  const [input, setInput] = useState('');
  const [thinkPrompt, setThinkPrompt] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await api.chat(input);
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: response.response || 'Processing complete.',
        timestamp: new Date(),
        type: response.plan ? 'plan' : 'text'
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('API Error:', error);
    }
  };

  const handleThink = async () => {
    if (!thinkPrompt.trim()) return;
    
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'user',
      content: `Deep think: ${thinkPrompt}`,
      timestamp: new Date()
    }]);

    try {
      const response = await api.think(thinkPrompt);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: response.conclusion?.statement || 'Thinking complete.',
        timestamp: new Date(),
        type: 'analysis'
      }]);
    } catch (error) {
      console.error('Think Error:', error);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-cyber-black">
      {/* Header */}
      <div className="h-16 border-b border-cyber-blue/20 px-6 flex items-center justify-between bg-cyber-dark/50">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-bold text-white capitalize">
            {activeTab === 'thinking' ? 'Deep Thinking Mode' : activeTab}
          </h2>
          {isProcessing && (
            <div className="flex items-center gap-2 text-cyber-blue">
              <Cpu size={16} className="animate-spin" />
              <span className="text-sm">Processing...</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyber-green animate-pulse" />
          <span className="text-xs text-gray-400">Cognitive Engine Active</span>
        </div>
      </div>

      {/* Workflow Visualizer */}
      <div className="px-6 py-4 border-b border-cyber-blue/10">
        <WorkflowVisualizer steps={workflowSteps} />
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {activeTab === 'chat' && (
          <>
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <AnimatePresence>
                {messages.map(msg => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
              </AnimatePresence>
              {isProcessing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-cyber-dark border border-cyber-blue/30 rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-cyber-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-cyber-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-cyber-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-6 border-t border-cyber-blue/20">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Enter your goal or command..."
                  className="flex-1 bg-cyber-dark border border-cyber-blue/30 rounded-xl px-4 py-3 
                           text-white placeholder-gray-500 focus:outline-none focus:border-cyber-blue
                           focus:ring-1 focus:ring-cyber-blue/50"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-cyber-pink to-cyber-purple rounded-xl
                           text-white font-semibold hover:opacity-90 transition-opacity
                           disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Send size={18} />
                  Send
                </button>
              </div>
            </div>
          </>
        )}

        {activeTab === 'thinking' && (
          <div className="flex-1 p-6">
            <div className="max-w-3xl mx-auto">
              <div className="mb-6">
                <label className="block text-sm text-gray-400 mb-2">
                  Enter a problem for deep analysis:
                </label>
                <textarea
                  value={thinkPrompt}
                  onChange={(e) => setThinkPrompt(e.target.value)}
                  rows={4}
                  className="w-full bg-cyber-dark border border-cyber-blue/30 rounded-xl px-4 py-3 
                           text-white placeholder-gray-500 focus:outline-none focus:border-cyber-purple
                           resize-none"
                  placeholder="Describe the problem you want me to think through..."
                />
                <button
                  onClick={handleThink}
                  className="mt-4 px-6 py-3 bg-gradient-to-r from-cyber-purple to-cyber-pink rounded-xl
                           text-white font-semibold flex items-center gap-2"
                >
                  <Lightbulb size={18} />
                  Start Deep Thinking
                </button>
              </div>

              <div className="space-y-4">
                {messages.filter(m => m.type === 'analysis').map(msg => (
                  <div key={msg.id} className="bg-cyber-dark/50 border border-cyber-purple/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Brain size={18} className="text-cyber-purple" />
                      <span className="text-cyber-purple font-semibold">Analysis</span>
                    </div>
                    <p className="text-gray-300 whitespace-pre-wrap">{msg.content}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'workflow' && (
          <div className="flex-1 p-6">
            <div className="grid grid-cols-2 gap-6 h-full">
              <div className="bg-cyber-dark/50 rounded-xl p-6 border border-cyber-pink/30">
                <h3 className="text-cyber-pink font-bold mb-4 flex items-center gap-2">
                  <Workflow size={18} />
                  Active Workflow
                </h3>
                <div className="space-y-4">
                  {workflowSteps.map((step) => (
                    <div
                      key={step.step}
                      className={`p-4 rounded-lg border ${
                        step.status === 'completed' ? 'border-cyber-green/50 bg-cyber-green/10' :
                        step.status === 'active' ? 'border-cyber-blue/50 bg-cyber-blue/10 animate-pulse' :
                        'border-gray-600/50 bg-gray-500/10'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{step.name}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          step.status === 'completed' ? 'bg-cyber-green/20 text-cyber-green' :
                          step.status === 'active' ? 'bg-cyber-blue/20 text-cyber-blue' :
                          'bg-gray-600/20 text-gray-400'
                        }`}>
                          {step.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-cyber-dark/50 rounded-xl p-6 border border-cyber-cyan/30">
                <h3 className="text-cyber-cyan font-bold mb-4 flex items-center gap-2">
                  <Activity size={18} />
                  Real-time Activity
                </h3>
                <div className="h-64 relative overflow-hidden rounded-lg bg-cyber-black/50">
                  <NeuralAnimation />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const RightPanel: React.FC<{ status: SystemStatus; memory: any }> = ({ status, memory }) => (
  <div className="w-80 bg-cyber-dark/80 backdrop-blur-xl border-l border-cyber-blue/20 flex flex-col">
    {/* System Status */}
    <div className="p-4 border-b border-cyber-blue/20">
      <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
        <Cpu size={16} className="text-cyber-blue" />
        System Status
      </h3>
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-400">Status</span>
          <span className={`text-xs px-2 py-1 rounded ${
            status.thinking ? 'bg-cyber-yellow/20 text-cyber-yellow' : 'bg-cyber-green/20 text-cyber-green'
          }`}>
            {status.thinking ? 'Processing' : 'Ready'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-400">Memory</span>
          <span className="text-xs text-cyber-cyan">{status.memory} items</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-400">Uptime</span>
          <span className="text-xs text-gray-300">{status.uptime}</span>
        </div>
      </div>
    </div>

    {/* Memory Visualizer */}
    <div className="p-4 border-b border-cyber-blue/20">
      <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
        <Database size={16} className="text-cyber-green" />
        Memory
      </h3>
      <MemoryVisualizer data={memory} />
    </div>

    {/* Quick Actions */}
    <div className="p-4 border-b border-cyber-blue/20">
      <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
        <Zap size={16} className="text-cyber-yellow" />
        Quick Actions
      </h3>
      <div className="grid grid-cols-2 gap-2">
        {[
          { icon: Play, label: 'Execute', color: 'green' },
          { icon: Pause, label: 'Pause', color: 'yellow' },
          { icon: RotateCcw, label: 'Reset', color: 'pink' },
          { icon: Eye, label: 'Inspect', color: 'blue' },
        ].map((action) => (
          <button
            key={action.label}
            className={`p-3 rounded-lg bg-cyber-black/50 border border-${action.color === 'green' ? 'cyber-green' : 
                       action.color === 'yellow' ? 'cyber-yellow' : action.color === 'pink' ? 'cyber-pink' : 'cyber-blue'}/30
                       hover:border-cyber-blue transition-colors group`}
          >
            <action.icon size={18} className={`mx-auto text-cyber-${action.color} mb-1`} />
            <span className="text-xs text-gray-400 group-hover:text-white">{action.label}</span>
          </button>
        ))}
      </div>
    </div>

    {/* Logs */}
    <div className="flex-1 p-4 overflow-hidden">
      <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
        <Terminal size={16} className="text-gray-400" />
        Live Logs
      </h3>
      <div className="h-48 overflow-y-auto bg-cyber-black/50 rounded-lg p-3 font-mono text-xs space-y-1">
        {[
          { time: '10:23:45', msg: 'Intent detected: task', color: 'cyan' },
          { time: '10:23:46', msg: 'Plan generated: 4 steps', color: 'green' },
          { time: '10:23:47', msg: 'Executing step 1...', color: 'yellow' },
          { time: '10:23:48', msg: 'Step 1 completed', color: 'green' },
          { time: '10:23:49', msg: 'Executing step 2...', color: 'yellow' },
        ].map((log, i) => (
          <div key={i} className="flex gap-2">
            <span className="text-gray-500">{log.time}</span>
            <span className={`text-cyber-${log.color}`}>{log.msg}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Main App
const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<SystemStatus>({
    status: 'ready',
    thinking: false,
    memory: 0,
    uptime: '00:00:00'
  });
  const [memory, setMemory] = useState({ short_term: { size: 0 }, long_term_size: 0 });

  const [workflowSteps] = useState<WorkflowStep[]>([
    { step: 1, name: 'Understanding', status: 'completed', icon: 'brain' },
    { step: 2, name: 'Planning', status: 'active', icon: 'map' },
    { step: 3, name: 'Executing', status: 'pending', icon: 'play' },
    { step: 4, name: 'Evaluating', status: 'pending', icon: 'check' }
  ]);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await api.getStatus();
        setStatus(prev => ({
          ...prev,
          status: data.status,
          thinking: data.thinking,
          memory: data.memory_items || 0
        }));
      } catch (error) {
        console.error('Status fetch error:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen w-screen bg-cyber-black flex overflow-hidden">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <MainPanel
        activeTab={activeTab}
        messages={messages}
        setMessages={setMessages}
        workflowSteps={workflowSteps}
        isProcessing={isProcessing}
      />
      <RightPanel status={status} memory={memory} />
    </div>
  );
};

export default App;
