import resend


_SOURCE_COLORS = {
    'Google Flights': '#4285F4',
    'Skyscanner':     '#0770E3',
    'Hulyo':          '#E65100',
    'Ryanair':        '#073590',
    'Wizzair':        '#C6007E',
    'Iberia':         '#CC0000',
}


def _build_source_rows(all_results, max_price, currency):
    if not all_results:
        return ''
    rows = ''
    for name, val in sorted(all_results.items(), key=lambda x: x[1][0]):
        p, url = val
        below  = p <= max_price
        color  = _SOURCE_COLORS.get(name, '#475569')
        badge  = (f'<span style="background:#F0FDF4;color:#10B981;font-size:10px;'
                  f'font-weight:bold;padding:2px 7px;border-radius:4px;'
                  f'margin-left:6px;">✓ below threshold</span>') if below else ''
        rows += f"""
        <a href="{url}" style="display:flex;align-items:center;justify-content:space-between;
           text-decoration:none;padding:11px 14px;border-radius:10px;margin-bottom:7px;
           background:#F8FAFF;border:1.5px solid {'#BFDBFE' if below else '#E8EEF6'};">
          <span style="display:flex;align-items:center;gap:8px;">
            <span style="width:10px;height:10px;border-radius:50%;
                         background:{color};display:inline-block;"></span>
            <span style="font-size:13px;font-weight:bold;color:#0F172A;">{name}</span>
            {badge}
          </span>
          <span style="font-size:15px;font-weight:bold;color:{'#10B981' if below else '#475569'};">
            {currency} {p:.0f} →
          </span>
        </a>"""
    return rows


def send_price_alert(api_key, to_email, alert, price, currency, source='', direct_url='', all_results=None):
    o, d = alert['origin'], alert['destination']
    tt   = '↔ Round trip' if alert.get('trip_type') == 'RT' else '→ One-way'
    bag  = '✅ Includes checked bag (23 kg)' if alert.get('include_luggage') else '⚠️ Check baggage policy'
    ret  = f"<br>Return: <b>{alert['return_date']}</b>" if alert.get('return_date') else ''
    src  = source or 'Flight search'

    from datetime import datetime as dt
    dep_sk = dt.strptime(alert['date'], '%Y-%m-%d').strftime('%y%m%d')
    if alert.get('trip_type') == 'RT' and alert.get('return_date'):
        ret_sk = dt.strptime(alert['return_date'], '%Y-%m-%d').strftime('%y%m%d')
        sk_url = (f"https://www.skyscanner.co.il/transport/flights/"
                  f"{o.lower()}/{d.lower()}/{dep_sk}/{ret_sk}/?adults=1&currency=USD")
        gf_url = (f"https://www.google.com/travel/flights?hl=en&q="
                  f"round+trip+flights+{o}+to+{d}+on+{alert['date']}+return+{alert['return_date']}")
    else:
        sk_url = (f"https://www.skyscanner.co.il/transport/flights/"
                  f"{o.lower()}/{d.lower()}/{dep_sk}/?adults=1&currency=USD")
        gf_url = (f"https://www.google.com/travel/flights?hl=en&q="
                  f"one+way+flights+{o}+to+{d}+on+{alert['date']}")
    hulyo_url = (f"https://www.hulyo.co.il/flights?origin={o}&destination={d}"
                 f"&date={alert['date']}&adults=1")
    if alert.get('trip_type') == 'RT' and alert.get('return_date'):
        hulyo_url += f"&returnDate={alert['return_date']}"

    # Primary "Book Now" is the direct results URL from the source that found the deal
    book_url = direct_url or gf_url

    # Source-specific button color
    src_colors = {
        'Google Flights': '#4285F4',
        'Skyscanner':     '#0770E3',
        'Hulyo':          '#E65100',
    }
    book_color = src_colors.get(source, '#1E3A5F')

    resend.api_key = api_key

    resend.Emails.send({
        'from':    'Flight Alerts <onboarding@resend.dev>',
        'to':      [to_email],
        'subject': f"✈ {o} → {d}  |  {currency} {price:.0f}  via {src}",
        'html':    f"""
<html><body style="font-family:-apple-system,Arial,sans-serif;background:#EEF2FF;padding:24px;margin:0;">
<div style="background:white;border-radius:16px;padding:0;max-width:480px;
            box-shadow:0 4px 24px rgba(0,0,0,0.10);overflow:hidden;">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#0A1628 0%,#0F2444 60%,#1A3A6B 100%);
              padding:24px 28px 20px;">
    <div style="color:rgba(255,255,255,0.5);font-size:10px;letter-spacing:3px;
                text-transform:uppercase;margin-bottom:6px;">Flight Price Alert</div>
    <div style="color:white;font-size:26px;font-weight:bold;letter-spacing:1px;">
      {o} &nbsp;✈&nbsp; {d}
    </div>
    <div style="color:rgba(255,255,255,0.5);font-size:12px;margin-top:4px;">{tt}</div>
  </div>

  <!-- Price band -->
  <div style="background:#F0FDF4;border-bottom:1px solid #D1FAE5;
              padding:16px 28px;display:flex;align-items:center;">
    <div>
      <div style="color:#065F46;font-size:11px;font-weight:bold;
                  letter-spacing:2px;text-transform:uppercase;">Found via {src}</div>
      <div style="color:#10B981;font-size:34px;font-weight:bold;
                  line-height:1.1;margin-top:2px;">{currency} {price:.0f}</div>
      <div style="color:#6EE7B7;font-size:11px;">
        Your max: {currency} {alert['max_price']:.0f}
        &nbsp;·&nbsp; Savings: {currency} {alert['max_price'] - price:.0f}
      </div>
    </div>
  </div>

  <!-- Details table -->
  <div style="padding:20px 28px;">
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <tr>
        <td style="padding:9px 0;color:#94A3B8;font-size:11px;font-weight:bold;
                   text-transform:uppercase;letter-spacing:1px;width:100px;">Departure</td>
        <td style="padding:9px 0;color:#0F172A;font-weight:bold;">{alert['date']}{ret}</td>
      </tr>
      <tr style="border-top:1px solid #F1F5F9;">
        <td style="padding:9px 0;color:#94A3B8;font-size:11px;font-weight:bold;
                   text-transform:uppercase;letter-spacing:1px;">Baggage</td>
        <td style="padding:9px 0;color:#475569;font-size:12px;">{bag}</td>
      </tr>
      <tr style="border-top:1px solid #F1F5F9;">
        <td style="padding:9px 0;color:#94A3B8;font-size:11px;font-weight:bold;
                   text-transform:uppercase;letter-spacing:1px;">Alert for</td>
        <td style="padding:9px 0;color:#475569;font-size:12px;">{to_email}</td>
      </tr>
    </table>
  </div>

  <!-- All sources -->
  <div style="padding:0 28px 24px;">
    <div style="color:#94A3B8;font-size:9px;font-weight:bold;letter-spacing:2px;
                text-transform:uppercase;margin-bottom:10px;">ALL PRICES FOUND</div>
    {_build_source_rows(all_results or {}, alert['max_price'], currency)}
  </div>

  <!-- Footer -->
  <div style="background:#F8FAFC;padding:12px 28px;border-top:1px solid #F1F5F9;">
    <p style="margin:0;font-size:10px;color:#CBD5E1;text-align:center;">
      Prices are live snapshots — always verify before purchasing.
      Flight Alerts Desktop Widget
    </p>
  </div>
</div>
</body></html>
""",
    })
