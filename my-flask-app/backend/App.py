from flask import Flask, render_template
import time
from flask import request
import json
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/selection', methods=['POST'])
def selection():
    return {
        'Task': 'selection',
        'Frontend': 'React',
        'Backend': 'Flask'
    }


@app.route('/training', methods=['POST'])
def training():
    model = request.form.get('model')
    dataset = request.form.get('dataset')
    print(model)
    print(dataset)
    return {
        'Task': 'training',
        'Frontend': 'React',
        'Backend': 'Flask'
    }


@app.route('/predict', methods=['POST'])
def predict():

    return {
        'task': 'predict',
        'frontend': 'React',
        'backend': 'Flask',
        'result' : 'success'
    }


@app.route('/evaluation', methods=['GET'])
def evaluation():
    return {
        'Task': 'evaluation',
        'Frontend': 'React',
        'Backend': 'Flask'
    }



if __name__ == '__main__':
    app.run(debug=True)
