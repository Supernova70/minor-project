"""
Email Service — IMAP fetching, MIME parsing, and database storage.

Connects to the configured IMAP inbox, fetches recent emails,
parses their structure (headers, body, attachments), and stores
everything in the database.
"""

import hashlib
import logging
import os
from typing import Tuple, List, Dict, Any, Optional

from imapclient import IMAPClient
from email import policy
from email.parser import BytesParser
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.email import Email, Attachment

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Handles email fetching, parsing, and storage."""

    def __init__(self, db: Session):
        self.db = db

    # ── Public API ───────────────────────────────────────

    def fetch_and_store(self, limit: int = 20) -> Tuple[int, int]:
        """
        Fetch recent emails and store new ones in the database.

        Returns:
            (new_count, total_fetched)
        """
        raw_emails = self._fetch_from_imap(limit)
        new_count = 0

        for email_data in raw_emails:
            # Skip duplicates
            existing = (
                self.db.query(Email)
                .filter(Email.message_id == str(email_data["message_id"]))
                .first()
            )
            if existing:
                continue

            email_obj = self._store_email(email_data)
            if email_obj:
                new_count += 1

        self.db.commit()
        return new_count, len(raw_emails)

    # ── IMAP Fetching ────────────────────────────────────

    def _fetch_from_imap(self, limit: int) -> List[Dict[str, Any]]:
        """Connect to IMAP, fetch raw emails, disconnect."""
        client = IMAPClient(
            settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            ssl=True,
        )

        try:
            client.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
            client.select_folder("INBOX", readonly=True)

            messages = client.search(["ALL"])
            recent = messages[-limit:] if len(messages) > limit else messages
            recent.reverse()  # Most recent first

            emails = []
            for msg_id in recent:
                try:
                    raw = client.fetch([msg_id], ["RFC822"])[msg_id]
                    parsed = BytesParser(policy=policy.default).parsebytes(
                        raw[b"RFC822"]
                    )
                    emails.append(self._parse_mime(parsed, msg_id))
                except Exception as e:
                    logger.error(f"Failed to parse email {msg_id}: {e}")

            return emails
        finally:
            try:
                client.logout()
            except Exception:
                pass

    # ── MIME Parsing ─────────────────────────────────────

    def _parse_mime(self, msg, msg_id: int) -> Dict[str, Any]:
        """Extract structured data from a parsed MIME message."""
        html_body = None
        text_body = None
        attachments: List[Dict[str, Any]] = []

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))

                # Attachment
                if "attachment" in disposition:
                    filename = part.get_filename()
                    if filename:
                        payload = part.get_payload(decode=True)
                        if payload:
                            attachments.append({
                                "filename": filename,
                                "content_type": ctype,
                                "size_bytes": len(payload),
                                "content": payload,
                            })
                    continue

                if ctype == "text/html" and html_body is None:
                    html_body = part.get_content()
                elif ctype == "text/plain" and text_body is None:
                    text_body = part.get_content()
        else:
            ctype = msg.get_content_type()
            if ctype == "text/html":
                html_body = msg.get_content()
            elif ctype == "text/plain":
                text_body = msg.get_content()

        return {
            "message_id": str(msg_id),
            "sender": msg.get("From", "Unknown"),
            "subject": msg.get("Subject", "No Subject"),
            "date": str(msg.get("Date", "")),
            "to_address": msg.get("To", ""),
            "body_html": html_body,
            "body_text": text_body,
            "has_html": html_body is not None,
            "attachments": attachments,
        }

    # ── Database Storage ─────────────────────────────────

    def _store_email(self, data: Dict[str, Any]) -> Optional[Email]:
        """Store a parsed email and its attachments in the database."""
        attachments_data = data.pop("attachments", [])

        email_obj = Email(
            message_id=data["message_id"],
            sender=data["sender"],
            subject=data["subject"],
            date=data.get("date"),
            to_address=data.get("to_address"),
            body_html=data.get("body_html"),
            body_text=data.get("body_text"),
            has_html=data.get("has_html", False),
            has_attachments=len(attachments_data) > 0,
        )
        self.db.add(email_obj)
        self.db.flush()  # Get the email ID

        # Save attachments
        storage_base = settings.ATTACHMENT_DIR
        os.makedirs(storage_base, exist_ok=True)

        for att_data in attachments_data:
            content = att_data.pop("content")
            sha256 = hashlib.sha256(content).hexdigest()

            # Save file to disk
            email_dir = os.path.join(storage_base, str(email_obj.id))
            os.makedirs(email_dir, exist_ok=True)
            filepath = os.path.join(email_dir, att_data["filename"])

            try:
                with open(filepath, "wb") as f:
                    f.write(content)
            except Exception as e:
                logger.error(f"Failed to save attachment {att_data['filename']}: {e}")
                filepath = None

            att_obj = Attachment(
                email_id=email_obj.id,
                filename=att_data["filename"],
                content_type=att_data.get("content_type"),
                size_bytes=att_data.get("size_bytes", 0),
                sha256_hash=sha256,
                storage_path=filepath,
            )
            self.db.add(att_obj)

        return email_obj
