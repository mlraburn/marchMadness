from flask import Flask, render_template, request, jsonify
import MattsMarchMadness
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


@app.route('/simulate-bracket', methods=['POST'])
def simulate_bracket():
    try:
        # Call the new function to generate a bracket
        generated_file = MattsMarchMadness.generate_web_bracket()

        # Return the result as JSON
        return jsonify({
            'status': 'success',
            'filename': generated_file,
            'message': 'Bracket simulation completed successfully!'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/static/<path:filename>')
def serve_file(filename):
    """Serve generated CSV files"""
    if filename.endswith('.csv') and filename.startswith('MMM__'):
        # Check if file exists in root directory
        if os.path.isfile(filename):
            return send_file(filename, as_attachment=False)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
