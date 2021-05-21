import requests

batch = 0
while True:
    user_input = input('What would you like to do? (Create DB, PUT Data, GET Data) ')

    if user_input.lower() == 'create db':
        requests.put('http://localhost:3000/create_db', json={'model_name': 'priceassist'})

    if user_input.lower() == 'put data':
        batch += 1
        requests.put('http://localhost:3000/add_data', json={'model_name': 'priceassist', 'data': [[1, batch, 0.1, 0.1, 0.1, 0.1]]})
    
    if user_input.lower() == 'get data':
        data = requests.get('http://localhost:3000/get_data', params={'model_name': 'priceassist', 'epoch': 1, 'batch': 4})
        print(data.json())