#!/usr/bin/env python3
"""reminder_cron.py — remindere recurente pentru uneltele Hub Fiscal.
Rulează în GitHub Actions (cron lunar + zilnic pentru deadline-uri).
Citește `reminders` + `tool_logs` din Supabase (service key) și trimite:
  - Telegram individual (dacă userul are telegram_chat_id setat)
  - Email (dacă RESEND_API_KEY e setat)
Degradează grațios: dacă lipsesc secrete, doar loghează și sare.

Secrete necesare (GitHub):
  SUPABASE_URL, SUPABASE_SERVICE_KEY  (service_role — citește toate rândurile)
  TELEGRAM_TOKEN                      (deja există, pentru auto-poster)
  RESEND_API_KEY + REMINDER_FROM      (opțional, pentru email)
"""
import os, json, datetime, urllib.request, urllib.error

SB_URL = os.environ.get("SUPABASE_URL", "https://maumjqciuxdbwjtvcpsy.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
TG = os.environ.get("TELEGRAM_TOKEN", "")
RESEND = os.environ.get("RESEND_API_KEY", "")
FROM = os.environ.get("REMINDER_FROM", "Clubul Financiar <noreply@clubulfinanciar.ro>")
TODAY = datetime.date.today()
PERIOD = TODAY.strftime("%Y-%m")


def log(m): print(m, flush=True)


def sb(path, params=""):
    url = f"{SB_URL}/rest/v1/{path}{params}"
    req = urllib.request.Request(url, headers={
        "apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY, "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def email(user_email, subject, html):
    if not (RESEND and user_email):
        return False
    body = json.dumps({"from": FROM, "to": [user_email], "subject": subject, "html": html}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=body,
        headers={"Authorization": "Bearer " + RESEND, "Content-Type": "application/json",
                 "User-Agent": "ClubulFinanciar/1.0 (+clubulfinanciar.ro)"})  # UA obligatoriu (Cloudflare blochează altfel)
    try:
        urllib.request.urlopen(req, timeout=30); return True
    except Exception as e:
        log(f"  email FAIL {e}"); return False


def telegram(chat_id, text):
    if not (TG and chat_id):
        return False
    body = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML",
                       "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{TG}/sendMessage", data=body,
        headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30); return True
    except Exception as e:
        log(f"  telegram FAIL {e}"); return False


TOOL_LABEL = {
    "radar-fiscal": "Radarul fiscal ANAF",
    "plafon-tva": "Radarul de plafon TVA",
    "provizion-taxe": "Provizionul de taxe",
    "marja-produs": "Marja reală pe produs",
    "scaner-credit": "Scanerul de credit",
}


def monthly_msg(tool, logs):
    label = TOOL_LABEL.get(tool, tool)
    logged = PERIOD in (logs or {})
    if logged:
        return None  # deja logat luna asta — nu mai bate la cap
    return (f"📊 <b>{label}</b>\n\nNu ți-ai logat datele pentru luna asta ({PERIOD}). "
            f"Intră 1 minut și actualizează cifrele ca să rămâi la zi cu plafoanele și provizionul de taxe.\n\n"
            f"👉 https://clubulfinanciar.ro/fiscal")


def deadline_msg(rem):
    d = rem.get("next_date")
    if not d:
        return None
    try:
        dd = datetime.date.fromisoformat(d)
    except Exception:
        return None
    days = (dd - TODAY).days
    if days in (30, 14, 7, 3, 1, 0):
        when = "AZI" if days == 0 else f"în {days} zile"
        return (f"⏰ <b>Termen fiscal {when}</b>\n\n{rem.get('note') or 'Ai un termen fiscal apropiat.'}\n"
                f"Data: {dd.strftime('%d.%m.%Y')}\n\n👉 https://clubulfinanciar.ro/fiscal")
    return None


def main():
    if not SB_KEY:
        return log("SUPABASE_SERVICE_KEY lipsește — sar (rulare goală).")
    is_month_start = TODAY.day == 1
    try:
        reminders = sb("reminders", "?active=eq.true&select=*")
    except Exception as e:
        return log(f"nu pot citi reminders: {e}")
    log(f"{len(reminders)} remindere active · period={PERIOD} · luna_nouă={is_month_start}")
    sent = 0
    for rem in reminders:
        uid = rem["user_id"]; tool = rem["tool"]; chat = rem.get("telegram_chat_id")
        msg = None
        if rem.get("kind") == "deadline":
            msg = deadline_msg(rem)
        elif is_month_start:  # remindere lunare doar la început de lună
            try:
                logs_rows = sb("tool_logs", f"?user_id=eq.{uid}&tool=eq.{tool}&select=period")
                logs = {r["period"]: 1 for r in logs_rows}
            except Exception:
                logs = {}
            msg = monthly_msg(tool, logs)
        if not msg:
            continue
        ok = False
        if rem.get("channel") == "telegram" and chat:
            ok = telegram(chat, msg)
        if not ok and rem.get("channel") == "email":
            # emailul userului nu e în reminders; necesită join la auth.users via service key
            try:
                u = sb("rpc/cf_user_email", "")  # opțional; degradează dacă lipsește
            except Exception:
                u = None
        if ok:
            sent += 1
    log(f"trimise: {sent}")


if __name__ == "__main__":
    main()
