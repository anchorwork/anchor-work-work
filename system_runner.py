# utils/system_runner.py
"""
System command execution utilities with permission controls.
Provides safe command execution with allow-list and logging.
"""

import subprocess
import shlex
import time
import logging
from pathlib import Path
from typing import Optional, Set
from agentlogging.unified_logger import log_event
import asyncio

logger = logging.getLogger(__name__)


class SystemRunner:
    """
    Handles system command execution with safety controls.
    """
    
    # Default safe commands that don't require full system access
    DEFAULT_SAFE_COMMANDS: Set[str] = {
        "ls", "pwd", "whoami", "python", "pip", "poetry", 
        "git", "echo", "cat", "head", "tail", "grep", "find"
    }
    
    def __init__(self, 
                 safe_commands: Optional[Set[str]] = None,
                 log_file: Optional[Path] = None):
        """
        Initialize SystemRunner.
        
        Args:
            safe_commands: Set of commands allowed without full access
            log_file: Path to log command executions
        """
        self.safe_commands = safe_commands or self.DEFAULT_SAFE_COMMANDS.copy()
        self.log_file = log_file
        self._full_access_granted = False
    
    def grant_full_access(self) -> None:
        """Grant unrestricted command execution."""
        self._full_access_granted = True
        logger.info("✅ Full system access granted")
    
    def revoke_full_access(self) -> None:
        """Revoke full access, return to allow-list mode."""
        self._full_access_granted = False
        logger.info("🔒 Full system access revoked")
    
    def has_full_access(self) -> bool:
        """Check if full system access is granted."""
        return self._full_access_granted
    
    def add_safe_command(self, command: str) -> None:
        """Add a command to the safe allow-list."""
        self.safe_commands.add(command)
        logger.info(f"➕ Added '{command}' to safe commands")
    
    def remove_safe_command(self, command: str) -> None:
        """Remove a command from the safe allow-list."""
        self.safe_commands.discard(command)
        logger.info(f"➖ Removed '{command}' from safe commands")
    
    def _log_command(self, cmd: str, result: str, user: str = None, session: str = None) -> None:
        """Log command execution to file and unified logger."""
        if not self.log_file:
            return
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            # Truncate result if too long
            max_len = 4000
            truncated_result = result[:max_len] + ("\n...[truncated]" if len(result) > max_len else "")
            with open(self.log_file, "a", encoding="utf-8") as f:
                timestamp = time.asctime()
                f.write(f"{timestamp} | {cmd}\n{truncated_result}\n---\n")
            log_event(
                "system_command",
                {
                    "cmd": cmd,
                    "result_preview": truncated_result[:500],
                    "user": user,
                    "session": session,
                    "success": not result.startswith("❌"),
                },
                agent=user,
                session_id=session,
                level="INFO" if not result.startswith("❌") else "ERROR"
            )
        except Exception as e:
            logger.warning(f"Failed to log command: {e}")
            log_event("system_command_log_error", {"cmd": cmd, "error": str(e)}, agent=user, session_id=session, level="ERROR")

    def _execute_command(self, parts: list, env: dict = None, cwd: str = None) -> str:
        """Execute command parts and return combined output."""
        try:
            proc = subprocess.run(
                parts,
                text=True,
                capture_output=True,
                timeout=60,
                env=env,
                cwd=cwd
            )
            return proc.stdout + proc.stderr
        except subprocess.TimeoutExpired:
            return f"❌ Command timed out: {' '.join(parts)}"
        except Exception as e:
            return f"❌ Command execution failed: {e}"

    async def run_command_async(self, cmd: str, require_permission: bool = True, user: str = None, session: str = None, env: dict = None, cwd: str = None) -> str:
        """Async version of run_command."""
        return await asyncio.to_thread(self.run_command, cmd, require_permission, user, session, env, cwd)

    def run_command(self, cmd: str, require_permission: bool = True, user: str = None, session: str = None, env: dict = None, cwd: str = None) -> str:
        """
        Execute a shell command with safety checks and structured logging.
        
        Args:
            cmd: Command string to execute
            require_permission: Whether to enforce permission checks
            user: User or agent requesting the command
            session: Session ID for traceability
            env: Optional environment variables
            cwd: Optional working directory
            
        Returns:
            Command output or error message
        """
        if not cmd.strip():
            return "❌ No command provided."
        
        try:
            parts = shlex.split(cmd)
        except ValueError as e:
            return f"❌ Invalid command syntax: {e}"
        
        if not parts:
            return "❌ No command provided."
        
        command_name = parts[0]
        
        # Check permissions
        if require_permission and not self._full_access_granted:
            if command_name not in self.safe_commands:
                log_event(
                    "system_command_denied",
                    {"cmd": cmd, "user": user, "session": session, "reason": "not in safe_commands"},
                    agent=user, session_id=session, level="WARNING"
                )
                return (
                    f"❌ Command '{command_name}' is not in the safe allow-list.\n"
                    f"Safe commands: {', '.join(sorted(self.safe_commands))}\n"
                    "Grant full access first or add this command to the safe list."
                )
        
        # Execute command
        logger.info(f"🖥️ Executing: {cmd}")
        result = self._execute_command(parts, env=env, cwd=cwd)
        
        # Log execution
        self._log_command(cmd, result, user=user, session=session)
        
        return result
    
    def run_safe_command(self, cmd: str, user: str = None, session: str = None, env: dict = None, cwd: str = None) -> str:
        """
        Execute a command that's always considered safe.
        Bypasses permission checks but still uses allow-list.
        """
        return self.run_command(cmd, require_permission=False, user=user, session=session, env=env, cwd=cwd)
    
    def get_status(self) -> dict:
        """Get current status of the system runner."""
        return {
            "full_access": self._full_access_granted,
            "safe_commands": sorted(self.safe_commands),
            "log_file": str(self.log_file) if self.log_file else None
        }


# Global instance for backward compatibility
_default_runner = SystemRunner()

def run_system_command(cmd: str, require_permission: bool = True) -> str:
    """
    Execute a system command using the default runner.
    
    Args:
        cmd: Command to execute
        require_permission: Whether to check permissions
        
    Returns:
        Command output
    """
    return _default_runner.run_command(cmd, require_permission)

def grant_system_access() -> None:
    """Grant full system access to the default runner."""
    _default_runner.grant_full_access()

def revoke_system_access() -> None:
    """Revoke full system access from the default runner."""
    _default_runner.revoke_full_access()

def has_system_access() -> bool:
    """Check if the default runner has full access."""
    return _default_runner.has_full_access()

def get_system_status() -> dict:
    """Get status of the default system runner."""
    return _default_runner.get_status()
