from __future__ import annotations

"""Tool: codebase_explorer

Advanced file exploration and analysis tool for AI agents to understand
the codebase structure, search for patterns, and get contextual information
about uploaded files.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
import json

from .base import BaseTool

_WORKSPACE_ROOT = Path(os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")).resolve()
_WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)


class CodebaseExplorerTool(BaseTool):
    name: str = "codebase_explorer"
    description: str = (
        "Advanced codebase exploration and analysis tool. Parameters:\n"
        "- action (str): 'list', 'analyze', 'search', or 'summary'.\n"
        "- path (str, optional): Specific directory/file path to focus on.\n"
        "- pattern (str, optional): Search pattern for 'search' action.\n"
        "- file_types (list, optional): Filter by file extensions (e.g., ['.py', '.js']).\n"
        "Returns: Structured information about the codebase."
    )

    async def run(
        self,
        action: Literal["list", "analyze", "search", "summary"],
        path: Optional[str] = None,
        pattern: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        **kwargs
    ) -> str:  # type: ignore[override]
        
        if action == "list":
            return await self._list_files(path, file_types)
        elif action == "analyze":
            return await self._analyze_structure(path)
        elif action == "search":
            return await self._search_content(pattern, path, file_types)
        elif action == "summary":
            return await self._get_summary(path)
        else:
            raise ValueError(f"Unknown action: {action}. Use 'list', 'analyze', 'search', or 'summary'.")

    async def _list_files(self, path: Optional[str] = None, file_types: Optional[List[str]] = None) -> str:
        """List files in the workspace with optional filtering."""
        base_path = _WORKSPACE_ROOT / (path or "")
        base_path = base_path.resolve()
        
        if not base_path.is_relative_to(_WORKSPACE_ROOT):
            raise ValueError("Access outside workspace is not allowed.")
        
        if not base_path.exists():
            return f"Path '{path}' does not exist in the workspace."
        
        files = []
        if base_path.is_file():
            files = [str(base_path.relative_to(_WORKSPACE_ROOT))]
        else:
            for file_path in base_path.rglob("*"):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(_WORKSPACE_ROOT))
                    if file_types:
                        if any(rel_path.endswith(ext) for ext in file_types):
                            files.append(rel_path)
                    else:
                        files.append(rel_path)
        
        # Group files by directory
        grouped = {}
        for file in sorted(files):
            dir_name = str(Path(file).parent) if Path(file).parent != Path('.') else 'root'
            if dir_name not in grouped:
                grouped[dir_name] = []
            grouped[dir_name].append(Path(file).name)
        
        result = f"Files in workspace{f' (path: {path})' if path else ''}:\n\n"
        for dir_name, files_list in grouped.items():
            result += f"📁 {dir_name}/\n"
            for file in files_list:
                file_ext = Path(file).suffix
                icon = self._get_file_icon(file_ext)
                result += f"  {icon} {file}\n"
            result += "\n"
        
        return result

    async def _analyze_structure(self, path: Optional[str] = None) -> str:
        """Analyze the structure and provide insights about the codebase."""
        base_path = _WORKSPACE_ROOT / (path or "")
        base_path = base_path.resolve()
        
        if not base_path.is_relative_to(_WORKSPACE_ROOT):
            raise ValueError("Access outside workspace is not allowed.")
        
        if not base_path.exists():
            return f"Path '{path}' does not exist in the workspace."
        
        # Collect file statistics
        stats = {
            'total_files': 0,
            'file_types': {},
            'directories': set(),
            'languages': {},
            'size_breakdown': {'small': 0, 'medium': 0, 'large': 0}
        }
        
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                stats['total_files'] += 1
                rel_path = str(file_path.relative_to(_WORKSPACE_ROOT))
                
                # Directory tracking
                stats['directories'].add(str(file_path.parent.relative_to(_WORKSPACE_ROOT)))
                
                # File extension tracking
                ext = file_path.suffix.lower()
                stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                
                # Language detection
                lang = self._detect_language(ext)
                if lang:
                    stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
                
                # Size categories
                try:
                    size = file_path.stat().st_size
                    if size < 1024:  # < 1KB
                        stats['size_breakdown']['small'] += 1
                    elif size < 50 * 1024:  # < 50KB
                        stats['size_breakdown']['medium'] += 1
                    else:
                        stats['size_breakdown']['large'] += 1
                except:
                    pass
        
        # Generate analysis report
        result = f"📊 Codebase Analysis{f' for {path}' if path else ''}:\n\n"
        result += f"📁 Total Files: {stats['total_files']}\n"
        result += f"📂 Directories: {len(stats['directories'])}\n\n"
        
        if stats['languages']:
            result += "🔤 Programming Languages:\n"
            for lang, count in sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True):
                result += f"  • {lang}: {count} files\n"
            result += "\n"
        
        if stats['file_types']:
            result += "📄 File Types:\n"
            for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
                ext_display = ext if ext else '(no extension)'
                result += f"  • {ext_display}: {count} files\n"
            result += "\n"
        
        result += "📏 File Sizes:\n"
        result += f"  • Small (<1KB): {stats['size_breakdown']['small']}\n"
        result += f"  • Medium (1KB-50KB): {stats['size_breakdown']['medium']}\n"
        result += f"  • Large (>50KB): {stats['size_breakdown']['large']}\n"
        
        return result

    async def _search_content(self, pattern: Optional[str], path: Optional[str] = None, file_types: Optional[List[str]] = None) -> str:
        """Search for patterns in file content."""
        if not pattern:
            return "Please provide a search pattern."
        
        base_path = _WORKSPACE_ROOT / (path or "")
        base_path = base_path.resolve()
        
        if not base_path.is_relative_to(_WORKSPACE_ROOT):
            raise ValueError("Access outside workspace is not allowed.")
        
        matches = []
        text_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.sql'}
        
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(_WORKSPACE_ROOT))
                
                # Filter by file types if specified
                if file_types and not any(rel_path.endswith(ext) for ext in file_types):
                    continue
                
                # Only search text files
                if file_path.suffix.lower() not in text_extensions:
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if pattern.lower() in content.lower():
                        # Find line numbers
                        lines = content.split('\n')
                        matching_lines = []
                        for i, line in enumerate(lines, 1):
                            if pattern.lower() in line.lower():
                                matching_lines.append(f"  Line {i}: {line.strip()}")
                                if len(matching_lines) >= 3:  # Limit to first 3 matches per file
                                    break
                        
                        matches.append({
                            'file': rel_path,
                            'matches': matching_lines
                        })
                except:
                    continue
        
        if not matches:
            return f"No matches found for pattern '{pattern}'"
        
        result = f"🔍 Search results for '{pattern}':\n\n"
        for match in matches[:10]:  # Limit to first 10 files
            result += f"📄 {match['file']}:\n"
            result += '\n'.join(match['matches'])
            result += "\n\n"
        
        if len(matches) > 10:
            result += f"... and {len(matches) - 10} more files with matches.\n"
        
        return result

    async def _get_summary(self, path: Optional[str] = None) -> str:
        """Get a high-level summary of the workspace or specific path."""
        base_path = _WORKSPACE_ROOT / (path or "")
        base_path = base_path.resolve()
        
        if not base_path.is_relative_to(_WORKSPACE_ROOT):
            raise ValueError("Access outside workspace is not allowed.")
        
        # Get quick analysis
        analysis = await self._analyze_structure(path)
        
        # Add project type detection
        project_indicators = {
            'Python': ['.py', 'requirements.txt', 'setup.py', 'pyproject.toml'],
            'Node.js/JavaScript': ['package.json', '.js', '.ts', 'node_modules'],
            'React': ['package.json', '.jsx', '.tsx', 'src'],
            'Next.js': ['next.config.js', '.next', 'pages', 'app'],
            'Django': ['manage.py', 'settings.py', 'urls.py'],
            'FastAPI': ['main.py', 'app', 'requirements.txt'],
            'Documentation': ['.md', '.rst', 'docs', 'README'],
        }
        
        detected_types = []
        for project_type, indicators in project_indicators.items():
            score = 0
            for indicator in indicators:
                for file_path in base_path.rglob("*"):
                    if indicator in str(file_path).lower():
                        score += 1
                        break
            if score >= 2:  # Need at least 2 indicators
                detected_types.append(project_type)
        
        summary = f"📋 Project Summary{f' for {path}' if path else ''}:\n\n"
        
        if detected_types:
            summary += f"🎯 Detected Project Types: {', '.join(detected_types)}\n\n"
        
        summary += analysis
        
        # Add recommendations based on file types
        summary += "\n💡 AI Assistant Capabilities:\n"
        summary += "  • CTO can help with code architecture, debugging, and technical decisions\n"
        summary += "  • CMO can analyze documentation, marketing materials, and user-facing content\n"
        summary += "  • CEO can review business documents, plans, and overall strategy\n"
        
        return summary

    def _get_file_icon(self, ext: str) -> str:
        """Get an emoji icon for file type."""
        icons = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.tsx': '⚛️', '.jsx': '⚛️',
            '.html': '🌐', '.css': '🎨', '.md': '📝', '.txt': '📄',
            '.json': '📋', '.yaml': '⚙️', '.yml': '⚙️', '.xml': '📄',
            '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.jpg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.svg': '🎨',
            '.mp4': '🎬', '.mp3': '🎵', '.wav': '🎵',
            '.zip': '📦', '.tar': '📦', '.gz': '📦',
        }
        return icons.get(ext.lower(), '📄')

    def _detect_language(self, ext: str) -> Optional[str]:
        """Detect programming language from file extension."""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript/React',
            '.jsx': 'JavaScript/React',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.dart': 'Dart',
            '.r': 'R',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.zsh': 'Zsh',
            '.ps1': 'PowerShell',
        }
        return lang_map.get(ext.lower()) 