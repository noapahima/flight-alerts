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


_KNOWN_AIRLINES = [
    'el al', 'iberia', 'ryanair', 'wizz', 'easyjet', 'lufthansa', 'swiss',
    'air france', 'klm', 'turkish', 'aegean', 'sky express', 'lot', 'air europa',
    'british airways', 'alitalia', 'ita airways', 'vueling', 'transavia',
    'tap air portugal', 'finnair', 'austrian', 'brussels airlines', 'norwegian',
    'pegasus', 'sun express', 'arkia', 'israir',
]


def airline_booking_url(airline, origin, destination, date,
                        return_date='', trip_type='OW'):
    """Return a direct booking URL for the given airline and route."""
    o, d = origin.upper(), destination.upper()
    dep  = datetime.strptime(date, '%Y-%m-%d')
    al   = airline.lower()

    if 'el al' in al or 'elal' in al:
        ret_param = f"&returnDate={return_date}" if trip_type == 'RT' and return_date else ''
        return (f"https://www.elal.com/en/Book-A-Flight/"
                f"?origin={o}&destination={d}&departureDate={date}"
                f"&tripType={'RT' if trip_type == 'RT' else 'OW'}&adults=1{ret_param}")

    if 'iberia' in al:
        url = (f"https://www.iberia.com/us/flights/search/"
               f"?originAirport={o}&destinationAirport={d}"
               f"&departDate={date}&adults=1&cabin=Y"
               f"&tripType={'RT' if trip_type == 'RT' else 'OW'}")
        if trip_type == 'RT' and return_date:
            url += f"&returnDate={return_date}"
        return url

    if 'ryanair' in al:
        fmt = dep.strftime('%Y-%m-%d')
        url = f"https://www.ryanair.com/en/us/booking/home/{o}/{d}/{fmt}"
        if trip_type == 'RT' and return_date:
            url += f"/{return_date}"
        return url

    if 'wizz' in al:
        fmt = dep.strftime('%Y-%m-%d')
        url = (f"https://wizzair.com/en-gb/booking/select-flight"
               f"/{o}/{d}/{fmt}")
        if trip_type == 'RT' and return_date:
            url += f"/{return_date}"
        return url + "/1/0/0"

    if 'easyjet' in al or 'easy jet' in al:
        return (f"https://www.easyjet.com/en/cheap-flights/{o.lower()}/{d.lower()}"
                f"?departing={dep.strftime('%d/%m/%Y')}")

    if 'lufthansa' in al:
        return (f"https://www.lufthansa.com/us/en/flights-from-{o.lower()}-to-{d.lower()}"
                f"?flightType={'round-trip' if trip_type == 'RT' else 'one-way'}"
                f"&outward={date}")

    if 'swiss' in al:
        return (f"https://www.swiss.com/us/en/book/flights"
                f"?origin={o}&destination={d}&outboundDate={date}"
                f"&tripType={'RT' if trip_type == 'RT' else 'OW'}&adults=1")

    if 'air france' in al:
        ret_param = f"&returnDate={return_date}" if trip_type == 'RT' and return_date else ''
        return (f"https://wwws.airfrance.us/search/offers?"
                f"pax=1:0:0:0:0:0:0:0&cabin=EC&lang=en"
                f"&tripType={'ROUND_TRIP' if trip_type == 'RT' else 'ONE_WAY'}"
                f"&segments=1::{o}:{date}:{d}{ret_param}")

    if 'klm' in al:
        ret_param = f"&returnDate={return_date}" if trip_type == 'RT' and return_date else ''
        return (f"https://www.klm.com/search/offers?"
                f"pax=1:0:0:0:0:0:0:0&cabin=EC"
                f"&tripType={'ROUND_TRIP' if trip_type == 'RT' else 'ONE_WAY'}"
                f"&segments=1::{o}:{date}:{d}{ret_param}")

    if 'british' in al or 'ba' == al:
        return (f"https://www.britishairways.com/travel/book/public/en_us"
                f"#outboundDate={date}&origin={o}&destination={d}"
                f"&cabin=M&adult=1&tripType={'RT' if trip_type == 'RT' else 'OW'}")

    if 'turkish' in al:
        return (f"https://www.turkishairlines.com/en-us/flights/from-{o.lower()}-to-{d.lower()}/"
                f"?date={date}&tripType={'ROUND_TRIP' if trip_type == 'RT' else 'ONE_WAY'}")

    if 'aegean' in al:
        return (f"https://en.aegeanair.com/book-online/flight-results/"
                f"?origin={o}&destination={d}&outboundDate={date}"
                f"&tripType={'RT' if trip_type == 'RT' else 'OW'}&adults=1")

    if 'lot' in al:
        return (f"https://www.lot.com/us/en/flight-search/results"
                f"?origin={o}&destination={d}&departureDate={date}"
                f"&tripType={'ROUND_TRIP' if trip_type == 'RT' else 'ONE_WAY'}&passengerType=ADT")

    if 'air europa' in al:
        return (f"https://booking.aireuropa.com/shop/flights"
                f"?origin={o}&destination={d}&departureDate={date}&adults=1"
                f"&tripType={'RT' if trip_type == 'RT' else 'OW'}")

    if 'vueling' in al:
        return (f"https://www.vueling.com/en/book-your-flight/from-{o.lower()}-to-{d.lower()}"
                f"?date={date}")

    if 'tap' in al:
        return (f"https://www.flytap.com/en-us/book-flights"
                f"?origin={o}&destination={d}&departDate={date}"
                f"&tripType={'RT' if trip_type == 'RT' else 'OW'}&adults=1")

    if 'finnair' in al:
        return (f"https://www.finnair.com/en/gb/booking?origin={o}&destination={d}"
                f"&departureDate={date}&tripType={'RETURN' if trip_type == 'RT' else 'ONEWAY'}&adult=1")

    if 'norwegian' in al:
        return (f"https://www.norwegian.com/en/booking/flight-search"
                f"?D_City={o}&A_City={d}&TripType={'R' if trip_type == 'RT' else 'S'}"
                f"&D_Day={dep.day}&D_Month={dep.strftime('%Y-%m')}&IncludeTransit=true")

    if 'transavia' in al:
        return (f"https://www.transavia.com/en-EU/book-a-flight/flights/"
                f"?searchType={'ROUND_TRIP' if trip_type == 'RT' else 'ONE_WAY'}"
                f"&origin={o}&destination={d}&outboundDate={date}&adults=1")

    if 'sky express' in al or 'skyexpress' in al:
        return f"https://www.skyexpress.gr/en/book-now/?from={o}&to={d}&date={date}"

    if 'arkia' in al:
        return f"https://www.arkia.com/en/flights?from={o}&to={d}&date={date}&adults=1"

    if 'israir' in al:
        return f"https://www.israirairlines.com/en/book/?from={o}&to={d}&date={date}"

    # Fallback: Google Flights pre-filled search
    tt_str = 'round+trip' if trip_type == 'RT' else 'one+way'
    q = f"{tt_str}+flights+from+{o}+to+{d}+on+{date}"
    if trip_type == 'RT' and return_date:
        q += f"+return+{return_date}"
    return f"https://www.google.com/travel/flights?hl=en&q={q}"


def _parse_gf_airlines(body_text, base_url, origin='', destination='',
                       date='', return_date='', trip_type='OW'):
    """Extract (airline_name, price_usd, direct_url) tuples from Google Flights page text."""
    results = []
    blocks = re.split(r'\n(?=\d{1,2}:\d{2})', body_text)
    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        price_usd = None
        price_ils = None
        for line in lines:
            m = re.search(r'₪\s*([\d,]+)', line)
            if m:
                price_ils = int(m.group(1).replace(',', ''))
                price_usd = int(price_ils / 3.0)
                break
            m = re.search(r'\$\s*(\d{2,4}(?:,\d{3})*)', line)
            if m:
                price_usd = int(m.group(1).replace(',', ''))
                break
        if not price_usd or not (100 < price_usd < 15000):
            continue
        # Skip Business Class results — only Economy
        block_lower = block.lower()
        if 'business class' in block_lower or 'first class' in block_lower:
            continue
        airline = None
        for name in _KNOWN_AIRLINES:
            if name in block_lower:
                airline = name.title()
                break
        if not airline:
            for line in lines[1:4]:
                if re.match(r'^[A-Z][a-z]', line) and not re.match(r'^\d', line):
                    if 'hr' not in line and 'min' not in line and '–' not in line:
                        airline = line
                        break
        if airline:
            if origin and destination and date:
                url = airline_booking_url(airline, origin, destination,
                                          date, return_date, trip_type)
            else:
                url = base_url
            # Store ILS price alongside USD so email can show both
            label = f'₪{price_ils:,}' if price_ils else ''
            results.append((airline, price_usd, url, label))
    return results


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

            # Parse DOM — Google shows ₪ prices; extract (airline, price) pairs
            body_text = page.inner_text('body')
            airline_prices = _parse_gf_airlines(
                body_text, search_url,
                origin, destination, date, return_date, trip_type)

            # Merge with network-intercepted prices (no airline info)
            for v in aria_prices + captured_prices:
                if v not in [e[1] for e in airline_prices]:
                    airline_prices.append(('Google Flights', v, search_url))

            if not airline_prices:
                return None

            # Try to click the cheapest flight card to get its direct booking URL
            cheapest = min(airline_prices, key=lambda x: x[1])
            cheapest_airline, cheapest_price, cheapest_url = cheapest
            try:
                # Find all flight list items and click the first (cheapest shown first)
                cards = page.locator('li[data-gs], div[jsname][data-id]').all()
                if not cards:
                    cards = page.locator('div[role="listitem"]').all()
                if cards:
                    with page.expect_navigation(timeout=8000):
                        cards[0].click()
                    booking_url = page.url
                    if 'booking' in booking_url and 'tfs=' in booking_url:
                        # Update cheapest entry with the direct booking URL
                        airline_prices = [
                            (e[0], e[1], booking_url if e[1] == cheapest_price else e[2])
                            + ((e[3],) if len(e) > 3 else ())
                            for e in airline_prices
                        ]
            except Exception:
                pass  # keep the airline direct URL as fallback

            return airline_prices
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
                v = int(int(m.group(1).replace(',', '')) / 3.0)
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
                v = int(int(m.group(1).replace(',', '')) / 3.0)
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
                       amadeus_key='', amadeus_secret='', airlines=None):
    """airlines: optional list of airline name strings to filter results."""
    results = {}  # name -> (price_usd, url, ils_label)

    def _airline_matches(name):
        if not airlines:
            return True
        nl = name.lower()
        return any(a.lower() in nl or nl in a.lower() for a in airlines)

    def run(name, fn):
        try:
            res = fn(origin, destination, date, return_date, trip_type)
            if res is None:
                print(f'  {name}: no results')
                return
            # Google Flights returns list of (airline, price, url[, ils_label])
            if isinstance(res, list):
                for entry in res:
                    airline, price, url = entry[0], entry[1], entry[2]
                    ils_label = entry[3] if len(entry) > 3 else ''
                    if _airline_matches(airline):
                        results[airline] = (price, url, ils_label)
                        lbl = f' ({ils_label})' if ils_label else ''
                        print(f'  {airline}: ${price}{lbl}')
                if res and not any(_airline_matches(e[0]) for e in res):
                    print(f'  {name}: no results matching airline filter')
            else:
                price, url = res
                if _airline_matches(name):
                    results[name] = (price, url, '')
                    print(f'  {name}: ${price}')
                else:
                    print(f'  {name}: filtered out by airline preference')
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
    price, url, ils_label = results[best]
    return {
        'min_price': price,
        'url':       url,
        'label':     ils_label,
        'currency':  'USD',
        'source':    best,
        'timestamp': datetime.now().strftime('%H:%M'),
        'all':       results,
    }
