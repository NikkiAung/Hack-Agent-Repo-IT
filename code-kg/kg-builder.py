import os
import json
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any

from neo4j import GraphDatabase, Driver
from anthropic import Client
from git import Repo
from tqdm import tqdm


SYSTEM_PROMPT = """You are a code analysis expert. Analyze the provided code and return ONLY a valid JSON object without any markdown formatting or explanations. Do not wrap the JSON in code blocks.
You are a code intelligence assistant that extracts a knowledge graph from a codebase.
Your goal is to identify and represent semantic relationships between components in the code.
Extract and return structured data showing entities (functions, classes, files, modules) and their relationships (calls, uses, defined-in, imports, inherits-from, etc).

Output as a list of triplets in the form:
(entity_1, relation, entity_2)

Include:

Functions calling other functions

Class-method ownership

File-to-file or module-to-module imports

Class inheritance

API endpoint definitions (if applicable)

Example output format:
(UserService, calls, validateUser)
(validateUser, defined-in, user_utils.py)
(AuthController, imports, UserService)
(Order, inherits-from, BaseModel)

Optional Enhancements:
You can add:

File paths or line numbers

Entity types in the triplet:
e.g. (function:validateUser, defined-in, file:user_utils.py)

Scope filtering, like only REST APIs or only classes
"""

ANALYSIS_PROMPT = """Extract the knowledge graph entities and relationships that exist in the following code.
Return STRICTLY and ONLY the JSON described earlier.
```{language}
{code}
```
"""


class RepoKnowledgeGraphBuilder:
    """
    Clone a GitHub repo, analyse files with Claude Sonnet 4 and create a knowledge graph in Neo4j.
    """

    def __init__(
        self,
        repo_url: str,
        local_path: str | Path | None = None,
        neo4j_uri: str | None = "bolt://localhost:7474",
        neo4j_user: str | None = "neo4j",
        neo4j_password: str | None = "password",
        file_extensions: List[str] | None = None,
        max_tokens_per_file: int = 8000,
        model: str = "claude-sonnet-4-20250514"
    ):
        self.repo_url = repo_url
        self.local_path = Path(local_path) if local_path else Path(tempfile.mkdtemp())
        self.file_extensions = file_extensions or [".py", ".js", ".ts", ".java", ".go", ".rb"]
        self.max_tokens_per_file = max_tokens_per_file
        self.neo4j_driver: Driver = GraphDatabase.driver(
            neo4j_uri, auth=(neo4j_user, neo4j_password)
        )
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set.")
        self.llm = Client(api_key=api_key)
        self.model = model

    # ----------------- Public API ----------------- #
    def run(self) -> None:
        self._clone_repo()
        graph_data = self._analyse_repository()
        self._push_to_neo4j(graph_data)

    # ----------------- Internal helpers ----------------- #
    def _clone_repo(self) -> None:
        if self.local_path.exists() and any(self.local_path.iterdir()):
            print(f"Path {self.local_path} not empty, skipping clone.")
            return
        Repo.clone_from(self.repo_url, self.local_path)
        print(f"Repository cloned to {self.local_path}")

    def _file_iter(self) -> List[Path]:
        return [
            p
            for p in self.local_path.rglob("*")
            if p.is_file() and p.suffix in self.file_extensions
        ]

    def _analyse_repository(self) -> Dict[str, List[Dict[str, Any]]]:
        all_nodes: Dict[str, Dict[str, Any]] = {}
        all_edges: List[Dict[str, Any]] = []

        for file_path in tqdm(self._file_iter(), desc="Analysing files"):
            code = file_path.read_text(encoding="utf-8", errors="ignore")
            # Truncate very long files to fit token limit
            code = code[: self.max_tokens_per_file * 4]  # 4 chars per token approx
            prompt = ANALYSIS_PROMPT.format(
                language=file_path.suffix.lstrip("."), code=code
            )
            response = self.llm.messages.create(
                model=self.model,
                system=SYSTEM_PROMPT,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            try:
                response_text = response.content[0].text
                # Strip markdown code block markers if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove closing ```
                response_text = response_text.strip()
                
                obj = json.loads(response_text)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for {file_path}")
                print(f"Response was: {response.content[0].text[:200]}...")  # Debug output
                continue

            # Handle both object and array responses
            if isinstance(obj, list):
                # If obj is a list, treat it as nodes directly
                for node in obj:
                    if isinstance(node, dict) and "id" in node:
                        all_nodes[node["id"]] = node
            elif isinstance(obj, dict):
                # If obj is a dict, extract nodes and edges
                for node in obj.get("nodes", []):
                    all_nodes[node["id"]] = node
                for edge in obj.get("edges", []):
                    all_edges.append(edge)
            else:
                print(f"Unexpected JSON structure for {file_path}: {type(obj)}")
                continue

        return {"nodes": list(all_nodes.values()), "edges": all_edges}

    def _push_to_neo4j(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        query_nodes = """
        UNWIND $nodes AS n
        MERGE (node:Entity {id: n.id})
        SET node += n
        """

        query_edges = """
        UNWIND $edges AS e
        MATCH (s:Entity {id: e.source})
        MATCH (t:Entity {id: e.target})
        MERGE (s)-[r:REL {type: e.type}]->(t)
        """

        with self.neo4j_driver.session() as session:
            session.run(query_nodes, parameters={"nodes": data["nodes"]})
            session.run(query_edges, parameters={"edges": data["edges"]})
        print("Knowledge graph imported into Neo4j!")

    # ----------------- CLI helper ----------------- #
    @classmethod
    def cli(cls):
        import argparse

        parser = argparse.ArgumentParser(description="Build a knowledge graph from a GitHub repo")
        parser.add_argument("--repo_url", help="GitHub repository URL (https://github.com/owner/repo)")
        parser.add_argument("--path", help="Local clone path (optional)")
        parser.add_argument("--neo4j-uri", default="bolt://localhost:7474")
        parser.add_argument("--neo4j-user", default="neo4j")
        parser.add_argument("--neo4j-password", default="12345678")
        parser.add_argument("--model", default="claude-3-5-sonnet-20241022")
        args = parser.parse_args()

        builder = cls(
            repo_url=args.repo_url,
            local_path=args.path,
            neo4j_uri=args.neo4j_uri,
            neo4j_user=args.neo4j_user,
            neo4j_password=args.neo4j_password,
            model=args.model
        )
        builder.run()


if __name__ == "__main__":
    RepoKnowledgeGraphBuilder.cli()
