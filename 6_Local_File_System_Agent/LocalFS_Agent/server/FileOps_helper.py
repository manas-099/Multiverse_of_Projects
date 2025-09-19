
# This will give us a list of dicts with all file info.

import logging
logging.basicConfig(level=logging.INFO)




import os
import shutil


import time
import hashlib
from pathlib import Path
from typing import List, Dict, Union
from mcp.server.fastmcp import FastMCP
mcp=FastMCP("FileOps_HelperServer")
@mcp.tool()
def build_file_index(roots: Union[str, list[str]]) -> list[dict]:
    """
    Recursively scans one or more root directories and returns a list of files with metadata.
    roots: str (single path) or list of paths
    """
    if isinstance(roots, str):  # convert single string to list
        roots = [roots]

    index = []
    for root_dir in roots:
        for dirpath, _, filenames in os.walk(root_dir):
            for f in filenames:
                p = Path(dirpath) / f
                try:
                    index.append({
                        "name": f,
                        "path": str(p),
                        "size": p.stat().st_size,
                        "modified": p.stat().st_mtime,
                        "ext": p.suffix.lower()
                    })
                except Exception:
                    pass
    return index



# Server keeps this global
index = []
@mcp.tool()
def refresh_index(roots: list[str]) -> str:
    """
    Refreshes the in-memory file index for the given roots.
    
    Args:
        roots: List of folder paths to scan.
    
    Returns:
        Confirmation message with number of files indexed.
    """
    global index
    index = build_file_index(roots)
    return f"Index refreshed: {len(index)} files under {roots}"


# Helper functions for LocalFS Agent.
# These tools allow an LLM-powered agent to query, analyze, and organize files
# 





# =========================
# 🔎 SEARCH TOOLS
# =========================
@mcp.tool()
def search_file_by_name(index: List[Dict], name: str) -> List[Dict]:
    """
    Search files by partial name (case-insensitive).
    
    Args:
        index: List of file metadata dicts.
        name: Substring to search in filenames.
    
    Returns:
        List of matching file metadata dicts.
    """
    return [f for f in index if name.lower() in f["name"].lower()]

@mcp.tool()
def find_by_extension(index: List[Dict], ext: str) -> List[Dict]:
    """
    Find all files with a given extension.
    
    Args:
        index: List of file metadata dicts.
        ext: File extension (e.g., 'pdf' or '.pdf').
    
    Returns:
        List of matching file metadata dicts.
    """
    ext = ext.lower() if ext.startswith(".") else "." + ext.lower()
    return [f for f in index if f["ext"] == ext]

@mcp.tool()
def find_by_type(index: List[Dict], types: List[str]) -> List[Dict]:
    """
    Find all files with extensions from a list.
    
    Args:
        index: List of file metadata dicts.
        types: List of file extensions (e.g., ['.jpg', '.png']).
    
    Returns:
        List of matching file metadata dicts.
    """
    types = [t.lower() if t.startswith(".") else "." + t.lower() for t in types]
    return [f for f in index if f["ext"] in types]


# =========================
# ⏱️ TIME-BASED TOOLS
# =========================
@mcp.tool()
def recent_files(index: List[Dict], n: int = 5) -> List[Dict]:
    """
    Get N most recently modified files.
    
    Args:
        index: List of file metadata dicts.
        n: Number of files to return.
    
    Returns:
        List of file metadata dicts sorted by modification date.
    """
    return sorted(index, key=lambda f: f["modified"], reverse=True)[:n]

@mcp.tool()
def files_modified_after(index: List[Dict], timestamp: float) -> List[Dict]:
    """
    Get files modified after a given UNIX timestamp.
    
    Args:
        index: List of file metadata dicts.
        timestamp: UNIX timestamp.
    
    Returns:
        List of matching file metadata dicts.
    """
    return [f for f in index if f["modified"] > timestamp]

@mcp.tool()
def files_modified_today(index: List[Dict]) -> List[Dict]:
    """
    Get all files modified today.
    
    Args:
        index: List of file metadata dicts.
    
    Returns:
        List of file metadata dicts modified today.
    """
    start_of_day = time.mktime(time.localtime()[:3] + (0, 0, 0, 0, 0, -1))
    return files_modified_after(index, start_of_day)


# =========================
# 📏 SIZE-BASED TOOLS
# =========================
@mcp.tool()
def large_files(index: List[Dict], min_size_mb: float) -> List[Dict]:
    """
    Find files larger than a given size in MB.
    
    Args:
        index: List of file metadata dicts.
        min_size_mb: Minimum file size in MB.
    
    Returns:
        List of matching file metadata dicts.
    """
    return [f for f in index if f["size"] >= min_size_mb * 1024 * 1024]

@mcp.tool()
def small_files(index: List[Dict], max_size_kb: float) -> List[Dict]:
    """
    Find files smaller than a given size in KB.
    
    Args:
        index: List of file metadata dicts.
        max_size_kb: Maximum file size in KB.
    
    Returns:
        List of matching file metadata dicts.
    """
    return [f for f in index if f["size"] <= max_size_kb * 1024]


# =========================
# 📂 FOLDER-BASED TOOLS
# =========================
@mcp.tool()
def files_in_folder(index: List[Dict], folder: str) -> List[Dict]:
    """
    List all files inside a specific folder (recursive).
    
    Args:
        index: List of file metadata dicts.
        folder: Path of the folder to search.
    
    Returns:
        List of matching file metadata dicts.
    """
    folder = str(Path(folder).resolve())
    return [f for f in index if str(Path(f["path"])).startswith(folder)]


# =========================
# 🧠 SMART UTILITIES
# =========================
@mcp.tool()
def group_by_extension(index: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group files by their extension.
    
    Args:
        index: List of file metadata dicts.
    
    Returns:
        Dictionary where keys are extensions and values are lists of files.
    """
    groups: Dict[str, List[Dict]] = {}
    for f in index:
        groups.setdefault(f["ext"], []).append(f)
    return groups

@mcp.tool()
def top_extensions(index: List[Dict], n: int = 5) -> List[tuple[str, int]]:
    """
    Find the most common file types by count.
    
    Args:
        index: List of file metadata dicts.
        n: Number of top file types to return.
    
    Returns:
        List of tuples (extension, count).
    """
    groups = group_by_extension(index)
    return sorted(((ext, len(files)) for ext, files in groups.items()), 
                  key=lambda x: x[1], reverse=True)[:n]

@mcp.tool()
def find_duplicates(index: List[Dict]) -> List[List[Dict]]:
    """
    Find duplicate files by comparing file hashes.
    
    Args:
        index: List of file metadata dicts.
    
    Returns:
        List of lists, where each inner list contains duplicate files.
    """
    seen: Dict[str, Dict] = {}
    duplicates: List[List[Dict]] = []
    for f in index:
        try:
            h = hashlib.md5(Path(f["path"]).read_bytes()).hexdigest()
            if h in seen:
                duplicates.append([seen[h], f])
            else:
                seen[h] = f
        except Exception:
            pass
    return duplicates



# File system manipulation tools for LocalFS Agent.
# These allow an LLM to safely read, write, delete, and organize files/folders.










# =========================
# 📖 READ & WRITE
# =========================
@mcp.tool()
def read_file(path: str, max_bytes: int = 5000) -> str:
    """
    Read the contents of a text file (truncated to avoid overload).
    
    Args:
        path: Path to the file.
        max_bytes: Maximum number of bytes to read.
    
    Returns:
        File contents as a string.
    """
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return p.read_text(errors="ignore")[:max_bytes]

@mcp.tool()
def write_file(path: str, content: str, overwrite: bool = False, append: bool = False) -> str:
    """
    Write or append text content to a file.
    
    Args:
        path: Path to the file.
        content: Text to write.
        overwrite: If True, overwrite the file if it exists.
        append: If True, append content to the file if it exists.
    
    Returns:
        Confirmation message.
    
    Raises:
        FileExistsError: If file exists and neither overwrite nor append is True.
    """
    p = Path(path)
    
    if p.exists():
        if append:
            with p.open("a", encoding="utf-8") as f:
                f.write(content)
            return f"Appended content to: {path}"
        elif overwrite:
            p.write_text(content)
            return f"Overwritten file: {path}"
        else:
            raise FileExistsError(f"File already exists: {path}")
    else:
        # File does not exist, create new
        p.write_text(content)
        return f"File created: {path}"

@mcp.tool()
def append_to_file(path: str, content: str) -> str:
    """
    Append text content to a file.
    
    Args:
        path: Path to the file.
        content: Text to append.
    
    Returns:
        Confirmation message.
    """
    p = Path(path)
    with p.open("a", encoding="utf-8") as f:
        f.write(content)
    return f"Content appended to: {path}"


# =========================
# 🗑️ DELETE OPS
# =========================
@mcp.tool()
def delete_file(path: str) -> str:
    """
    Delete a file.
    
    Args:
        path: Path to the file.
    
    Returns:
        Confirmation message.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not p.is_file():
        raise IsADirectoryError(f"Path is a folder, not a file: {path}")
    p.unlink()
    return f"Deleted file: {path}"

@mcp.tool()
def delete_folder(path: str) -> str:
    """
    Delete a folder and all its contents.
    
    Args:
        path: Path to the folder.
    
    Returns:
        Confirmation message.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Folder not found: {path}")
    if not p.is_dir():
        raise NotADirectoryError(f"Path is a file, not a folder: {path}")
    shutil.rmtree(p)
    return f"Deleted folder: {path}"


# =========================
# 📂 FILE & FOLDER OPS
# =========================
@mcp.tool()
def create_folder(path: str) -> str:
    """
    Create a new folder (including parent directories if needed).
    
    Args:
        path: Path of the new folder.
    
    Returns:
        Confirmation message.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return f"Created folder: {path}"

@mcp.tool()
def move_file(src: str, dst: str) -> str:
    """
    Move a file to a new location.
    
    Args:
        src: Source file path.
        dst: Destination file path.
    
    Returns:
        Confirmation message.
    """
    shutil.move(src, dst)
    return f"Moved file from {src} to {dst}"

@mcp.tool()
def copy_file(src: str, dst: str) -> str:
    """
    Copy a file to a new location.
    
    Args:
        src: Source file path.
        dst: Destination file path.
    
    Returns:
        Confirmation message.
    """
    shutil.copy2(src, dst)
    return f"Copied file from {src} to {dst}"

@mcp.tool()
def rename_file(path: str, new_name: str) -> str:
    """
    Rename a file within the same folder.
    
    Args:
        path: Path to the file.
        new_name: New filename (not full path).
    
    Returns:
        Confirmation message.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    new_path = p.with_name(new_name)
    p.rename(new_path)
    return f"Renamed {path} to {new_path}"

print("server is running....")

if __name__=='__main__':
    mcp.run(transport='stdio')
    