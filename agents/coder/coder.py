from agents.base_agent import BaseAgent
from tools import coder_tools
import os

class Coder(BaseAgent):
    def __init__(self, agent_id: str = "coder"):
        super().__init__(agent_id)
        # Register all Coder tools and rituals as before...

    def index_codebase(self, source_dir: str = "."):
        return coder_tools.index_codebase(source_dir)

    def codebase_search(self, query: str, top_k: int = 5) -> list:
        return coder_tools.codebase_search(query, top_k)

    def codebase_qa(self, question: str) -> str:
        return coder_tools.codebase_qa(question)

    def review_code(self, code: str) -> str:
        return coder_tools.review_code(code)

    def explain_code(self, code: str) -> str:
        return coder_tools.explain_code(code)

    def log_debug_ritual(self, bug_desc: str, fix_desc: str):
        return coder_tools.log_debug_ritual(bug_desc, fix_desc)

    def track_coding_mood(self, mood: str, context: str = ""):
        return coder_tools.track_coding_mood(mood, context)

    def pair_program(self, partner_agent, task: str):
        return coder_tools.pair_program(partner_agent, task)

    def teach_code(self, topic: str, recipient_agent):
        return coder_tools.teach_code(topic, recipient_agent)

    def refactor_code(self, code: str, instruction: str) -> str:
        return coder_tools.refactor_code(code, instruction)

    def generate_tests(self, code: str) -> str:
        return coder_tools.generate_tests(code)

    def migrate_code(self, code: str, from_framework: str, to_framework: str) -> str:
        return coder_tools.migrate_code(code, from_framework, to_framework)

    def visualize_dependencies(self, code: str) -> str:
        return coder_tools.visualize_dependencies(code)

    def security_scan(self, code: str) -> str:
        return coder_tools.security_scan(code)

    def code_poetry(self, topic: str) -> str:
        return coder_tools.code_poetry(topic)

    def code_ritual_mode(self, task: str) -> str:
        return coder_tools.code_ritual_mode(task)

    def ask_for_human_review(self, code: str, reason: str = ""):
        return coder_tools.ask_for_human_review(code, reason)

    def feedback_loop(self, code: str, result: str):
        return coder_tools.feedback_loop(code, result)

    def github_pr(self, repo: str, branch: str, code: str, message: str, github_token: str, auto_merge: bool = False, backup_before_push: bool = True, backup_drive_folder: str = "your-google-drive-folder", backup_path: str = "codebase-backups/"):
        """
        Create a GitHub pull request and optionally backup codebase to Google Drive before PR.
        """
        return coder_tools.github_pr(repo, branch, code, message, github_token, auto_merge, backup_before_push, backup_drive_folder, backup_path)

    def slack_answer(self, question: str):
        return coder_tools.slack_answer(question)

    def notify_owner(self, message: str):
        return coder_tools.notify_owner(message)

    def safe_code_update(self, repo: str, code: dict, message: str, base_branch: str = "main", wait_for_ci: bool = False, auto_merge: bool = False, backup_drive_folder: str = "your-google-drive-folder"):
        """
        Proxy to coder_tools.safe_code_update for code update workflow.
        """
        return coder_tools.safe_code_update(
            repo=repo,
            code=code,
            message=message,
            base_branch=base_branch,
            wait_for_ci=wait_for_ci,
            auto_merge=auto_merge,
            backup_drive_folder=backup_drive_folder
        )