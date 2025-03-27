from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    # Run a Python file (e.g., "example.py")
    try:
        result = subprocess.run(['python', 'MattsMarchMadness.py'], capture_output=True, text=True)
        output = result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        output = f"Error occurred: {str(e)}"
    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)
