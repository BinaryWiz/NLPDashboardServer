import requests

while True:
    user_input = input('What would you like to do? (CreateDB, PUTData) ')

    if user_input.lower() == 'createdb':
        requests.put('http://localhost:3000/create_db', json={'model_name': 'priceassist'})

    if user_input.lower() == 'putdata':
        requests.put('http://localhost:3000/add_data', json={'model_name': 'priceassist', 'data': [[1, 1, 0.1, 0.1, 0.1, 0.1], [1, 2, 0.1, 0.1, 0.1, 0.1]]})
