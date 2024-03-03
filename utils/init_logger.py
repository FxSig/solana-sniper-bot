import logging
import os


def config_logger():
    local_log_path = 'data/log.log'
    if not os.path.exists('./data'):
        os.mkdir('./data')

    if not os.path.exists(local_log_path):
        with open(local_log_path, 'w') as fr:
            pass

    logging.basicConfig(filename=local_log_path, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='a')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    return logger
