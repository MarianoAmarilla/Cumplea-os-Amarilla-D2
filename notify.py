"""
notify.py — Corre diariamente y envía avisos de cumpleaños
por email (Resend) y/o Microsoft Teams (webhook).
El email incluye un adjunto .ics para agregar el cumpleaños
al calendario como evento anual recurrente.

Variables de entorno requeridas:
  SUPABASE_URL          - URL de tu proyecto Supabase
  SUPABASE_SERVICE_KEY  - Service Role Key de Supabase
  RESEND_API_KEY        - API Key de resend.com
  RESEND_FROM           - Email remitente verificado en Resend
  TEAMS_WEBHOOK_URL     - URL del webhook de Teams (opcional)
"""

import os
import uuid
import base64
import requests
from datetime import date, timedelta

# ── Config desde variables de entorno ───────────────────────────
SUPABASE_URL         = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
RESEND_API_KEY       = os.environ["RESEND_API_KEY"]
RESEND_FROM          = os.environ.get("RESEND_FROM", "Cumpleaños Equipo <onboarding@resend.dev>")
TEAMS_WEBHOOK_URL    = os.environ.get("TEAMS_WEBHOOK_URL", "")


def get_all_profiles() -> list[dict]:
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/members?select=name,email,birthday",
        headers=headers, timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_tomorrows_birthdays(profiles: list[dict]) -> list[dict]:
    """Filtra los perfiles cuyo cumpleaños es mañana."""
    tomorrow = date.today() + timedelta(days=1)
    mm_dd = f"{tomorrow.month:02d}-{tomorrow.day:02d}"
    return [p for p in profiles if p.get("birthday") and p["birthday"][5:] == mm_dd]


def make_ics(person: dict) -> bytes:
    """Genera un .ics con el cumpleaños como evento anual recurrente."""
    name = person.get("name") or person.get("email", "Alguien")
    bday = person["birthday"]
    dtstart = bday.replace("-", "")
    y, m, d = int(bday[:4]), int(bday[5:7]), int(bday[8:])
    dtend = (date(y, m, d) + timedelta(days=1)).strftime("%Y%m%d")
    uid = str(uuid.uuid4())
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Cumpleaños Equipo//ES\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uid}\r\n"
        f"DTSTART;VALUE=DATE:{dtstart}\r\n"
        f"DTEND;VALUE=DATE:{dtend}\r\n"
        "RRULE:FREQ=YEARLY\r\n"
        f"SUMMARY:🎂 Cumpleaños de {name}\r\n"
        f"DESCRIPTION:Mañana es el cumpleaños de {name}. ¡No te olvides de felicitarlo/a!\r\n"
        "TRANSP:TRANSPARENT\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    return ics.encode("utf-8")


def send_email(recipients: list[str], birthday_person: dict):
    """Envía email a todos los recipients via Resend."""
    tomorrow = date.today() + timedelta(days=1)
    name = birthday_person.get("name") or birthday_person.get("email")
    safe_name = name.replace(" ", "_")

    subject = f"🎂 Mañana es el cumpleaños de {name}!"
    body_html = f"""
    <div style="font-family:Segoe UI,sans-serif;max-width:500px;margin:auto">
      <div style="background:#667eea;padding:30px;border-radius:12px 12px 0 0;text-align:center">
        <div style="font-size:3rem">🎂</div>
        <h1 style="color:white;margin:8px 0">¡Cumpleaños mañana!</h1>
      </div>
      <div style="background:#f7f7f7;padding:24px;border-radius:0 0 12px 12px">
        <p style="font-size:1.1rem;color:#333">
          Mañana, <strong>{tomorrow.strftime('%d/%m/%Y')}</strong>,
          es el cumpleaños de <strong style="color:#667eea">{name}</strong>.
        </p>
        <p style="color:#666;margin-top:16px">¡Acordate de felicitarlo/a! 🎉</p>
        <p style="color:#999;margin-top:20px;font-size:0.85rem">
          📅 El archivo adjunto (.ics) agrega el cumpleaños a tu calendario como recordatorio anual.
        </p>
      </div>
    </div>
    """

    ics_data = make_ics(birthday_person)
    ics_b64 = base64.b64encode(ics_data).decode("utf-8")

    payload = {
        "from": RESEND_FROM,
        "to": recipients,
        "subject": subject,
        "html": body_html,
        "attachments": [
            {
                "filename": f"cumple_{safe_name}.ics",
                "content": ics_b64,
                "content_type": "text/calendar",
            }
        ],
    }

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=10,
    )
    if resp.ok:
        print(f"  Email enviado a {len(recipients)} destinatarios")
    else:
        print(f"  Error Resend: {resp.status_code} {resp.text}")


def send_teams(birthday_person: dict):
    """Envía una Adaptive Card a Microsoft Teams via webhook."""
    if not TEAMS_WEBHOOK_URL:
        return

    tomorrow = date.today() + timedelta(days=1)
    name = birthday_person.get("name") or birthday_person.get("email")
    payload = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {"type": "TextBlock", "text": "🎂 ¡Cumpleaños mañana!", "weight": "Bolder", "size": "ExtraLarge", "color": "Accent"},
                    {"type": "TextBlock", "text": f"Mañana es el cumpleaños de **{name}** 🎉", "wrap": True, "size": "Large"},
                    {"type": "TextBlock", "text": f"Fecha: {tomorrow.strftime('%d/%m/%Y')}", "isSubtle": True},
                ],
            },
        }],
    }
    resp = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=10)
    if resp.ok:
        print(f"  Teams notificado para {name}")
    else:
        print(f"  Error Teams: {resp.status_code} {resp.text}")


def main():
    print(f"=== Chequeo de cumpleaños — {date.today()} ===")
    profiles = get_all_profiles()
    print(f"Perfiles encontrados: {len(profiles)}")

    todays = get_tomorrows_birthdays(profiles)
    if not todays:
        print("No hay cumpleaños mañana. ¡Hasta mañana!")
        return

    all_emails = [p["email"] for p in profiles if p.get("email")]

    for person in todays:
        print(f"\n🎂 Cumpleaños mañana: {person.get('name') or person['email']}")
        send_email(all_emails, person)
        send_teams(person)

    print("\n✓ Notificaciones enviadas.")


if __name__ == "__main__":
    main()
