import resend

_SOURCE_COLORS = {
    'Google Flights': '#4285F4',
    'Skyscanner':     '#0770E3',
    'Hulyo':          '#E65100',
    'Ryanair':        '#073590',
    'Wizzair':        '#C6007E',
    'Iberia':         '#CC0000',
}


def _source_rows_html(all_results, max_price, currency):
    if not all_results:
        return ''
    html = ''
    try:
        for name, val in sorted(all_results.items(), key=lambda x: x[1][0]):
            p, url = val
            below  = p <= max_price
            color  = _SOURCE_COLORS.get(name, '#475569')
            border = '#BFDBFE' if below else '#E8EEF6'
            price_color = '#10B981' if below else '#475569'
            badge = ('<span style="background:#F0FDF4;color:#10B981;font-size:10px;'
                     'font-weight:bold;padding:2px 7px;border-radius:4px;margin-left:6px;">'
                     '&#10003; below threshold</span>') if below else ''
            html += (
                f'<a href="{url}" style="display:flex;align-items:center;'
                f'justify-content:space-between;text-decoration:none;padding:11px 14px;'
                f'border-radius:10px;margin-bottom:7px;background:#F8FAFF;'
                f'border:1.5px solid {border};">'
                f'<span style="display:flex;align-items:center;gap:8px;">'
                f'<span style="width:10px;height:10px;border-radius:50%;'
                f'background:{color};display:inline-block;"></span>'
                f'<span style="font-size:13px;font-weight:bold;color:#0F172A;">{name}</span>'
                f'{badge}</span>'
                f'<span style="font-size:15px;font-weight:bold;color:{price_color};">'
                f'{currency} {p:.0f} &rarr;</span></a>'
            )
    except Exception as e:
        html = f'<p style="color:#EF4444;">Error building rows: {e}</p>'
    return html


def send_price_alert(api_key, to_email, alert, price, currency,
                     source='', direct_url='', all_results=None):
    o, d   = alert['origin'], alert['destination']
    tt     = '&#8596; Round trip' if alert.get('trip_type') == 'RT' else '&#8594; One-way'
    bag    = '&#10003; Includes checked bag (23 kg)' if alert.get('include_luggage') else '&#9888; Check baggage policy'
    ret    = f'<br>Return: <b>{alert["return_date"]}</b>' if alert.get('return_date') else ''
    src    = source or 'Flight search'
    savings = alert['max_price'] - price

    from datetime import datetime as dt
    dep_sk = dt.strptime(alert['date'], '%Y-%m-%d').strftime('%y%m%d')
    if alert.get('trip_type') == 'RT' and alert.get('return_date'):
        ret_sk  = dt.strptime(alert['return_date'], '%Y-%m-%d').strftime('%y%m%d')
        sk_url  = (f"https://www.skyscanner.co.il/transport/flights/"
                   f"{o.lower()}/{d.lower()}/{dep_sk}/{ret_sk}/?adults=1&currency=USD")
        gf_url  = (f"https://www.google.com/travel/flights?hl=en&q="
                   f"round+trip+flights+{o}+to+{d}+on+{alert['date']}+return+{alert['return_date']}")
    else:
        sk_url  = (f"https://www.skyscanner.co.il/transport/flights/"
                   f"{o.lower()}/{d.lower()}/{dep_sk}/?adults=1&currency=USD")
        gf_url  = (f"https://www.google.com/travel/flights?hl=en&q="
                   f"one+way+flights+{o}+to+{d}+on+{alert['date']}")
    hulyo_url = (f"https://www.hulyo.co.il/flights?origin={o}&destination={d}"
                 f"&date={alert['date']}&adults=1")
    if alert.get('trip_type') == 'RT' and alert.get('return_date'):
        hulyo_url += f"&returnDate={alert['return_date']}"

    book_url   = direct_url or gf_url
    book_color = _SOURCE_COLORS.get(source, '#1E3A5F')

    # Build source rows separately so any error doesn't kill the whole email
    source_rows = _source_rows_html(all_results or {}, alert['max_price'], currency)

    html = (
        '<html><body style="font-family:Arial,sans-serif;background:#EEF2FF;padding:24px;margin:0;">'
        '<div style="background:white;border-radius:16px;padding:0;max-width:480px;'
        'box-shadow:0 4px 24px rgba(0,0,0,0.10);overflow:hidden;">'

        # Header
        '<div style="background:linear-gradient(135deg,#0A1628 0%,#0F2444 60%,#1A3A6B 100%);'
        'padding:24px 28px 20px;">'
        '<div style="color:rgba(255,255,255,0.5);font-size:10px;letter-spacing:3px;'
        'text-transform:uppercase;margin-bottom:6px;">Flight Price Alert</div>'
        f'<div style="color:white;font-size:26px;font-weight:bold;letter-spacing:1px;">'
        f'{o} &#9992; {d}</div>'
        f'<div style="color:rgba(255,255,255,0.5);font-size:12px;margin-top:4px;">{tt}</div>'
        '</div>'

        # Price band
        '<div style="background:#F0FDF4;border-bottom:1px solid #D1FAE5;padding:16px 28px;">'
        f'<div style="color:#065F46;font-size:11px;font-weight:bold;'
        f'letter-spacing:2px;text-transform:uppercase;">Found via {src}</div>'
        f'<div style="color:#10B981;font-size:34px;font-weight:bold;'
        f'line-height:1.1;margin-top:2px;">{currency} {price:.0f}</div>'
        f'<div style="color:#6EE7B7;font-size:11px;">'
        f'Your max: {currency} {alert["max_price"]:.0f}'
        f'&nbsp;&middot;&nbsp;Savings: {currency} {savings:.0f}</div>'
        '</div>'

        # Details
        '<div style="padding:20px 28px;">'
        '<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        f'<tr><td style="padding:9px 0;color:#94A3B8;font-size:11px;font-weight:bold;'
        f'text-transform:uppercase;letter-spacing:1px;width:100px;">Departure</td>'
        f'<td style="padding:9px 0;color:#0F172A;font-weight:bold;">{alert["date"]}{ret}</td></tr>'
        f'<tr style="border-top:1px solid #F1F5F9;">'
        f'<td style="padding:9px 0;color:#94A3B8;font-size:11px;font-weight:bold;'
        f'text-transform:uppercase;letter-spacing:1px;">Baggage</td>'
        f'<td style="padding:9px 0;color:#475569;font-size:12px;">{bag}</td></tr>'
        f'<tr style="border-top:1px solid #F1F5F9;">'
        f'<td style="padding:9px 0;color:#94A3B8;font-size:11px;font-weight:bold;'
        f'text-transform:uppercase;letter-spacing:1px;">Alert for</td>'
        f'<td style="padding:9px 0;color:#475569;font-size:12px;">{to_email}</td></tr>'
        '</table></div>'

        # Source rows
        '<div style="padding:0 28px 24px;">'
        '<div style="color:#94A3B8;font-size:9px;font-weight:bold;letter-spacing:2px;'
        'text-transform:uppercase;margin-bottom:10px;">ALL PRICES FOUND</div>'
        + source_rows +
        '</div>'

        # Footer
        '<div style="background:#F8FAFC;padding:12px 28px;border-top:1px solid #F1F5F9;">'
        '<p style="margin:0;font-size:10px;color:#CBD5E1;text-align:center;">'
        'Prices are live snapshots &#8212; always verify before purchasing.</p>'
        '</div>'
        '</div></body></html>'
    )

    resend.api_key = api_key
    resend.Emails.send({
        'from':    'Flight Alerts <onboarding@resend.dev>',
        'to':      [to_email],
        'subject': f'✈ {o} → {d}  |  {currency} {price:.0f}  via {src}',
        'html':    html,
    })


def send_no_deal_summary(api_key, to_email, alert, price, currency, all_results=None):
    """Send a summary email when check finished but price is above threshold."""
    o, d  = alert['origin'], alert['destination']
    tt    = '↔ Round trip' if alert.get('trip_type') == 'RT' else '→ One-way'
    ret   = f' → {alert["return_date"]}' if alert.get('return_date') else ''

    source_rows = _source_rows_html(all_results or {}, alert['max_price'], currency)

    if price:
        body_html = (
            f'<p style="font-size:15px;color:#0F172A;">Cheapest found: '
            f'<b>{currency} {price:.0f}</b> — above your max of '
            f'<b>{currency} {alert["max_price"]:.0f}</b>.</p>'
            f'<p style="font-size:13px;color:#64748B;">We\'ll keep watching and alert you '
            f'the moment a price drops below your threshold.</p>'
            + (f'<div style="margin-top:16px;">{source_rows}</div>' if source_rows else '')
        )
        subject = f'🔍 {o} → {d}  |  checked — cheapest {currency} {price:.0f}'
    else:
        body_html = (
            f'<p style="font-size:15px;color:#0F172A;">No flights found for this route on these dates.</p>'
            f'<p style="font-size:13px;color:#64748B;">We\'ll keep checking every hour.</p>'
        )
        subject = f'🔍 {o} → {d}  |  no flights found'

    html = (
        '<html><body style="font-family:Arial,sans-serif;background:#EEF2FF;padding:24px;margin:0;">'
        '<div style="background:white;border-radius:16px;padding:0;max-width:480px;'
        'box-shadow:0 4px 24px rgba(0,0,0,0.10);overflow:hidden;">'
        '<div style="background:linear-gradient(135deg,#1E293B 0%,#334155 100%);padding:20px 28px;">'
        '<div style="color:rgba(255,255,255,0.5);font-size:10px;letter-spacing:3px;'
        'text-transform:uppercase;margin-bottom:4px;">Search Complete</div>'
        f'<div style="color:white;font-size:22px;font-weight:bold;">{o} ✈ {d}</div>'
        f'<div style="color:rgba(255,255,255,0.5);font-size:12px;">{tt} &nbsp;·&nbsp; '
        f'{alert["date"]}{ret}</div>'
        '</div>'
        f'<div style="padding:24px 28px;">{body_html}</div>'
        '<div style="background:#F8FAFC;padding:12px 28px;border-top:1px solid #F1F5F9;">'
        '<p style="margin:0;font-size:10px;color:#CBD5E1;text-align:center;">'
        'Prices are live snapshots — always verify before purchasing.</p>'
        '</div>'
        '</div></body></html>'
    )

    resend.api_key = api_key
    resend.Emails.send({
        'from':    'Flight Alerts <onboarding@resend.dev>',
        'to':      [to_email],
        'subject': subject,
        'html':    html,
    })
