import requests
from os import getenv
from pymongo import MongoClient
import urllib.parse
from bson.objectid import ObjectId

dbUri = 'mongodb://%s:%s' % (getenv('DB_URL'), getenv('DB_PORT'))
if getenv('DB_USERNAME') != None:
    dbUri = 'mongodb://%s:%s@%s:%s' % (urllib.parse.quote_plus(getenv('DB_USERNAME')),
                                       urllib.parse.quote_plus(getenv('DB_PASSWORD')), getenv('DB_URL'), getenv('DB_PORT'))

client = MongoClient(dbUri)
db = client[getenv('DB_NAME')]


def getAppSetting():
    appSetting = db.appSetting.find_one()
    if appSetting == None:
        defaultSetting = {'lastBlock': 0}
        db.appSetting.insert_one(defaultSetting)

        appSetting = defaultSetting

    return appSetting


def updateAppSetting(data):
    db.appSetting.update_one(
        {}, {'$set': data}
    )


def addDebt(debtId):
    db.debt.insert_one({
        'debtId': debtId
    })


def getAllDebt():
    return db.debt.find({})


def deleteOneDebt(debtId):
    db.debt.delete_one({'debtId': debtId})
