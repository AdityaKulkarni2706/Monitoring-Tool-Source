from flask import Flask, render_template, request, redirect, Response, make_response
import newmachine
import sqlite3
import json
import credential_checker
import random
import hashlib


app = Flask(__name__)

@app.route('/signup', methods = ['GET', 'POST'])
def SignUp():
    if request.method == 'GET':
        return render_template('registerpage.html')
    else :
        
        username = request.form['username']

        sha256 = hashlib.sha256()
       
        password = (request.form['password']).encode()
        sha256.update(password)
        password_hash = sha256.hexdigest()

        

        
        credential_checker.InsertCredentials(username, password_hash)
        return redirect('/login')




@app.route('/login', methods = ['GET', 'POST'])
def LogIn():
    if request.method == 'GET':
        return render_template('loginpage.html')
    else:
        username = request.form['username']
        sha256 = hashlib.sha256()

        password = (request.form['password']).encode()
        sha256.update(password)
        password_hash = sha256.hexdigest()

        result = credential_checker.getCredentials(username)
        
        if result == (username, str(password_hash)):
            
            response = make_response(redirect('/'))
            unique_id = credential_checker.UUID_Assigning(username)
            response.set_cookie('session_id', unique_id)
            
            username_db = credential_checker.checkCookie(unique_id)
            
            if username_db == None:
                redirect('/login')
            
            print(username_db)
            
            return response
            
        return redirect('/login')
    


@app.route('/', methods = ['GET'])

def take_inp():
    ans = credential_checker.fetchSession()
    if ans == None:
        return redirect('/login')
    

    newmachine.createTables()

    
    new_websites = newmachine.Get_Website_Summary()

    
    
    
    

    return render_template('homepage.html', w=new_websites)



@app.route('/addwebsite', methods = ['POST'])   
def user_web_input():
    
    web_url = request.form['url']
    if 'http' not in web_url or 'https' not in web_url:
        return redirect('/error')
    
    newmachine.insertWebsites(web_url)
    
    return redirect('/')
@app.route('/error', methods = ['GET'])
def show_error_page():
    return render_template('errorpage.html')

@app.route('/website/<id>')
def website_details(id):
    website = newmachine.getWebsiteById(id)
    return render_template('websitepage.html',website=website)

@app.route('/website/<id>/metrics')
def getJSONMetrics(id):
    metrics = newmachine.getMetricsForWebsite(id)
    json_obj = json.dumps(metrics, indent=4)
    return json_obj

@app.route('/website/<id>/hourly')
def getHourlyData(id):
    HourlyMetrics = newmachine.getHourAvailability(id)
    json_obj = json.dumps(HourlyMetrics, indent=4)
    return json_obj

@app.route('/website/<id>/for24')
def getPrev24Hour(id):
    Hour24Metrics = newmachine.get24HrMetrics(id)
    json_obj = json.dumps(Hour24Metrics, indent = 4)
    return json_obj