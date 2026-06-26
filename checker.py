"""
Reliable flight price checker using Playwright.
Sources: Google Flights, Skyscanner, Hulyo — run in parallel.
Returns min price + direct URL to those exact results.
"""
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


def _ctx(p):
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        user_agent=(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        ),
        locale='en-US',
        viewport={'width': 1280, 'height': 900},
        timezone_id='America/New_York',
    )
    return browser, ctx.new_page()


def _dismiss(page):
    for sel in ['button:has-text("Accept all")', 'button:has-text("I Accept")',
                'button:has-text("Accept")', '[aria-label*="ccept"]']:
        try:
            page.locator(sel).first.click(timeout=1500)
            return
        except Exception:
            pass


def _parse_usd(text):
    hits = re.findall(r'\$\s*(\d{1,4}(?:,\d{3})*)', text)
    return [int(h.replace(',', '')) for h in hits if 30 < int(h.replace(',', '')) < 15000]


def _parse_ils(text):
    hits = re.findall(r'₪\s*(\d{3,5}(?:,\d{3})*)', text)
    return [int(int(h.replace(',', '')) / 3.7) for h in hits
            if 100 < int(h.replace(',', '')) < 60000]


# ── Google Flights ──────────────────────────────────────────────────────────

def _google_flights(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _ctx(p)
        try:
            tt  = 'round trip' if trip_type == 'RT' and return_date else 'one way'
            q   = f"{tt} flights from {origin} to {destination} on {date}"
            if trip_type == 'RT' and return_date:
                q += f" return {return_date}"

            search_url = f"https://www.google.com/travel/flights?hl=en&q={q.replace(' ', '+')}"
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)

            loaded = False
            for sel in ['div[role="listitem"]', 'span[data-gs]', '[aria-label*="$"]']:
                try:
                    page.wait_for_selector(sel, timeout=9000)
                    loaded = True
                    break
                except PWTimeout:
                    pass
            if not loaded:
                page.wait_for_timeout(5000)

            # Capture the live URL after results load (includes encoded flight params)
            final_url = page.url or search_url

            prices = []
            for el in page.locator('[aria-label]').all()[:60]:
                try:
                    lbl = el.get_attribute('aria-label') or ''
                    prices.extend(_parse_usd(lbl))
                except Exception:
                    pass
            prices.extend(_parse_usd(page.inner_text('body')))
            prices = sorted(set(prices))
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── Skyscanner ──────────────────────────────────────────────────────────────

def _skyscanner(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _ctx(p)
        try:
            dep = datetime.strptime(date, '%Y-%m-%d').strftime('%y%m%d')
            if trip_type == 'RT' and return_date:
                ret = datetime.strptime(return_date, '%Y-%m-%d').strftime('%y%m%d')
                search_url = (f"https://www.skyscanner.com/transport/flights/"
                              f"{origin.lower()}/{destination.lower()}/{dep}/{ret}/"
                              f"?adults=1&currency=USD")
            else:
                search_url = (f"https://www.skyscanner.com/transport/flights/"
                              f"{origin.lower()}/{destination.lower()}/{dep}/"
                              f"?adults=1&currency=USD")

            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            try:
                page.wait_for_selector('[data-testid*="price"], [class*="Price"]', timeout=10000)
            except PWTimeout:
                page.wait_for_timeout(6000)

            final_url = page.url or search_url
            prices = _parse_usd(page.inner_text('body'))
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── Hulyo ───────────────────────────────────────────────────────────────────

def _hulyo(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _ctx(p)
        try:
            search_url = (f"https://www.hulyo.co.il/flights"
                          f"?origin={origin}&destination={destination}"
                          f"&date={date}&adults=1"
                          f"&tripType={'RT' if trip_type == 'RT' else 'OW'}")
            if trip_type == 'RT' and return_date:
                search_url += f"&returnDate={return_date}"

            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            page.wait_for_timeout(7000)

            final_url = page.url or search_url
            text   = page.inner_text('body')
            prices = _parse_usd(text) + _parse_ils(text)
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── Ryanair ─────────────────────────────────────────────────────────────────

def _ryanair(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _ctx(p)
        try:
            d = datetime.strptime(date, '%Y-%m-%d')
            search_url = (
                f"https://www.ryanair.com/gb/en/trip/flights/select"
                f"?adults=1&teens=0&children=0&infants=0"
                f"&dateOut={date}&dateIn={return_date if trip_type=='RT' and return_date else ''}"
                f"&isConnectedFlight=false&isReturn={'true' if trip_type=='RT' else 'false'}"
                f"&discount=0&originIata={origin}&destinationIata={destination}"
                f"&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0"
                f"&tpStartDate={date}&tpEndDate={return_date or date}"
                f"&tpDiscount=0&tpPromoCode=&tpOriginIata={origin}&tpDestinationIata={destination}"
            )
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            try:
                page.wait_for_selector('[data-ref*="price"], [class*="price"]', timeout=10000)
            except PWTimeout:
                page.wait_for_timeout(6000)
            final_url = page.url or search_url
            prices = _parse_usd(page.inner_text('body'))
            # Ryanair shows EUR — rough convert
            eur_hits = re.findall(r'€\s*(\d{1,4}(?:,\d{3})*)', page.inner_text('body'))
            prices += [int(int(h.replace(',', '')) * 1.08) for h in eur_hits
                       if 10 < int(h.replace(',', '')) < 10000]
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── Wizzair ──────────────────────────────────────────────────────────────────

def _wizzair(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _ctx(p)
        try:
            search_url = (
                f"https://wizzair.com/en-gb/flights/timetable/{origin}/{destination}/{date}"
            )
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            try:
                page.wait_for_selector('[class*="price"], [class*="fare"]', timeout=10000)
            except PWTimeout:
                page.wait_for_timeout(6000)
            final_url = page.url or search_url
            text   = page.inner_text('body')
            prices = _parse_usd(text)
            eur_hits = re.findall(r'€\s*(\d{1,4}(?:,\d{3})*)', text)
            prices += [int(int(h.replace(',', '')) * 1.08) for h in eur_hits
                       if 10 < int(h.replace(',', '')) < 10000]
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── Iberia ───────────────────────────────────────────────────────────────────

def _iberia(origin, destination, date, return_date='', trip_type='OW'):
    with sync_playwright() as p:
        browser, page = _ctx(p)
        try:
            if trip_type == 'RT' and return_date:
                search_url = (
                    f"https://www.iberia.com/us/flights/search/"
                    f"?originAirport={origin}&destinationAirport={destination}"
                    f"&departDate={date}&returnDate={return_date}&adults=1&cabin=Y&tripType=RT"
                )
            else:
                search_url = (
                    f"https://www.iberia.com/us/flights/search/"
                    f"?originAirport={origin}&destinationAirport={destination}"
                    f"&departDate={date}&adults=1&cabin=Y&tripType=OW"
                )
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            _dismiss(page)
            try:
                page.wait_for_selector('[class*="price"], [data-price]', timeout=10000)
            except PWTimeout:
                page.wait_for_timeout(6000)
            final_url = page.url or search_url
            prices = _parse_usd(page.inner_text('body'))
            eur_hits = re.findall(r'€\s*(\d{1,4}(?:,\d{3})*)', page.inner_text('body'))
            prices += [int(int(h.replace(',', '')) * 1.08) for h in eur_hits
                       if 10 < int(h.replace(',', '')) < 10000]
            return (min(prices), final_url) if prices else None
        finally:
            browser.close()


# ── Main entry ──────────────────────────────────────────────────────────────

SOURCES = {
    'Google Flights': _google_flights,
    'Skyscanner':     _skyscanner,
    'Hulyo':          _hulyo,
    'Ryanair':        _ryanair,
    'Wizzair':        _wizzair,
    'Iberia':         _iberia,
}


def get_cheapest_price(origin, destination, date,
                       return_date='', trip_type='OW', include_luggage=False):
    results = {}   # name -> (price, url)

    def run(name, fn):
        try:
            res = fn(origin, destination, date, return_date, trip_type)
            if res:
                price, url = res
                results[name] = (price, url)
                print(f'  {name}: ${price}  →  {url[:60]}')
        except Exception as e:
            print(f'  {name} error: {e}')

    with ThreadPoolExecutor(max_workers=len(SOURCES)) as ex:
        futs = {ex.submit(run, n, fn): n for n, fn in SOURCES.items()}
        for f in as_completed(futs, timeout=90):
            pass

    if not results:
        return None

    best = min(results, key=lambda n: results[n][0])
    price, url = results[best]
    return {
        'min_price': price,
        'url':       url,
        'currency':  'USD',
        'source':    best,
        'timestamp': datetime.now().strftime('%H:%M'),
        'all':       results,   # {name: (price, url)}
    }
