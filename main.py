'''
A web app based on Flask, that scrapes all news titles from the main page of an arabic news website ('JO24')
every 10 minutes.
The program filters the titles that are relevant to a predefined set of words, and scrapes their full text.
It translates the full texts to hebrew and saves the data to a database and to an excel sheet.
This program requires the user to have PostgreSQL installed, since it saves the data locally.
'''

from flask import Flask, render_template
from crawler import Main

app = Flask(__name__)
m = Main()

@app.route('/')
@app.route('/templates/main_jo24.html')
def index(name=None):
    cur_id = m.cur_id
    return render_template('main_jo24.html', name=name, cur_id=cur_id)

@app.route('/start', methods=['GET', 'POST'])
def start():
    try:
        m.button = 'on'
        # Call the function that starts the page scraping.
        m.clock()
    except:
        pass
    return '', 204

@app.route('/stop', methods=['GET', 'POST'])
def stop():
    m.button = 'off'
    return '', 204

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    m.button = 'off'
    # Call the function that deletes tha db.
    m.delete()
    return '', 204

if __name__ == "__main__":
    app.run(threaded=True)
