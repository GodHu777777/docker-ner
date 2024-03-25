from flask import Flask, render_template
import time

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/selection', methods=['GET'])
def selection():
    return {
        'Task': 'selection',
        'Frontend': 'React',
        'Backend': 'Flask'
    }


@app.route('/predict', methods=['GET'])
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


@app.route('/training', methods=['GET'])
def training():
    return {
        'Task': 'training',
        'Frontend': 'React',
        'Backend': 'Flask'
    }


if __name__ == '__main__':
    app.run(debug=True)
