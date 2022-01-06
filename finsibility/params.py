from finsibility import finsy
import finsibility.constants as constants

STOCK_QUOTE_PRARAM = {
        'apikey':  finsy.config.get(constants.STOCK_KEY_TXT),
        'symbol': '',
    }