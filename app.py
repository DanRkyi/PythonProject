import os
import chardet
from flask import Flask, request, render_template, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import pygal
import pandas as pd

ALLOWED_EXTENTIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS

def get_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def check_data_integrity(file_path):

    encoding = get_encoding(file_path)

    data = pd.read_csv(file_path, delimiter=';', encoding=encoding)

    # Ожидаемые столбцы
    expected_columns = ['Title', 'Year', 'Director']

    for column in expected_columns:
        if column not in data.columns:
            return False

    # Если все ожидаемые столбцы присутствуют True
    return True

def create_app():
    app = Flask(__name__)
    last_valid_data = None

    @app.route('/', methods=['GET', 'POST'])
    def upload():
        global last_valid_data
        movies = []
        chart = None
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                new_filename = f'{filename.split(".")[0]}_{str(datetime.now().year)}.csv'
                save_location = os.path.join('input', new_filename)
                file.save(save_location)

                if check_data_integrity(save_location):
                    lines = open('input/' + new_filename, 'r').readlines()
                    for i in lines:
                        x = i.strip().split(';')
                        if (x[6] == 'Bergman, Ingmar'):
                            movies.append({'Title': x[2], 'Year': x[0]})

                    if movies:
                        pie_chart = pygal.Pie()
                        pie_chart.title = 'Movies Directed by Ingmar Bergman'
                        for movie in movies:
                            pie_chart.add(movie['Title'], int(movie['Year']))

                        chart = pie_chart.render_data_uri()
                        last_valid_data = (movies, chart)
                else:
                    if last_valid_data is not None:
                        movies, chart = last_valid_data
                    else:
                        flash('Uploaded file is not valid and no previous valid data available.')

        return render_template('index.html', movies=movies, chart=chart)

    return app

app = create_app()

