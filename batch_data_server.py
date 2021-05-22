import sqlite3
import os
from typing import Dict, Tuple, List
from flask import Flask, request
from flask_cors import cross_origin
from helpers.error_tracking import print_unk_error
from helpers.helper_functions import chunk_list

DATABASE_PATH = 'databases/'

app = Flask(__name__)
BATCH_DATABASE_COLUMNS = 'Epoch INTEGER, Batch INTEGER, Accuracy REAL, Loss REAL, RunningAccuracy REAL, RunningLoss REAL'
EXAMPLES_DATABASE_COLUMNS = 'Epoch INTEGER, Batch INTEGER, Title1 TEXT, Title2 TEXT, SoftmaxPos REAL, SoftmaxNeg REAL, Prediction INTEGER, Label INTEGER'
BATCH_TABLE = 'batch_data'
EXAMPLES_TABLE = 'examples_data'

@app.route('/create_db', methods=['PUT'])
@cross_origin()
def create_database() -> Tuple[Dict, int]:
    '''
    Create a new database given the model's name
    '''
    try:
        model_name: str = request.json['model_name'].lower()
        
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

        return {'success': True}, 201

    except sqlite3.OperationalError as e:
        print('Message: {}'.format(str(e)))
        print('Database most likely already exists.')
        
        # Return 409 state-conflict error
        return {'success': False}, 409

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

@app.route('/delete_db', methods=['DELETE'])
@cross_origin()
def delete_batch_db() -> Tuple[Dict, int]:
    model_name: str = request.json['model_name'].lower()
    db_path: str = '{}/{}.db'.format(DATABASE_PATH, model_name)
    if os.path.exists(db_path):
        os.remove(db_path)
        return {'success': True}, 200
    else:
        return {'success': False, 'message': 'Database does not exist'}, 404

@app.route('/add_batch_data', methods=['PUT'])
@cross_origin()
def add_batch_data() -> Tuple[Dict, int]:
    '''
    Add rows of data from training to the database
    '''
    model_name: str = request.json['model_name'].lower()
    batch_stats: List[List[int, int, float, float, float, float]] = request.json['data']
    try:
        # Open connection to the database
        conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
        cur = conn.cursor()
        
        # Insert the values into the database
        for batch_stat in batch_stats:
            cur.execute(''' INSERT into {} values ({}, {}, {}, {}, {}, {}) '''.format(BATCH_TABLE, *batch_stat))
        
        # Save the changes
        conn.commit()
        cur.close()
        conn.close()

        return {'success': True}, 201

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
        # Open connection to database
        conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
        cur = conn.cursor()

        # Get all the rows that would be new data for the front-end
        cur.execute('SELECT * from {} WHERE Epoch > {} OR (Epoch == {} AND Batch > {})'.format(BATCH_TABLE, epoch, epoch, batch))
        rows: List[List[int, int, float, float, float]] = cur.fetchall()

        # Close the connections
        cur.close()
        conn.close()
        
        return {'data': rows, 'success': True}, 200

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

@app.route('/add_examples_data', methods=['PUT'])
@cross_origin()
def add_examples() -> Tuple[Dict, int]:
    '''
    Add example data
    '''
    model_name: str = request.json['model_name'].lower()
    batches: List[List[int, int, str, str, float, float, int, int]] = request.json['data']
    try:
        # Open connection to the database
        conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
        cur = conn.cursor()
        
        # Insert the values into the database
        for batch in batches:
            for example in batch:
                cur.execute(''' INSERT into {} values ({}, {}, "{}", "{}", {}, {}, {}, {}) '''.format(EXAMPLES_TABLE, *example))
        
        # Save the changes
        conn.commit()
        cur.close()
        conn.close()

        return {'success': True}, 201

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

@app.route('/get_examples_data', methods=['GET'])
@cross_origin()
def get_examples() -> Tuple[Dict, int]:
    model_name: str = request.args.get('model_name')
    epoch: int = int(request.args.get('epoch'))
    batch: int = int(request.args.get('batch'))
    batch_size: int = int(request.args.get('batch_size'))
    try:
        # Open connection to database
        conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
        cur = conn.cursor()

        # Get all the rows that would be new data for the front-end
        cur.execute('SELECT * from {} WHERE Epoch > {} OR (Epoch == {} AND Batch > {})'.format(EXAMPLES_TABLE, epoch, epoch, batch))
        rows: List[List[int, int, str, str, float, float, int, int]] = cur.fetchall()
        
        # Divide the rows into the batches
        rows = chunk_list(rows, batch_size)

        # Close the connections
        cur.close()
        conn.close()
        
        return {'data': rows, 'success': True}, 200

    except Exception as e:
        print_unk_error(e)
        return {'success': False}, 400

if __name__ == '__main__':
    app.run('localhost', port=3000, debug=True)
