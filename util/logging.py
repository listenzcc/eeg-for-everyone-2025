from loguru import logger

logger.add('logs/debug.log', level='DEBUG', rotation='10 MB')
