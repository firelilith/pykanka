import logging
from pykanka import *

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

with open("secrets", "r") as f:
    token = f.readline()

