import requests
from urllib import parse
from os import getenv


def getAddressData(address, params={}):
    return requests.get(getenv('NODE_URL') + '/addresses/data/' + address, params=params).json()


def getDappData(key=None):
    params = None
    if key != None:
        params = {'key': key}
    return requests.get(getenv('NODE_URL') + '/addresses/data/' + getenv('DAPP_ADDRESS'), params=params).json()


def getLatestBlockHeight():
    return requests.get(getenv('NODE_URL') + '/blocks/height').json()['height']


def getBlockByHieght(height):
    return requests.get(getenv('NODE_URL') + '/blocks/at/' + str(height)).json()
