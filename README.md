# Arabic2Hebrew-Crawler

A web app based on Flask, that scrapes all news titles from the main page of an Arabic news website (['JO24'](https://www.jo24.net/))
every 10 minutes.
The program filters the titles that are relevant to a predefined set of words, and scrapes their full text.
It translates the full texts to Hebrew and saves the data to a database and to an excel sheet.
This program requires the user to have PostgreSQL installed, since it saves the data locally.
I've created this projects for my studies.

### Requierments

- [PostgresSQL](https://www.postgresql.org/download/)
- The following modules:

```
psycopg2==2.7.4
googletrans==2.2.0
Flask==0.12.2
SQLAlchemy==1.2.6
beautifulsoup4==4.6.3
pandas==0.23.4
```

## Built With

* [Flask](http://flask.pocoo.org/) 
* [PostgreSQL](https://www.postgresql.org) 
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## Authors

* **Lotem Nadir** 

