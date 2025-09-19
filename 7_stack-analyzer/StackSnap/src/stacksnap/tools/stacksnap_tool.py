# src/stacksnap/tools/stacksnap_tool.py

import requests
import json
import re
import toml  # pip install toml
import xml.etree.ElementTree as ET
from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List
from langchain_core.tools import tool
from typing import Dict, Tuple, Any


# -------------------------
# Manifest & folders config
# -------------------------
manifest_files = [
    "package.json", "yarn.lock", "package-lock.json",
    "requirements.txt", "Pipfile", "pyproject.toml", "setup.py", "environment.yml",
    "Cargo.toml", "go.mod", "composer.json", "Gemfile",
    "build.gradle", "pom.xml", ".csproj", "packages.config",
    "Dockerfile", "Makefile"
]

# Common folders to check in monorepos
common_folders = ["", "packages", "examples", "apps"]

# -------------------------
# Pydantic context model
# -------------------------
class RepoContext(BaseModel):
    url: HttpUrl
    readme: str = Field(default="", max_length=5000)
    manifests: Dict[str, str] = Field(default_factory=dict)
    file_extensions: Dict[str, int] = Field(default_factory=dict)

# -------------------------
# Helper functions
# -------------------------
def fetch_file(owner: str, repo: str, path: str) -> str:
    """
    Fetch a raw file from GitHub repo. Returns empty string if not found or error occurs.
    """
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
    except requests.RequestException as e:
        print(f"[Warning] Failed to fetch {path}: {e}")
    return ""

def gather_context_api(state: dict) -> dict:
    """
    Gather repo context including README, manifests, and file extensions.
    Updates 'state' with 'context'.
    """
    repo_url = state.get("url")
    if not repo_url:
        raise ValueError("Missing 'url' in state")

    try:
        parts = repo_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
    except Exception as e:
        raise ValueError(f"Invalid GitHub URL: {repo_url}") from e

    # 1️⃣ Gather README
    readme = ""
    for folder in common_folders:
        for name in ["README.md", "readme.md"]:
            path = f"{folder}/{name}" if folder else name
            content = fetch_file(owner, repo, path)
            if content:
                readme = content
                break
        if readme:
            break

    # 2️⃣ Gather manifests
    manifests = {}
    for folder in common_folders:
        for mf in manifest_files:
            path = f"{folder}/{mf}" if folder else mf
            content = fetch_file(owner, repo, path)
            if content:
                manifests[path] = content

    # 3️⃣ Count file extensions using GitHub API (optional)
    file_extensions = {}
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            tree = r.json().get("tree", [])
            for item in tree:
                if item.get("type") == "blob":
                    ext = item["path"].split(".")[-1] if "." in item["path"] else ""
                    if ext:
                        file_extensions[ext] = file_extensions.get(ext, 0) + 1
        else:
            print(f"[Warning] Could not fetch repo tree: HTTP {r.status_code}")
    except requests.RequestException as e:
        print(f"[Warning] Error fetching repo tree: {e}")

    # Create validated context object
    context = RepoContext(
        url=repo_url,
        readme=readme,
        manifests=manifests,
        file_extensions=file_extensions
    )

    state["context"] = context.dict()
    return state

# -------------------------
# Analyze manifests
# -------------------------
def analyze_manifests(manifests: Dict[str,str]) -> Dict[str, List[str]]:
    """
    Analyze manifests to infer tech stack (languages, frameworks, libraries, DevOps, others)
    """
    stack = {
        "Languages": [],
        "Frameworks": [],
        "Libraries": [],
        "DevOps": [],
        "Others": []
    }

    for path, content in manifests.items():
        path_lower = path.lower()

        try:
            # Python
            if path_lower.endswith(("requirements.txt", "pipfile", "pyproject.toml", "setup.py")):
                stack["Languages"].append("Python")
                if path_lower.endswith("requirements.txt") or path_lower.endswith("setup.py"):
                    for line in content.splitlines():
                        line = line.strip()
                        if line and not line.startswith("#"):
                            pkg = re.split(r"[=<>!]", line)[0].strip()
                            if pkg:
                                stack["Libraries"].append(pkg)
                elif path_lower.endswith("pyproject.toml"):
                    try:
                        pyproject = toml.loads(content)
                        deps = pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {})
                        for dep in deps:
                            if dep != "python":
                                stack["Libraries"].append(dep)
                    except Exception as e:
                        print(f"[Warning] Failed to parse {path}: {e}")

            # Node.js
            elif path_lower.endswith(("package.json", "yarn.lock", "package-lock.json")):
                stack["Languages"].append("JavaScript/Node.js")
                try:
                    package_json = json.loads(content)
                    deps = package_json.get("dependencies", {})
                    dev_deps = package_json.get("devDependencies", {})
                    for dep in list(deps.keys()) + list(dev_deps.keys()):
                        stack["Libraries"].append(dep)
                    for fw in ["next", "express", "react", "vue", "angular"]:
                        if fw in deps or fw in dev_deps:
                            stack["Frameworks"].append(fw)
                except Exception as e:
                    print(f"[Warning] Failed to parse {path}: {e}")

            # Rust
            elif path_lower.endswith("cargo.toml"):
                stack["Languages"].append("Rust")
                try:
                    cargo = toml.loads(content)
                    deps = cargo.get("dependencies", {})
                    for dep in deps:
                        stack["Libraries"].append(dep)
                except Exception as e:
                    print(f"[Warning] Failed to parse {path}: {e}")

            # Go
            elif path_lower.endswith("go.mod"):
                stack["Languages"].append("Go")
                lines = content.splitlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith("require"):
                        parts = line.split()
                        if len(parts) >= 2:
                            stack["Libraries"].append(parts[1])

            # Ruby
            elif path_lower.endswith("gemfile"):
                stack["Languages"].append("Ruby")
                for line in content.splitlines():
                    match = re.match(r'^\s*gem\s+["\']([^"\']+)["\']', line)
                    if match:
                        stack["Libraries"].append(match.group(1))

            # Java
            elif path_lower.endswith("build.gradle"):
                stack["Languages"].append("Java/Kotlin")
                matches = re.findall(r'implementation\s+["\']([^"\']+)["\']', content)
                stack["Libraries"].extend(matches)
            elif path_lower.endswith("pom.xml"):
                stack["Languages"].append("Java")
                try:
                    root = ET.fromstring(content)
                    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
                    for dep in root.findall(".//m:dependency", ns):
                        group = dep.find("m:groupId", ns)
                        artifact = dep.find("m:artifactId", ns)
                        if group is not None and artifact is not None:
                            stack["Libraries"].append(f"{group.text}:{artifact.text}")
                except Exception as e:
                    print(f"[Warning] Failed to parse {path}: {e}")

            # DevOps / Infra
            elif path_lower.endswith(("dockerfile", "makefile")):
                stack["DevOps"].append(path)

            else:
                stack["Others"].append(path)

        except Exception as e:
            print(f"[Warning] Error analyzing {path}: {e}")

    # Remove duplicates
    for key in stack:
        stack[key] = list(set(stack[key]))

    return stack




@tool
def stacks_analyzer(repo_url:str)->Tuple[Dict[str, Any], Dict[str, list]]:
    """
    Analyze the tech stack of a GitHub repository using StackSnap tools.

    This function performs the following steps:
    1. Validates the input GitHub repository URL.
    2. Gathers repository context, including README and manifest files.
    3. Analyzes manifest files to infer the tech stack (languages, frameworks, libraries, DevOps tools, etc.).
    
    Args:
        repo_url (str): The URL of the GitHub repository to analyze.
    
    Raises:
        ValueError: If the `repo_url` is empty or invalid.
    
    Returns:
        Tuple[Dict[str, Any], Dict[str, list]]:
            - context (dict): Contains repository information, README content, manifest files, etc.
                Example keys: "url", "readme", "manifests", "file_extensions".
            - stack_info (dict): Analyzed tech stack categories and items.
                Example keys: "Languages", "Frameworks", "Libraries", "DevOps", "Others".
    
 
    """
    if not repo_url:
        raise ValueError("Repo URL cannot be empty")
    state = {"url": repo_url}
    # Gather context
    state = gather_context_api(state)
    context = state["context"]
    # Analyze manifests
    stack_info = analyze_manifests(context["manifests"])
    return context,stack_info #stack_info is dict , context list ,can access readme and url
# -------------------------
# Main entry point
# -------------------------
if __name__ == "__main__":
    try:
        repo_url = input("Enter GitHub repo URL: ").strip()
        if not repo_url:
            raise ValueError("Repo URL cannot be empty")

        state = {"url": repo_url}

        # Gather context
        state = gather_context_api(state)
        context = state["context"]

        # Analyze manifests
        stack_info = analyze_manifests(context["manifests"])

        

        # Print final StackSnap report
        print("\n=== STACKSNAP REPORT ===")
        print("Repository URL:", context["url"])
        print("\nREADME (first 500 chars):\n", context["readme"][:500])
        print("\nTech Stack:")
        for category, items in stack_info.items():
            print(f"{category}: {items}")

        if context["file_extensions"]:
            print("\nFile Extensions Count (optional):")
            print(context["file_extensions"])

    except Exception as e:
        print(f"[Error] Failed to run StackSnap: {e}")
