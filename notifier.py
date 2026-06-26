import resend


def send_price_alert(api_key, to_email, alert, price, currency, source='', direct_url=''):
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

  <!-- CTA buttons -->
  <div style="padding:0 28px 24px;">
    <a href="{book_url}"
       style="display:block;background:{book_color};color:white;padding:14px;
              text-decoration:none;border-radius:10px;font-size:14px;font-weight:bold;
              text-align:center;margin-bottom:10px;letter-spacing:0.5px;">
      🎯  Book on {src} — {currency} {price:.0f}
    </a>
    <div style="display:flex;gap:8px;">
      <a href="{gf_url}"
         style="flex:1;background:#F0F7FF;color:#1E40AF;padding:10px;
                text-decoration:none;border-radius:8px;font-size:12px;font-weight:bold;
                text-align:center;border:1px solid #BFDBFE;">
        Google Flights
      </a>
      <a href="{sk_url}"
         style="flex:1;background:#F0F7FF;color:#1E40AF;padding:10px;
                text-decoration:none;border-radius:8px;font-size:12px;font-weight:bold;
                text-align:center;border:1px solid #BFDBFE;">
        Skyscanner
      </a>
      <a href="{hulyo_url}"
         style="flex:1;background:#FFF7ED;color:#C2410C;padding:10px;
                text-decoration:none;border-radius:8px;font-size:12px;font-weight:bold;
                text-align:center;border:1px solid #FED7AA;">
        חוליו
      </a>
    </div>
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
