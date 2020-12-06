import requests
import json
from datetime import datetime, timedelta
import colorama as color
import termcolor as colors
color.init()


def status():
    
    """ Checks the status of the API """
    
    url = 'https://api.whatsonchain.com/v1/bsv/main/woc'
    url_2 = 'http://api.nbp.pl/api/exchangerates/rates/a/usd/'
    
    response = requests.get(url)
    status_url = response.status_code
    
    response_2 = requests.get(url_2)
    status_url_2 = response_2.status_code
       
    if status_url == 200 and status_url_2 == 200:
        print(colors.colored("Connection with API - OK", "green"))
    else:
        while True:
            print(colors.colored("No connection to API", "red"))
            input()
            
def data():

    """ Retrieves the current data """

    url_1 = 'https://api.whatsonchain.com/v1/bsv/main/circulatingsupply'
    url_2 = 'https://api.whatsonchain.com/v1/bsv/main/chain/info'
    url_3 = 'https://api.whatsonchain.com/v1/bsv/main/exchangerate'
    url_usd = 'http://api.nbp.pl/api/exchangerates/rates/a/usd/'
    
    response_usd = requests.get(url_usd)
    data_usd = response_usd.json()
    rates = data_usd['rates']
    rates_0 = rates[0] 
    mid = rates_0['mid'] # USD/PLN
    
    response_1 = requests.get(url_1)
    data_1 = response_1.json()
    
    response_2 = requests.get(url_2)
    data_2 = response_2.json()
    blocks = data_2['blocks']
    
    response_3 = requests.get(url_3)
    data_3 = response_3.json()
    exchangerate = data_3['rate']
    exchangerate_fl = float(exchangerate)
    ex_usd = round(exchangerate_fl, 2)
    pln_x = mid * exchangerate_fl
    pln = round(pln_x, 2)
    print("- Supply:", data_1)
    print("- The last block:", blocks)
    print("- Exchange:", ex_usd, "USD")
    print("- Exchange:", pln, "PLN")
    return blocks, pln

 
def data_block(blocks, pln):

    """ Gets information about the last block """

    url = 'https://api.whatsonchain.com/v1/bsv/main/block/height/' + str(block)
    response = requests.get(url)
    data = response.json()
    
    miner = data['miner']
    size = data['size']
    txcount = data['txcount']
    totalFees = data['totalFees']

    pln_fees = pln * totalFees
    MB = size / 1048576
    
    megabajt = round(MB, 2)
    l_tx = txcount
    l_miner = miner
    fee = round(pln_fees, 2)
    print("- Block size:", megabajt, "Mb")
    print("- The number of transactions in the block:", l_tx)
    print("- All fees:", fee, "PLN")
    print("- Miner:", miner)


def height_time(height):

    """ Gets the date of the block """

    url = 'https://api.whatsonchain.com/v1/bsv/main/block/height/' + str(height)
    response = requests.get(url)
    data = response.json()
    time = data['time']
    time_conv = datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    return time_conv
    

def adress_history(adress):

    """ Gets the history of the transaction """

    url = 'https://api.whatsonchain.com/v1/bsv/main/address/' + adress + '/history'
    response = requests.get(url)
    data = response.json()
    try:
        tx_hash = data[:] # <-- Determines the total number of transactions per address
        all_tx = len(tx_hash) # <-- Determines the total number of transactions per address
        print(" Total number of transactions:", all_tx)
        if all_tx > 0:
            first_seen = tx_hash[0]
            height = first_seen['height']
            time_conv = height_time(height)
            print(" Address [", adress, "]")
            print(" First seen on the day", time_conv, "block [", height, "]")
        return tx_hash
    except TypeError:
        print(colors.colored(" No transaction", "yellow"))
        answer()
    

def tx_history(tx_hash):

    """ Retrieves and creates a list of transactions """

    list_tx = []
    
    for i in tx_hash:
        single_tx = i['tx_hash']
        list_tx.append(single_tx)
    return list_tx


def tx_info(list_tx, adress):

    """ Get the details of each transaction """

    dict_tx = list_tx
    
    for i in list_tx: # <-- Delist transactions
        url = 'https://api.whatsonchain.com/v1/bsv/main/tx/hash/' + i
        response = requests.get(url)
        data = response.json()
        vout = data['vout'] # <-- Only checks issued
        how_vout = len(vout[:]) # <-- Checks the number of addresses in issued
        for index in range(how_vout):
            one_vout = vout[index]
            try:
                scriptPubKey = one_vout['scriptPubKey']
                addresses = scriptPubKey['addresses']
                one_addresses = addresses[0]
                if adress == one_addresses:
                    dict_tx.remove(i)
            except (KeyError, TypeError):
                pass

    print(colors.colored("\n Transactions issued ?", "green"))
    dict_number = len(dict_tx)
    if dict_number < 1:
        print(colors.colored(" No issued", "yellow"))
    elif dict_number >= 1:
        print(" [", dict_number, "] transaction")
    return dict_tx


def out_tx(dict_tx):

    """ Checks the addresses to which the BSV was issued """

    for i in dict_tx:
        url = 'https://api.whatsonchain.com/v1/bsv/main/tx/hash/' + i
        response = requests.get(url)
        data = response.json()
        vout = data['vout'] # <-- Only checks issued
        how_vout = len(vout[:]) # <-- Checks the number of addresses in issued
        for index in range(how_vout):
            one_vout = vout[index]
            value = one_vout['value']
            scriptPubKey = one_vout['scriptPubKey']
            try:
                addresses = scriptPubKey['addresses']
                one_addresses = addresses[0]
                print(" ->", one_addresses, "-> [", value, "BSV ]")
            except (KeyError, TypeError):
                pass
            try:
                opReturn = scriptPubKey['opReturn']
                parts = opReturn['parts']
                print(" -- Message:", parts[0], "-> [", value, "BSV ]")
            except (KeyError, TypeError):
                pass          


def adress_info():

    """ Retrieves information about the searched address """
    
    adress = None
    while not adress:
        adress = input("\n Enter your BSV wallet address:")
    url = 'https://api.whatsonchain.com/v1/bsv/main/address/' + adress + '/info'
    response = requests.get(url)
    data = response.json()
    isvalid = data['isvalid']
    while isvalid != True:
        print(colors.colored(" The address does not exist", "red"))
        adress = input("\n Enter your BSV wallet address:")
        url = 'https://api.whatsonchain.com/v1/bsv/main/address/' + adress + '/info'
        response = requests.get(url)
        data = response.json()
        isvalid = data['isvalid']
    return adress


def answer():

    """ Question """
    
    answer = input("\n Do you start? (y/n): ")
    
    while answer.lower() == "y":
        status()
        block, pln = data()
        data_block(block, pln)
        adress = adress_info()
        tx_hash = adress_history(adress)
        list_tx = tx_history(tx_hash)
        dict_tx = tx_info(list_tx, adress)
        out_tx(dict_tx)
        answer = input("\n Do you start? (y/n): ")
        
status()
block, pln = data()
data_block(block, pln)
adress = adress_info()
tx_hash = adress_history(adress)
list_tx = tx_history(tx_hash)
dict_tx = tx_info(list_tx, adress)
out_tx(dict_tx)
answer()
input("End..")
