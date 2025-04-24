from flask import Flask, render_template, request, jsonify, send_file
import MattsMarchMadness
import pandas as pd
import os

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
    try:
        print(f"Request for file: {filename}")

        if filename.endswith('.csv') and filename.startswith('MMM__'):
            # Try to serve from static directory
            filepath = os.path.join('static', filename)
            print(f"Looking for file at: {filepath}")

            if os.path.isfile(filepath):
                print(f"File found, returning: {filepath}")
                return send_file(filepath, as_attachment=False, mimetype='text/csv')
            else:
                print(f"File not found at: {filepath}")
                # Try root directory as fallback
                if os.path.isfile(filename):
                    print(f"File found in root: {filename}")
                    return send_file(filename, as_attachment=False, mimetype='text/csv')

        # Let Flask handle normal static files
        print(f"Delegating to default static file handler")
        return app.send_static_file(filename)
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return f"Error serving file: {str(e)}", 404


if __name__ == '__main__':
    # Use PORT environment variable if available (for Google Cloud)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)