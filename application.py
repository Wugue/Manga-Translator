from flask import Flask, render_template, abort, redirect, request, after_this_request
import os.path
from keys import OCRkey
from werkzeug.utils import secure_filename
import requests
import json
import urllib
import shutil

application = Flask(__name__,
    static_url_path='',
    static_folder='.')

OCRurl = 'https://api.ocr.space/parse/image'
size = 0

def sortLeft(array):
    result = []
    if len(array) < 2:
        return array
    i = int(len(array)/2)
    l = sortLeft(array[:i])
    r = sortLeft(array[i:])
    while (len(l) > 0) or (len(r) > 0):
        if len(l) == 0:
            result = result + r
            break
        elif len(r) == 0:
            result = result + l
            break
        elif r[0][1] < l[0][1]:
            result.append(l[0])
            l.pop(0)
        else:
            result.append(r[0])
            r.pop(0)
    return result

def sortTop(array):
    result = []
    if len(array) < 2:
        return array
    i = int(len(array)/2)
    l = sortTop(array[:i])
    r = sortTop(array[i:])
    while (len(l) > 0) or (len(r) > 0):
        if len(l) == 0:
            result = result + r
            break
        elif len(r) == 0:
            result = result + l
            break
        elif r[0][0] > l[0][0] or (abs(r[0][0] - l[0][0]) < 175 and r[0][1] < l[0][1]):
            result.append(l[0])
            l.pop(0)
        else:
            result.append(r[0])
            r.pop(0)
    return result

@application.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        global size
        if size > 5000:
            shutil.rmtree('./uploads/')
            os.mkdir('./uploads/')
            size = 0
        data = []
        pages = request.files.getlist('file')
        for page in pages:
            pageName = str(size) + '_' + secure_filename(page.filename)
            if not (pageName.endswith('.png') or pageName.endswith('.jpg') or pageName.endswith('.pdf')):
                continue
            pageData = []
            size += 1
            page.save('./uploads/' + pageName)
            fields = {'language':'jpn', 'apikey' : OCRkey, 'isOverlayRequired' : True}
            files = {
                'file': open('./uploads/' + pageName, 'rb')
            }
            response = requests.post(url=OCRurl, data=fields, files=files)
            #print(response.json()['ParsedResults'][0]['TextOverlay']['Lines'])
            entries = response.json()['ParsedResults'][0]['TextOverlay']['Lines']
            linesPosition = []
            for entry in entries:
                entryLine = ''
                if entry['MaxHeight'] < 15:
                    continue;
                if len(entry['Words']) > 1 and  (entry['Words'][0]['Top'] + 15 > entry['Words'][1]['Top'] or entry['Words'][0]['Left'] + 15 < entry['Words'][1]['Left']):
                    continue
                for word in entry['Words']:
                    if word['WordText'] == ':':
                        entryLine += '...'
                    else:
                        entryLine += word['WordText']
                linesPosition.append((entry['Words'][0]['Top'], entry['Words'][0]['Left'], entryLine))
            linesPosition = sortLeft(linesPosition)
            linesTop = []
            while linesPosition:
                current = linesPosition.pop(0)
                temp = linesPosition.copy()
                for line in temp:
                    if current[1] - 80 < line[1] and abs(current[0] - line[0]) < 70:
                        current = (line[0], line[1], current[2] + line[2])
                        linesPosition.remove(line)
                linesTop.append((current[0], current[1], current[2]))
            linesTop = sortTop(linesTop)




            #return render_template('format.html')
            #lines = response.json()['ParsedResults'][0]['ParsedText'].split('\r\n')
            for line in linesTop:
                #pageData.append(line[2])
                pageData.append((line[2], requests.get("https://translate.googleapis.com/translate_a/single?client=gtx&sl=ja&tl=en&dt=t&ie=UTF-8&q=" + urllib.parse.quote(line[2])).json()[0][0][0]))
            data.append(('./uploads/' + pageName, pageData))

        return render_template('home.html', lst=data)

        
    else:
        return render_template('guide.html')


if __name__ == '__main__':
    application.run(debug=False)

    #{'MinTop': 28.0, 'Words': [{'Height': 82.0, 'WordText': 'の', 'Top': 28.0, 'Width': 79.0, 'Left': 103.0}, {'Height': 48.0, 'WordText': 'ん', 'Top': 56.0, 'Width': 45.0, 'Left': 175.0}], 'MaxHeight': 82.0},
