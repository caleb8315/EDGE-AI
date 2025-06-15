from __future__ import annotations

"""Tool: send_email

Send an email via SMTP or another provider.  Currently a no-op stub unless
SMTP credentials are configured through environment variables.
"""

import os
import smtplib
from email.message import EmailMessage
from typing import List, Optional

from .base import BaseTool


class SendEmailTool(BaseTool):
    name: str = "send_email"
    description: str = (
        "Send a plaintext email. Parameters:\n"
        "- to (str | List[str]): Recipient email address(es).\n"
        "- subject (str): Email subject.\n"
        "- body (str): Plaintext email body.\n"
        "Returns: Confirmation string or error message.  (Stub returns placeholder if SMTP not configured.)"
    )

    async def run(self, to: str | List[str], subject: str, body: str, *, cc: Optional[str | List[str]] = None) -> str:  # type: ignore[override]
        smtp_host = os.getenv("SMTP_HOST")
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if not (smtp_host and smtp_user and smtp_pass):
            return (
                "[send_email stub] SMTP credentials missing – would send email to "
                f"{to} with subject '{subject}'."
            )

        if isinstance(to, str):
            recipients = [to]
        else:
            recipients = list(to)
        if cc:
            if isinstance(cc, str):
                recipients.append(cc)
            else:
                recipients.extend(cc)

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = ", ".join(recipients)
        msg.set_content(body)

        # Run blocking call in thread executor to keep coroutine responsive
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send, smtp_host, smtp_port, smtp_user, smtp_pass, msg)
        return "Email sent successfully"


def _send(host: str, port: int, user: str, password: str, msg: EmailMessage) -> None:
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg) 