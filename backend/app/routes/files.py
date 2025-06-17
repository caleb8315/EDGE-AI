from __future__ import annotations

"""File browsing endpoints for EDGE workspace resources."""

from fastapi import APIRouter, HTTPException, Response, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse, PlainTextResponse
from typing import List
from pathlib import Path
import os
import shutil

from app.config import ENVIRONMENT  # just to ensure config import works
from app.services.supabase_service import supabase_service
from app.auth import get_current_user, AuthUser

WORKSPACE_ROOT = Path(os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")).resolve()

router = APIRouter(prefix="/files", tags=["files"])

def get_user_workspace(auth_user: AuthUser) -> Path:
    """Get the workspace directory for a specific authenticated user."""
    user_workspace = WORKSPACE_ROOT / auth_user.auth_id
    user_workspace.mkdir(parents=True, exist_ok=True)
    return user_workspace

@router.get("/list", response_model=List[str])
async def list_files(subdir: str | None = None, current_user: AuthUser = Depends(get_current_user)):
    """Return relative file paths under the workspace.

    If *subdir* is provided, list inside that directory.
    """
    user_workspace = get_user_workspace(current_user)
    base = (user_workspace / subdir).resolve() if subdir else user_workspace
    if not base.is_relative_to(user_workspace):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not base.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    files = []
    for p in base.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(user_workspace)))
    return files


@router.get("/completed-tasks/{user_id}", response_model=List[str])
async def list_user_completed_tasks(user_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Return completed task files for a specific user."""
    user_workspace = get_user_workspace(current_user)
    user_tasks_dir = user_workspace / "completed_tasks" / user_id
    if not user_tasks_dir.exists():
        return []
    
    if not user_tasks_dir.is_relative_to(user_workspace):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    files = []
    for p in user_tasks_dir.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(user_workspace)))
    return files


@router.get("/raw")
async def get_file(path: str, current_user: AuthUser = Depends(get_current_user)):
    """Return the raw contents of *path* inside workspace.

    For binary files >1 MB we return as attachment; small text files are
    returned inline.
    """
    user_workspace = get_user_workspace(current_user)
    abs_path = (user_workspace / path).resolve()
    if not abs_path.is_relative_to(user_workspace):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Heuristic: treat as text if under 1 MB and endswith typical text ext
    text_ext = {".md", ".txt", ".mmd", ".py", ".json", ".yaml", ".yml"}
    if abs_path.suffix in text_ext and abs_path.stat().st_size < 1_000_000:
        return PlainTextResponse(abs_path.read_text())

    # Otherwise send as downloadable file
    return FileResponse(str(abs_path), filename=abs_path.name)


@router.post("/mkdir")
async def make_directory(path: str, current_user: AuthUser = Depends(get_current_user)):
    """Create a directory under the workspace (including parents)."""
    user_workspace = get_user_workspace(current_user)
    abs_path = (user_workspace / path).resolve()
    if not abs_path.is_relative_to(user_workspace):
        raise HTTPException(status_code=400, detail="Invalid path")
    try:
        abs_path.mkdir(parents=True, exist_ok=True)
        return {"detail": "Directory created", "path": path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    directory: str = Form(default=""),
    user_id: str = Form(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """Upload multiple files to a directory in the workspace, preserving folder structure."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Determine target directory
    user_workspace = get_user_workspace(current_user)
    target_dir = user_workspace / directory if directory else user_workspace
    target_dir = target_dir.resolve()
    
    if not target_dir.is_relative_to(user_workspace):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    # Create directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = []
    
    # Process files with better error handling and logging
    for i, file in enumerate(files):
        if not file.filename:
            continue
        
        print(f"Processing file {i+1}/{len(files)}: {file.filename}")
        
        # For folder uploads, the filename includes the relative path
        # We need to preserve this structure
        filename = file.filename
        
        # Sanitize the path components to prevent directory traversal
        path_parts = []
        for part in filename.split('/'):
            # Remove dangerous path components
            clean_part = part.replace("..", "").replace("\\", "_")
            if clean_part and clean_part != '.':
                path_parts.append(clean_part)
        
        if not path_parts:
            continue
            
        # Reconstruct the safe path
        safe_path = '/'.join(path_parts)
        file_path = target_dir / safe_path
        
        try:
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            content = await file.read()
            file_path.write_bytes(content)
            
            # Store relative path for response
            rel_path = str(file_path.relative_to(user_workspace))
            uploaded_files.append(rel_path)
            print(f"Successfully saved: {rel_path}")
            
        except Exception as e:
            print(f"Failed to save {filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save {filename}: {str(e)}")
    
    # Return success immediately, update company files in background
    response_data = {"uploaded_files": uploaded_files, "count": len(uploaded_files)}
    
    # Update company's codebase_files field asynchronously (don't wait for it)
    import asyncio
    async def update_company_files():
        try:
            company = await supabase_service.get_company_by_user(user_id)
            if company:
                existing_files = company.get("codebase_files", []) or []
                # Add new files to existing list (avoid duplicates)
                updated_files = list(set(existing_files + uploaded_files))
                await supabase_service.update_company(company["id"], {"codebase_files": updated_files})
        except Exception as e:
            # Don't fail the upload if company update fails, just log it
            print(f"Warning: Failed to update company codebase_files: {e}")

    # Start the company update task but don't wait for it
    asyncio.create_task(update_company_files())
    
    return response_data


@router.get("/summary")
async def get_files_summary(current_user: AuthUser = Depends(get_current_user)):
    """Get a summary of files available for AI agent analysis."""
    user_workspace = get_user_workspace(current_user)
    if not user_workspace.exists():
        return {"total_files": 0, "file_types": {}, "ai_accessible": []}
    
    files = []
    file_types = {}
    ai_accessible = []
    
    # AI-friendly file types
    ai_readable_extensions = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.md', '.txt', 
        '.json', '.yaml', '.yml', '.xml', '.sql', '.pdf', '.csv'
    }
    
    for file_path in user_workspace.rglob("*"):
        if file_path.is_file():
            rel_path = str(file_path.relative_to(user_workspace))
            files.append(rel_path)
            
            ext = file_path.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
            
            if ext in ai_readable_extensions:
                ai_accessible.append({
                    "path": rel_path,
                    "type": ext,
                    "size": file_path.stat().st_size if file_path.exists() else 0
                })
    
    return {
        "total_files": len(files),
        "file_types": file_types,
        "ai_accessible_count": len(ai_accessible),
        "ai_accessible_files": ai_accessible[:20],  # Limit for UI
        "workspace_tools": [
            "codebase_explorer - analyze project structure and search code",
            "file_manager - read/write individual files", 
            "calendar_tool - manage calendar events",
            "search_google - search for information online"
        ]
    } 