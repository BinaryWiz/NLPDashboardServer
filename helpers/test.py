import requests

batch = 0
while True:
    user_input = input('What would you like to do? (Create DB, PUT Batch Data, GET Batch Data, Delete DB) ')

    if user_input.lower() == 'create db':
        model_name = input('What would you like the model name to be? ')
        requests.put('http://localhost:3000/create_db', json={'model_name': model_name})

    if user_input.lower() == 'delete db':
        model_name = input('What model database would you like to delete? ')
        response = requests.delete('http://localhost:3000/delete_db', json={'model_name': model_name})
        print(response.json())

    if user_input.lower() == 'put batch data':
        batch += 1
        requests.put('http://localhost:3000/add_batch_data', json={'model_name': 'priceassist', 'data': [[1, batch, 0.1, 0.1, 0.1, 0.1]]})
    
    if user_input.lower() == 'get batch data':
        response = requests.get('http://localhost:3000/get_batch_data', params={'model_name': 'priceassist', 'epoch': 1, 'batch': 4})
        print(response.json())

    if user_input.lower() == 'put examples data':
        data = [
            [[1, 1, 'Title 1', 'Title 2', 0.75, 0.25, 1, 1]] * 32,
            [[1, 2, 'Title 1', 'Title 2', 0.4, 0.6, 0, 1]] * 32,
            [[1, 3, 'Title 1', 'Title 2', 0.7, 0.3, 1, 0]] * 32,
            [[1, 4, 'Title 1', 'Title 2', 0.2, 0.8, 0, 0]] * 32
        ]
        response = requests.put('http://localhost:3000/add_examples_data', json={'model_name': 'priceassist', 'data': data})
        print(response.json())

    if user_input.lower() == 'get examples data':
        response = requests.get('http://localhost:3000/get_examples_data', params={'model_name': 'priceassist', 'epoch': 1, 'batch': 2})
        print(response.json())