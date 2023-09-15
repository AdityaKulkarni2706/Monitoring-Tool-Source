import sqlite3
import requests
import datetime
import webapp
import time



def createTables():
   
    conn = sqlite3.connect('newdb.db')
    cursor = conn.cursor()
    create_websites_query = "CREATE TABLE IF NOT EXISTS websites(id INTEGER PRIMARY KEY, url TEXT NOT NULL)"
    create_metrics_query = "CREATE TABLE IF NOT EXISTS metrics(web_id INTEGER NOT NULL, date TEXT NOT NULL, availability INTEGER NOT NULL, response_time INTEGER NOT NULL)"
    cursor.execute(create_websites_query)
    cursor.execute(create_metrics_query)
    conn.commit()

def insertWebsites(url):
    conn = sqlite3.connect('newdb.db') 
    cursor = conn.cursor()
    
   
    args = (url,)
    insert_query = "INSERT INTO websites(url) VALUES(?)"
        
    cursor.execute(insert_query, args)
    conn.commit()
    conn.close()
    



def getWebsites():
    conn = sqlite3.connect('newdb.db')
    cursor = conn.cursor()
    get_url_query = "SELECT id, url from websites"
    cursor.execute(get_url_query)
    rows = cursor.fetchall()
    websites = []
    for row in rows:
        website= {}
        website["id"] = row[0]
        website['url'] = row[1]
        websites.append(website)
        conn.commit()
    
    return websites
    


def insertMetrics(web_id, date, response_time, availability):
    conn = sqlite3.connect('newdb.db')
    cursor = conn.cursor()
    insert_query = "INSERT INTO metrics(web_id, date, availability, response_time) VALUES(?,?,?,?)"

    to_insert = (web_id, date, availability, response_time)
    
    cursor.execute(insert_query, to_insert)
    conn.commit()
    print()


def monitor():
    websites = getWebsites()
    print(websites)
   
    for website in websites:            #website = {id = .. , url = ...}
        start_time = datetime.datetime.now()
        availability = 0
        
        try : 
            requests.get(website['url'])
            if requests.get(website['url']).status_code == 200:
                availability=1
            
            
            availability = 1
        except:
            availability=0
        
        
        end_time = datetime.datetime.now()
        response_time = int((end_time-start_time).microseconds / 1000)
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        

        # if requests.get(website['url']).status_code == 200:
        #     availability = 1
        # else : 
        #     availability = 0
        print(website['id'], date, response_time, availability)
       
        insertMetrics(website['id'], date, response_time, availability)
    
def Get_Website_Summary():
    conn = sqlite3.connect('newdb.db')
    cursor = conn.cursor()
    
    query = "SELECT websites.id, websites.url, (SELECT availability FROM metrics WHERE web_id = websites.id	ORDER BY DATE DESC LIMIT 1) as availability FROM websites"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    conn.commit()
    conn.close()
    website_summary = []
    for row in rows:
        website = {}
        website['id']=row[0]
        website['url'] = row[1]
        website['availability'] = row[2]
        website_summary.append(website)
    
    return website_summary

def getMetricsForWebsite(id):
    conn = sqlite3.connect('newdb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT web_id, date, availability, response_time FROM metrics WHERE web_id = ?", (id,))
    metrics_ = cursor.fetchall()
    final_metrics = []
    for row in metrics_:
        dict = {}
        dict['id'] = row[0]
        dict['date'] = row[1]
        dict['availability'] = row[2]
        dict['response_time'] = row[3]
        final_metrics.append(dict)
    return final_metrics


    

def getWebsiteById(id):
    conn = sqlite3.connect('newdb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM websites WHERE id=?", (id,))
    url = cursor.fetchall()

    return url[0][0]

def getHourAvailability(id): #####################################
    conn = sqlite3.connect('newdb.db')
    cursor = conn.cursor()

    cursor.execute(" SELECT strftime('%Y-%m-%d %H:00:00', date) AS hour,AVG(availability)*100 AS percent_availability,AVG(response_time) AS avg_response_time FROM metrics WHERE  web_id = ? AND hour >= datetime('now', '-0.5 day') GROUP BY hour", (id,))
    rows = cursor.fetchall()
    hour_avail_array = []
    for row in rows:
        dict = {}
        dict['date'] = row[0]
        dict['availability'] = row[1]
        dict['response_time'] = row[2]
        
        hour_avail_array.append(dict)
    return hour_avail_array
def get24HrMetrics(id):
    conn = sqlite3.connect('newdb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT strftime('%Y-%m-%d %H:00:00', date) AS hour,AVG(availability)*100 AS percent_availability,AVG(response_time) AS avg_response_time FROM metrics WHERE  web_id = ? AND hour >= datetime('now', '-1 day') GROUP BY hour", (id,))
    rows = cursor.fetchall()
    hour_avail_array = []
    for row in rows:
        dict = {}
        dict['date'] = row[0]
        dict['availability'] = row[1]
        dict['response_time'] = row[2]
        
        hour_avail_array.append(dict)
    return hour_avail_array
    
    

if __name__ == "__main__":
     
     while True:
         monitor()
         time.sleep(5)
   

