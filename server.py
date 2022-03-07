#ADGSTUDIOS - server.py
from flask import Flask, Request, jsonify, redirect, request, render_template
from flask_graphql import GraphQLView
import graphene
from graphqlbackend import Query
import graphqlbackend as gb
from flask_cors import CORS, cross_origin
import os
import dblayer as db
import requests
import json
import cloudscraper
from bs4 import BeautifulSoup
import re
import urllib.parse
view_func = GraphQLView.as_view(
    'graphql', schema=graphene.Schema(query=Query), graphiql=True)
app = Flask(__name__, template_folder='./pages')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.add_url_rule('/graphql', view_func=view_func)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/api/v1/getnfts', methods=['GET', 'POST'])
def getnfts():
    if request.method == 'POST':
        if request.data:
            return jsonify(gb.get_address(request.data['walletaddress']))
    else:
        return 'invalid request'

@app.route('/api/v1/returnNFTLink/<contractAddress>/<tokenID>')
def returnNFTLink(contractAddress,tokenID):
    try:
        url = "https://opensea.io/assets/{0}/{1}".format(contractAddress,tokenID)
        scraper = cloudscraper.create_scraper(
        browser={'browser': 'firefox', 'platform': 'windows', 'mobile': False})
        html = scraper.get(url).content
        soup = BeautifulSoup(html, 'lxml')
        if len(soup.findAll('source')) > 0:
            return {'video':re.findall('"([^"]*)"', str(soup.findAll('source')[0]))[1]}
        for x in soup.findAll('meta'):
                if 'https://lh3.googleusercontent.com' in str(x):
                    return {'image':re.findall('"([^"]*)"', str(x))[0]}
    except Exception as e:
        print(e)
        return 'failed'

@app.route('/viewnfts/<walletaddress>', methods=['GET'])
def viewnfts(walletaddress):
          try:
             df = gb.get_address(urllib.parse.unquote_plus(walletaddress))
          except:
             return render_template('viewnft.html',walletaddress="Please enter a valid wallet address")
          nftimagelink = []
          for index, row in df.iterrows():
              nftimagelink.append(returnNFTLink(row['ContractAddress'],row['tokenID']))
          df['NFTImageLink'] = nftimagelink
          payload = ''
          for index, row in df.iterrows():
            try:
              if row['NFTImageLink']['image']:
                payload += '<tr>' +'<td>'+str(row['tokenID']) +'</td>'+ '<td>'+str(row['ContractAddress']) +'</td>'+ '<td>'+'<img style="width:310px" src="{0}">'.format(str(row['NFTImageLink']['image']))+'</img>'+'</td>'+ '</tr>'
            except:
                try:
                  payload += '<tr>' +'<td>'+str(row['tokenID']) +'</td>'+ '<td>'+str(row['ContractAddress']) +'</td>'+ '<td>'+'<video autoplay loop muted style="width:310px" controls="controls" src="{0}">'.format(str(row['NFTImageLink']['video']))+'</video>'+'</td>'+ '</tr>'
                except:
                  payload += '<tr>' +'<td>'+str(row['tokenID']) +'</td>'+ '<td>'+str(row['ContractAddress']) +'</td>'+'<td>'+'No NFT Found'+'</td>'+ '</tr>'
          
          return render_template('viewnft.html', blockchainaddress=walletaddress,payload=payload)     

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
