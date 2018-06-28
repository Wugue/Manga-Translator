from flask import Flask, render_template, abort, redirect, request
import os.path
app = Flask(__name__,
    static_url_path='',
    static_folder='.')

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        tree = 3
    else:
        return render_template('format.html')


if __name__ == '__main__':
    app.run(debug=True)
