from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
