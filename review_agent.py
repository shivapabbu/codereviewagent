#!/usr/bin/env python3
"""
AWS Bedrock Code Review Agent - Backend
Analyzes code files or diffs and provides suggestions.
"""

import os
import json
import boto3
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

load_dotenv()

console = Console()

# Initialize Bedrock client
try:
    bedrock = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
except Exception as e:
    console.print(f"[bold red]Error initializing Bedrock client: {e}[/bold red]")
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
        console.print(f"[bold red]Error calling Bedrock: {e}[/bold red]")
        return {
            "error": str(e),
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

