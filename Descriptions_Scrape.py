import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector as mysql
import logging

def connect_to_db():
    HOST = 'darchiviuku.cluster-ro-ct2brvwy8za8.us-east-1.rds.amazonaws.com'
    DATABASE = "datacollection"
    USER = "admin"
    PASSWORD = 'd5Sj5U7lZqwNYsqRjhJI'
    db_connection = mysql.connect(
        host=HOST, database=DATABASE, user=USER, password=PASSWORD)
    return db_connection

mysql_connection = connect_to_db()
mysql_cursor = mysql_connection.cursor()

# Configure the logging module
logging.basicConfig(filename='website-description-logger.log', level=logging.DEBUG)


df = pd.read_csv("Output.csv")
# df2 = pd.DataFrame()

count = 0
for domain in df['Domain']:
    count+=1
    logging.debug(f"Counter - {count} (Running for {domain}) \n")
    try:
        url = f"https://{domain}"
        response = requests.get(url, verify=False, timeout=10) # Set verify=False to ignore SSL certificate errors
        if response.status_code >= 400:
            url = f"http://{domain}"
            response = requests.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        status = response.status_code
        # find the meta tag with name 'description'
        description_tag = soup.find('meta', attrs={'name': 'description'})
        # check if the tag exists
        if description_tag is not None:
            # get the content attribute value of the tag
            description = description_tag.get('content')
        else:
            description = None
    except Exception as e:
        description = "MESSAGE:"+e
        status = None
        logging.debug(f"Error {e} \n")
    # append the domain and description to the DataFrame
    mysql_cursor.execute(
                'insert into website_descriptions (Domain, Description, Status_Code)  values(%s,%s, %d)', (domain,description, status))
    # df2 = df2.append({'domain': domain, 'description': description, 'Status Code': status}, ignore_index=True)
