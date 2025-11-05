"""
FastAPI Backend for AWS Bedrock Code Review Agent
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
from pathlib import Path

# Add parent directory to path to import review_agent
sys.path.insert(0, str(Path(__file__).parent.parent))

from review_agent import (
    analyze_code,
    analyze_file,
    analyze_diff,
    save_results,
    apply_fix_to_file,
    extract_suggestion_code,
    analyze_git_repo,
    analyze_directory,
    analyze_multiple_files,
    get_code_files
)

app = FastAPI(
    title="AWS Bedrock Code Review Agent API",
    description="REST API for code review using AWS Bedrock",
    version="1.0.0"
)

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CodeReviewRequest(BaseModel):
    code: str
    file_path: Optional[str] = None


class ApplyFixRequest(BaseModel):
    file_path: str
    issue: dict


class GitReviewRequest(BaseModel):
    repo_path: str
    base_ref: Optional[str] = None
    head_ref: Optional[str] = None


class DirectoryReviewRequest(BaseModel):
    directory: str
    max_files: int = 50


class MultipleFilesRequest(BaseModel):
    file_paths: List[str]


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "AWS Bedrock Code Review Agent API"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is healthy"}


@app.post("/api/review/code")
async def review_code(request: CodeReviewRequest):
    """
    Review code from text input
    """
    try:
        results = analyze_code(request.code, request.file_path)
        
        # Save results
        if "error" not in results:
            save_results(results)
        
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/file")
async def review_file(file: UploadFile = File(...), file_path: Optional[str] = Form(None)):
    """
    Review code from uploaded file
    """
    try:
        # Read file content
        content = await file.read()
        code_content = content.decode('utf-8')
        
        # Use provided file_path or filename
        target_path = file_path or file.filename
        
        # Determine if it's a diff file
        is_diff = (
            file.filename and (
                file.filename.endswith('.diff') or 
                file.filename.endswith('.patch') or 
                'diff' in file.filename.lower()
            )
        )
        
        if is_diff:
            results = analyze_diff(target_path) if target_path else analyze_code(code_content, target_path)
        else:
            results = analyze_code(code_content, target_path)
        
        # Save results
        if "error" not in results:
            save_results(results)
        
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/file-path")
async def review_file_path(file_path: str = Form(...)):
    """
    Review code from file path on server
    """
    try:
        # Determine if it's a diff file
        is_diff = (
            file_path.endswith('.diff') or 
            file_path.endswith('.patch') or 
            'diff' in file_path.lower()
        )
        
        if is_diff:
            results = analyze_diff(file_path)
        else:
            results = analyze_file(file_path)
        
        # Save results
        if "error" not in results:
            save_results(results)
        
        return JSONResponse(content=results)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fix/apply")
async def apply_fix(request: ApplyFixRequest):
    """
    Apply a fix to a file
    """
    try:
        success, message = apply_fix_to_file(request.file_path, request.issue)
        
        if success:
            return JSONResponse(content={"success": True, "message": message})
        else:
            raise HTTPException(status_code=400, detail=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/results")
async def get_recent_results(limit: int = 10):
    """
    Get recent review results
    """
    try:
        import json
        from pathlib import Path
        import datetime
        
        results_dir = Path(__file__).parent.parent / "results"
        results_files = sorted(results_dir.glob("review_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        results = []
        for file_path in results_files[:limit]:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['review_file'] = file_path.name
                    results.append(data)
            except Exception:
                continue
        
        return JSONResponse(content={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/git")
async def review_git_repo(request: GitReviewRequest):
    """
    Review a git repository by analyzing the diff
    """
    try:
        results = analyze_git_repo(request.repo_path, request.base_ref, request.head_ref)
        
        # Save results
        if "error" not in results:
            save_results(results)
        
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/directory")
async def review_directory(request: DirectoryReviewRequest):
    """
    Review all code files in a directory
    """
    try:
        results = analyze_directory(request.directory, request.max_files)
        
        # Save results
        if "error" not in results:
            save_results(results)
        
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/multiple")
async def review_multiple_files(request: MultipleFilesRequest):
    """
    Review multiple files at once
    """
    try:
        results = analyze_multiple_files(request.file_paths)
        
        # Save results
        if "error" not in results:
            save_results(results)
        
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/multiple-upload")
async def review_multiple_upload(files: List[UploadFile] = File(...)):
    """
    Review multiple uploaded files at once
    """
    try:
        import tempfile
        
        file_paths = []
        temp_files = []
        
        # Save uploaded files temporarily
        for file in files:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}")
            temp_files.append(temp_file)
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            file_paths.append(temp_file.name)
        
        try:
            results = analyze_multiple_files(file_paths)
            
            # Save results
            if "error" not in results:
                save_results(results)
            
            return JSONResponse(content=results)
        finally:
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/list")
async def list_code_files(directory: str, extensions: Optional[str] = None):
    """
    List code files in a directory
    """
    try:
        ext_list = extensions.split(',') if extensions else None
        files = get_code_files(directory, ext_list)
        return JSONResponse(content={"files": files, "count": len(files)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

