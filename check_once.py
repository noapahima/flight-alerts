"""
Runs once: checks all alerts in alerts.json and sends emails if price is below threshold.
Used by GitHub Actions — no UI needed.
"""
import json
import os
from pathlib import Path

import checker
import notifier


def main():
    alerts_file = Path('alerts.json')
    if not alerts_file.exists():
        print('No alerts.json found')
        return

    alerts = json.loads(alerts_file.read_text())
    api_key = os.environ.get('RESEND_API_KEY', '')

    if not alerts:
        print('No alerts configured')
        return

    for alert in alerts:
        print(f"\nChecking {alert['origin']} → {alert['destination']}  "
              f"({alert['date']})  max ${alert['max_price']}")
        try:
            result = checker.get_cheapest_price(
                alert['origin'], alert['destination'], alert['date'],
                alert.get('return_date', ''), alert.get('trip_type', 'OW'),
                alert.get('include_luggage', False),
                airlines=alert.get('airlines') or None)

            if result:
                price = result['min_price']
                print(f"  Found: ${price} via {result['source']}")
                if price <= alert['max_price']:
                    print(f"  Sending alert to {alert['email']} ...")
                    notifier.send_price_alert(
                        api_key, alert['email'], alert,
                        price, result['currency'],
                        result['source'], result.get('url', ''),
                        result.get('all', {}))
                    print('  Email sent!')
                else:
                    print(f"  Above threshold (${alert['max_price']}) — sending summary")
                    notifier.send_no_deal_summary(
                        api_key, alert['email'], alert,
                        price, result['currency'], result.get('all', {}))
            else:
                print('  No prices found — sending summary')
                notifier.send_no_deal_summary(
                    api_key, alert['email'], alert, None, 'USD', {})
        except Exception as e:
            print(f'  Error: {e}')


if __name__ == '__main__':
    main()
