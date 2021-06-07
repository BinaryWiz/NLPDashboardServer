import sqlite3
import os
from typing import Dict, Tuple, List
from flask import Flask, request
from flask_cors import cross_origin
from helpers.error_tracking import print_unk_error
from helpers.helper_functions import chunk_list

DATABASE_PATH = 'databases/'

# Create the path for database files
if not os.path.exists(DATABASE_PATH):
    os.makedirs(DATABASE_PATH)

app = Flask(__name__)
BATCH_DATABASE_COLUMNS = 'Epoch INTEGER, Batch INTEGER, Accuracy REAL, Loss REAL, RunningAccuracy REAL, RunningLoss REAL'
EXAMPLES_DATABASE_COLUMNS = 'Epoch INTEGER, Batch INTEGER, Title1 TEXT, Title2 TEXT, SoftmaxPos REAL, SoftmaxNeg REAL, Prediction INTEGER, Label INTEGER'
BATCH_TABLE = 'batch_data'
EXAMPLES_TABLE = 'examples_data'
MODEL_NAMES_FILE = 'models_saved.txt'

@app.route('/create_db', methods=['POST'])
@cross_origin()
def create_database() -> Tuple[Dict, int]:
    '''
    Create a new database given the model's name
    '''

    try:
        model_name: str = request.json['model_name']
        if not os.path.exists('{}/{}.db'.format(DATABASE_PATH, model_name)):
            # Open connection to databse
            conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))

            # Use a cursor to create the database
            cur = conn.cursor()
            cur.execute('''CREATE TABLE {} ({})'''.format(BATCH_TABLE, BATCH_DATABASE_COLUMNS))
            cur.execute('''CREATE TABLE {} ({})'''.format(EXAMPLES_TABLE, EXAMPLES_DATABASE_COLUMNS))

            # Save changes and close connection
            conn.commit()
            cur.close()
            conn.close()

            # Add the model name to the list of models
            with open('{}/{}'.format(DATABASE_PATH, MODEL_NAMES_FILE), 'a') as model_names_file:
                model_names_file.write(model_name + '\n')                

            return {'success': True}, 201
        else:
            return {'success': False}, 409

    except sqlite3.OperationalError as e:
        print('Message: {}'.format(str(e)))

        # Return 409 state-conflict error
        return {'success': False}, 409

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

@app.route('/get_avail_models', methods=['GET'])
@cross_origin()
def get_available_models() -> Tuple[Dict, int]:
    '''
    Return a list of available models to view in dashboard
    '''

    # Get the list of model names from the server
    with open('{}/{}'.format(DATABASE_PATH, MODEL_NAMES_FILE), 'r') as model_names_file:
        model_names: List[str] = model_names_file.readlines()
        model_names = [model.strip() for model in model_names]
    
    return {'success': True, 'data': model_names}, 200

@app.route('/delete_db', methods=['DELETE'])
@cross_origin()
def delete_batch_db() -> Tuple[Dict, int]:
    '''
    Deletes a database based on the name
    '''

    model_name: str = request.json['model_name']
    db_path: str = '{}/{}.db'.format(DATABASE_PATH, model_name)
    if os.path.exists(db_path):
        # Delete the db file
        os.remove(db_path)
        
        # Open the file and delete the model name from the list of available models
        with open('{}/{}'.format(DATABASE_PATH, MODEL_NAMES_FILE), 'r+') as model_names_file:
            model_names = model_names_file.readlines()
            model_names.remove(model_name + '\n')
            model_names_file.truncate(0)
            model_names_file.seek(0)
            for model in model_names:
                model_names_file.write(model)
        
        return {'success': True}, 200
    else:
        return {'success': False, 'message': 'Database does not exist'}, 404

@app.route('/add_batch_data', methods=['PUT'])
@cross_origin()
def add_batch_data() -> Tuple[Dict, int]:
    '''
    Add rows of data from training to the database
    '''

    model_name: str = request.json['model_name']
    batch_stats: List[Dict[int, int, float, float, float, float]] = request.json['data']
    try:
        if os.path.exists('{}/{}.db'.format(DATABASE_PATH, model_name)):
            # Open connection to the database
            conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
            cur = conn.cursor()
            
            # Insert the values into the database
            for batch_stat in batch_stats:
                cur.execute(''' INSERT into {} values (?, ?, ?, ?, ?, ?) '''.format(BATCH_TABLE),
                ([batch_stat['epoch'], batch_stat['batch'], batch_stat['accuracy'], batch_stat['loss'], batch_stat['runningAccuracy'], batch_stat['runningLoss']]))
            
            # Save the changes
            conn.commit()
            cur.close()
            conn.close()

            return {'success': True}, 201
        else:
            return {'success': False}, 404

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

@app.route('/get_batch_data', methods=['GET'])
@cross_origin()
def get_batch_data() -> Tuple[Dict, int]:
    '''
    Returns specific rows of the batch data database given the last point 
    '''

    model_name: str = request.args.get('model_name')
    epoch: int = request.args.get('epoch')
    batch: int = request.args.get('batch')
    try:
        if os.path.exists('{}/{}.db'.format(DATABASE_PATH, model_name)):
            # Open connection to database
            conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
            cur = conn.cursor()

            # Get all the rows that would be new data for the front-end
            cur.execute('SELECT * from {} WHERE Epoch > {} OR (Epoch == {} AND Batch > {})'.format(BATCH_TABLE, epoch, epoch, batch))
            rows: List[List[int, int, float, float, float]] = cur.fetchall()
            labels: List[str, str, str, str, str, str] = ['epoch', 'batch', 'accuracy', 'loss', 'runningAccuracy', 'runningLoss']
            dict_rows = []
            for row in rows:
                dict_rows.append(dict(zip(labels, row)))

            # Close the connections
            cur.close()
            conn.close()
            
            return {'data': dict_rows, 'success': True}, 200
        else:
            return {'success': False}, 404

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

@app.route('/add_examples_data', methods=['PUT'])
@cross_origin()
def add_examples() -> Tuple[Dict, int]:
    '''
    Add example data
    '''

    model_name: str = request.json['model_name']
    batches: List[Dict[int, int, str, str, float, float, int, int]] = request.json['data']
    try:
        if os.path.exists('{}/{}.db'.format(DATABASE_PATH, model_name)):
            # Open connection to the database
            conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
            cur = conn.cursor()
            
            # Insert the values into the database
            for batch in batches:
                for example in batch:
                    cur.execute(''' INSERT into {} values (?, ?, ?, ?, ?, ?, ?, ?) '''.format(EXAMPLES_TABLE),
                    ([example['epoch'], example['batch'], example['title1'],
                    example['title2'], example['positivePercentage'], example['negativePercentage'], example['modelPrediction'], example['label']]))
            
            # Save the changes
            conn.commit()
            cur.close()
            conn.close()

            return {'success': True}, 201
        else:
            return {'success': False}, 404

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

@app.route('/get_examples_data', methods=['GET'])
@cross_origin()
def get_examples() -> Tuple[Dict, int]:
    '''
    Returns example data for a particular batch
    '''

    model_name: str = request.args.get('model_name')
    epoch: int = int(request.args.get('epoch'))
    batch: int = int(request.args.get('batch'))
    try:
        if os.path.exists('{}/{}.db'.format(DATABASE_PATH, model_name)):
            # Open connection to database
            conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
            cur = conn.cursor()

            # Get the batch data at the particular epoch and batch
            cur.execute('SELECT * from {} WHERE Epoch = {} AND Batch = {}'.format(EXAMPLES_TABLE, epoch, batch))
            rows: List[List[int, int, str, str, float, float, int, int]] = cur.fetchall()
            labels: List[str, str, str, str, str, str, str, str] = ['epoch', 'batch', 'title1', 'title2', 'positivePercentage',
                                                                    'negativePercentage', 'modelPrediction', 'label']
            dict_rows = []
            for row in rows:
                dict_rows.append(dict(zip(labels, row)))

            # Close the connections
            cur.close()
            conn.close()
            
            return {'data': dict_rows, 'success': True}, 200
        else:
            return {'success': False}, 404

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

if __name__ == '__main__':
    app.run('localhost', port=3000, debug=True)
