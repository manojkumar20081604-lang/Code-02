import { useState, useEffect, useRef } from 'react';

interface CodeBlock {
  id: string;
  code: string;
  language: string;
  output?: string;
  timestamp: number;
}

interface CodeEditorProps {
  initialCode?: string;
  language?: string;
  onRun?: (code: string) => void;
  readOnly?: boolean;
}

const syntaxHighlight = (code: string, language: string): string => {
  const keywords: Record<string, string[]> = {
    python: ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'return', 'try', 'except', 'with', 'as', 'lambda', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'],
    javascript: ['const', 'let', 'var', 'function', 'class', 'import', 'export', 'if', 'else', 'for', 'while', 'return', 'try', 'catch', 'async', 'await', 'new', 'this', 'true', 'false', 'null', 'undefined'],
    typescript: ['const', 'let', 'var', 'function', 'class', 'interface', 'type', 'import', 'export', 'if', 'else', 'for', 'while', 'return', 'try', 'catch', 'async', 'await', 'new', 'this', 'true', 'false', 'null', 'undefined', 'void', 'any', 'interface']
  };

  let highlighted = code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  highlighted = highlighted.replace(/(["'`])(?:(?!\1)[^\\]|\\.)*\1/g, '<span style="color: #a5d6ff">$&</span>');

  highlighted = highlighted.replace(/(\/\/.*$)/gm, '<span style="color: #6a737d; font-style: italic;">$1</span>');
  highlighted = highlighted.replace(/(\/\*[\s\S]*?\*\/)/g, '<span style="color: #6a737d; font-style: italic;">$1</span>');

  const langKeywords = keywords[language] || keywords.javascript;
  langKeywords.forEach(keyword => {
    const regex = new RegExp(`\\b(${keyword})\\b`, 'g');
    highlighted = highlighted.replace(regex, '<span style="color: #ff79c6; font-weight: bold;">$1</span>');
  });

  highlighted = highlighted.replace(/\b(\d+\.?\d*)\b/g, '<span style="color: #bd93f9;">$1</span>');

  return highlighted;
};

export default function CodeEditor({ initialCode = '', language = 'python', onRun, readOnly = false }: CodeEditorProps) {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [lines, setLines] = useState(1);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const highlightRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLines(code.split('\n').length);
  }, [code]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = (e.target as HTMLTextAreaElement).selectionStart;
      const end = (e.target as HTMLTextAreaElement).selectionEnd;
      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      setCode(newCode);
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 4;
        }
      }, 0);
    }

    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleRun();
    }
  };

  const handleRun = async () => {
    if (!code.trim() || isRunning) return;
    
    setIsRunning(true);
    setOutput(prev => [...prev, `> Running ${language} code...`]);

    try {
      if (window.electronAPI?.runCode) {
        const result = await window.electronAPI.runCode(code, language);
        if (result.success) {
          if (result.output) {
            setOutput(prev => [...prev, result.output]);
          }
          if (result.errors) {
            setOutput(prev => [...prev, `Error: ${result.errors}`]);
          }
        }
      } else {
        setOutput(prev => [...prev, `[Simulated output for ${language}]`, 'Code executed successfully!']);
      }
    } catch (error) {
      setOutput(prev => [...prev, `Error: ${error}`]);
    }

    setIsRunning(false);
  };

  return (
    <div className="bg-[#1e1e1e] rounded-xl border border-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-[#404040]">
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400 uppercase tracking-wider">{language}</span>
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-[#ff5f56]"></div>
            <div className="w-3 h-3 rounded-full bg-[#ffbd2e]"></div>
            <div className="w-3 h-3 rounded-full bg-[#27c93f]"></div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">{code.length} chars</span>
          {!readOnly && (
            <button
              onClick={handleRun}
              disabled={isRunning}
              className="px-3 py-1 bg-primary text-black text-xs font-medium rounded hover:bg-primary/80 disabled:opacity-50 transition-all flex items-center gap-1"
            >
              {isRunning ? (
                <>
                  <div className="w-3 h-3 border-2 border-black/30 border-t-black rounded-full animate-spin"></div>
                  Running
                </>
              ) : (
                <>▶ Run (Ctrl+Enter)</>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Editor */}
      <div className="relative flex">
        {/* Line numbers */}
        <div className="py-3 px-2 bg-[#1e1e1e] border-r border-[#404040] text-right select-none">
          {Array.from({ length: lines }, (_, i) => (
            <div key={i} className="text-gray-500 text-xs leading-6 font-mono">
              {i + 1}
            </div>
          ))}
        </div>

        {/* Code area */}
        <div className="relative flex-1">
          <div
            ref={highlightRef}
            className="absolute inset-0 p-3 font-mono text-sm leading-6 overflow-auto pointer-events-none whitespace-pre-wrap break-keep"
            dangerouslySetInnerHTML={{ __html: syntaxHighlight(code, language) }}
            style={{ color: '#e2e8f0' }}
          />
          <textarea
            ref={textareaRef}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={handleKeyDown}
            readOnly={readOnly}
            className="relative w-full h-full min-h-[200px] p-3 font-mono text-sm leading-6 bg-transparent text-transparent caret-white resize-none focus:outline-none"
            spellCheck={false}
          />
        </div>
      </div>

      {/* Output */}
      {output.length > 0 && (
        <div className="border-t border-[#404040] bg-[#1a1a1a]">
          <div className="px-4 py-2 text-xs text-gray-400 border-b border-[#404040]">
            Output
          </div>
          <div className="p-3 font-mono text-sm text-green-400 max-h-40 overflow-auto">
            {output.map((line, i) => (
              <div key={i} className={line.startsWith('Error') ? 'text-red-400' : ''}>
                {line}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
