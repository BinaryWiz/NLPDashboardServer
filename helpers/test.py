import requests

batch = 0
while True:
    user_input = input('What would you like to do? (Create Batch DB, PUT Batch Data, GET Batch Data, Delete Batch DB) ')

    if user_input.lower() == 'create batch db':
        model_name = input('What would you like the model name to be? ')
        requests.put('http://localhost:3000/create_batch_db', json={'model_name': model_name})

    if user_input.lower() == 'put batch data':
        batch += 1
        requests.put('http://localhost:3000/add_batch_data', json={'model_name': 'priceassist', 'data': [[1, batch, 0.1, 0.1, 0.1, 0.1]]})
    
    if user_input.lower() == 'get batch data':
        data = requests.get('http://localhost:3000/get_batch_data', params={'model_name': 'priceassist', 'epoch': 1, 'batch': 4})
        print(data.json())

    if user_input.lower() == 'delete batch db':
        model_name = input('What model database would you like to delete? ')
        data = requests.delete('http://localhost:3000/delete_batch_db', json={'model_name': model_name})
        print(data.json())