from flask import Flask, render_template, request
import subprocess
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/analysis')
def analysis():
    try:
        df = pd.read_csv('analysis.csv')
        df.sort_values(by=['MELO'], ascending=False, inplace=True)
        data_table = df.to_html(classes='table', table_id='analysis-table', index=False)
    except Exception as e:
        data_table = f"<p>Error loading analysis: {str(e)}</p>"
    return render_template('analysis.html', table=data_table)

@app.route('/generate-bracket', methods=['GET', 'POST'])
def generate_bracket():
    return render_template('simulate.html')


if __name__ == '__main__':
    app.run(debug=True)
