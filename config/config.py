# Algemene configuratie en toleranties

# COM-poort instellingen
SERIAL_PORT = 'COM7'
BAUD_RATE = 9600

# MySQL database instellingen (productiegebruik)
DB_CONFIG = {
    'host': 'mysql.kvdelsen.nl',
    'port': 3306,
    'user': 'rotator',
    'password': 's!P30DtH0UVv!#',
    'database': 'pallet_db'
}

# Toleranties (relatieve afwijking)
MATCH_TOLERANCE_LB = 0.05  # 5% voor lengte/breedte
MATCH_TOLERANCE_H = 0.10   # 10% voor hoogte

# Gewichten per dimensie
WEIGHTS = {
    'length': 0.45,
    'width': 0.45,
    'height': 0.10
}

# mm-per-pixel voor camera meting
MM_PER_PIXEL = 0.052
