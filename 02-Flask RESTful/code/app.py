from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'jose'
api = Api(app)

# /auth
jwt = JWT(app, authenticate, identity)

# list carrying items
items = []

# Defining the resource
class Item(Resource):
    # Parsing the request
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type = float,     # Price only float
        required = True,  # No req without price
        help = "This field cannot be left blank"
    )

    @jwt_required()
    def get(self, name):
        # filter(filter_func, list_of_items)
        # next would give first item found by the list but have to return none if no item found
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'item': item}, 200 if item else 404


    def post(self, name):
        # If found an item so no need to add it just return message
        if next(filter(lambda x: x['name'] == name, items), None):
            return {'message': 'An item with name {} already exists.'.format(name)}, 400

        # If the req doesn't have proper content type, this will trigger error
        # get_json(force,silent)
        # force=True ;dont need content-type header, nice but dangerous
        # silent=True ;dont give error but return none
        # data = request.get_json()  # Without payload
        data = Item.parser.parse_args()
        
        item = {'name': name, 'price': data['price']}
        items.append(item)
        return item, 201

    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': 'Item deleted'}

    def put(self, name):
        # Getting items data
        # data = request.get_json() # without payload
        data = Item.parser.parse_args()  # Parsing args come thru json payload

        # Filtering list for the searched item
        item = next(filter(lambda x: x['name'] == name, items), None)
        # If item not in the list
        if item is None:
            item = {'name': name, 'price': data['price']}
            items.append(item)
        # If item found in the list
        else:
            item.update(data)
        return item



class ItemList(Resource):
    def get(self):
        return {'items': items}



# Adding resource and determine how its going to be access
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

app.run(port=5000, debug=True)
