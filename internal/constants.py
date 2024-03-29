EMAIL_REGEXP = r'^[a-zA-Z][a-zA-Z0-9_\.\-]+@([a-zA-Z0-9-]{2,}\.)+([a-zA-Z]{2,4}|[a-zA-Z]{2}\.[a-zA-Z]{2})$'
USER_PASSWORD_REGEXP = r'((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{12,32})'
HASH_ENCODING = 'utf-8'
BCRYPT_REGEXP = r'^\$2[aby]?\$\d{1,2}\$[.\/A-Za-z0-9]{53}$'
EN_US_CE_COLLATION_NAME = 'english_ci'
RU_RU_CE_COLLATION_NAME = 'russian_ci'
JWT_TOKEN_REGEXP = r'(^[\w-]*\.[\w-]*\.[\w-]*$)'
OGRN_REGEXP = r'^([0-9]{13,15})?$'
PLACES_DUPLICATION_RADIUS = 100
WS_FOR_LAWYER_TIME_PERIOD = 3
WS_NEW_STRIKES_TIME_PERIOD = 60

