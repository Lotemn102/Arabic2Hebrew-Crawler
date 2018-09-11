'''
A web app based on Flask, that scrapes all news titles from the main page of an arabic news website ('JO24')
every 10 minutes.
The program filters the titles that are relevant to a predefined set of words, and scrapes their full text.
It translates the full texts to hebrew and saves the data to a database and to an excel sheet.
This program requires the user to have PostgreSQL installed, since it saves the data locally.
'''

# -*- coding: utf-8 -*-

import urllib.request
from bs4 import BeautifulSoup
from googletrans import Translator
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time as tm
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse

class Main():
    # Asks for the password for the db.
    # MUST CHANGE TO YOUR PASSWORD IN ORDER TO RUN THE APP.
    pw = 'DB_PASSWORD'

    def __init__(self):
        # Initialize the id.
        self.cur_id = 1

        # Connect to the local postgresql db.
        self.con = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password=" + Main.pw)
        self.cur = self.con.cursor()

        # Checks if table already exists.
        try:
            self.cur.execute("SELECT EXISTS (SELECT * FROM data);")
        # If not, it creates one:
        except (psycopg2.OperationalError, psycopg2.ProgrammingError):
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            # Create the table
            self.cur.execute("CREATE TABLE data (id integer, source text, translation text, time text, url text);")

        # Set start time for 'clock' function later.
        self.starttime = tm.time()

        # initialize on/off button to 'off'.
        self.button = 'off'

    # Function to insert the data into the database.
    def insert(self, id, source, translate, time, url):
        self.cur.execute("INSERT INTO data (id, source, translation, time, url) VALUES(%s, %s, %s, %s, %s)",
            (id, source, translate, time, url))
        self.con.commit()
        return

    # Function for saving the PostgreSql table to an excel sheet.
    # It first takes the data from the db table as a pandas data frame,
    # then it writes it to an excel sheet.
    # Couldn't find easier way that also won't screw up the encoding of the arabic text.
    def save(self):
        path_xl = 'static/files/table.xlsx'
        engine = create_engine('postgresql://postgres:' + Main.pw +'@localhost:5432/postgres')
        df = pd.read_sql_query('select * from data', con=engine)
        writer = pd.ExcelWriter(path_xl)
        df.to_excel(writer, startrow=0, startcol=0)
        writer.save()

    # Function to make the program scrape the website every 10 minutes and save the data.
    def clock(self):
        while self.button == 'on':
            self.scrape_and_translate()
            self.save()
            tm.sleep(600 - ((tm.time() - self.starttime) % 60.0))  # 600 sec = 10 minutes

    # Function to empty the database.
    def delete(self):
        self.cur.execute("DELETE FROM data;")
        self.con.commit()

    # Main function. Scraps the data, filters the relevant news and translates them.
    def scrape_and_translate(self):
        # Specify the url of the main page.
        url = 'https://www.jo24.net/category/%D9%85%D8%AD%D8%A7%D9%81%D8%B8%D8%A7%D8%AA/page/0-0'

        # Set the html to the variable 'page'.
        page = urllib.request.urlopen(url)

        # Parses the html using beautiful soup.
        soup = BeautifulSoup(page, 'html.parser')

        # Set 'news' dictionary to collect all news titles.
        news = {}

        # Making sure the program will save new data after the last row in the 'data' db.
        self.cur.execute('select max(id) from data')
        self.cur_id = self.cur.fetchone()
        if self.cur_id[0] == None:
            self.cur_id = 1
        else:
            self.cur_id = self.cur_id[0] + 1

        # Scrape all titles and links from the main page, save them to the 'news' dictionary.
        for div in soup.find_all('div', attrs={'class': 'content'}):
            a = div.find('a')
            text = a.string
            start = 'https://www.jo24.net/'
            url = div.a.get('href')
            url = url[1:]
            url = urllib.parse.quote(url, safe='')
            link = (start+url)
            news[text] = link

        # Check if the url is already in the data base, to avoid duplications.
        for l in news.keys():
            url = news[l]
            fine_url = urllib.parse.unquote(url)
            self.cur.execute("select exists(select from data where url='%s');" % fine_url)

            # Check if it's a new url.
            if (self.cur.fetchone()) == (False,):
                if self.button == 'on':
                    a = l.split()
                    # Check if title is relevant for the wanted set of words.
                    words_set = ['مسيرة', 'بمسيرة', 'مسيرات', 'احتجاج', 'احتجاجا', 'احتجاجات', 'احتجاجية', 'محتجون',
                                 'محتجين', 'مئات', 'المئات', 'وقفة', 'اعتصام', 'الوقفة', 'الاعتصام', 'المسيرة',
                                 'الاحتجاج', 'اعتصامات', 'معتصمو', 'معتصمي', 'يحتجون', 'المحتجون']
                    for word in words_set:
                        if word in a:
                            # If relevant, searches for the full article url.
                            page = urllib.request.urlopen(url)
                            soup = BeautifulSoup(page, 'html.parser')

                            # Getting the full article text.
                            text = soup.find('div', attrs={'style': 'direction:rtl; text-align:right'}).text

                            # Translates the article from arabic to hebrew.
                            try:
                                translator = Translator()
                                translator = translator.translate(text, src='ar', dest='iw')
                            except:
                                translator = None

                            # Get the date of the article.
                            try:
                                time = soup.find('div', attrs={'class': 'post-date'}).text
                            except:
                                time = None

                            # Writing the data to the database.
                            if text != '':
                                self.insert(self.cur_id, text, translator.text, time, fine_url)
                                self.cur_id = self.cur_id+1
                            else:
                                pass
            else:
                pass
