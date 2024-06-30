import logging

class Logger(object):

    logging.basicConfig(
        filename='output.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S'
    )
    
    def logInfo(self, infoMessage: str) -> None:
        logging.info(infoMessage)

    def logWarning(self, warningMessage: str) -> None:
        logging.warning(warningMessage)

    def logCritical(self, criticalMessage: str) -> None:
        logging.critical(criticalMessage)

    def logError(self, errorMessage: str) -> None:
        logging.error(errorMessage)