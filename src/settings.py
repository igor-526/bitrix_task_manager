import os

BASE_BITRIX_WEBHOOK_URL = os.environ.get('BASE_BITRIX_WEBHOOK_URL')
BITRIX_TG_ID_FIELD = os.environ.get('BITRIX_TG_ID_FIELD')
TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
TG_REDIS_URL = f'redis://{os.environ.get("REDIS_HOST")}:6379/2'
