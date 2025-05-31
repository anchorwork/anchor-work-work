"""
Coder-specific tools for Anchorwork.
Includes code generation, review, explanation, patching, and codebase search utilities.
"""
import os
from typing import List
from utils.llm_client import LLMClient
from utils.memory_pipeline import get_memory_pipeline
from agentlogging.unified_logger import log_event
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional
import requests
import tempfile
import shutil
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import uuid
import re
import time
import json

logger = logging.getLogger(__name__)

def _run_command(cmd: list, cwd: str = ".") -> str:
    """Execute a command and return combined stdout/stderr."""
    try:
        proc = subprocess.run(
            cmd, 
            cwd=cwd, 
            text=True, 
            capture_output=True, 
            timeout=120
        )
        return proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        return f"❌ Command timed out: {' '.join(cmd)}"
    except Exception as e:
        return f"❌ Command failed: {e}"

def run_ruff(targets: list = None, cwd: str = ".") -> str:
    """Run ruff linting on specified targets."""
    if targets is None:
        targets = ["src", "routes"]
    cmd = [sys.executable, "-m", "ruff"] + targets
    return _run_command(cmd, cwd)

def run_mypy(targets: list = None, cwd: str = ".", ignore_missing: bool = True) -> str:
    """Run mypy type checking on specified targets."""
    if targets is None:
        targets = ["src", "routes"]
    cmd = [sys.executable, "-m", "mypy"] + targets
    if ignore_missing:
        cmd.append("--ignore-missing-imports")
    return _run_command(cmd, cwd)

def run_pylint(targets: list = None, cwd: str = ".", disable: str = "R,C") -> str:
    """Run pylint analysis on specified targets."""
    if targets is None:
        targets = ["src", "routes"]
    cmd = [sys.executable, "-m", "pylint"] + targets
    if disable:
        cmd.extend(["--disable", disable])
    return _run_command(cmd, cwd)

def run_bandit(targets: list = None, cwd: str = ".", quiet: bool = True) -> str:
    """Run bandit security analysis on specified targets."""
    if targets is None:
        targets = ["src", "routes"]
    cmd = [sys.executable, "-m", "bandit", "-r"] + targets
    if quiet:
        cmd.insert(-len(targets), "-q")
    return _run_command(cmd, cwd)

def run_all_static_analysis(targets: list = None, cwd: str = ".") -> Dict[str, str]:
    """
    Run all static analysis tools and return results.
    """
    if targets is None:
        targets = ["src", "routes"]
    logger.info("🧹 Running comprehensive static analysis...")
    results = {
        "ruff": run_ruff(targets, cwd),
        "mypy": run_mypy(targets, cwd),
        "pylint": run_pylint(targets, cwd),
        "bandit": run_bandit(targets, cwd),
    }
    logger.info("✅ Static analysis complete")
    return results

def save_analysis_reports(results: Dict[str, str], output_dir: Path) -> None:
    """
    Save static analysis results to individual report files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    for tool_name, output in results.items():
        report_file = output_dir / f"{tool_name}_report.txt"
        content = output or f"No {tool_name} issues."
        report_file.write_text(content, encoding="utf-8")
        logger.info(f"📝 Saved {tool_name} report to {report_file}")

def get_analysis_summary(results: Dict[str, str]) -> str:
    """
    Generate a human-readable summary of static analysis results.
    """
    summary_lines = []
    for tool_name, output in results.items():
        if not output.strip():
            summary_lines.append(f"✅ {tool_name}: No issues")
        else:
            line_count = output.count('\n')
            summary_lines.append(f"⚠️ {tool_name}: {line_count} lines of output")
    return "\n".join(summary_lines)

def generate_code(prompt: str, agent_id: str = "coder") -> str:
    """
    Generate code from a prompt using the LLM.
    Args:
        prompt (str): The code prompt or task description.
    Returns:
        str: Generated code.
    """
    llm = LLMClient()
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "generate_code"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "generate_code"})
    return response

def review_code(code: str, agent_id: str = "coder") -> str:
    """
    Review code for style, security, and performance using the LLM.
    Args:
        code (str): The code to review.
    Returns:
        str: Review feedback.
    """
    llm = LLMClient()
    prompt = f"Review this code for style, security, and performance:\n{code}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "review_code"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "review_code"})
    return response

def explain_code(code: str, agent_id: str = "coder") -> str:
    """
    Explain code step by step using the LLM.
    Args:
        code (str): The code to explain.
    Returns:
        str: Step-by-step explanation.
    """
    llm = LLMClient()
    prompt = f"Explain this code step by step:\n{code}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "explain_code"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "explain_code"})
    return response

def patch_code(original_code: str, patch_instructions: str) -> str:
    """
    Apply a patch or refactor to code using the LLM.
    Args:
        original_code (str): The original code.
        patch_instructions (str): Instructions for the patch or refactor.
    Returns:
        str: Patched or refactored code.
    """
    llm = LLMClient()
    prompt = f"Refactor or patch the following code as per instructions:\nInstructions: {patch_instructions}\nCode:\n{original_code}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id="coder")
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "patch_code"}, agent="coder", level="INFO")
    pipeline = get_memory_pipeline("coder")
    pipeline.append({"prompt": prompt, "response": response, "task": "patch_code"})
    return response

def codebase_search(query: str, top_k: int = 5) -> List[str]:
    """
    Search the codebase for relevant code snippets using vector memory.
    Args:
        query (str): Search query.
        top_k (int): Number of top results to return.
    Returns:
        List[str]: List of code snippets or file contents.
    """
    from utils.vector_memory import PineconeMemory
    pinecone = PineconeMemory(index_name="codebase")
    results = pinecone.query(query=query, k=top_k)
    return [r.get("text", "") for r in results]

def index_codebase(source_dir: str = ".") -> None:
    """
    Index the codebase for semantic search and memory.
    Args:
        source_dir (str): Directory to index.
    Returns:
        None
    """
    pass

def codebase_qa(question: str) -> str:
    """
    Answer a question about the codebase using semantic search and LLM.
    Args:
        question (str): The question to answer.
    Returns:
        str: Answer from the codebase context.
    """
    pass

def log_debug_ritual(bug_desc: str, fix_desc: str) -> None:
    """
    Log a debugging ritual for self-improvement and education.
    Args:
        bug_desc (str): Description of the bug.
        fix_desc (str): Description of the fix.
    Returns:
        None
    """
    pass

def track_coding_mood(mood: str, context: str = "") -> None:
    """
    Track the coder's mood and context for self-reflection.
    Args:
        mood (str): Mood description.
        context (str): Additional context.
    Returns:
        None
    """
    pass

def pair_program(partner_agent, task: str) -> str:
    """
    Simulate or facilitate pair programming with another agent.
    Args:
        partner_agent: The partner agent object.
        task (str): The programming task.
    Returns:
        str: Narration or result of the pair programming session.
    """
    pass

def teach_code(topic: str, recipient_agent) -> str:
    """
    Teach a coding topic to another agent.
    Args:
        topic (str): The topic to teach.
        recipient_agent: The agent to receive the lesson.
    Returns:
        str: Lesson content or outline.
    """
    pass

def refactor_code(code: str, instruction: str) -> str:
    """
    Refactor code according to a given instruction using LLM.
    Args:
        code (str): The code to refactor.
        instruction (str): Refactoring instruction.
    Returns:
        str: Refactored code.
    """
    pass

def generate_tests(code: str) -> str:
    """
    Generate tests for the given code.
    Args:
        code (str): The code to generate tests for.
    Returns:
        str: Generated test code.
    """
    pass

def migrate_code(code: str, from_framework: str, to_framework: str) -> str:
    """
    Migrate code from one framework to another using LLM.
    Args:
        code (str): The code to migrate.
        from_framework (str): Source framework.
        to_framework (str): Target framework.
    Returns:
        str: Migrated code.
    """
    pass

def visualize_dependencies(code: str) -> str:
    """
    Visualize code dependencies as a graph or summary.
    Args:
        code (str): The code to analyze.
    Returns:
        str: Visualization or summary.
    """
    pass

def security_scan(code: str) -> str:
    """
    Scan code for security issues and suggest fixes.
    Args:
        code (str): The code to scan.
    Returns:
        str: Security analysis and suggestions.
    """
    pass

def code_poetry(topic: str) -> str:
    """
    Generate a Python code snippet as a poem or haiku about a topic.
    Args:
        topic (str): The topic for the poem.
    Returns:
        str: Code poem or haiku.
    """
    pass

def code_ritual_mode(task: str) -> str:
    """
    Provide a creative ritual or affirmation for coding tasks.
    Args:
        task (str): The coding task.
    Returns:
        str: Ritual or affirmation.
    """
    pass

def ask_for_human_review(code: str, reason: str = "") -> None:
    """
    Request a human review for code, optionally providing a reason.
    Args:
        code (str): The code to review.
        reason (str): Reason for review.
    Returns:
        None
    """
    pass

def feedback_loop(code: str, result: str) -> None:
    """
    Log feedback from code execution or deployment for self-improvement.
    Args:
        code (str): The code that was run.
        result (str): The result or feedback.
    Returns:
        None
    """
    pass

def backup_codebase_to_google_drive(repo_url: str, drive_folder_id: str) -> str:
    """
    Clone the main branch from GitHub, zip it, store the zip in data/, upload to Google Drive, and keep only one .zip backup in data/.
    Args:
        repo_url (str): HTTPS URL of the GitHub repo (e.g., https://github.com/owner/repo.git)
        drive_folder_id (str): Google Drive folder ID to upload to.
    Returns:
        str: Confirmation message or backup file link.
    """
    # 1. Clone repo to temp dir
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        clone_path = Path(temp_dir) / repo_name
        subprocess.run(["git", "clone", "--depth", "1", repo_url, str(clone_path)], check=True)
        # 2. Zip the codebase
        zip_name = f"anchorwork-main-{datetime.datetime.now().strftime('%Y%m%d')}.zip"
        persistent_zip_path = Path("data") / zip_name
        shutil.make_archive(str(persistent_zip_path.with_suffix('')), 'zip', root_dir=clone_path)
        # 3. Remove any other .zip backups in data/
        for f in Path("data").glob("anchorwork-main-*.zip"):
            if f != persistent_zip_path:
                f.unlink()
        # 4. Upload to Google Drive
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path or not os.path.exists(creds_path):
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set or file not found.")
        creds = service_account.Credentials.from_service_account_file(creds_path, scopes=["https://www.googleapis.com/auth/drive.file"])
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': zip_name,
            'parents': [drive_folder_id]
        }
        media = MediaFileUpload(str(persistent_zip_path), mimetype='application/zip')
        uploaded = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
        print(f"[Backup] Uploaded {persistent_zip_path} to Google Drive folder {drive_folder_id}")
        return f"Backed up {persistent_zip_path} to Google Drive: {uploaded.get('webViewLink', 'No link')}"


def github_pr(repo_url: str, branch: str, code: dict, message: str, github_token: str, auto_merge: bool = False, backup_before_push: bool = True, backup_drive_folder: str = "your-google-drive-folder", backup_path: str = "codebase-backups/") -> str:
    """
    Create a GitHub pull request by creating a branch, committing code, pushing, and opening a PR.
    Optionally, backup the original codebase to Google Drive before merging.
    """
    # 1. Backup original codebase before making changes
    if backup_before_push:
        backup_codebase_to_google_drive(repo_url, backup_drive_folder)
    # 2. Ensure repo is cloned locally
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    if not Path(repo_name).exists():
        subprocess.run(["git", "clone", repo_url], check=True)
    os.chdir(repo_name)
    # 3. Create new branch
    subprocess.run(["git", "checkout", "-b", branch], check=True)
    # 4. Write code to file (assumes code is a dict: {filename: content})
    if isinstance(code, dict):
        for filename, content in code.items():
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
    else:
        raise ValueError("code must be a dict of {filename: content}")
    # 5. Commit changes
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    # 6. Push branch
    subprocess.run(["git", "push", "origin", branch], check=True)
    # 7. Open PR using GitHub API
    api_url = f"https://api.github.com/repos/{repo_name}/pulls"
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github+json"}
    pr_data = {
        "title": message,
        "head": branch,
        "base": "main",
        "body": "Automated PR by coder agent."
    }
    response = requests.post(api_url, headers=headers, data=json.dumps(pr_data))
    if response.status_code == 201:
        pr_url = response.json().get("html_url", "")
    else:
        pr_url = f"Failed to create PR: {response.text}"
    # 8. Change back to original directory
    os.chdir("..")
    return pr_url

def safe_code_update(repo_url: str, code: dict, message: str, base_branch: str = "main", wait_for_ci: bool = False, auto_merge: bool = False, backup_drive_folder: str = "your-google-drive-folder") -> str:
    """
    Safely update code by creating a branch, committing, pushing, and opening a PR.
    Before merging, backup the original codebase to Google Drive.
    Optionally waits for CI to pass before merging and auto-merges if requested.
    """
    uuid_str = str(uuid.uuid4().hex[:8])
    branch = f"feature/agent-update-{uuid_str}"
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise RuntimeError("GITHUB_TOKEN not set in environment.")
    pr_url = github_pr(
        repo_url=repo_url,
        branch=branch,
        code=code,
        message=message,
        github_token=github_token,
        auto_merge=False,
        backup_before_push=True,
        backup_drive_folder=backup_drive_folder
    )
    pr_number = None
    if wait_for_ci and pr_url.startswith("https://github.com/"):
        m = re.search(r'/pull/(\d+)', pr_url)
        if m:
            pr_number = m.group(1)
            owner, repo_name = repo_url.split('/')[-2:]
            checks_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}/commits"
            headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github+json"}
            resp = requests.get(checks_url, headers=headers)
            if resp.status_code == 200 and resp.json():
                sha = resp.json()[-1]["sha"]
                status_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits/{sha}/status"
                print("Waiting for CI checks to complete...")
                for _ in range(60):  # Wait up to ~10 minutes
                    status_resp = requests.get(status_url, headers=headers)
                    if status_resp.status_code == 200:
                        state = status_resp.json().get("state")
                        if state == "success":
                            print("✅ All CI checks passed!")
                            if auto_merge and pr_number:
                                merge_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}/merge"
                                merge_resp = requests.put(merge_url, headers=headers, json={"commit_title": message})
                                if merge_resp.status_code == 200:
                                    print("🚀 PR auto-merged!")
                                else:
                                    print(f"⚠️ Auto-merge failed: {merge_resp.text}")
                            break
                        elif state == "failure":
                            print("❌ CI checks failed!")
                            break
                        else:
                            print(f"CI status: {state or 'pending'}... waiting...")
                    time.sleep(10)
    return pr_url

# Coder-specific wrappers for static analysis

def coder_run_ruff(targets: list = None, cwd: str = ".") -> str:
    return run_ruff(targets, cwd)

def coder_run_mypy(targets: list = None, cwd: str = ".", ignore_missing: bool = True) -> str:
    return run_mypy(targets, cwd, ignore_missing)

def coder_run_pylint(targets: list = None, cwd: str = ".", disable: str = "R,C") -> str:
    return run_pylint(targets, cwd, disable)

def coder_run_bandit(targets: list = None, cwd: str = ".", quiet: bool = True) -> str:
    return run_bandit(targets, cwd, quiet)

def coder_run_all_static_analysis(targets: list = None, cwd: str = ".") -> dict:
    return run_all_static_analysis(targets, cwd)

def coder_save_analysis_reports(results: dict, output_dir) -> None:
    return save_analysis_reports(results, output_dir)

def coder_get_analysis_summary(results: dict) -> str:
    return get_analysis_summary(results)
