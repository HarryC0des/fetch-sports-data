import html
import requests

from src.pipeline.common import (
    build_run_id,
    get_env,
    load_json,
    log_end,
    log_error,
    log_info,
    log_start,
    log_warning,
    resolve_run_date,
)


SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def build_subject(delivery, run_date):
    return delivery.get("subject") or f"NBA Takes - {run_date}"


def render_text(delivery, run_date, unsubscribe_url):
    lines = [f"Your NBA takes for {run_date}:"]
    for take in delivery.get("takes", []):
        teams = ", ".join(take.get("teams", []))
        lines.append(f"- {teams}: {take.get('take_text', '').strip()}")
    if unsubscribe_url:
        lines.append("")
        lines.append(f"Unsubscribe: {unsubscribe_url}")
    return "\n".join(lines)


def render_html(delivery, run_date, unsubscribe_url):
    items = []
    for take in delivery.get("takes", []):
        teams = html.escape(", ".join(take.get("teams", [])))
        text = html.escape(take.get("take_text", "").strip())
        items.append(f"<li><strong>{teams}</strong>: {text}</li>")
    items_html = "\n".join(items)

    footer = ""
    if unsubscribe_url:
        footer = f'<p><a href="{html.escape(unsubscribe_url)}">Unsubscribe</a></p>'

    return (
        "<html><body>"
        f"<p>Your NBA takes for {html.escape(run_date)}:</p>"
        f"<ol>{items_html}</ol>"
        f"{footer}"
        "</body></html>"
    )


def send_email(api_key, from_email, from_name, delivery, run_date, unsubscribe_url):
    subject = build_subject(delivery, run_date)
    text_body = render_text(delivery, run_date, unsubscribe_url)
    html_body = render_html(delivery, run_date, unsubscribe_url)

    payload = {
        "personalizations": [
            {"to": [{"email": delivery["email"]}], "subject": subject}
        ],
        "from": {"email": from_email, "name": from_name},
        "content": [
            {"type": "text/plain", "value": text_body},
            {"type": "text/html", "value": html_body},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        SENDGRID_API_URL, headers=headers, json=payload, timeout=20
    )
    return response


def main():
    run_id = build_run_id()
    run_date = resolve_run_date()
    input_path = get_env("DELIVERIES_PATH", default="/tmp/deliveries.json")
    sendgrid_key = get_env("SENDGRID_API_KEY", required=True)
    from_email = get_env("SENDGRID_FROM_EMAIL", required=True)
    from_name = get_env("SENDGRID_FROM_NAME", default="Sports Takes")
    unsubscribe_url = get_env("UNSUBSCRIBE_URL", default="")

    log_start("send_emails", run_id, run_date)

    deliveries_payload = load_json(input_path)
    deliveries = deliveries_payload.get("deliveries", [])
    log_info(f"Loaded {len(deliveries)} deliveries from {input_path}")

    if not deliveries:
        log_warning("No deliveries to send")
        log_end("send_emails", "deliveries=0 sent=0 failed=0")
        return

    sent_count = 0
    failed_count = 0
    missing_unsubscribe = 0

    for delivery in deliveries:
        delivery_unsubscribe = delivery.get("unsubscribe_url") or unsubscribe_url
        if not delivery_unsubscribe:
            missing_unsubscribe += 1
        response = send_email(
            api_key=sendgrid_key,
            from_email=from_email,
            from_name=from_name,
            delivery=delivery,
            run_date=run_date,
            unsubscribe_url=delivery_unsubscribe,
        )

        if response.status_code == 202:
            sent_count += 1
        else:
            failed_count += 1
            log_error(
                f"SendGrid error for user_id={delivery.get('user_id')}: "
                f"{response.status_code}"
            )

    log_end(
        "send_emails",
        f"deliveries={len(deliveries)} sent={sent_count} failed={failed_count}",
    )

    if missing_unsubscribe:
        log_warning(
            f"{missing_unsubscribe} deliveries missing unsubscribe URL"
        )


if __name__ == "__main__":
    main()
