
PROJECT_NAME = 'pari_bot'
BOT_TOKEN = '753085269:AAFoSJ6lDrMgB99c4VxblKq2Jvfo-2IEE_A'

BOT_URL = PROJECT_NAME
#
WEBHOOK_HOST = 'telegram-bot.arya.pp.ua'  # server ip address
WEBHOOK_PORT = 443
WEBHOOK_LISTEN_HOST = '127.0.0.1'  # In some VPS you may need to put here the IP addr
WEBHOOK_LISTEN_PORT = 10007

WEBHOOK_SSL_CERT = '/etc/letsencrypt/live/telegram-bot.arya.pp.ua/fullchain.pem'  # Path to the ssl certificate

# WEBHOOK_SSL_CERT = os.path.dirname(os.path.realpath(__file__)) + '/webhook_cert.pem'
# WEBHOOK_SSL_PRIV = os.path.dirname(os.path.realpath(__file__)) + '/webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % BOT_URL

# WEBHOOK_HOST = '92.53.70.230'  # server ip address
# WEBHOOK_PORT = 443
# WEBHOOK_LISTEN = '0.0.0.0'
#
# WEBHOOK_SSL_CERT = os.path.dirname(os.path.realpath(__file__)) + '/webhook_cert.pem'
# WEBHOOK_SSL_PRIV = os.path.dirname(os.path.realpath(__file__)) + '/webhook_pkey.pem'
#
# WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
# WEBHOOK_URL_PATH = "/%s/" % BOT_TOKEN

