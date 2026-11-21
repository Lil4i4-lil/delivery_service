# ----- Коэффициенты для расчета стоимости доставки -----
FORMULA_WEIGHT_COEFFICIENT = '0.5'
FORMULA_COST_COEFFICIENT = '0.01'


# ----- Приложение parcels -----
# Файл models.py
PARCEL_TYPE_NAME_MAX_LENGTH = 32
PARCEL_TYPE_CLOTHES = 'clothes'
PARCEL_TYPE_ELECTRONICS = 'electronics'
PARCEL_TYPE_OTHER = 'other'

PARCEL_NAME_MAX_LENGTH = 255
PARCEL_WEIGHT_MAX_DIGITS = 8
PARCEL_WEIGHT_DECIMAL_PLACES = 3
PARCEL_COST_MAX_DIGITS = 12
PARCEL_COST_DECIMAL_PLACES = 2

PARCEL_MIN_WEIGHT = 0
PARCEL_MAX_WEIGHT = 100
PARCEL_MIN_COST = 0

# Файл tasks.py
TASK_MAX_RETRIES = 3
TASK_DEFAULT_RETRY_DELAY = 60

# Файл services.py
CBR_URL = 'https://www.cbr-xml-daily.ru/daily_json.js'
CACHE_KEY = 'cbr_usd_rate'
CACHE_TIMEOUT = 60 * 60  # 1 час
REQUEST_TIMEOUT = 10


# ----- Приложение users -----
# Файл models.py
PHONE_NUMBER_MAX_LENGTH = 12
