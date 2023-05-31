import encodings

EMAIL_REGEXP = r'^[a-zA-Z][a-zA-Z0-9_\.\-]+@([a-zA-Z0-9-]{2,}\.)+([a-zA-Z]{2,4}|[a-zA-Z]{2}\.[a-zA-Z]{2})$'
USER_PASSWORD_REGEXP = r'((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{12,32})'
HASH_ENCODING = encodings.utf_8.getregentry().name
BCRYPT_REGEXP = '^[$]2[abxy]?[$](?:0[4-9]|[12][0-9]|3[01])[$][./0-9a-zA-Z]{53}$'
