# utils/notification.py
"""
Error notification and alerting utilities.
Provides functions to send alerts via Slack, email, and other channels.
"""

import os
import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages various notification channels for alerts and errors."""
    
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK")
        self.email_config = {
            'smtp_server': os.getenv("SMTP_SERVER"),
            'smtp_port': int(os.getenv("SMTP_PORT", "587")),
            'smtp_user': os.getenv("SMTP_USER"),
            'smtp_password': os.getenv("SMTP_PASSWORD"),
            'from_email': os.getenv("FROM_EMAIL"),
            'to_emails': os.getenv("ALERT_EMAILS", "").split(",") if os.getenv("ALERT_EMAILS") else []
        }
    
    def notify_ops(self, subject: str, body: str, level: str = "error") -> bool:
        """
        Send notification to operations team via available channels.
        
        Args:
            subject: Alert subject line
            body: Alert message body
            level: Alert level (error, warning, info)
            
        Returns:
            True if at least one notification was sent successfully
        """
        success = False
        
        # Try Slack first
        if self.slack_webhook:
            if self._send_slack_notification(subject, body, level):
                success = True
        
        # Try email if configured
        if self.email_config['smtp_server'] and self.email_config['to_emails']:
            if self._send_email_notification(subject, body, level):
                success = True
        
        # Log locally as fallback
        log_level = getattr(logging, level.upper(), logging.ERROR)
        logger.log(log_level, f"ALERT: {subject}\n{body}")
        
        return success
    
    def _send_slack_notification(self, subject: str, body: str, level: str = "error") -> bool:
        """Send notification to Slack via webhook."""
        try:
            # Choose emoji based on level
            emoji_map = {
                'error': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️',
                'success': '✅'
            }
            emoji = emoji_map.get(level, '📢')
            
            # Format message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"{emoji} **{subject}**\n```{body[:3900]}```\n*{timestamp}*"
            
            # Send to Slack
            response = requests.post(
                self.slack_webhook,
                json={"text": message},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Slack notification sent successfully")
                return True
            else:
                logger.warning(f"Slack notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"Failed to send Slack notification: {e}")
            return False
    
    def _send_email_notification(self, subject: str, body: str, level: str = "error") -> bool:
        """Send notification via email."""
        try:
            config = self.email_config
            if not all([config['smtp_server'], config['smtp_user'], config['to_emails']]):
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config['from_email'] or config['smtp_user']
            msg['To'] = ", ".join(config['to_emails'])
            msg['Subject'] = f"[{level.upper()}] {subject}"
            
            # Format body
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email_body = f"Alert Time: {timestamp}\nLevel: {level.upper()}\n\n{body}"
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['smtp_user'], config['smtp_password'])
                server.send_message(msg)
            
            logger.info("✅ Email notification sent successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to send email notification: {e}")
            return False
    
    def send_success_notification(self, subject: str, body: str) -> bool:
        """Send a success/info notification."""
        return self.notify_ops(subject, body, level="success")
    
    def send_warning_notification(self, subject: str, body: str) -> bool:
        """Send a warning notification."""
        return self.notify_ops(subject, body, level="warning")
    
    def send_error_notification(self, subject: str, body: str) -> bool:
        """Send an error notification."""
        return self.notify_ops(subject, body, level="error")


# Global notification manager instance
_global_notifier: Optional[NotificationManager] = None

def get_notification_manager() -> NotificationManager:
    """Get or create the global notification manager instance."""
    global _global_notifier
    if _global_notifier is None:
        _global_notifier = NotificationManager()
    return _global_notifier

def notify_ops(subject: str, body: str, level: str = "error") -> bool:
    """
    Convenience function to send notifications to operations team.
    
    Args:
        subject: Alert subject line
        body: Alert message body  
        level: Alert level (error, warning, info, success)
        
    Returns:
        True if notification was sent successfully
    """
    notifier = get_notification_manager()
    return notifier.notify_ops(subject, body, level)

def send_crash_alert(component: str, error: str, traceback: str = "") -> bool:
    """Send a crash/error alert with formatted details."""
    subject = f"{component} Crash Alert"
    body = f"Component: {component}\nError: {error}\n\nTraceback:\n{traceback}"
    return notify_ops(subject, body, level="error")

def send_performance_alert(component: str, metric: str, value: Any, threshold: Any) -> bool:
    """Send a performance threshold alert."""
    subject = f"{component} Performance Alert"
    body = f"Component: {component}\nMetric: {metric}\nValue: {value}\nThreshold: {threshold}"
    return notify_ops(subject, body, level="warning")

def send_deployment_notification(component: str, version: str, status: str) -> bool:
    """Send a deployment status notification."""
    subject = f"{component} Deployment {status}"
    body = f"Component: {component}\nVersion: {version}\nStatus: {status}"
    level = "success" if status.lower() in ["success", "complete"] else "info"
    return notify_ops(subject, body, level=level)
