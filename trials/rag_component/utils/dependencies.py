"""
Dependency Management for RAG Component

Utility functions and classes for managing package dependencies.
"""

import logging
import importlib
from typing import Dict, List, Tuple, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Global dependency flags
DEPENDENCY_STATUS = {
    'crewai': False,
    'embedchain': False,
    'github': False,
    'google_genai': False,
}

class DependencyManager:
    """
    Manages package dependencies and provides placeholders
    for missing dependencies.
    """
    
    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """
        Check if required packages are installed.
        
        Returns:
            Dict[str, bool]: Status of each dependency
        """
        # Check CrewAI
        try:
            importlib.import_module('crewai')
            DEPENDENCY_STATUS['crewai'] = True
        except ImportError:
            logger.warning("CrewAI not installed. Run: pip install crewai crewai-tools")
            DEPENDENCY_STATUS['crewai'] = False
            
        # Check EmbedChain
        try:
            importlib.import_module('embedchain')
            DEPENDENCY_STATUS['embedchain'] = True
        except ImportError:
            logger.warning("Embedchain not installed. Run: pip install embedchain")
            DEPENDENCY_STATUS['embedchain'] = False
            
        # Check GitHub
        try:
            importlib.import_module('github')
            DEPENDENCY_STATUS['github'] = True
        except ImportError:
            logger.warning("PyGithub not installed. Run: pip install PyGithub")
            DEPENDENCY_STATUS['github'] = False
            
        # Check Google Generative AI
        try:
            importlib.import_module('google.generativeai')
            DEPENDENCY_STATUS['google_genai'] = True
        except ImportError:
            logger.warning("Google Generative AI not installed. Run: pip install google-generativeai")
            DEPENDENCY_STATUS['google_genai'] = False
            
        return DEPENDENCY_STATUS
    
    @staticmethod
    def get_placeholder_classes():
        """
        Get placeholder classes for missing dependencies.
        
        Returns:
            dict: Dictionary of placeholder classes
        """
        placeholders = {}
        
        # CrewAI placeholders
        if not DEPENDENCY_STATUS['crewai']:
            class Agent:
                def __init__(self, *args, **kwargs):
                    pass
            
            class Task:
                def __init__(self, *args, **kwargs):
                    pass
            
            class Crew:
                def __init__(self, *args, **kwargs):
                    pass
                
                def kickoff(self):
                    return "CrewAI not installed. This is a placeholder response."
            
            class Process:
                sequential = "sequential"
            
            class RagTool:
                def __init__(self, *args, **kwargs):
                    pass
                
                def add(self, *args, **kwargs):
                    pass
                
                def run(self, query):
                    return f"RagTool not available. Query: {query}"
            
            def tool(func):
                return func
                
            placeholders.update({
                'Agent': Agent,
                'Task': Task,
                'Crew': Crew,
                'Process': Process,
                'RagTool': RagTool,
                'tool': tool
            })
        
        # GitHub placeholders
        if not DEPENDENCY_STATUS['github']:
            class Repository:
                def __init__(self, *args, **kwargs):
                    self.name = "placeholder"
                    self.owner = type('obj', (object,), {'login': 'placeholder'})
                    self.description = "PyGithub not installed"
                    self.updated_at = None
                    self.stargazers_count = 0
                    self.forks_count = 0
                    self.language = None
                
                def get_contents(self, path):
                    return []
                    
                def get_topics(self):
                    return []
            
            placeholders['Repository'] = Repository
        
        return placeholders

# Initialize dependency status
DependencyManager.check_dependencies() 