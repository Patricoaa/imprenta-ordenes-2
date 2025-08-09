from __future__ import annotations
import smtplib
from email.mime.text import MIMEText
from typing import Optional
from flask import current_app

from ..extensions import db
from ..models import NotificationLog


def send_email(to_email: str, subject: str, body: str, orden_id: Optional[int] = None) -> bool:
    cfg = current_app.config
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = cfg.get("SMTP_FROM")
    msg["To"] = to_email

    log = NotificationLog(
        orden_id=orden_id,
        destinatario=to_email,
        canal="email",
        asunto=subject,
        mensaje=body,
        estado="pendiente",
    )
    db.session.add(log)
    db.session.flush()

    try:
        with smtplib.SMTP(cfg.get("SMTP_HOST"), cfg.get("SMTP_PORT")) as server:
            if cfg.get("SMTP_USE_TLS"):
                server.starttls()
            username = cfg.get("SMTP_USERNAME")
            password = cfg.get("SMTP_PASSWORD")
            if username and password:
                server.login(username, password)
            server.send_message(msg)
        log.estado = "enviado"
        db.session.commit()
        return True
    except Exception as exc:  # noqa: BLE001
        log.estado = "error"
        log.respuesta = str(exc)
        db.session.commit()
        return False


def send_whatsapp(to_number: str, body: str, orden_id: Optional[int] = None) -> bool:
    # Stub: integrate with provider (e.g., Twilio, Meta API). For now, just log.
    log = NotificationLog(
        orden_id=orden_id,
        destinatario=to_number,
        canal="whatsapp",
        mensaje=body,
        estado="simulado",
    )
    db.session.add(log)
    db.session.commit()
    return True