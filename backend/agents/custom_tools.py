#!/usr/bin/env python3
"""
Custom CrewAI Tools for Repository Analysis

This module contains specialized tools for repository analysis, code understanding,
and documentation generation. These tools extend the base CrewAI functionality
with domain-specific capabilities.
"""

import os
import ast
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse

import git
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_java as tsjava
import tree_sitter_cpp as tscpp
import tree_sitter_go as tsgo
import tree_sitter_rust as tsrust


class GitHubRepoCloneTool(BaseTool):
    """Tool for cloning GitHub repositories for analysis"""
    
    name: str = "GitHub Repository Clone Tool"
    description: str = (
        "Clone a GitHub repository to a local directory for analysis. "
        "Supports both public and private repositories (with proper authentication)."
    )
    
    def _run(self, repo_url: str, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """Clone a repository and return metadata"""
        try:
            # Parse repository URL
            parsed_url = urlparse(repo_url)
            if 'github.com' not in parsed_url.netloc:
                return {"error": "Only GitHub repositories are supported"}
            
            # Extract owner and repo name
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) < 2:
                return {"error": "Invalid GitHub repository URL"}
            
            owner, repo_name = path_parts[0], path_parts[1].replace('.git', '')
            
            # Set target directory
            if not target_dir:
                target_dir = tempfile.mkdtemp(prefix=f"{owner}_{repo_name}_")
            
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Clone repository
            repo = git.Repo.clone_from(repo_url, target_path)
            
            # Get repository metadata
            metadata = {
                "repo_url": repo_url,
                "owner": owner,
                "repo_name": repo_name,
                "local_path": str(target_path),
                "default_branch": repo.active_branch.name,
                "total_commits": len(list(repo.iter_commits())),
                "contributors": len(set(commit.author.email for commit in repo.iter_commits())),
                "last_commit": {
                    "hash": repo.head.commit.hexsha,
                    "message": repo.head.commit.message.strip(),
                    "author": repo.head.commit.author.name,
                    "date": repo.head.commit.committed_datetime.isoformat()
                }
            }
            
            return {"success": True, "metadata": metadata}
            
        except Exception as e:
            return {"error": f"Failed to clone repository: {str(e)}"}


class CodeStructureAnalyzerTool(BaseTool):
    """Tool for analyzing code structure using Tree-sitter"""
    
    name: str = "Code Structure Analyzer Tool"
    description: str = (
        "Analyze code structure and extract functions, classes, imports, "
        "and other structural elements from source code files."
    )
    
    def __init__(self):
        super().__init__()
        # Initialize parsers as instance variable, not field
        object.__setattr__(self, 'parsers', self._initialize_parsers())
    
    def _initialize_parsers(self) -> Dict[str, Parser]:
        """Initialize Tree-sitter parsers for different languages"""
        parsers = {}
        
        language_modules = {
            'python': tspython,
            'javascript': tsjavascript,
            'typescript': tstypescript,
            'java': tsjava,
            'cpp': tscpp,
            'c': tscpp,
            'go': tsgo,
            'rust': tsrust
        }
        
        for lang_name, module in language_modules.items():
            try:
                language = Language(module.language(), lang_name)
                parser = Parser()
                parser.set_language(language)
                parsers[lang_name] = parser
            except Exception as e:
                print(f"Warning: Could not initialize {lang_name} parser: {e}")
        
        return parsers
    
    def _get_language_from_extension(self, file_path: str) -> Optional[str]:
        """Determine programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust'
        }
        
        suffix = Path(file_path).suffix.lower()
        return ext_map.get(suffix)
    
    def _extract_functions(self, tree, source_code: bytes, language: str) -> List[Dict[str, Any]]:
        """Extract function definitions from the syntax tree"""
        functions = []
        
        def traverse(node):
            if language == 'python' and node.type == 'function_def':
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = source_code[name_node.start_byte:name_node.end_byte].decode('utf-8')
                    functions.append({
                        'name': func_name,
                        'type': 'function',
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'language': language
                    })
            
            elif language in ['javascript', 'typescript'] and node.type in ['function_declaration', 'method_definition']:
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = source_code[name_node.start_byte:name_node.end_byte].decode('utf-8')
                    functions.append({
                        'name': func_name,
                        'type': 'function',
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'language': language
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return functions
    
    def _extract_classes(self, tree, source_code: bytes, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions from the syntax tree"""
        classes = []
        
        def traverse(node):
            if language == 'python' and node.type == 'class_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    class_name = source_code[name_node.start_byte:name_node.end_byte].decode('utf-8')
                    classes.append({
                        'name': class_name,
                        'type': 'class',
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'language': language
                    })
            
            elif language in ['javascript', 'typescript'] and node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    class_name = source_code[name_node.start_byte:name_node.end_byte].decode('utf-8')
                    classes.append({
                        'name': class_name,
                        'type': 'class',
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'language': language
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return classes
    
    def _run(self, file_path: str) -> Dict[str, Any]:
        """Analyze code structure of a file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            language = self._get_language_from_extension(str(file_path))
            if not language or language not in self.parsers:
                return {"error": f"Unsupported language for file: {file_path}"}
            
            # Read file content
            with open(file_path, 'rb') as f:
                source_code = f.read()
            
            # Parse the code
            parser = self.parsers[language]
            tree = parser.parse(source_code)
            
            # Extract structural elements
            functions = self._extract_functions(tree, source_code, language)
            classes = self._extract_classes(tree, source_code, language)
            
            # Calculate metrics
            lines_of_code = len(source_code.decode('utf-8').splitlines())
            
            return {
                "success": True,
                "file_path": str(file_path),
                "language": language,
                "lines_of_code": lines_of_code,
                "functions": functions,
                "classes": classes,
                "total_functions": len(functions),
                "total_classes": len(classes)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze code structure: {str(e)}"}


class DependencyAnalyzerTool(BaseTool):
    """Tool for analyzing project dependencies"""
    
    name: str = "Dependency Analyzer Tool"
    description: str = (
        "Analyze project dependencies from various package management files "
        "like package.json, requirements.txt, Cargo.toml, etc."
    )
    
    def _analyze_package_json(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Node.js package.json file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            dependencies = data.get('dependencies', {})
            dev_dependencies = data.get('devDependencies', {})
            
            return {
                "package_manager": "npm",
                "dependencies": dependencies,
                "dev_dependencies": dev_dependencies,
                "total_dependencies": len(dependencies) + len(dev_dependencies),
                "scripts": data.get('scripts', {})
            }
        except Exception as e:
            return {"error": f"Failed to parse package.json: {str(e)}"}
    
    def _analyze_requirements_txt(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python requirements.txt file"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            dependencies = {}
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' in line:
                        name, version = line.split('==', 1)
                        dependencies[name.strip()] = version.strip()
                    elif '>=' in line:
                        name, version = line.split('>=', 1)
                        dependencies[name.strip()] = f">={version.strip()}"
                    else:
                        dependencies[line] = "*"
            
            return {
                "package_manager": "pip",
                "dependencies": dependencies,
                "total_dependencies": len(dependencies)
            }
        except Exception as e:
            return {"error": f"Failed to parse requirements.txt: {str(e)}"}
    
    def _analyze_pyproject_toml(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python pyproject.toml file"""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                data = tomli.load(f)
            
            project = data.get('project', {})
            dependencies = project.get('dependencies', [])
            
            # Convert list to dict format
            deps_dict = {}
            for dep in dependencies:
                if '>=' in dep:
                    name, version = dep.split('>=', 1)
                    deps_dict[name.strip()] = f">={version.strip()}"
                elif '==' in dep:
                    name, version = dep.split('==', 1)
                    deps_dict[name.strip()] = version.strip()
                else:
                    deps_dict[dep.strip()] = "*"
            
            return {
                "package_manager": "pip",
                "dependencies": deps_dict,
                "total_dependencies": len(deps_dict),
                "build_system": data.get('build-system', {})
            }
        except Exception as e:
            return {"error": f"Failed to parse pyproject.toml: {str(e)}"}
    
    def _run(self, project_path: str) -> Dict[str, Any]:
        """Analyze dependencies in a project directory"""
        try:
            project_path = Path(project_path)
            if not project_path.exists():
                return {"error": f"Project path not found: {project_path}"}
            
            results = {"dependency_files": []}
            
            # Check for different dependency files
            dependency_files = {
                'package.json': self._analyze_package_json,
                'requirements.txt': self._analyze_requirements_txt,
                'pyproject.toml': self._analyze_pyproject_toml
            }
            
            for filename, analyzer in dependency_files.items():
                file_path = project_path / filename
                if file_path.exists():
                    analysis = analyzer(file_path)
                    analysis['file'] = filename
                    results['dependency_files'].append(analysis)
            
            if not results['dependency_files']:
                return {"error": "No dependency files found in project"}
            
            return {"success": True, "analysis": results}
            
        except Exception as e:
            return {"error": f"Failed to analyze dependencies: {str(e)}"}


class GitHistoryAnalyzerTool(BaseTool):
    """Tool for analyzing Git repository history and statistics"""
    
    name: str = "Git History Analyzer Tool"
    description: str = (
        "Analyze Git repository history, including commit patterns, "
        "contributor statistics, and code change metrics."
    )
    
    def _run(self, repo_path: str, max_commits: int = 100) -> Dict[str, Any]:
        """Analyze Git repository history"""
        try:
            repo_path = Path(repo_path)
            if not repo_path.exists():
                return {"error": f"Repository path not found: {repo_path}"}
            
            repo = git.Repo(repo_path)
            
            # Get commit history
            commits = list(repo.iter_commits(max_count=max_commits))
            
            # Analyze contributors
            contributors = {}
            commit_dates = []
            
            for commit in commits:
                author = commit.author.name
                email = commit.author.email
                date = commit.committed_datetime
                
                commit_dates.append(date)
                
                if author not in contributors:
                    contributors[author] = {
                        'email': email,
                        'commits': 0,
                        'first_commit': date,
                        'last_commit': date
                    }
                
                contributors[author]['commits'] += 1
                if date < contributors[author]['first_commit']:
                    contributors[author]['first_commit'] = date
                if date > contributors[author]['last_commit']:
                    contributors[author]['last_commit'] = date
            
            # Calculate statistics
            total_commits = len(commits)
            total_contributors = len(contributors)
            
            # Get branch information
            branches = [ref.name for ref in repo.refs if isinstance(ref, git.Head)]
            
            # Get repository size (approximate)
            repo_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file())
            
            return {
                "success": True,
                "repository_path": str(repo_path),
                "total_commits": total_commits,
                "total_contributors": total_contributors,
                "contributors": {
                    name: {
                        'email': info['email'],
                        'commits': info['commits'],
                        'first_commit': info['first_commit'].isoformat(),
                        'last_commit': info['last_commit'].isoformat()
                    }
                    for name, info in contributors.items()
                },
                "branches": branches,
                "repository_size_bytes": repo_size,
                "latest_commit": {
                    "hash": commits[0].hexsha,
                    "message": commits[0].message.strip(),
                    "author": commits[0].author.name,
                    "date": commits[0].committed_datetime.isoformat()
                } if commits else None
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze Git history: {str(e)}"}


class DocumentationGeneratorTool(BaseTool):
    """Tool for generating documentation from code analysis"""
    
    name: str = "Documentation Generator Tool"
    description: str = (
        "Generate comprehensive documentation from code analysis results, "
        "including API documentation, architecture overviews, and usage guides."
    )
    
    def _generate_api_docs(self, functions: List[Dict], classes: List[Dict]) -> str:
        """Generate API documentation from functions and classes"""
        docs = ["# API Documentation\n"]
        
        if classes:
            docs.append("## Classes\n")
            for cls in classes:
                docs.append(f"### {cls['name']}\n")
                docs.append(f"- **Location**: Line {cls['start_line']}-{cls['end_line']}\n")
                docs.append(f"- **Language**: {cls['language']}\n\n")
        
        if functions:
            docs.append("## Functions\n")
            for func in functions:
                docs.append(f"### {func['name']}\n")
                docs.append(f"- **Location**: Line {func['start_line']}-{func['end_line']}\n")
                docs.append(f"- **Language**: {func['language']}\n\n")
        
        return "".join(docs)
    
    def _generate_project_overview(self, analysis_results: Dict[str, Any]) -> str:
        """Generate project overview documentation"""
        docs = ["# Project Overview\n\n"]
        
        # Repository information
        if 'metadata' in analysis_results:
            metadata = analysis_results['metadata']
            docs.append(f"**Repository**: {metadata.get('repo_name', 'Unknown')}\n")
            docs.append(f"**Owner**: {metadata.get('owner', 'Unknown')}\n")
            docs.append(f"**Default Branch**: {metadata.get('default_branch', 'Unknown')}\n")
            docs.append(f"**Total Commits**: {metadata.get('total_commits', 'Unknown')}\n")
            docs.append(f"**Contributors**: {metadata.get('contributors', 'Unknown')}\n\n")
        
        # Code statistics
        if 'code_analysis' in analysis_results:
            code_stats = analysis_results['code_analysis']
            docs.append("## Code Statistics\n\n")
            docs.append(f"- **Total Files Analyzed**: {len(code_stats)}\n")
            
            total_functions = sum(len(file_data.get('functions', [])) for file_data in code_stats.values())
            total_classes = sum(len(file_data.get('classes', [])) for file_data in code_stats.values())
            total_lines = sum(file_data.get('lines_of_code', 0) for file_data in code_stats.values())
            
            docs.append(f"- **Total Functions**: {total_functions}\n")
            docs.append(f"- **Total Classes**: {total_classes}\n")
            docs.append(f"- **Total Lines of Code**: {total_lines}\n\n")
        
        # Dependencies
        if 'dependencies' in analysis_results:
            deps = analysis_results['dependencies']
            docs.append("## Dependencies\n\n")
            for dep_file in deps.get('dependency_files', []):
                if 'error' not in dep_file:
                    docs.append(f"### {dep_file['file']}\n")
                    docs.append(f"- **Package Manager**: {dep_file.get('package_manager', 'Unknown')}\n")
                    docs.append(f"- **Total Dependencies**: {dep_file.get('total_dependencies', 0)}\n\n")
        
        return "".join(docs)
    
    def _run(self, analysis_results: Dict[str, Any], output_format: str = "markdown") -> Dict[str, Any]:
        """Generate documentation from analysis results"""
        try:
            if output_format != "markdown":
                return {"error": "Only markdown format is currently supported"}
            
            documentation = {}
            
            # Generate project overview
            documentation['project_overview'] = self._generate_project_overview(analysis_results)
            
            # Generate API documentation if code analysis is available
            if 'code_analysis' in analysis_results:
                all_functions = []
                all_classes = []
                
                for file_data in analysis_results['code_analysis'].values():
                    if isinstance(file_data, dict):
                        all_functions.extend(file_data.get('functions', []))
                        all_classes.extend(file_data.get('classes', []))
                
                documentation['api_docs'] = self._generate_api_docs(all_functions, all_classes)
            
            return {
                "success": True,
                "documentation": documentation,
                "format": output_format
            }
            
        except Exception as e:
            return {"error": f"Failed to generate documentation: {str(e)}"}


class ArchitectureDiagramTool(BaseTool):
    """Tool for generating architecture diagrams from code analysis"""
    
    name: str = "Architecture Diagram Tool"
    description: str = (
        "Generate architecture diagrams and visualizations from code structure "
        "and dependency analysis results."
    )
    
    def _generate_mermaid_diagram(self, analysis_results: Dict[str, Any]) -> str:
        """Generate Mermaid diagram from analysis results"""
        diagram = ["graph TD\n"]
        
        # Add nodes for each file/module
        if 'code_analysis' in analysis_results:
            for file_path, file_data in analysis_results['code_analysis'].items():
                if isinstance(file_data, dict) and 'success' in file_data:
                    file_name = Path(file_path).stem
                    diagram.append(f"    {file_name}[{file_name}]\n")
                    
                    # Add classes as sub-nodes
                    for cls in file_data.get('classes', []):
                        class_id = f"{file_name}_{cls['name']}"
                        diagram.append(f"    {class_id}[{cls['name']}]\n")
                        diagram.append(f"    {file_name} --> {class_id}\n")
        
        return "".join(diagram)
    
    def _run(self, analysis_results: Dict[str, Any], diagram_type: str = "mermaid") -> Dict[str, Any]:
        """Generate architecture diagram"""
        try:
            if diagram_type != "mermaid":
                return {"error": "Only mermaid diagram type is currently supported"}
            
            diagram = self._generate_mermaid_diagram(analysis_results)
            
            return {
                "success": True,
                "diagram": diagram,
                "diagram_type": diagram_type
            }
            
        except Exception as e:
            return {"error": f"Failed to generate architecture diagram: {str(e)}"}