"""
Flight price checker — intercepts Google Flights network responses for accurate prices.
Falls back to DOM extraction if interception fails.
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout



_AIRPORT_NAMES = {
    'TLV': ['tlv', 'tel aviv', 'תל אביב', 'בן גוריון', 'ben gurion'],
    'MAD': ['mad', 'madrid', 'מדריד', 'barajas'],
    'LHR': ['lhr', 'london', 'heathrow', 'לונדון'],
    'CDG': ['cdg', 'paris', 'פריז', 'charles de gaulle'],
    'FCO': ['fco', 'rome', 'רומא', 'fiumicino'],
    'BCN': ['bcn', 'barcelona', 'ברצלונה'],
    'JFK': ['jfk', 'new york', 'ניו יורק', 'kennedy'],
    'BKK': ['bkk', 'bangkok', 'בנגקוק', 'suvarnabhumi'],
    'DXB': ['dxb', 'dubai', 'דובאי'],
    'ATH': ['ath', 'athens', 'אתונה'],
    'NYC': ['nyc', 'new york', 'ניו יורק'],
    'LAX': ['lax', 'los angeles', 'לוס אנג׳לס'],
    'MIA': ['mia', 'miami', 'מיאמי'],
    'ORD': ['ord', 'chicago', 'שיקגו'],
    'AMS': ['ams', 'amsterdam', 'אמסטרדם'],
    'FRA': ['fra', 'frankfurt', 'פרנקפורט'],
    'IST': ['ist', 'istanbul', 'איסטנבול'],
    'CAI': ['cai', 'cairo', 'קהיר'],
    'BEY': ['bey', 'beirut', 'ביירות'],
}


def _page_has_route(body, origin, destination):
    """Check that both origin and destination appear on page (IATA code or city name)."""
    b = body.lower()
    o_terms = _AIRPORT_NAMES.get(origin.upper(), [origin.lower()])
    d_terms = _AIRPORT_NAMES.get(destination.upper(), [destination.lower()])
    has_origin = any(t in b for t in o_terms)
    has_dest   = any(t in b for t in d_terms)
    return has_origin and has_dest


def _browser_ctx(p):
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        user_agent=(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        ),
        locale='en-US',
        viewport={'width': 1280, 'height': 900},
    )
    return browser, ctx.new_page()


def _dismiss(page):
    for sel in ['button:has-text("Accept all")', 'button:has-text("Accept")',
                '[aria-label*="ccept"]']:
        try:
            page.locator(sel).first.click(timeout=1500)
            return
        except Exception:
            pass


# ── Google Flights (primary) ─────────────────────────────────────────────────

def _google_flights(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _browser_ctx(p)
        captured_prices = []

        def handle_response(response):
            url = response.url
            if 'travel/flights' not in url and 'batchexecute' not in url:
                return
            try:
                body = response.text()
                # Google Flights returns prices in patterns like "1,234" or "234" after currency
                for m in re.finditer(r'"USD","(\d{2,4})"', body):
                    v = int(m.group(1))
                    if 100 < v < 15000:
                        captured_prices.append(v)
                for m in re.finditer(r'\$(\d{2,4}(?:,\d{3})*)', body):
                    v = int(m.group(1).replace(',', ''))
                    if 100 < v < 15000:
                        captured_prices.append(v)
            except Exception:
                pass

        page.on('response', handle_response)

        try:
            tt  = 'round trip' if trip_type == 'RT' and return_date else 'one way'
            q   = f"{tt} flights from {origin} to {destination} on {date}"
            if trip_type == 'RT' and return_date:
                q += f" return {return_date}"

            search_url = f"https://www.google.com/travel/flights?hl=en&q={q.replace(' ', '+')}"
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)

            # Wait for flight cards to appear
            found_cards = False
            for sel in ['div[role="listitem"]', '[data-gs]', '[aria-label*="$"]',
                        'div[jsname]']:
                try:
                    page.wait_for_selector(sel, timeout=8000)
                    found_cards = True
                    break
                except PWTimeout:
                    pass

            if not found_cards:
                page.wait_for_timeout(6000)

            # Extract prices from aria-labels on flight cards (most reliable)
            aria_prices = []
            for el in page.locator('[aria-label]').all()[:80]:
                try:
                    lbl = el.get_attribute('aria-label') or ''
                    for m in re.finditer(r'\$\s*(\d{2,4}(?:,\d{3})*)', lbl):
                        v = int(m.group(1).replace(',', ''))
                        if 100 < v < 15000:
                            aria_prices.append(v)
                except Exception:
                    pass

            # Also parse from DOM text — Google shows ₪ (ILS) prices for Israeli users
            body_text = page.inner_text('body')
            for m in re.finditer(r'\$\s*(\d{2,4}(?:,\d{3})*)', body_text):
                v = int(m.group(1).replace(',', ''))
                if 100 < v < 15000:
                    aria_prices.append(v)
            for m in re.finditer(r'₪\s*([\d,]+)', body_text):
                v = int(m.group(1).replace(',', '')) // 4  # ₪ → USD approx
                if 100 < v < 15000:
                    aria_prices.append(v)

            all_prices = sorted(set(aria_prices + captured_prices))

            final_url = page.url or search_url
            all_prices = sorted(set(all_prices))
            return (min(all_prices), final_url) if all_prices else None
        finally:
            browser.close()


# ── Skyscanner ───────────────────────────────────────────────────────────────

def _skyscanner(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _browser_ctx(p)
        try:
            dep = datetime.strptime(date, '%Y-%m-%d').strftime('%y%m%d')
            if trip_type == 'RT' and return_date:
                ret = datetime.strptime(return_date, '%Y-%m-%d').strftime('%y%m%d')
                url = (f"https://www.skyscanner.com/transport/flights/"
                       f"{origin.lower()}/{destination.lower()}/{dep}/{ret}/"
                       f"?adults=1&currency=USD")
            else:
                url = (f"https://www.skyscanner.com/transport/flights/"
                       f"{origin.lower()}/{destination.lower()}/{dep}/"
                       f"?adults=1&currency=USD")

            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            try:
                page.wait_for_selector('[data-testid*="price"], [class*="Price"]',
                                       timeout=10000)
            except PWTimeout:
                page.wait_for_timeout(6000)

            final_url  = page.url or url
            body       = page.inner_text('body')
            body_lower = body.lower()

            if not _page_has_route(body, origin, destination):
                print(f'  Skyscanner: {origin}/{destination} not on page')
                return None

            if sum(1 for kw in ['nonstop', 'stop', 'economy', 'depart', 'arrive', 'hr']
                   if kw in body_lower) >= 3:
                prices = [int(m.group(1).replace(',', ''))
                          for m in re.finditer(r'\$\s*(\d{2,4}(?:,\d{3})*)', body)
                          if 100 < int(m.group(1).replace(',', '')) < 15000]
                prices = sorted(set(prices))
                return (min(prices), final_url) if prices else None
            return None
        finally:
            browser.close()


# ── Hulyo ────────────────────────────────────────────────────────────────────

def _hulyo(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _browser_ctx(p)
        try:
            url = (f"https://www.hulyo.co.il/flights"
                   f"?origin={origin}&destination={destination}"
                   f"&date={date}&adults=1"
                   f"&tripType={'RT' if trip_type == 'RT' else 'OW'}")
            if trip_type == 'RT' and return_date:
                url += f"&returnDate={return_date}"

            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            page.wait_for_timeout(7000)

            final_url  = page.url or url
            body       = page.inner_text('body')
            body_lower = body.lower()

            if not _page_has_route(body, origin, destination):
                print(f'  Hulyo: {origin}/{destination} not on page')
                return None

            flight_kws = ['טיסה', 'המראה', 'נחיתה', 'ישיר', 'עצירה',
                          'flight', 'depart', 'nonstop', 'economy']
            if sum(1 for kw in flight_kws if kw in body_lower) < 2:
                return None

            prices = []
            for m in re.finditer(r'\$\s*(\d{2,4}(?:,\d{3})*)', body):
                v = int(m.group(1).replace(',', ''))
                if 100 < v < 15000:
                    prices.append(v)
            for m in re.finditer(r'₪\s*(\d{3,5}(?:,\d{3})*)', body):
                v = int(int(m.group(1).replace(',', '')) / 3.7)
                if 100 < v < 15000:
                    prices.append(v)

            prices = sorted(set(prices))
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── El Al ────────────────────────────────────────────────────────────────────

def _elal(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _browser_ctx(p)
        try:
            d = datetime.strptime(date, '%Y-%m-%d')
            url = (
                f"https://www.elal.com/en/Flights-And-Destinations/Book-Flights/Pages/default.aspx"
                f"#outboundDate={d.strftime('%d/%m/%Y')}"
                f"&origin={origin}&destination={destination}&adults=1"
                f"&tripType={'2' if trip_type == 'RT' else '1'}"
            )
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            page.wait_for_timeout(8000)

            final_url  = page.url or url
            body       = page.inner_text('body')
            body_lower = body.lower()

            if not _page_has_route(body, origin, destination):
                print(f'  El Al: {origin}/{destination} not on page')
                return None

            flight_kws = ['flight', 'depart', 'arrive', 'nonstop', 'economy',
                          'טיסה', 'המראה', 'נחיתה', 'מחיר', 'price', '$']
            if sum(1 for kw in flight_kws if kw.lower() in body_lower) < 2:
                return None

            prices = []
            for m in re.finditer(r'\$\s*(\d{2,4}(?:,\d{3})*)', body):
                v = int(m.group(1).replace(',', ''))
                if 100 < v < 15000:
                    prices.append(v)
            for m in re.finditer(r'₪\s*(\d{3,5}(?:,\d{3})*)', body):
                v = int(int(m.group(1).replace(',', '')) / 3.7)
                if 100 < v < 15000:
                    prices.append(v)

            prices = sorted(set(prices))
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── Iberia ────────────────────────────────────────────────────────────────────

def _iberia(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _browser_ctx(p)
        try:
            url = (
                f"https://www.iberia.com/us/flights/search/"
                f"?originAirport={origin}&destinationAirport={destination}"
                f"&departDate={date}&adults=1&cabin=Y"
                f"&tripType={'RT' if trip_type == 'RT' else 'OW'}"
            )
            if trip_type == 'RT' and return_date:
                url += f"&returnDate={return_date}"

            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            try:
                page.wait_for_selector('[class*="price"], [class*="Price"], [data-price]',
                                       timeout=12000)
            except PWTimeout:
                page.wait_for_timeout(8000)

            final_url  = page.url or url
            body       = page.inner_text('body')
            body_lower = body.lower()

            if not _page_has_route(body, origin, destination):
                print(f'  Iberia: {origin}/{destination} not on page')
                return None

            flight_kws = ['flight', 'nonstop', 'economy', 'depart', 'arrive', 'iberia']
            if sum(1 for kw in flight_kws if kw.lower() in body_lower) < 2:
                return None

            prices = []
            for m in re.finditer(r'\$\s*(\d{2,4}(?:,\d{3})*)', body):
                v = int(m.group(1).replace(',', ''))
                if 100 < v < 15000:
                    prices.append(v)
            for m in re.finditer(r'€\s*(\d{2,4}(?:,\d{3})*)', body):
                v = int(int(m.group(1).replace(',', '')) * 1.08)
                if 100 < v < 15000:
                    prices.append(v)

            prices = sorted(set(prices))
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── Main entry ───────────────────────────────────────────────────────────────

SOURCES = {
    'Google Flights': _google_flights,
    'Skyscanner':     _skyscanner,
    'El Al':          _elal,
    'Iberia':         _iberia,
}


def get_cheapest_price(origin, destination, date,
                       return_date='', trip_type='OW', include_luggage=False,
                       amadeus_key='', amadeus_secret=''):
    results = {}  # name -> (price, url)

    def run(name, fn):
        try:
            res = fn(origin, destination, date, return_date, trip_type)
            if res:
                price, url = res
                results[name] = (price, url)
                print(f'  {name}: ${price}')
            else:
                print(f'  {name}: no results')
        except Exception as e:
            print(f'  {name} error: {e}')

    with ThreadPoolExecutor(max_workers=len(SOURCES)) as ex:
        futs = {ex.submit(run, n, fn): n for n, fn in SOURCES.items()}
        try:
            for f in as_completed(futs, timeout=360):  # 6 min — enough for all scrapers
                pass
        except Exception:
            pass  # use whatever results came back in time

    if not results:
        return None

    best = min(results, key=lambda n: results[n][0])
    price, url = results[best]
    return {
        'min_price': price,
        'url':       url,
        'label':     '',
        'currency':  'USD',
        'source':    best,
        'timestamp': datetime.now().strftime('%H:%M'),
        'all':       results,
    }
