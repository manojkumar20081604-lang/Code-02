"""
02 v1 - Developer Assistant
Code generation, debugging, and project analysis
"""

import os
import re
import subprocess
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("02-Dev")

class CodeLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    BASH = "bash"

@dataclass
class CodeSnippet:
    language: str
    code: str
    description: str
    complexity: str = "medium"
    lines: int = 0

@dataclass
class CodeAnalysis:
    language: str
    issues: List[str]
    suggestions: List[str]
    complexity: str
    lines: int
    functions: List[str]

class DevAssistant:
    """
    Developer Assistant - Helps with code-related tasks.
    
    Features:
    - Code generation
    - Code explanation
    - Bug detection
    - Project analysis
    - File operations
    - Command execution
    """
    
    def __init__(self):
        self.templates = self._load_templates()
        self.language_patterns = {
            CodeLanguage.PYTHON: [".py", "python", "py"],
            CodeLanguage.JAVASCRIPT: [".js", "javascript", "node"],
            CodeLanguage.TYPESCRIPT: [".ts", "typescript"],
            CodeLanguage.JAVA: [".java"],
            CodeLanguage.HTML: [".html", "html"],
            CodeLanguage.CSS: [".css"],
            CodeLanguage.SQL: [".sql"],
            CodeLanguage.BASH: [".sh", "bash", "shell"],
        }
        
    def _load_templates(self) -> Dict:
        """Load code templates"""
        return {
            "python_function": '''def {name}({params}):
    """{description}"""
    {body}
    return {return_val}
''',
            "python_class": '''class {name}:
    """{description}"""
    
    def __init__(self{init_params}):
        {init_body}
    
{methods}
''',
            "javascript_function": '''function {name}({params}) {{
    // {description}
    {body}
    return {return_val};
}}
''',
            "api_endpoint": '''@app.route('/{endpoint}', methods=['{methods}'])
def {name}():
    """{description}"""
    {body}
    return {return_val}
''',
            "react_component": '''import React from 'react';

function {name}({{ props }}) {{
    return (
        <div className="{class_name}">
            {content}
        </div>
    );
}}

export default {name};
''',
        }
    
    def detect_language(self, text: str) -> str:
        """Detect programming language from text"""
        text_lower = text.lower()
        
        for lang, patterns in self.language_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return lang.value
        
        # Default to python
        return "python"
    
    def generate_code(
        self, 
        task: str, 
        language: str = None, 
        context: Dict = None
    ) -> CodeSnippet:
        """Generate code based on task description"""
        if not language:
            language = self.detect_language(task)
        
        logger.info(f"Generating {language} code for: {task[:50]}...")
        
        # Simple template-based generation
        code = ""
        description = task
        
        if "function" in task.lower() or "def" in task.lower():
            if language == "python":
                name = self._extract_name(task) or "my_function"
                code = self.templates["python_function"].format(
                    name=name,
                    params="param1, param2",
                    description="Generated function",
                    body="    # Your code here\n    pass",
                    return_val="None"
                )
            elif language in ["javascript", "typescript"]:
                name = self._extract_name(task) or "myFunction"
                code = self.templates["javascript_function"].format(
                    name=name,
                    params="param1, param2",
                    description="Generated function",
                    body="    // Your code here",
                    return_val="null"
                )
        
        elif "class" in task.lower():
            if language == "python":
                name = self._extract_name(task) or "MyClass"
                code = self.templates["python_class"].format(
                    name=name,
                    description="Generated class",
                    init_params="",
                    init_body="    pass",
                    methods="    pass"
                )
        
        elif "api" in task.lower() or "endpoint" in task.lower():
            name = self._extract_name(task) or "endpoint"
            code = self.templates["api_endpoint"].format(
                endpoint=name,
                methods="POST",
                name=name,
                description="API endpoint",
                body="    # Handle request",
                return_val='{"message": "success"}'
            )
        
        elif "react" in task.lower() or "component" in task.lower():
            name = self._extract_name(task) or "MyComponent"
            code = self.templates["react_component"].format(
                name=name,
                class_name=name.lower(),
                content="    // Your JSX here"
            )
        
        elif "web" in task.lower() or "html" in task.lower():
            code = self._generate_html_skeleton(task)
        
        else:
            code = self._generate_generic(task, language)
        
        return CodeSnippet(
            language=language,
            code=code,
            description=description,
            lines=len(code.split('\n'))
        )
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from task description"""
        patterns = [
            r'called\s+(\w+)',
            r'named\s+(\w+)',
            r'function\s+(\w+)',
            r'class\s+(\w+)',
            r'for\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _generate_html_skeleton(self, task: str) -> str:
        """Generate HTML skeleton"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
    </style>
</head>
<body>
    <h1>Hello World</h1>
    <p>Your content here</p>
    
    <script>
        // Your JavaScript here
    </script>
</body>
</html>'''
    
    def _generate_generic(self, task: str, language: str) -> str:
        """Generate generic code"""
        if language == "python":
            return f'''# Task: {task}

def main():
    # Your implementation here
    pass

if __name__ == "__main__":
    main()
'''
        elif language == "javascript":
            return f'''// Task: {task}

// Your implementation here
'''
        else:
            return f'// {language} code for: {task}'
    
    def explain_code(self, code: str) -> str:
        """Explain what code does"""
        lines = code.strip().split('\n')
        explanation = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('#'):
                continue
            
            # Simple pattern matching
            if 'def ' in line:
                explanation.append(f"Line {i}: Defines a function")
            elif 'class ' in line:
                explanation.append(f"Line {i}: Defines a class")
            elif 'import ' in line:
                explanation.append(f"Line {i}: Imports a module")
            elif 'return ' in line:
                explanation.append(f"Line {i}: Returns a value")
            elif 'if ' in line:
                explanation.append(f"Line {i}: Conditional statement")
            elif 'for ' in line:
                explanation.append(f"Line {i}: Loop iteration")
            elif 'while ' in line:
                explanation.append(f"Line {i}: While loop")
        
        return '\n'.join(explanation) if explanation else "Code analysis complete."
    
    def analyze_code(self, code: str, language: str = None) -> CodeAnalysis:
        """Analyze code for issues and complexity"""
        if not language:
            language = self.detect_language(code)
        
        lines = code.split('\n')
        issues = []
        suggestions = []
        functions = []
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for long lines
            if len(line) > 120:
                issues.append(f"Line {i}: Line too long ({len(line)} chars)")
            
            # Check for TODO/FIXME
            if 'TODO' in line or 'FIXME' in line:
                suggestions.append(f"Line {i}: Unresolved TODO/FIXME")
            
            # Detect functions
            if language == "python" and line_stripped.startswith('def '):
                func_name = line_stripped.split('(')[0].replace('def ', '')
                functions.append(func_name)
            
            if language == "javascript" and 'function ' in line_stripped:
                match = re.search(r'function\s+(\w+)', line_stripped)
                if match:
                    functions.append(match.group(1))
        
        # Calculate complexity
        complexity = "low"
        if len(issues) > 5 or len(lines) > 100:
            complexity = "high"
        elif len(issues) > 2 or len(lines) > 50:
            complexity = "medium"
        
        return CodeAnalysis(
            language=language,
            issues=issues,
            suggestions=suggestions,
            complexity=complexity,
            lines=len(lines),
            functions=functions
        )
    
    def fix_common_errors(self, error: str, language: str = "python") -> List[str]:
        """Suggest fixes for common errors"""
        fixes = []
        error_lower = error.lower()
        
        common_fixes = {
            "indentation": [
                "Use 4 spaces for indentation",
                "Check for mixed tabs and spaces",
                "Ensure consistent indentation throughout"
            ],
            "syntax": [
                "Check for missing colons",
                "Verify all parentheses are closed",
                "Check for missing quotes around strings"
            ],
            "undefined": [
                "Variable not defined - declare it first",
                "Check for typos in variable names",
                "Import required modules"
            ],
            "import": [
                "Module not found - install with pip/npm",
                "Check module name spelling",
                "Verify __init__.py exists for local imports"
            ],
            "type": [
                "Type mismatch - check variable types",
                "Use type() to debug",
                "Consider type conversion"
            ]
        }
        
        for error_type, suggestions in common_fixes.items():
            if error_type in error_lower:
                fixes.extend(suggestions)
        
        return fixes if fixes else ["Review the error message carefully", "Check documentation"]
    
    def execute_code(self, code: str, language: str) -> Tuple[str, str]:
        """Execute code and return output"""
        import tempfile
        import os
        
        # Create temp file
        ext_map = {
            "python": ".py",
            "javascript": ".js",
            "bash": ".sh"
        }
        
        ext = ext_map.get(language, ".txt")
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            if language == "python":
                result = subprocess.run(
                    ['python', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            elif language == "javascript":
                result = subprocess.run(
                    ['node', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                return "", f"Execution not supported for {language}"
            
            return result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return "", "Execution timed out"
        except Exception as e:
            return "", str(e)
        finally:
            os.unlink(temp_path)
    
    def generate_readme(self, project_name: str, description: str = "", language: str = "python") -> str:
        """Generate README.md for a project"""
        lang_badges = {
            "python": "![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)",
            "javascript": "![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)",
        }
        
        return f'''# {project_name}

{lang_badges.get(language, "")}

{description}

## Installation

```bash
# Install dependencies
```

## Usage

```bash
# Run the project
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

MIT
'''


__all__ = ['DevAssistant', 'CodeSnippet', 'CodeAnalysis', 'CodeLanguage']
