import logging

from flask import Flask, render_template, request, jsonify, send_file
import MattsMarchMadness
import pandas as pd
import os
from google.cloud import storage
import tempfile
import logging

BUCKET_NAME = "march-madness-bucket"
LIVE_BRACKET_FILENAME = "mens-live.csv"
PROJECT_ID = "march-madness-457809"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Ensure static directory exists
os.makedirs('static', exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('simulate.html')


@app.route('/analysis')
def analysis():
    try:
        df = pd.read_csv('analysis.csv')
        df.sort_values(by=['MELO'], ascending=False, inplace=True)
        data_table = df.to_html(classes='table', table_id='analysis-table', index=False)
    except Exception as e:
        data_table = f"<p>Error loading analysis: {str(e)}</p>"
    return render_template('analysis.html', table=data_table)


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


@app.route('/static/mens-live.csv')
def serve_live_bracket():
    """
    Endpoint to serve the mens-live.csv file from Google Cloud Storage
    This makes the file appear as if it's in the /static directory
    """
    try:
        logger.info("Attempting to serve mens-live.csv from Google Cloud Storage")

        # Get the file content from GCS
        content = get_live_bracket_from_gcs()

        if content is None:
            logger.info("Unable to retrieve mens-live.csv from Google Cloud Storage")
            return "Error: Unable to retrieve live bracket", 500

        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.csv')
        with os.fdopen(fd, 'w') as f:
            f.write(content)

        # Send the temporary file
        logger.info(f"Serving live bracket from Google Cloud Storage in temp folder: {temp_path}")
        return send_file(
            temp_path,
            as_attachment=False,
            download_name=LIVE_BRACKET_FILENAME,
            mimetype='text/csv'
        )
    except Exception as e:
        logger.info(f"Unable to serve live bracket from Google Cloud Storage: {str(e)}")
        return f"Error serving live bracket: {str(e)}", 500

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


def get_live_bracket_from_gcs():
    """
    Retrieves the mens-live.csv file from Google Cloud Storage
    Returns the file content as a string
    """
    try:
        # Create a client with explicit project ID
        logger.info(f"Creating storage client with project ID: {PROJECT_ID}")
        storage_client = storage.Client(project=PROJECT_ID)

        # Get the bucket
        logger.info(f"Accessing bucket: {BUCKET_NAME}")
        bucket = storage_client.bucket(BUCKET_NAME)

        # Get the blob (file)
        logger.info(f"Retrieving file: {LIVE_BRACKET_FILENAME}")
        blob = bucket.blob(LIVE_BRACKET_FILENAME)

        # Download the file content as a string
        content = blob.download_as_string().decode('utf-8')
        logger.info("Successfully retrieved content from GCS")

        return content
    except Exception as e:
        logger.error(f"Error retrieving live bracket from GCS: {str(e)}")

        # Check for common authentication issues
        if "credentials" in str(e).lower():
            logger.error("""
            Authentication error detected. Please make sure you have set up Application Default Credentials:
            1. Run 'gcloud auth application-default login' in your terminal
            2. Or set GOOGLE_APPLICATION_CREDENTIALS environment variable to point to a service account key file
            """)

            # Check if running locally
            if os.environ.get('K_SERVICE') is None:  # K_SERVICE is set in Cloud Run
                logger.error("""
                It appears you're running in a local development environment.
                Please authenticate with 'gcloud auth application-default login'
                """)

        # Fallback: Try to use a local file if it exists
        try:
            local_path = os.path.join('static', LIVE_BRACKET_FILENAME)
            if os.path.exists(local_path):
                logger.info(f"Falling back to local file: {local_path}")
                with open(local_path, 'r') as f:
                    return f.read()
            else:
                logger.warning(f"Local fallback file not found at: {local_path}")
        except Exception as local_error:
            logger.error(f"Failed to load local fallback file: {str(local_error)}")

        return None


def download_live_bracket_to_temp():
    """
    Downloads the mens-live.csv file from Cloud Storage to a temporary file
    Returns the path to the temporary file
    """
    try:
        # Create a client with explicit project ID
        storage_client = storage.Client(project=PROJECT_ID)

        # Get the bucket
        bucket = storage_client.bucket(BUCKET_NAME)

        # Get the blob (file)
        blob = bucket.blob(LIVE_BRACKET_FILENAME)

        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)

        # Download the blob to the temporary file
        blob.download_to_filename(temp_path)
        logger.info(f"File downloaded to temporary location: {temp_path}")

        return temp_path
    except Exception as e:
        logger.error(f"Error downloading live bracket to temp file: {str(e)}")

        # Fallback: Try to use a local file if it exists
        try:
            local_path = os.path.join('static', LIVE_BRACKET_FILENAME)
            if os.path.exists(local_path):
                logger.info(f"Copying local file to temp: {local_path}")
                fd, temp_path = tempfile.mkstemp(suffix='.csv')
                os.close(fd)
                with open(local_path, 'r') as src, open(temp_path, 'w') as dst:
                    dst.write(src.read())
                return temp_path
            else:
                logger.warning(f"Local fallback file not found at: {local_path}")
        except Exception as local_error:
            logger.error(f"Failed to copy local fallback file: {str(local_error)}")

        return None

if __name__ == '__main__':
    # Use PORT environment variable if available (for Google Cloud)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)