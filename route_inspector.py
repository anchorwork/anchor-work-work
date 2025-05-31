# utils/route_inspector.py
"""
Route analysis and documentation utilities.
Provides functions to discover, analyze, and document API routes.
"""

import re
import ast
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from agentlogging.unified_logger import log_event

logger = logging.getLogger(__name__)


class RouteInspector:
    """Analyzes and documents API routes in the codebase."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(".")
        self.route_patterns = [
            r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'router\.add_api_route\(["\']([^"\']+)["\']',
        ]
    
    def discover_routes(self, directories: List[str] = None) -> List[Dict[str, Any]]:
        """
        Discover all API routes in the specified directories.
        
        Args:
            directories: List of directory names to search (default: ["routes", "agents"])
            
        Returns:
            List of route information dictionaries
        """
        if directories is None:
            directories = ["routes", "agents"]
        
        routes = []
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue
                
            for py_file in dir_path.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                    
                try:
                    file_routes = self._extract_routes_from_file(py_file)
                    routes.extend(file_routes)
                except Exception as e:
                    logger.warning(f"Error analyzing {py_file}: {e}")
        
        return sorted(routes, key=lambda x: x['path'])
    
    def _extract_routes_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract route information from a Python file."""
        routes = []
        content = file_path.read_text(encoding="utf-8")
        
        # Extract routes using regex patterns
        for pattern in self.route_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if len(match.groups()) == 2:
                    method, path = match.groups()
                else:
                    method = "unknown"
                    path = match.groups()[0]
                
                route_info = {
                    'method': method.upper(),
                    'path': path,
                    'file': str(file_path.relative_to(self.project_root)),
                    'line': content[:match.start()].count('\n') + 1
                }
                
                # Try to extract function name and docstring
                func_info = self._extract_function_info(content, match.end())
                route_info.update(func_info)
                
                routes.append(route_info)
        
        return routes
    
    def _extract_function_info(self, content: str, start_pos: int) -> Dict[str, Any]:
        """Extract function name and docstring following a route decorator."""
        # Find the function definition after the decorator
        remaining_content = content[start_pos:]
        
        # Look for function definition
        func_match = re.search(r'async\s+def\s+(\w+)|def\s+(\w+)', remaining_content)
        if not func_match:
            return {'function': 'unknown', 'docstring': ''}
        
        func_name = func_match.group(1) or func_match.group(2)
        
        # Try to extract docstring using AST
        try:
            # Find the start of the function
            func_start = start_pos + func_match.start()
            lines = content[:func_start].count('\n')
            
            # Parse just enough to get the function
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if (isinstance(node, ast.FunctionDef) and 
                    node.name == func_name and 
                    node.lineno > lines):
                    
                    docstring = ast.get_docstring(node) or ''
                    return {
                        'function': func_name,
                        'docstring': docstring.strip()
                    }
        except:
            pass
        
        return {'function': func_name, 'docstring': ''}
    
    def generate_route_index(self, routes: List[Dict[str, Any]]) -> str:
        """
        Generate a markdown index of all discovered routes.
        
        Args:
            routes: List of route information from discover_routes()
            
        Returns:
            Markdown formatted route index
        """
        if not routes:
            return "# Route Index\n\nNo routes discovered."
        
        lines = [
            "# API Route Index",
            f"",
            f"**Total Routes:** {len(routes)}",
            "",
            "## Routes by Endpoint",
            ""
        ]
        
        for route in routes:
            lines.append(f"### {route['method']} {route['path']}")
            lines.append(f"- **Function:** `{route['function']}`")
            lines.append(f"- **File:** `{route['file']}:{route['line']}`")
            
            if route['docstring']:
                lines.append(f"- **Description:** {route['docstring']}")
            else:
                lines.append(f"- **Description:** _(No documentation)_")
            
            lines.append("")
        
        # Add summary by method
        method_counts = {}
        for route in routes:
            method = route['method']
            method_counts[method] = method_counts.get(method, 0) + 1
        
        lines.append("## Summary by Method")
        lines.append("")
        for method, count in sorted(method_counts.items()):
            lines.append(f"- **{method}:** {count} routes")
        
        return "\n".join(lines)
    
    def analyze_route_coverage(self, routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze route coverage and documentation quality.
        
        Args:
            routes: List of route information
            
        Returns:
            Analysis results dictionary
        """
        total_routes = len(routes)
        documented_routes = sum(1 for r in routes if r['docstring'])
        undocumented_routes = total_routes - documented_routes
        
        # Group by file
        files = {}
        for route in routes:
            file_name = route['file']
            if file_name not in files:
                files[file_name] = []
            files[file_name].append(route)
        
        # Find missing documentation
        missing_docs = [r for r in routes if not r['docstring']]
        
        return {
            'total_routes': total_routes,
            'documented_routes': documented_routes,
            'undocumented_routes': undocumented_routes,
            'documentation_rate': documented_routes / total_routes if total_routes > 0 else 0,
            'files_with_routes': len(files),
            'routes_per_file': {f: len(routes) for f, routes in files.items()},
            'missing_documentation': missing_docs
        }
    
    def suggest_improvements(self, analysis: Dict[str, Any]) -> str:
        """Generate suggestions for improving route documentation and structure."""
        suggestions = []
        
        doc_rate = analysis['documentation_rate']
        if doc_rate < 0.5:
            suggestions.append(
                f"📚 Low documentation rate ({doc_rate:.1%}). Consider adding docstrings to route handlers."
            )
        
        if analysis['undocumented_routes'] > 0:
            suggestions.append(
                f"📝 {analysis['undocumented_routes']} routes lack documentation. "
                "Adding docstrings improves API discoverability."
            )
        
        # Check for files with many routes
        heavy_files = [f for f, count in analysis['routes_per_file'].items() if count > 10]
        if heavy_files:
            suggestions.append(
                f"🔄 Consider splitting large route files: {', '.join(heavy_files)}"
            )
        
        if not suggestions:
            suggestions.append("✅ Route structure and documentation look good!")
        
        return "\n".join(suggestions)


# Global inspector instance
_global_inspector: Optional[RouteInspector] = None

def get_route_inspector(project_root: Path = None) -> RouteInspector:
    """Get or create the global route inspector instance."""
    global _global_inspector
    if _global_inspector is None:
        _global_inspector = RouteInspector(project_root)
    return _global_inspector

def discover_routes(directories: List[str] = None, project_root: Path = None) -> List[Dict[str, Any]]:
    """Convenience function to discover routes."""
    inspector = get_route_inspector(project_root)
    return inspector.discover_routes(directories)

def generate_route_documentation(directories: List[str] = None, project_root: Path = None, output_format: str = "markdown") -> str:
    """Generate comprehensive route documentation. Supports markdown or json output."""
    inspector = get_route_inspector(project_root)
    routes = inspector.discover_routes(directories)
    log_event("route_discovery_complete", {"total_routes": len(routes)}, level="INFO")
    if not routes:
        return "No routes found in the specified directories."
    
    # Generate main index
    index = inspector.generate_route_index(routes)
    
    # Add analysis
    analysis = inspector.analyze_route_coverage(routes)
    suggestions = inspector.suggest_improvements(analysis)
    
    if output_format == "json":
        return json.dumps({
            "routes": routes,
            "analysis": analysis,
            "suggestions": suggestions
        }, indent=2)
    
    return f"{index}\n\n## Analysis & Suggestions\n\n{suggestions}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate API route documentation.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--output", type=str, default=None, help="Output file path (for JSON)")
    args = parser.parse_args()
    output = generate_route_documentation(output_format=args.format)
    if args.format == "json":
        output_path = args.output or "routes.json"
        with open(output_path, "w") as f:
            f.write(output)
        print(f"JSON route documentation written to {output_path}")
    else:
        print(output)
