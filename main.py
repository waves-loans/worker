import repo
import waves_api
from os import getenv
import pywaves as pw
import time

pw.setNode(getenv('NODE_URL'), getenv('NODE_CHAIN'), getenv('NODE_CHAIN_ID'))


def takeOne(item):
    if len(item) == 0:
        return None

    return item[0]['value']


def nodeReader():
    appSetting = repo.getAppSetting()
    wavesLastBlock = waves_api.getLatestBlockHeight() - 1

    if appSetting['lastBlock'] < wavesLastBlock:
        for height in range(appSetting['lastBlock'] + 1, wavesLastBlock + 1):
            currentBlock = waves_api.getBlockByHieght(height)
            if len(currentBlock['transactions']):
                for transaction in currentBlock['transactions']:
                    if transaction['type'] == 16 and transaction['dApp'] == getenv("DAPP_ADDRESS") and transaction['call']['function'] == 'borrow':
                        repo.addDebt(transaction['id'])

    repo.updateAppSetting({'lastBlock': wavesLastBlock})


def removeResolvedDebts():
    debts = repo.getAllDebt()
    for debt in debts:
        res = waves_api.getAddressData(getenv('DAPP_ADDRESS'),
                                       {'key': 'borrow_' + debt['debtId'] + '_resolved'})
        if len(res) > 0 and res[0]['value'] == True:
            repo.deleteOneDebt(debt['debtId'])


BASE_INTEREST = 0.005
TIME_FACTOR = 0.000001
SELLING_THRESHOLD = 0.005


def takeColat():
    debts = repo.getAllDebt()
    for debt in debts:
        collateral_amount = takeOne(waves_api.getDappData(
            'borrow_' + debt['debtId'] + '_collateralAmount')) / 10 ** 8
        borrow_amount = takeOne(waves_api.getDappData(
            'borrow_' + debt['debtId'] + '_borrowAmount')) / 10 ** 6
        borrow_start_time = takeOne(waves_api.getDappData(
            'borrow_' + debt['debtId'] + '_startTime')) / 10 ** 3
        usdn_to_waves_price = takeOne(waves_api.getAddressData(
            getenv('NUTRINO_CONTROL_DAPP_ADDRESS'), {'key': 'price'})) / 10 ** 6
        collateral_worth = usdn_to_waves_price * collateral_amount
        interest = borrow_amount * \
            (BASE_INTEREST + (TIME_FACTOR *
             (time.time() - borrow_start_time) // 600) + SELLING_THRESHOLD)
        if borrow_amount + interest >= collateral_worth:
            account = pw.Address(privateKey=getenv('ADMIN_PRIVATE_KEY'))
            tx = account.invokeScript(getenv('DAPP_ADDRESS'), 'takeCollateral', [
                                      {'type': 'string', 'value': debt['debtId']}], [])
            if 'error' in tx:
                print(tx)
            else:
                repo.deleteOneDebt(debt['debtId'])


def resolveDebtPool():
    debtPoolAmount = takeOne(waves_api.getDappData('debtPool'))
    if debtPoolAmount != None and debtPoolAmount > 0:
        debtPoolWithout = debtPoolAmount / 10 ** 8
        usdn_to_waves_price = takeOne(waves_api.getAddressData(
            getenv('NUTRINO_CONTROL_DAPP_ADDRESS'), {'key': 'price'})) / 10 ** 6
        account = pw.Address(privateKey=getenv('ADMIN_PRIVATE_KEY'))
        tx = account.invokeScript(getenv('DAPP_ADDRESS'), 'resolveDebtPool', [], [
                                  {'amount': int(debtPoolWithout * usdn_to_waves_price * 0.96 * 10 ** 6), 'assetId': getenv('USDN')}])
        if 'error' in tx:
            print(tx)


nodeReader()
removeResolvedDebts()
takeColat()
resolveDebtPool()
