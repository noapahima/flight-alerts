"""
Airport database for autocomplete.
Format: (IATA, city, country, airport name)
"""

AIRPORTS = [
    # ── Israel ──────────────────────────────────────────────────────────────
    ('TLV', 'Tel Aviv',    'Israel',  'Ben Gurion International'),
    ('ETH', 'Eilat',       'Israel',  'Ramon International'),
    ('HFA', 'Haifa',       'Israel',  'Haifa Airport'),
    ('VDA', 'Eilat',       'Israel',  'Ovda Airport'),

    # ── UK ──────────────────────────────────────────────────────────────────
    ('LHR', 'London',      'England', 'Heathrow'),
    ('LGW', 'London',      'England', 'Gatwick'),
    ('STN', 'London',      'England', 'Stansted'),
    ('LTN', 'London',      'England', 'Luton'),
    ('LCY', 'London',      'England', 'City Airport'),
    ('MAN', 'Manchester',  'England', 'Manchester Airport'),
    ('EDI', 'Edinburgh',   'Scotland','Edinburgh Airport'),
    ('BHX', 'Birmingham',  'England', 'Birmingham Airport'),
    ('BRS', 'Bristol',     'England', 'Bristol Airport'),

    # ── France ──────────────────────────────────────────────────────────────
    ('CDG', 'Paris',       'France',  'Charles de Gaulle'),
    ('ORY', 'Paris',       'France',  'Orly'),
    ('NCE', 'Nice',        'France',  'Côte d\'Azur'),
    ('LYS', 'Lyon',        'France',  'Saint-Exupéry'),
    ('MRS', 'Marseille',   'France',  'Provence Airport'),
    ('TLS', 'Toulouse',    'France',  'Blagnac Airport'),

    # ── Germany ─────────────────────────────────────────────────────────────
    ('FRA', 'Frankfurt',   'Germany', 'Frankfurt Airport'),
    ('MUC', 'Munich',      'Germany', 'Munich Airport'),
    ('BER', 'Berlin',      'Germany', 'Brandenburg Airport'),
    ('DUS', 'Düsseldorf',  'Germany', 'Düsseldorf Airport'),
    ('HAM', 'Hamburg',     'Germany', 'Hamburg Airport'),
    ('CGN', 'Cologne',     'Germany', 'Cologne Bonn Airport'),
    ('STR', 'Stuttgart',   'Germany', 'Stuttgart Airport'),

    # ── Spain ───────────────────────────────────────────────────────────────
    ('MAD', 'Madrid',      'Spain',   'Barajas'),
    ('BCN', 'Barcelona',   'Spain',   'El Prat'),
    ('AGP', 'Malaga',      'Spain',   'Costa del Sol'),
    ('ALC', 'Alicante',    'Spain',   'Alicante Airport'),
    ('PMI', 'Palma',       'Spain',   'Palma de Mallorca'),
    ('IBZ', 'Ibiza',       'Spain',   'Ibiza Airport'),
    ('VLC', 'Valencia',    'Spain',   'Valencia Airport'),
    ('SVQ', 'Seville',     'Spain',   'San Pablo Airport'),
    ('BIO', 'Bilbao',      'Spain',   'Bilbao Airport'),
    ('TFS', 'Tenerife',    'Spain',   'Tenerife South'),
    ('LPA', 'Gran Canaria','Spain',   'Gran Canaria Airport'),
    ('ACE', 'Lanzarote',   'Spain',   'Lanzarote Airport'),
    ('FUE', 'Fuerteventura','Spain',  'Fuerteventura Airport'),

    # ── Italy ───────────────────────────────────────────────────────────────
    ('FCO', 'Rome',        'Italy',   'Fiumicino'),
    ('CIA', 'Rome',        'Italy',   'Ciampino'),
    ('MXP', 'Milan',       'Italy',   'Malpensa'),
    ('LIN', 'Milan',       'Italy',   'Linate'),
    ('BGY', 'Milan',       'Italy',   'Bergamo Orio al Serio'),
    ('VCE', 'Venice',      'Italy',   'Marco Polo'),
    ('NAP', 'Naples',      'Italy',   'Naples Airport'),
    ('PSA', 'Pisa',        'Italy',   'Galileo Galilei'),
    ('BLQ', 'Bologna',     'Italy',   'Guglielmo Marconi'),
    ('CTA', 'Catania',     'Italy',   'Fontanarossa'),
    ('PMO', 'Palermo',     'Italy',   'Falcone-Borsellino'),

    # ── Netherlands ─────────────────────────────────────────────────────────
    ('AMS', 'Amsterdam',   'Netherlands', 'Schiphol'),

    # ── Belgium ─────────────────────────────────────────────────────────────
    ('BRU', 'Brussels',    'Belgium', 'Brussels Airport'),

    # ── Austria ─────────────────────────────────────────────────────────────
    ('VIE', 'Vienna',      'Austria', 'Vienna International'),

    # ── Switzerland ─────────────────────────────────────────────────────────
    ('ZRH', 'Zurich',      'Switzerland', 'Zurich Airport'),
    ('GVA', 'Geneva',      'Switzerland', 'Geneva Airport'),
    ('BSL', 'Basel',       'Switzerland', 'EuroAirport'),

    # ── Portugal ────────────────────────────────────────────────────────────
    ('LIS', 'Lisbon',      'Portugal', 'Humberto Delgado'),
    ('OPO', 'Porto',       'Portugal', 'Francisco Sá Carneiro'),
    ('FAO', 'Faro',        'Portugal', 'Faro Airport'),

    # ── Greece ──────────────────────────────────────────────────────────────
    ('ATH', 'Athens',      'Greece',  'Eleftherios Venizelos'),
    ('SKG', 'Thessaloniki','Greece',  'Macedonia Airport'),
    ('HER', 'Heraklion',   'Greece',  'Crete Airport'),
    ('RHO', 'Rhodes',      'Greece',  'Rhodes Airport'),
    ('KGS', 'Kos',         'Greece',  'Kos Airport'),
    ('CFU', 'Corfu',       'Greece',  'Corfu Airport'),
    ('ZTH', 'Zakynthos',   'Greece',  'Zakynthos Airport'),
    ('JTR', 'Santorini',   'Greece',  'Santorini Airport'),
    ('JMK', 'Mykonos',     'Greece',  'Mykonos Airport'),
    ('MJT', 'Mytilene',    'Greece',  'Mytilene Airport'),
    ('SKI', 'Skiathos',    'Greece',  'Skiathos Airport'),

    # ── Cyprus ──────────────────────────────────────────────────────────────
    ('LCA', 'Larnaca',     'Cyprus',  'Larnaca Airport'),
    ('PFO', 'Paphos',      'Cyprus',  'Paphos Airport'),

    # ── Turkey ──────────────────────────────────────────────────────────────
    ('IST', 'Istanbul',    'Turkey',  'Istanbul Airport'),
    ('SAW', 'Istanbul',    'Turkey',  'Sabiha Gökçen'),
    ('AYT', 'Antalya',     'Turkey',  'Antalya Airport'),
    ('ADB', 'Izmir',       'Turkey',  'Adnan Menderes'),
    ('ESB', 'Ankara',      'Turkey',  'Esenboğa'),
    ('DLM', 'Dalaman',     'Turkey',  'Dalaman Airport'),
    ('BJV', 'Bodrum',      'Turkey',  'Milas-Bodrum'),

    # ── Eastern Europe ──────────────────────────────────────────────────────
    ('WAW', 'Warsaw',      'Poland',  'Chopin Airport'),
    ('KRK', 'Krakow',      'Poland',  'John Paul II Airport'),
    ('BUD', 'Budapest',    'Hungary', 'Budapest Airport'),
    ('PRG', 'Prague',      'Czech Republic', 'Václav Havel Airport'),
    ('BRQ', 'Brno',        'Czech Republic', 'Brno Airport'),
    ('OTP', 'Bucharest',   'Romania', 'Henri Coandă Airport'),
    ('CLJ', 'Cluj-Napoca', 'Romania', 'Avram Iancu Airport'),
    ('SOF', 'Sofia',       'Bulgaria','Sofia Airport'),
    ('VAR', 'Varna',       'Bulgaria','Varna Airport'),
    ('BOJ', 'Burgas',      'Bulgaria','Burgas Airport'),
    ('LJU', 'Ljubljana',   'Slovenia','Jože Pučnik Airport'),
    ('ZAG', 'Zagreb',      'Croatia', 'Zagreb Airport'),
    ('DBV', 'Dubrovnik',   'Croatia', 'Dubrovnik Airport'),
    ('SPU', 'Split',       'Croatia', 'Split Airport'),
    ('SKP', 'Skopje',      'North Macedonia', 'Alexander the Great'),
    ('TGD', 'Podgorica',   'Montenegro', 'Podgorica Airport'),
    ('TIV', 'Tivat',       'Montenegro', 'Tivat Airport'),
    ('BEG', 'Belgrade',    'Serbia',  'Nikola Tesla Airport'),
    ('BTS', 'Bratislava',  'Slovakia','M. R. Štefánik Airport'),
    ('RIX', 'Riga',        'Latvia',  'Riga Airport'),
    ('TLL', 'Tallinn',     'Estonia', 'Lennart Meri Airport'),
    ('VNO', 'Vilnius',     'Lithuania','Vilnius Airport'),

    # ── Scandinavia ─────────────────────────────────────────────────────────
    ('CPH', 'Copenhagen',  'Denmark', 'Copenhagen Airport'),
    ('ARN', 'Stockholm',   'Sweden',  'Arlanda'),
    ('GOT', 'Gothenburg',  'Sweden',  'Landvetter'),
    ('OSL', 'Oslo',        'Norway',  'Gardermoen'),
    ('HEL', 'Helsinki',    'Finland', 'Helsinki-Vantaa'),

    # ── Ireland ─────────────────────────────────────────────────────────────
    ('DUB', 'Dublin',      'Ireland', 'Dublin Airport'),

    # ── Morocco ─────────────────────────────────────────────────────────────
    ('CMN', 'Casablanca',  'Morocco', 'Mohammed V'),
    ('RAK', 'Marrakech',   'Morocco', 'Menara Airport'),
    ('AGA', 'Agadir',      'Morocco', 'Al Massira Airport'),

    # ── Egypt ───────────────────────────────────────────────────────────────
    ('CAI', 'Cairo',       'Egypt',   'Cairo International'),
    ('HRG', 'Hurghada',    'Egypt',   'Hurghada Airport'),
    ('SSH', 'Sharm el-Sheikh','Egypt','Sharm el-Sheikh Airport'),
    ('LXR', 'Luxor',       'Egypt',   'Luxor Airport'),
    ('ASW', 'Aswan',       'Egypt',   'Aswan Airport'),

    # ── Jordan ──────────────────────────────────────────────────────────────
    ('AMM', 'Amman',       'Jordan',  'Queen Alia International'),
    ('AQJ', 'Aqaba',       'Jordan',  'King Hussein Airport'),

    # ── UAE ─────────────────────────────────────────────────────────────────
    ('DXB', 'Dubai',       'UAE',     'Dubai International'),
    ('DWC', 'Dubai',       'UAE',     'Al Maktoum International'),
    ('AUH', 'Abu Dhabi',   'UAE',     'Zayed International'),
    ('SHJ', 'Sharjah',     'UAE',     'Sharjah Airport'),

    # ── Qatar ───────────────────────────────────────────────────────────────
    ('DOH', 'Doha',        'Qatar',   'Hamad International'),

    # ── Saudi Arabia ────────────────────────────────────────────────────────
    ('RUH', 'Riyadh',      'Saudi Arabia', 'King Khalid International'),
    ('JED', 'Jeddah',      'Saudi Arabia', 'King Abdulaziz International'),

    # ── Bahrain / Kuwait / Oman ──────────────────────────────────────────────
    ('BAH', 'Manama',      'Bahrain', 'Bahrain International'),
    ('KWI', 'Kuwait City', 'Kuwait',  'Kuwait International'),
    ('MCT', 'Muscat',      'Oman',    'Muscat International'),

    # ── India ───────────────────────────────────────────────────────────────
    ('DEL', 'Delhi',       'India',   'Indira Gandhi International'),
    ('BOM', 'Mumbai',      'India',   'Chhatrapati Shivaji Maharaj'),
    ('BLR', 'Bangalore',   'India',   'Kempegowda International'),
    ('MAA', 'Chennai',     'India',   'Chennai Airport'),
    ('CCU', 'Kolkata',     'India',   'Netaji Subhas Chandra Bose'),
    ('GOI', 'Goa',         'India',   'Goa International'),

    # ── Asia ────────────────────────────────────────────────────────────────
    ('BKK', 'Bangkok',     'Thailand','Suvarnabhumi'),
    ('DMK', 'Bangkok',     'Thailand','Don Mueang'),
    ('HKT', 'Phuket',      'Thailand','Phuket Airport'),
    ('CNX', 'Chiang Mai',  'Thailand','Chiang Mai Airport'),
    ('SIN', 'Singapore',   'Singapore','Changi Airport'),
    ('KUL', 'Kuala Lumpur','Malaysia','Kuala Lumpur International'),
    ('HKG', 'Hong Kong',   'Hong Kong','Hong Kong International'),
    ('PVG', 'Shanghai',    'China',   'Pudong International'),
    ('PEK', 'Beijing',     'China',   'Capital International'),
    ('CAN', 'Guangzhou',   'China',   'Baiyun International'),
    ('NRT', 'Tokyo',       'Japan',   'Narita International'),
    ('HND', 'Tokyo',       'Japan',   'Haneda Airport'),
    ('KIX', 'Osaka',       'Japan',   'Kansai International'),
    ('ICN', 'Seoul',       'South Korea', 'Incheon International'),
    ('TPE', 'Taipei',      'Taiwan',  'Taoyuan International'),
    ('MNL', 'Manila',      'Philippines','Ninoy Aquino International'),
    ('CGK', 'Jakarta',     'Indonesia','Soekarno-Hatta'),
    ('DPS', 'Bali',        'Indonesia','Ngurah Rai'),
    ('CMB', 'Colombo',     'Sri Lanka','Bandaranaike International'),
    ('MLE', 'Malé',        'Maldives','Velana International'),
    ('KTM', 'Kathmandu',   'Nepal',   'Tribhuvan International'),
    ('DAC', 'Dhaka',       'Bangladesh','Hazrat Shahjalal'),

    # ── USA ─────────────────────────────────────────────────────────────────
    ('JFK', 'New York',    'USA',     'John F. Kennedy'),
    ('EWR', 'New York',    'USA',     'Newark Liberty'),
    ('LGA', 'New York',    'USA',     'LaGuardia'),
    ('LAX', 'Los Angeles', 'USA',     'Los Angeles International'),
    ('SFO', 'San Francisco','USA',    'San Francisco International'),
    ('ORD', 'Chicago',     'USA',     "O'Hare International"),
    ('MDW', 'Chicago',     'USA',     'Midway International'),
    ('MIA', 'Miami',       'USA',     'Miami International'),
    ('MCO', 'Orlando',     'USA',     'Orlando International'),
    ('BOS', 'Boston',      'USA',     'Logan International'),
    ('DFW', 'Dallas',      'USA',     'Dallas Fort Worth'),
    ('IAH', 'Houston',     'USA',     'George Bush Intercontinental'),
    ('DEN', 'Denver',      'USA',     'Denver International'),
    ('SEA', 'Seattle',     'USA',     'Seattle-Tacoma'),
    ('ATL', 'Atlanta',     'USA',     'Hartsfield-Jackson'),
    ('PHX', 'Phoenix',     'USA',     'Phoenix Sky Harbor'),
    ('LAS', 'Las Vegas',   'USA',     'Harry Reid International'),
    ('SAN', 'San Diego',   'USA',     'San Diego International'),
    ('MSP', 'Minneapolis', 'USA',     'Minneapolis-Saint Paul'),
    ('DTW', 'Detroit',     'USA',     'Detroit Metropolitan'),
    ('PHL', 'Philadelphia','USA',     'Philadelphia International'),
    ('DCA', 'Washington',  'USA',     'Reagan National'),
    ('IAD', 'Washington',  'USA',     'Dulles International'),
    ('BWI', 'Baltimore',   'USA',     'Baltimore/Washington'),
    ('CLT', 'Charlotte',   'USA',     'Charlotte Douglas'),
    ('MSY', 'New Orleans', 'USA',     'Louis Armstrong'),

    # ── Canada ──────────────────────────────────────────────────────────────
    ('YYZ', 'Toronto',     'Canada',  'Pearson International'),
    ('YVR', 'Vancouver',   'Canada',  'Vancouver International'),
    ('YUL', 'Montreal',    'Canada',  'Trudeau International'),

    # ── South America ───────────────────────────────────────────────────────
    ('GRU', 'São Paulo',   'Brazil',  'Guarulhos International'),
    ('EZE', 'Buenos Aires','Argentina','Ezeiza International'),
    ('SCL', 'Santiago',    'Chile',   'Arturo Merino Benítez'),
    ('BOG', 'Bogotá',      'Colombia','El Dorado International'),
    ('LIM', 'Lima',        'Peru',    'Jorge Chávez International'),

    # ── Africa ──────────────────────────────────────────────────────────────
    ('JNB', 'Johannesburg','South Africa','O.R. Tambo International'),
    ('CPT', 'Cape Town',   'South Africa','Cape Town International'),
    ('NBO', 'Nairobi',     'Kenya',   'Jomo Kenyatta International'),
    ('ADD', 'Addis Ababa', 'Ethiopia','Bole International'),
    ('LOS', 'Lagos',       'Nigeria', 'Murtala Muhammed International'),
    ('TUN', 'Tunis',       'Tunisia', 'Tunis-Carthage International'),

    # ── Australia / NZ ──────────────────────────────────────────────────────
    ('SYD', 'Sydney',      'Australia','Sydney Kingsford Smith'),
    ('MEL', 'Melbourne',   'Australia','Melbourne Airport'),
    ('BNE', 'Brisbane',    'Australia','Brisbane Airport'),
    ('AKL', 'Auckland',    'New Zealand','Auckland Airport'),
]


def search(query: str, limit: int = 12) -> list[dict]:
    """Return airports matching query (IATA, city, country, or airport name)."""
    q = query.strip().lower()
    if not q:
        return []
    results = []
    for iata, city, country, name in AIRPORTS:
        if (q in iata.lower() or q in city.lower() or
                q in country.lower() or q in name.lower()):
            results.append({'iata': iata, 'city': city,
                            'country': country, 'name': name})
    return results[:limit]
