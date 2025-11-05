#!/usr/bin/env python3
"""
AWS Bedrock Code Review Agent - Backend
Analyzes code files or diffs and provides suggestions.
"""

import os
import json
import boto3
import re
import subprocess
import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Load .env file from the project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)
# Also try loading from current directory
load_dotenv(override=False)

console = Console()

def sanitize_credential(value: Optional[str]) -> Optional[str]:
    """Remove quotes and whitespace from credentials."""
    if not value:
        return None
    # Remove surrounding quotes (single or double)
    value = value.strip().strip('"').strip("'")
    # Remove any remaining whitespace
    value = value.strip()
    return value if value else None

# Initialize Bedrock client
try:
    # Try multiple environment variable names for compatibility
    aws_region = sanitize_credential(os.getenv("AWS_REGION")) or sanitize_credential(os.getenv("AWS_DEFAULT_REGION")) or "us-east-1"
    aws_key = sanitize_credential(os.getenv("AWS_ACCESS_KEY_ID")) or sanitize_credential(os.getenv("AWS_ACCESS_KEY"))
    aws_secret = sanitize_credential(os.getenv("AWS_SECRET_ACCESS_KEY")) or sanitize_credential(os.getenv("AWS_SECRET_KEY"))
    aws_session_token = sanitize_credential(os.getenv("AWS_SESSION_TOKEN")) or sanitize_credential(os.getenv("AWS_SECURITY_TOKEN"))
    
    # Check if using temporary credentials (ASIA prefix requires session token)
    is_temporary_credential = aws_key and aws_key.startswith("ASIA")
    
    if is_temporary_credential and not aws_session_token:
        console.print("[bold red]⚠️  Error: Temporary credentials detected (ASIA prefix) but AWS_SESSION_TOKEN is missing![/bold red]")
        console.print("[dim]Temporary credentials require AWS_SESSION_TOKEN. Add it to your .env file or use permanent credentials (AKIA prefix)[/dim]")
        bedrock = None
    elif not aws_key or not aws_secret:
        console.print("[bold yellow]⚠️  Warning: AWS credentials not found in environment variables[/bold yellow]")
        console.print("[dim]Trying to use default AWS credential chain (AWS CLI, IAM roles, etc.)[/dim]")
        # Try without explicit credentials (use default AWS credential chain)
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name=aws_region
        )
    else:
        # Use explicit credentials
        client_params = {
            "service_name": "bedrock-runtime",
            "region_name": aws_region,
            "aws_access_key_id": aws_key,
            "aws_secret_access_key": aws_secret
        }
        
        # Add session token if present (for temporary credentials)
        if aws_session_token:
            client_params["aws_session_token"] = aws_session_token
        
        bedrock = boto3.client(**client_params)
except Exception as e:
    console.print(f"[bold red]Error initializing Bedrock client: {e}[/bold red]")
    console.print("[dim]Tip: Check your .env file format - credentials should not have quotes around them[/dim]")
    bedrock = None

MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")


def analyze_code(code_diff: str, file_path: Optional[str] = None) -> Dict:
    """
    Analyze code using AWS Bedrock Claude model.
    
    Args:
        code_diff: The code diff or file content to analyze
        file_path: Optional file path for context
    
    Returns:
        Dictionary containing suggestions and analysis
    """
    if bedrock is None:
        return {
            "error": "Bedrock client not initialized",
            "suggestions": []
        }
    
    # Construct the prompt for code review
    prompt = f"""You are an expert AI code reviewer. Analyze the following code and provide a comprehensive review.

Code to review:
{code_diff}

Please provide your review in the following JSON format:
{{
    "summary": "Brief summary of the review",
    "issues": [
        {{
            "type": "bug|style|documentation|performance|security",
            "severity": "high|medium|low",
            "line": <line_number>,
            "message": "Description of the issue",
            "suggestion": "Code suggestion in markdown format with ```suggestion blocks"
        }}
    ],
    "missing_docstrings": [
        {{
            "function": "function_name",
            "line": <line_number>,
            "suggestion": "Suggested docstring"
        }}
    ],
    "overall_score": <score_out_of_10>
}}

Focus on:
1. Code style and formatting issues
2. Missing function/method docstrings
3. Potential bugs or logical errors
4. Performance improvements
5. Security concerns
6. Best practices violations

Return ONLY valid JSON, no additional text."""

    try:
        if bedrock is None:
            return {
                "error": "Bedrock client not initialized. Please check your AWS credentials.",
                "suggestions": []
            }
        
        # Use Claude 3 API format for Bedrock
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        
        # Extract the content from Claude's response
        content = response_body.get('content', [])
        if content:
            text_content = content[0].get('text', '')
            
            # Try to parse JSON from the response
            try:
                # Extract JSON from markdown code blocks if present
                if '```json' in text_content:
                    json_start = text_content.find('```json') + 7
                    json_end = text_content.find('```', json_start)
                    text_content = text_content[json_start:json_end].strip()
                elif '```' in text_content:
                    json_start = text_content.find('```') + 3
                    json_end = text_content.find('```', json_start)
                    text_content = text_content[json_start:json_end].strip()
                
                result = json.loads(text_content)
                result['file_path'] = file_path
                return result
            except json.JSONDecodeError:
                # Fallback: return as text if JSON parsing fails
                return {
                    "summary": "Review completed",
                    "raw_response": text_content,
                    "issues": [],
                    "missing_docstrings": [],
                    "file_path": file_path,
                    "overall_score": 5
                }
        else:
            return {
                "error": "No content in response",
                "suggestions": []
            }
            
    except Exception as e:
        error_msg = str(e)
        console.print(f"[bold red]Error calling Bedrock: {error_msg}[/bold red]")
        
        # Provide helpful error messages
        if "UnrecognizedClientException" in error_msg or "invalid" in error_msg.lower():
            error_msg += "\n\n💡 Troubleshooting tips:\n"
            error_msg += "1. Check your AWS credentials in .env file\n"
            error_msg += "2. Ensure credentials don't have quotes around them (e.g., use KEY=value not KEY='value')\n"
            error_msg += "3. Verify credentials are valid and not expired\n"
            error_msg += "4. Check that Bedrock is enabled in your AWS account\n"
            error_msg += "5. Verify the AWS region is correct\n"
        
        return {
            "error": error_msg,
            "suggestions": []
        }


def analyze_file(file_path: str) -> Dict:
    """Analyze a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        console.print(f"[bold cyan]Analyzing: {file_path}[/bold cyan]")
        return analyze_code(content, file_path)
    except FileNotFoundError:
        return {"error": f"File not found: {file_path}", "suggestions": []}
    except Exception as e:
        return {"error": str(e), "suggestions": []}


def analyze_diff(diff_path: str) -> Dict:
    """Analyze a diff file."""
    try:
        with open(diff_path, 'r', encoding='utf-8') as f:
            diff_content = f.read()
        
        console.print(f"[bold cyan]Analyzing diff: {diff_path}[/bold cyan]")
        return analyze_code(diff_content, diff_path)
    except FileNotFoundError:
        return {"error": f"Diff file not found: {diff_path}", "suggestions": []}
    except Exception as e:
        return {"error": str(e), "suggestions": []}


def save_results(results: Dict, output_dir: str = "results") -> str:
    """Save review results to JSON file."""
    Path(output_dir).mkdir(exist_ok=True)
    
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = results.get('file_path', 'unknown').replace('/', '_')
    output_path = f"{output_dir}/review_{file_name}_{timestamp}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    return output_path


def display_results(results: Dict):
    """Display review results in a formatted way."""
    if "error" in results:
        console.print(f"[bold red]Error: {results['error']}[/bold red]")
        return
    
    console.print("\n[bold green]📋 Review Summary[/bold green]")
    console.print(Panel(results.get('summary', 'No summary available')))
    
    issues = results.get('issues', [])
    if issues:
        console.print(f"\n[bold yellow]⚠️  Found {len(issues)} issues:[/bold yellow]\n")
        for issue in issues:
            severity_color = {
                'high': 'red',
                'medium': 'yellow',
                'low': 'blue'
            }.get(issue.get('severity', 'low'), 'white')
            
            console.print(f"[{severity_color}][{issue.get('severity', 'unknown').upper()}] {issue.get('type', 'unknown')}[/{severity_color}]")
            console.print(f"  Line {issue.get('line', 'N/A')}: {issue.get('message', 'No message')}")
            if issue.get('suggestion'):
                console.print(f"  [dim]Suggestion: {issue.get('suggestion')[:100]}...[/dim]")
    
    missing_docs = results.get('missing_docstrings', [])
    if missing_docs:
        console.print(f"\n[bold cyan]📝 Missing docstrings ({len(missing_docs)}):[/bold cyan]\n")
        for doc in missing_docs:
            console.print(f"  Function: {doc.get('function', 'unknown')} (Line {doc.get('line', 'N/A')})")
    
    score = results.get('overall_score', 0)
    console.print(f"\n[bold]Overall Score: {score}/10[/bold]")


def extract_suggestion_code(suggestion_text: str) -> Optional[str]:
    """
    Extract code from GitHub suggestion format (```suggestion blocks).
    
    Args:
        suggestion_text: Text containing suggestion code blocks
    
    Returns:
        Extracted code or None
    """
    # Match ```suggestion blocks
    pattern = r'```suggestion\s*\n(.*?)```'
    matches = re.findall(pattern, suggestion_text, re.DOTALL)
    if matches:
        return matches[0].strip()
    
    # Match regular code blocks if no suggestion blocks found
    pattern = r'```(?:python|py|)\s*\n(.*?)```'
    matches = re.findall(pattern, suggestion_text, re.DOTALL)
    if matches:
        return matches[0].strip()
    
    return None


def apply_suggestion_to_file(file_path: str, line_number: int, suggestion_code: str, 
                              context_lines: int = 3) -> Tuple[bool, str]:
    """
    Apply a suggestion to a file at a specific line.
    
    Args:
        file_path: Path to the file to modify
        line_number: Line number where the suggestion should be applied (1-indexed)
        suggestion_code: The suggested code to insert
        context_lines: Number of context lines to replace around the target line
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_number < 1 or line_number > len(lines):
            return False, f"Line number {line_number} is out of range (file has {len(lines)} lines)"
        
        # Convert to 0-indexed
        idx = line_number - 1
        
        # Determine the range to replace
        start_idx = max(0, idx - context_lines)
        end_idx = min(len(lines), idx + context_lines + 1)
        
        # Split suggestion into lines
        suggestion_lines = suggestion_code.split('\n')
        if suggestion_lines and not suggestion_lines[-1].endswith('\n'):
            suggestion_lines[-1] += '\n'
        else:
            suggestion_lines = [line + '\n' if not line.endswith('\n') else line 
                              for line in suggestion_lines]
        
        # Create backup
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Apply the suggestion
        new_lines = lines[:start_idx] + suggestion_lines + lines[end_idx:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return True, f"Applied suggestion to {file_path} (backup saved to {backup_path})"
    
    except Exception as e:
        return False, f"Error applying suggestion: {str(e)}"


def apply_fix_to_file(file_path: str, issue: Dict) -> Tuple[bool, str]:
    """
    Apply a fix from an issue dictionary to a file.
    
    Args:
        file_path: Path to the file to modify
        issue: Issue dictionary containing suggestion
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    suggestion_text = issue.get('suggestion', '')
    line_number = issue.get('line', 1)
    
    suggestion_code = extract_suggestion_code(suggestion_text)
    if not suggestion_code:
        return False, "No valid suggestion code found in issue"
    
    return apply_suggestion_to_file(file_path, line_number, suggestion_code)


def get_git_diff(repo_path: str, base_ref: Optional[str] = None, head_ref: Optional[str] = None) -> str:
    """
    Get git diff for a repository.
    
    Args:
        repo_path: Path to git repository
        base_ref: Base branch/commit (default: HEAD)
        head_ref: Head branch/commit (default: working directory)
    
    Returns:
        Git diff as string
    """
    try:
        os.chdir(repo_path)
        
        if base_ref and head_ref:
            cmd = ['git', 'diff', base_ref, head_ref]
        elif base_ref:
            cmd = ['git', 'diff', base_ref]
        else:
            # Get unstaged changes
            cmd = ['git', 'diff']
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting git diff: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_git_repo(repo_path: str, base_ref: Optional[str] = None, head_ref: Optional[str] = None) -> Dict:
    """
    Analyze a git repository by reviewing the diff.
    
    Args:
        repo_path: Path to git repository
        base_ref: Base branch/commit to compare against
        head_ref: Head branch/commit
    
    Returns:
        Dictionary containing review results
    """
    if not os.path.isdir(repo_path):
        return {"error": f"Repository path not found: {repo_path}"}
    
    git_dir = Path(repo_path) / '.git'
    if not git_dir.exists():
        return {"error": f"Not a git repository: {repo_path}"}
    
    diff_content = get_git_diff(repo_path, base_ref, head_ref)
    
    if not diff_content.strip():
        return {
            "summary": "No changes detected in the specified range",
            "issues": [],
            "missing_docstrings": [],
            "overall_score": 10,
            "file_path": repo_path,
            "git_info": {
                "repo_path": repo_path,
                "base_ref": base_ref or "HEAD",
                "head_ref": head_ref or "working directory"
            }
        }
    
    # Analyze the diff
    diff_description = f"Git diff from {base_ref or 'HEAD'} to {head_ref or 'working directory'}"
    results = analyze_code(diff_content, diff_description)
    results['file_path'] = repo_path
    results['git_info'] = {
        "repo_path": repo_path,
        "base_ref": base_ref or "HEAD",
        "head_ref": head_ref or "working directory",
        "diff_length": len(diff_content)
    }
    
    return results


def get_code_files(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Get all code files in a directory.
    
    Args:
        directory: Directory path to scan
        extensions: List of file extensions to include (default: common code extensions)
    
    Returns:
        List of file paths
    """
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']
    
    code_files = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        return code_files
    
    for ext in extensions:
        pattern = f"**/*{ext}"
        code_files.extend(directory_path.glob(pattern))
    
    # Filter out common directories to ignore
    ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next'}
    filtered_files = [
        str(f) for f in code_files 
        if not any(ignore_dir in str(f) for ignore_dir in ignore_dirs)
    ]
    
    return sorted(filtered_files)


def analyze_directory(directory: str, max_files: int = 50) -> Dict:
    """
    Analyze all code files in a directory.
    
    Args:
        directory: Directory path to analyze
        max_files: Maximum number of files to analyze (default: 50)
    
    Returns:
        Dictionary containing aggregated review results
    """
    if not os.path.isdir(directory):
        return {"error": f"Directory not found: {directory}"}
    
    code_files = get_code_files(directory)
    
    if not code_files:
        return {
            "summary": "No code files found in directory",
            "issues": [],
            "missing_docstrings": [],
            "overall_score": 0,
            "file_path": directory,
            "files_analyzed": 0
        }
    
    if len(code_files) > max_files:
        code_files = code_files[:max_files]
        console.print(f"[yellow]⚠️  Limiting analysis to first {max_files} files[/yellow]")
    
    all_issues = []
    all_missing_docs = []
    file_results = []
    total_score = 0
    analyzed_count = 0
    
    for file_path in code_files:
        try:
            console.print(f"[cyan]Analyzing: {file_path}[/cyan]")
            result = analyze_file(file_path)
            
            if "error" not in result:
                # Add file path to each issue
                for issue in result.get('issues', []):
                    issue['file_path'] = file_path
                    all_issues.append(issue)
                
                for doc in result.get('missing_docstrings', []):
                    doc['file_path'] = file_path
                    all_missing_docs.append(doc)
                
                file_results.append({
                    "file_path": file_path,
                    "score": result.get('overall_score', 0),
                    "issue_count": len(result.get('issues', [])),
                    "missing_docs_count": len(result.get('missing_docstrings', []))
                })
                
                total_score += result.get('overall_score', 0)
                analyzed_count += 1
        except Exception as e:
            console.print(f"[red]Error analyzing {file_path}: {e}[/red]")
            continue
    
    avg_score = total_score / analyzed_count if analyzed_count > 0 else 0
    
    return {
        "summary": f"Analyzed {analyzed_count} files in {directory}. Found {len(all_issues)} total issues and {len(all_missing_docs)} missing docstrings.",
        "issues": all_issues,
        "missing_docstrings": all_missing_docs,
        "overall_score": round(avg_score, 1),
        "file_path": directory,
        "files_analyzed": analyzed_count,
        "total_files": len(code_files),
        "file_results": file_results
    }


def analyze_multiple_files(file_paths: List[str]) -> Dict:
    """
    Analyze multiple files and return aggregated results.
    
    Args:
        file_paths: List of file paths to analyze
    
    Returns:
        Dictionary containing aggregated review results
    """
    if not file_paths:
        return {"error": "No files provided"}
    
    all_issues = []
    all_missing_docs = []
    file_results = []
    total_score = 0
    analyzed_count = 0
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            console.print(f"[yellow]⚠️  File not found: {file_path}[/yellow]")
            continue
        
        try:
            console.print(f"[cyan]Analyzing: {file_path}[/cyan]")
            result = analyze_file(file_path)
            
            if "error" not in result:
                # Add file path to each issue
                for issue in result.get('issues', []):
                    issue['file_path'] = file_path
                    all_issues.append(issue)
                
                for doc in result.get('missing_docstrings', []):
                    doc['file_path'] = file_path
                    all_missing_docs.append(doc)
                
                file_results.append({
                    "file_path": file_path,
                    "score": result.get('overall_score', 0),
                    "issue_count": len(result.get('issues', [])),
                    "missing_docs_count": len(result.get('missing_docstrings', []))
                })
                
                total_score += result.get('overall_score', 0)
                analyzed_count += 1
        except Exception as e:
            console.print(f"[red]Error analyzing {file_path}: {e}[/red]")
            continue
    
    avg_score = total_score / analyzed_count if analyzed_count > 0 else 0
    
    return {
        "summary": f"Analyzed {analyzed_count} files. Found {len(all_issues)} total issues and {len(all_missing_docs)} missing docstrings.",
        "issues": all_issues,
        "missing_docstrings": all_missing_docs,
        "overall_score": round(avg_score, 1),
        "file_path": "multiple files",
        "files_analyzed": analyzed_count,
        "file_results": file_results
    }


if __name__ == "__main__":
    console.print("[bold cyan]🔍 AWS Bedrock Code Review Agent[/bold cyan]\n")
    
    file_path = input("Enter file path or diff file: ").strip()
    
    if not file_path:
        console.print("[bold red]No file path provided[/bold red]")
        exit(1)
    
    # Determine if it's a diff or regular file
    if file_path.endswith('.diff') or file_path.endswith('.patch') or 'diff' in file_path.lower():
        results = analyze_diff(file_path)
    else:
        results = analyze_file(file_path)
    
    console.print("\n[bold yellow]Analyzing code with Bedrock...[/bold yellow]\n")
    
    display_results(results)
    
    # Save results
    output_path = save_results(results)
    console.print(f"\n[bold green]✅ Results saved to: {output_path}[/bold green]")

