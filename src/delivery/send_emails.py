import html
import re
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
DEFAULT_TEMPLATE_ID = "98126e36-56b8-4cb1-b9cf-6477132dea50"


def build_subject(delivery, run_date):
    return delivery.get("subject") or f"NBA Takes - {run_date}"


def render_text(delivery, run_date, unsubscribe_url):
    lines = [f"Your NBA takes for {run_date}:"]
    for take in delivery.get("takes", []):
        focus_team = take.get("focus_team")
        teams = focus_team or ", ".join(take.get("teams", []))
        lines.append(f"- {teams}: {take.get('take_text', '').strip()}")
    if unsubscribe_url:
        lines.append("")
        lines.append(f"Unsubscribe: {unsubscribe_url}")
    return "\n".join(lines)


def render_html(delivery, run_date, unsubscribe_url):
    items = []
    for take in delivery.get("takes", []):
        focus_team = take.get("focus_team")
        teams = html.escape(focus_team or ", ".join(take.get("teams", [])))
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


def slugify_team_name(team_name):
    if not team_name:
        return ""
    value = team_name.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def build_template_data(delivery, logo_base_url, logo_ext):
    data = {}
    takes = delivery.get("takes", []) or []
    for index in range(3):
        slot = index + 1
        team_key = f"nba_team_{slot}"
        take_key = f"nba_take_{slot}"
        logo_key = f"nba_logo_{slot}"
        if index >= len(takes):
            data[team_key] = ""
            data[take_key] = ""
            data[logo_key] = ""
            continue

        take = takes[index]
        focus_team = take.get("focus_team")
        team_name = focus_team or (take.get("teams") or [""])[0]
        take_text = take.get("take_text", "").strip()
        slug = slugify_team_name(team_name)
        if logo_base_url and slug:
            logo_url = f"{logo_base_url}/{slug}.{logo_ext}"
        else:
            logo_url = ""

        data[team_key] = team_name
        data[take_key] = take_text
        data[logo_key] = logo_url

    return data


def resolve_unsubscribe_links(delivery, asm_group_id, fallback_url):
    if asm_group_id:
        return "<%asm_group_unsubscribe_raw_url%>", "<%asm_group_unsubscribe_url%>"
    url = delivery.get("unsubscribe_url") or fallback_url
    return url, url


def send_email(
    api_key,
    from_email,
    from_name,
    delivery,
    run_date,
    unsubscribe_url,
    asm_group_id,
    template_id,
    logo_base_url,
    logo_ext,
):
    subject = build_subject(delivery, run_date)
    text_unsubscribe, html_unsubscribe = resolve_unsubscribe_links(
        delivery, asm_group_id, unsubscribe_url
    )
    text_body = render_text(delivery, run_date, text_unsubscribe)
    html_body = render_html(delivery, run_date, html_unsubscribe)

    payload = {
        "personalizations": [
            {"to": [{"email": delivery["email"]}], "subject": subject}
        ],
        "from": {"email": from_email, "name": from_name},
    }
    if template_id:
        payload["template_id"] = template_id
        payload["personalizations"][0]["dynamic_template_data"] = build_template_data(
            delivery, logo_base_url, logo_ext
        )
    else:
        payload["content"] = [
            {"type": "text/plain", "value": text_body},
            {"type": "text/html", "value": html_body},
        ]
    if asm_group_id:
        payload["asm"] = {"group_id": int(asm_group_id)}

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
    asm_group_id = get_env("SENDGRID_ASM_GROUP_ID", default="")
    template_id = get_env("SENDGRID_TEMPLATE_ID", default=DEFAULT_TEMPLATE_ID)
    logo_base_url = get_env("NBA_LOGO_BASE_URL", default="")
    logo_ext = get_env("NBA_LOGO_EXT", default="png")

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

    if asm_group_id:
        try:
            int(asm_group_id)
        except ValueError:
            log_error("SENDGRID_ASM_GROUP_ID must be an integer")
            asm_group_id = ""
        else:
            log_info(f"Using SendGrid ASM group unsubscribe (group_id={asm_group_id})")
    if template_id:
        if not logo_base_url:
            log_error("NBA_LOGO_BASE_URL is required when using a SendGrid template.")
            return

    for delivery in deliveries:
        delivery_unsubscribe = delivery.get("unsubscribe_url") or unsubscribe_url
        if not asm_group_id and not delivery_unsubscribe:
            missing_unsubscribe += 1
        response = send_email(
            api_key=sendgrid_key,
            from_email=from_email,
            from_name=from_name,
            delivery=delivery,
            run_date=run_date,
            unsubscribe_url=delivery_unsubscribe,
            asm_group_id=asm_group_id,
            template_id=template_id,
            logo_base_url=logo_base_url,
            logo_ext=logo_ext,
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
