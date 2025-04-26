from fast_bitrix24 import BitrixAsync
from settings import BASE_BITRIX_WEBHOOK_URL
import logging

bitrix = BitrixAsync(BASE_BITRIX_WEBHOOK_URL)
logging.getLogger('fast_bitrix24').addHandler(
    logging.StreamHandler()
)
