from flask import Flask, render_template, abort, redirect, request
import os.path
from keys import OCRkey
from werkzeug.utils import secure_filename
import requests
import json
import urllib

app = Flask(__name__,
    static_url_path='',
    static_folder='.')

OCRurl = 'https://api.ocr.space/parse/image'

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        pages = request.files.getlist('file')
        for page in pages:
            page.save('./uploads/' + secure_filename(page.filename))
            fields = {'language':'jpn', 'apikey' : OCRkey}
            files = {
                'file': open('./uploads/' + secure_filename(page.filename), 'rb')
            }
            response = requests.post(url=OCRurl, data=fields, files=files)
            #print(json.loads(response.json())['ParsedText'])
            lines = response.json()['ParsedResults'][0]['ParsedText'].split('\r\n')
            for line in lines:
                # response2 = requests.get("https://translate.googleapis.com/translate_a/single?client=gtx&sl=ja&tl=en&dt=t&q=" + urllib.parse.quote_plus(line))
                # print(line)
                # print(response2.text)
                print(requests.get("https://translate.googleapis.com/translate_a/single?client=gtx&sl=ja&tl=en&dt=t&ie=UTF-8&q=" + urllib.parse.quote(line)).json()[0][0][0])

        
    else:
        return render_template('format.html')


if __name__ == '__main__':
    app.run(debug=True)
