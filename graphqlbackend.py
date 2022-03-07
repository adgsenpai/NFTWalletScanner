from graphene import ObjectType, String, Boolean, ID, Field, Int, List, Float, JSONString

import json

import pandas as pd

from random import randrange
from dblayer import *


# gets all NFTs for a given address
def get_address(address):
    with open('key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    api_url = "https://api.etherscan.io/api?module=account&action=tokennfttx&address=" + \
        address + "&startblock=0&endblock=999999999&sort=asc&apikey=" + key

    x = requests.get(api_url)
    alltransactions = x.json().get("result")
    contracts = []
    ids = []
    print("all", address, alltransactions)
    for t in alltransactions:

        if t.get("to") == address:
            # print(t)
            contract_address = t.get("contractAddress")
            token_id = t.get("tokenID")
            # print(contract_address, token_id)
            contracts.append(contract_address)
            ids.append(int(token_id))
    return x

# helper for get_random_address


def fetch_random():

    df = pd.read_csv('data.csv')
    df = df.values.tolist()
    row = df[randrange(len(df))]
    owner = row[0]
    address = row[1]
    print("1", address, len(address), owner)
    return address, owner

# fetches a random address from file of known addresses


def get_random_address():
    address, owner = fetch_random()
    with open('key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    api_url = "https://api.etherscan.io/api?module=account&action=tokennfttx&address=" + \
        address + "&startblock=0&endblock=999999999&sort=asc&apikey=" + key
    print(api_url)
    x = requests.get(api_url)
    print(x.json())
    alltransactions = x.json().get("result")
    contracts = []
    ids = []
    for t in alltransactions:
        if t.get("to") == address:
            # print(t)
            contract_address = t.get("contractAddress")
            token_id = t.get("tokenID")
            # print(contract_address, token_id)
            contracts.append(contract_address)
            ids.append(int(token_id))
    return contracts, ids, address, owner


class NFTS(ObjectType):
    uri = List(JSONString)
    address = String()
    images = List(String)
    name = String()


class Nulltype(ObjectType):
    result = Boolean()


class Query(ObjectType):
    vp = List(NFTS, wa=String())
    getglobalgallery = List(NFTS)
    getlatestgallery = List(NFTS)
    getusergallery = List(NFTS, wa=String())
    globalnfts = List(NFTS)
    random = List(NFTS)
    addtoglobal = List(Boolean,  wa=String(), tkid=String())
    addtousergallery = List(Boolean,  us=String(), wa=String(), tkid=String())
    removefromusergallery = List(
        Boolean, us=String(), wa=String(), tkid=String())

    def resolve_vp(self, info, wa):
        contract_address, token_id = get_address(wa)
        uri, image_links = get_uri(contract_address, token_id, wa)
        stuff = {"uri": uri, "address": wa,
                 "images": image_links, "owner": "You"}
        return [stuff]

    def resolve_random(self, info):

        # contract_address, token_id, owner_address, owner = get_random_address()
        contract_address, token_id = get_latest_opensea()
        uri, image_links = get_uri(contract_address, token_id, "")

        stuff = {"uri": uri, "address": "", "images": image_links, "name": ""}
        return [stuff]

    def resolve_getglobalgallery(self, info):

        uri, image_links = get_global_gallery()
        print(uri)
        print(image_links)
        stuff = {"uri": uri, "address": "Global",
                 "images": image_links, "owner": "Users"}
        return [stuff]

    def resolve_getusergallery(self, info, wa):

        uri, image_links = get_user_gallery(wa)
        stuff = {"uri": uri, "address": wa, "images": image_links, "owner": wa}
        return [stuff]

    def resolve_addtoglobal(self, info, wa, tkid):
        print(wa, tkid)
        tkid = int(tkid)
        create_nft(wa, tkid)
        return [True]

    def resolve_addtousergallery(self, info, us, wa, tkid):
        print(us, wa, tkid)
        tkid = int(tkid)
        add_to_gallery(us, wa, tkid)
        return [True]

    def resolve_removefromusergallery(self, info, us, wa, tkid):
        print(us, wa, tkid)
        tkid = int(tkid)
        remove_from_gallery(us, wa, tkid)
        return [True]

    def resolve_getlatestgallery(self, info):
        uri, images = get_latest_gallery()
        stuff = {"uri": uri, "address": "Global",
                 "images": images, "owner": "Users"}
        return [stuff]


if __name__ == "__main__":

    contract_address, token_id = get_latest_opensea()
    uri, image_links = get_uri(contract_address, token_id, "")
    print(uri)
    print(image_links)
