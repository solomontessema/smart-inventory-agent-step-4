import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
from datetime import timezone
from agents.inventory_agent import run_inventory_agent
from config import AGENT_EMAIL_ADDRESS, AGENT_EMAIL_PASSWORD, BOSS_EMAIL_ADDRESS

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def get_recent_unseen_boss_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(AGENT_EMAIL_ADDRESS, AGENT_EMAIL_PASSWORD)
    mail.select("inbox")

    # Search for unseen emails from the boss
    status, messages = mail.search(None, f'(UNSEEN FROM "{BOSS_EMAIL_ADDRESS}")')
    email_ids = messages[0].split()
    recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=2)

    for eid in reversed(email_ids):  # Start from latest
        status, msg_data = mail.fetch(eid, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Check timestamp
        msg_date = parsedate_to_datetime(msg["Date"])
        if msg_date < recent_cutoff:
            continue

        # Decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        subject = subject.decode(encoding) if isinstance(subject, bytes) else subject

        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="ignore")
                    break
        else:
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset, errors="ignore")

        mail.logout()
        return subject, body

    mail.logout()
    return None, None  # No matching email found

def main():
    subject, body = get_recent_unseen_boss_email()
    if body:
        run_inventory_agent(f"Send me an email on this request: {body}")

if __name__ == "__main__":
    main()