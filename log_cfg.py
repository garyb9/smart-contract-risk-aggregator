import logging 

logging.basicConfig(
    format='%(asctime)s:%(msecs)d[%(process)d]\t%(name)s:\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

# log = logging.getLogger()