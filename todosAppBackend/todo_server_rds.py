# Import Flask modules
from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

# Create an object named app with CORS
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Configure sqlite database
fo = open("config.txt", "r")
db_uri = fo.readline().strip()
db_pw = fo.readline().strip()

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://todos_user:{db_pw}@{db_uri}/todos_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# get all todos
def get_all_todos():
    query = """
    SELECT * FROM todos;
    """
    result = db.session.execute(query)
    todos = [{'task_id': row[0], 'title':row[1], 'description':row[2],
              'is_done': row[3]} for row in result]
    return todos

# query a todo by task_id
def find_todo(task_id):
    query = f"""
    SELECT * FROM todos WHERE task_id={task_id};
    """

    row = db.session.execute(query).first()
    todo = None
    if row is not None:
        todo = {'task_id': row[0], 'title': row[1],
                'description': row[2], 'is_done': row[3]}
    return todo

# create a todo in db
def insert_todo(title, description):
    insert = f"""
    INSERT INTO todos (title, description)
    VALUES ('{title}', '{description}');
    """
    result = db.session.execute(insert)
    db.session.commit()

    query = f"""
    SELECT * FROM todos WHERE task_id={result.lastrowid};
    """
    row = db.session.execute(query).first()
    return {'task_id': row[0], 'title': row[1], 'description': row[2], 'is_done': row[3]}

# update a todo in db
def change_todo(todo):
    update = f"""
    UPDATE todos
    SET title='{todo['title']}', description = '{todo['description']}', is_done = {todo['is_done']}
    WHERE task_id= {todo['task_id']};
    """

    result = db.session.execute(update)
    db.session.commit()

    query = f"""
    SELECT * FROM todos WHERE task_id={todo['task_id']};
    """
    row = db.session.execute(query).first()
    return {'task_id': row[0], 'title': row[1], 'description': row[2], 'is_done': row[3]}

# remove todo from db
def remove_todo(todo):
    delete = f"""
    DELETE FROM todos
    WHERE task_id= {todo['task_id']};
    """

    result = db.session.execute(delete)
    db.session.commit()

    query = f"""
    SELECT * FROM todos WHERE task_id={todo['task_id']};
    """
    row = db.session.execute(query).first()
    return True if row is None else False

# root
@app.route('/')
def home():
    return "Welcome to Hakan's To Do API Service"

# retrieve all todos
@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify({'todos': get_all_todos()})

# get one todo
@app.route('/todos/<int:task_id>', methods=['GET'])
def get_todo(task_id):
    todo = find_todo(task_id)
    if todo == None:
        abort(404)
    todo['is_done'] = ['false', 'true'][int(todo['is_done'])]
    return jsonify({'todo found': todo})

# create a todo
@app.route('/todos', methods=['POST'])
def add_todo():
    if not request.json or not 'title' in request.json:
        abort(400)
    return jsonify({'newly added todo': insert_todo(request.json['title'], request.json.get('description', ''))}), 201

# update a todo
@app.route('/todos/<int:task_id>', methods=['PUT'])
def update_todo(task_id):
    todo = find_todo(task_id)
    if todo == None:
        print('cant find todo')
        abort(404)
    if not request.json:
        print('no data')
        abort(400)
    if 'is_done' in request.json:
        if request.json['is_done'].lower() not in ['true', 'false', '1', '0']:
            print('smth wrong with is done:', request.json['is_done'])
            abort(400)
        else:
            print('no is done')
            values = {'true': 1, 'false': 0, '1': 1, '0': 0}
            todo['is_done'] = values[request.json['is_done'].lower()]

    todo['title'] = request.json.get('title', todo['title'])
    todo['description'] = request.json.get('description', todo['description'])
    todo['is_done'] = request.json.get('is_done', todo['is_done'])
    return jsonify({'updated todo': change_todo(todo)})

# delete a todo
@app.route('/todos/<int:task_id>', methods=['DELETE'])
def delete_todo(task_id):
    todo = find_todo(task_id)
    if todo == None:
        abort(404)
    return jsonify({'result': remove_todo(todo)})


# run flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)