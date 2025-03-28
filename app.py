from flask import Flask, render_template, request
import subprocess
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    output = ""
    if request.method == 'POST':
        # Get user input from the form
        user_input = request.form.get('user_input')

        # Pass the user input to your Python file
        try:
            result = subprocess.run(
                ['python', 'MattsMarchMadness.py', user_input],  # Pass input as a command-line argument
                capture_output=True,
                text=True
            )
            output = result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            output = f"Error occurred: {str(e)}"

    return render_template('index.html', output=output)


@app.route('/analysis')
def analysis():
    # Load CSV data using pandas
    try:
        df = pd.read_csv('analysis.csv')
        # Convert the dataframe to an HTML table
        data_table = df.to_html(classes='table table-striped', index=False)
    except Exception as e:
        data_table = f"<p>Error loading analysis: {str(e)}</p>"

    # Render the analysis page with the table
    return render_template('analysis.html', table=data_table)

if __name__ == '__main__':
    app.run(debug=True)
