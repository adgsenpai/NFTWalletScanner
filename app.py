from flask import Flask
from flask_graphql import GraphQLView
import graphene
from graphqlbackend import Query
import graphqlbackend as gb
from flask_cors import CORS, cross_origin
import os
import dblayer as db




view_func = GraphQLView.as_view('graphql', schema=graphene.Schema(query=Query), graphiql=True)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.add_url_rule('/graphql', view_func=view_func)
 
@app.route('/')
def home():
    return str(gb.get_address("0xf56345338cb4cddaf915ebef3bfde63e70fe3053"))
 
if __name__ == '__main__':
    app.run(host='0.0.0.0')
                                    #contract address
#https://api.opensea.io/api/v1/asset/0x026dce20bf77e08ca8aceb6b239cc54bb9d638ac/1/?format=json&include_orders=true