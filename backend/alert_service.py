"""
Alert Service Module
Handles email alerts for high-risk user activities.
Uses SMTP configuration from environment variables.
If SMTP is not configured, alerts are logged but not sent.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AlertService:
    """Service for sending email alerts on high-risk activity."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.configured = bool(self.smtp_user and self.smtp_password)

    def send_email_alert(
        self, to_email: str, subject: str, body_text: str, body_html: str = None
    ) -> bool:
        """
        Send an email alert.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body_text: Plain text body
            body_html: Optional HTML body (falls back to plain text)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.configured:
            logger.warning(
                "Email alert skipped — SMTP not configured. "
                "Set SMTP_USER and SMTP_PASSWORD in your .env file."
            )
            return False

        if not to_email:
            logger.warning("Email alert skipped — no recipient address provided.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Attach plain-text part first (fallback for email clients)
            msg.attach(MIMEText(body_text, "plain"))

            # Attach HTML part if provided
            if body_html:
                msg.attach(MIMEText(body_html, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, [to_email], msg.as_string())

            logger.info(f"✅ Email alert sent to {to_email}: {subject}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error(
                "❌ SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD."
            )
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email alert: {e}")
            return False

    def send_high_risk_alert(
        self, user_id: str, risk_score: float, email: str = None
    ) -> bool:
        """
        Send a high-risk activity alert email.

        Args:
            user_id: The user ID that triggered the alert
            risk_score: The computed risk score (0–100)
            email: Recipient email; falls back to ALERT_EMAIL env var

        Returns:
            True if sent successfully, False otherwise
        """
        recipient = email or os.getenv("ALERT_EMAIL", "")

        if not recipient:
            logger.warning(
                "High-risk alert skipped — no recipient. "
                "Set ALERT_EMAIL in your .env file."
            )
            return False

        risk_level = "🔴 CRITICAL" if risk_score >= 80 else "🟠 HIGH"
        subject = f"{risk_level} Risk Alert — User {user_id} (Score: {risk_score:.1f})"

        body_text = (
            f"HIGH RISK ACTIVITY DETECTED\n"
            f"============================\n"
            f"User ID   : {user_id}\n"
            f"Risk Score: {risk_score:.1f} / 100\n"
            f"Risk Level: {risk_level}\n\n"
            f"Please review this activity in the User Behavior Analytics dashboard.\n"
        )

        body_html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: {'#cc0000' if risk_score >= 80 else '#ff6600'};">
              {risk_level} Risk Alert
            </h2>
            <table border="1" cellpadding="8" cellspacing="0"
                   style="border-collapse: collapse; min-width: 300px;">
              <tr><th>User ID</th><td>{user_id}</td></tr>
              <tr><th>Risk Score</th><td>{risk_score:.1f} / 100</td></tr>
              <tr><th>Risk Level</th><td>{risk_level}</td></tr>
            </table>
            <p>Please review this activity in the
               <strong>User Behavior Analytics</strong> dashboard immediately.</p>
          </body>
        </html>
        """

        return self.send_email_alert(recipient, subject, body_text, body_html)


# Singleton instance used throughout the application
alert_service = AlertService()
