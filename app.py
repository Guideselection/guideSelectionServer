from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_mail import Mail, Message
from pymongo.errors import InvalidOperation, DuplicateKeyError
import random
import jwt
from datetime import datetime, timedelta
import time
import driveAPI
import os
import io
import tempfile
from googleapiclient.discovery import build
from werkzeug.utils import secure_filename
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2 import service_account

app=Flask(__name__)
CORS(app)



app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your email server
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'guideselection.cse@sathyabama.ac.in'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'ucik ubno mwzi onwe'  # Replace with your email password

mail = Mail(app)



client = MongoClient('mongodb+srv://PradeeP1G:Pradeep%402003@cluster0.50omidk.mongodb.net/SIST_Courses?retryWrites=true&w=majority')

# mongodb+srv://PradeeP1G:Pradeep%402003@cluster0.50omidk.mongodb.net

db = client.SIST_Courses

CORS(app)

# @app.route('/')
# def index():
#     return render_template

@app.route('/users', methods = ['POST', 'GET'])
def data():
    if request.method=='POST':
        body = request.json
        fname=body['firstName']
        lname=body['lastName']
        emailId=body['emailId']

        db['users'].insert_one({
            "firstName":fname,
            "lastName":lname,
            "emailId":emailId
        })

        return jsonify({
            'status':'Data is posted to MongoDB',
            'firstName':fname,
            "lastName":lname,
            'emailId':emailId
        })


@app.route('/data', methods=['GET'])
def get_data():
    collection = db.users  # Replace <collection_name> with the name of your collection
    data = collection.find()  # Retrieve all documents from the collection

    result = []
    i=0  # Store the retrieved data
    for document in data:
        result.append({})
        result[i]["Course_Code"] = document["Course_Code"]
        result[i]["Course_name"] = document["Course_Name"]
        result[i]["Course_Credit"] = document["Course_Credit"]
        i+=1
    return jsonify(result)  # Return the data as a JSON response






@app.route('/add', methods=['POST'])
def add_data():
    # Get the data from the request
    data = request.get_json()
    # data = request.

    # Insert the data into the collection
    collection = db.users  # Replace <collection_name> with the name of your collection
    result = collection.insert_one(data)


    # Return the ID of the inserted document
    return jsonify({'inserted_id': str(result.inserted_id)})


@app.route('/api/update/<string:id>', methods=['PUT'])
def update_data(id):
    # Get the update data from the request
    data = request.get_json()
    filter = {'_id': ObjectId(id)}
    update = {'$set': data}

    # Update the data in the collection
    collection = db.users  # Replace <collection_name> with the name of your collection
    result = collection.update_many(filter, update)

    # Return the number of documents updated
    return jsonify({'updated_count': result.modified_count})







@app.route('/api/update', methods=['PUT'])
def update_all_data():
    # Get the update data from the request
    data = request.get_json()
    filter = {}
    update = { '$rename': { "EMAIL ID (University Mail ID)": "EMAIL ID" } }

    # Update the data in the collection
    collection = db.facultylist  # Replace <collection_name> with the name of your collection
    result = collection.update_many(filter, update)

    # Return the number of documents updated
    return jsonify({'updated_count': "updated"})




secret_key = 'SathyabamaInstituteOfScienceAndTechnology'

def generate_token(email):
    # Define the payload for the token (you can include additional claims if needed)
    payload = {'email': email,
               'exp': datetime.utcnow() + timedelta(minutes=100)
               }

    # Define the secret key used to sign the token
    # Make sure to keep this key secure and preferably stored in a configuration file
    

    # Generate the token with the payload and secret key
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return token

@app.route("/checkAuthentication/<string:mailId>", methods=["GET"])
def checkAuthentication(mailId):
    token = request.headers.get("Authorization")
    # print(token)
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        email = decoded_token['email']
        if str(mailId)==str(email):
            print("Authenticated")
            return jsonify({"message":"Authenticated"})
        else:
            return jsonify({"message":"Token Tampered"})
    except:
        return jsonify({"message":"Not Authenticated"})


@app.route('/api/check/<string:mail>', methods=["GET"])
def check_account_avalable(mail):
    collection = db.users
    filter={'email':mail}
    result = collection.find_one(filter)
    print(result)
    if result:
        return jsonify({"first_time":result['firstTime']})
    else:
        return jsonify({"data":"mail not found"})



@app.route('/api/check/<string:mailid>/<string:password>', methods=['GET'])
def check_data(mailid,password):
    # Get the update data from the request


    if str(mailid)[:6]=="CSE-25":
        filter = {"teamId":mailid}
        collection = db.users  # Replace <collection_name> with the name of your collection
        result = collection.find_one(filter)

        token = generate_token(result["email"])

        if result is None:
            return jsonify({'is_account_available': "false"})
        else:
            if str(password)==str(result['password']):
                return jsonify({'is_account_available': "true",
                                "is_password_correct":"true",
                                "token":token,
                                "first_time":"false",
                                "Is_Email_sent":"false",
                                "userEmail":result["email"],
                                "teamId":mailid
                            })
            else:
                return jsonify({'is_account_available': "true", "is_password_correct":"false",password:result["password"], "first_time":"false", "Is_Email_sent":"false"})




    filter = {'email': mailid}

    # Update the data in the collection
    collection = db.users  # Replace <collection_name> with the name of your collection
    result = collection.find_one(filter)
    if result is None:
        return jsonify({'is_account_available': "false"})
    
    id = result["_id"]


    token = generate_token(mailid)
    
    tokenforfirsttime = generate_token(mailid)


    if result["firstTime"]:
            # return jsonify({"is_account_available":"true","_id":str(id), "token":token, "first_login":"true"})



        otp = random.randint(100000,999999)



        if result:
            try:
                msg = Message("One-Time Password (OTP) for Registration",  # Email subject
                            sender='guideselection.cse@sathyabama.ac.in',  # Replace with your email address
                            recipients=[mailid])  # Replace with the recipient's email address
                # msg.body = 'This is a test email sent from Flask-Mail'  # Email body
                msg.html = f"""
                            <html>
                            <body>
                                <p>Dear {result['Full Name']},</p>
                                <p>Your One-Time Password (OTP) for registration is:</p>
                                <div style="display: flex; justify-content: center;">
                                    <h2 style="color: #007bff; font-size: 24px; font-weight: bold;">{otp}</h2>
                                </div>
                                <p>Please use this OTP to complete your registration process.</p>
                                <p>If you did not request this OTP or have any questions, please contact our support team.</p>
                                <p>Thank you for choosing to register with us.</p>
                                <br/><br/><br/>
                                <p>Best Regards,</p>
                                <p>School of Computing,</p>
                                <p>Sathyabama Institute of Science & Technology</p>
                            </body>
                            </html>
                            """


                mail.send(msg)

                return jsonify({"is_account_available":"true", "Is_Email_sent":"true","_id":str(id), "OTP":otp, "token":token, "token_for_first_time":tokenforfirsttime , "name":result["Full Name"], "regNo":result["regNo"], "phoneNo":result["Mobile Number"], "section":result["section"],  "first_time":"true"})
            except Exception as e:
                print(e,"error")
                return jsonify({"is_account_available":"true" ,"_id":str(id), "Is_Email_sent":"false", "first_time":"true"})
        else:
            return jsonify({'is_account_available': "false" , "Is_Email_sent":"false"})
    
    elif str(password)==result['password']:


        return jsonify({'is_account_available': "true",
                            "is_password_correct":"true","_id":str(id),
                            "token":token,
                            "first_time":"false",
                            "Is_Email_sent":"false",
                            "teamId":result["teamId"],
                            "userEmail":mailid
                        })

    else:
        return jsonify({'is_account_available': "true", "is_password_correct":"false",password:result["password"], "first_time":"false", "Is_Email_sent":"false"})





    # Return the number of documents updated
    # if result:
    #     return jsonify({'is_account_available': "true", "_id":str(id)})
    # else:
    #     return jsonify({'is_account_available': "false"})







@app.route('/api/check/verified/<string:mailid>/<string:id>', methods=['GET'])
def Send_otp(id,mailid):
    # Get the update data from the request
    # data = request.get_json()

    otp = random.randint(100000,999999)

    try:
        msg = Message(f'Your OTP is {otp}',  # Email subject
                      sender='guideselection.cse@sathyabama.ac.in',  # Replace with your email address
                      recipients=[mailid])  # Replace with the recipient's email address
        msg.body = 'This is a test email sent from Flask-Mail'  # Email body

        mail.send(msg)
        return jsonify({"Is_Email_sent":"true", "OTP":otp})
    except Exception as e:
        print(e)
        return jsonify({"Is_Email_sent":"false"})










@app.route('/api/delete/<string:id>', methods=['DELETE'])
def delete_data(id):
    # Delete the data from the collection
    collection = db.users  # Replace <collection_name> with the name of your collection
    result = collection.delete_one({'_id': ObjectId(id)})

    # Return the number of documents deleted
    return jsonify({'deleted_count': result.deleted_count})





@app.route('/guide_list', methods=['GET'])
def get_Guide_List():
    collection = db.facultylist

    data = collection.find()  # Retrieve all documents from the collection

    result = []
    i=0  # Store the retrieved data
    for document in data:
        result.append({})
        result[i]["id"] = i+1
        result[i]["NAME"] = document["NAME OF THE FACULTY"]
        result[i]["VACANCIES"] = document["TOTAL BATCHES"]
        result[i]["DESIGNATION"] = document["DESIGNATION"]
        result[i]["DOMAIN1"] = document["DOMAIN 1"]
        result[i]["DOMAIN2"] = document["DOMAIN 2"]
        result[i]["DOMAIN3"] = document["DOMAIN 3"]
        result[i]["UniversityEMAILID"] = document["University EMAIL ID"]
        result[i]['IMAGE'] = document["IMAGE"]
        result[i]['EMPID'] = document["EMP ID"]
        i+=1

    # print(result)
    return jsonify(result)





@app.route('/create_collection/<string:mailId>', methods=['POST'])
def create_collection_single(mailId):
    data = request.json  # Assuming the request data is in JSON format

    # Get the collection name and data from the request JSON
    # collection_name = data.get('collection_name')
    collection_data = data.get('data')

    # Create the collection
    collection = db["registeredStudentsData"]

    status = {
        "documentation":False,
        "ppt":False,
        "guideApproval":False,
        "researchPaper":{
            "approval":False,
            "communicated":False,
            "accepted":False,
            "payment":False
        }
    }

    documents = {
        "researchPaper":None,
        "documentation":None,
        "ppt":None
    }

    comments = []

    collection_data["status"] = status
    collection_data["documentation"] = documents
    collection_data["comments"] = comments
    collection_data["editProjectDetails"] = False
    collection_data["marks"] = 0


    teamiId = f"CSE-{str(datetime.now().year % 100 + 1)}-{str(int(collection_data['regNo'])%10000)}"
    collection_data["teamId"] = teamiId

    users_collection = db["users"]
    registered_users = db["registeredUsers"]
    filter = {"email" : mailId}
    update = {"$set": {"teamId": teamiId}}
    users_collection.update_one(filter, update)
    registered_users.update_one(filter, update)

    usersCollection = db["users"]

    collection_data["image"] = usersCollection.find_one(filter)["image"]

    # Insert data into the collection
    inserted_data = collection.insert_one(collection_data)



    collection = db["facultylist"]
    document = collection.find_one({ "University EMAIL ID": collection_data["selectedGuideMailId"] })
    updated_data = {"allStudents":[], "allTeams":[]}


    if document:
        if "allStudents" in document:
            document["allStudents"].append(mailId)
        else:
            document["allStudents"] = [mailId]

        if "allTeams" in document:
            document["allTeams"].append(teamiId)
        else:
            document["allTeams"] = [teamiId]

    updated_data["allStudents"] = document["allStudents"]
    updated_data["allTeams"] = document["allTeams"]


    # print(filter_data, updated_data)

    # Update the data in the collection
    
    result = collection.update_one({ "University EMAIL ID": collection_data["selectedGuideMailId"] }, {'$set': updated_data})


                    
    #Send Mail To Student
    password = collection_data['password']
    print(teamiId, password)

    try:
        msg = Message(f'Project Submission Confirmation',  # Email subject
                      sender='guideselection.cse@sathyabama.ac.in',  # Replace with your email address
                      recipients=[mailId])  # Replace with the recipient's email address
        msg.html = f"""
        <html>
        <body>
            <p>Dear {collection_data['name']},</p>
            <p>We are writing to inform you that we have received your project submission successfully. Thank you for your effort and contribution.</p>
            <b>Project Details:</b><br/>
            <ul>
            <li>Project Id - {teamiId}</li>
            <li>Project Name - {collection_data["projectTitle"]}</li>
            <li>Project Domain - {collection_data["projectDomain"]}</li>
            <li>Project Description - {collection_data["projectDesc"]}</li>
            <li>Guide Name - {collection_data["selectedGuide"]}</li>
            </ul><br/>
            
            <ul>
            <b>Login Credentials:</b><br/>
            <li>Project Id - {teamiId}</li>
            <li>Password - {password}</li>
            </ul><br/>
            <p>Your guide will review your project thoroughly and get back to you with feedback.
            </p><br/><br/><br/>
            <p>Best Regards,</p>
            <p>School of Computing,</p>
            <p>Sathyabama Institute of Science & Technology</p>
        </body>
        </html>
        """

        mail.send(msg)
        return jsonify({"Is_Email_sent":"true"})
    except Exception as e:
        print(e)
        return jsonify({"Is_Email_sent":"false","message": "Collection created and data inserted successfully!", "inserted_id": str(inserted_data.inserted_id)})


    

@app.route('/create_collection/<string:mailId1>/<string:mailId2>', methods=['POST'])
def create_collection_duo(mailId1, mailId2):
    data = request.json  # Assuming the request data is in JSON format

    # Get the collection name and data from the request JSON
    # collection_name = data.get('collection_name')
    collection_data = data.get('data')

    status = {
        "documentation":False,
        "ppt":False,
        "guideApproval":False,
        "researchPaper":{
            "approval":False,
            "communicated":False,
            "accepted":False,
            "payment":False
        }
    }

    documents = {
        "researchPaper":None,
        "documentation":None,
        "ppt":None
    }

    comments = []

    collection_data["status"] = status
    collection_data["documentation"] = documents
    collection_data["comments"] = comments
    collection_data["editProjectDetails"] = False
    collection_data["marks"] = 0
    collection_data["p2marks"] = 0


    



    # Create the collection
    collection = db["registeredStudentsData"]


    teamiId = f"CSE-{str(datetime.now().year % 100 + 1)}-{str(int(collection_data['regNo'])%10000)}"
    collection_data["teamId"] = teamiId

    users_collection = db["users"]
    registered_users = db["registeredUsers"]
    filter1 = {"email" : mailId1}
    filter2 = {"email" : mailId2}
    update = {"$set": {"teamId": teamiId}}
    users_collection.update_one(filter1, update)
    registered_users.update_one(filter1, update)
    users_collection.update_one(filter2, update)
    registered_users.update_one(filter2, update)

    usersCollection = db["users"]
    collection_data["image"] = usersCollection.find_one(filter1)["image"]
    collection_data["p2image"] = usersCollection.find_one(filter2)["image"]


    # Insert data into the collection
    inserted_data = collection.insert_one(collection_data)


    collection = db["facultylist"]
    document = collection.find_one({ "University EMAIL ID": collection_data["selectedGuideMailId"] })
    updated_data = {"allStudents":[]}
    if document:
        if "allStudents" in document:
            document["allStudents"].append(mailId1)
            document["allStudents"].append(mailId2)
        else:
            document["allStudents"] = [mailId1, mailId2]

        if "allTeams" in document:
            document["allTeams"].append(teamiId)
        else:
            document["allTeams"] = [teamiId]

    updated_data["allStudents"] = document["allStudents"]
    updated_data["allTeams"] = document["allTeams"]


    # print(filter_data, updated_data)

    # Update the data in the collection
    
    result = collection.update_one({ "University EMAIL ID": collection_data["selectedGuideMailId"] }, {'$set': updated_data})


                    
    #Send Mail To Student
    password = collection_data['password']
    print(teamiId, password)

    print(mailId1, mailId2)

    try:
        msg = Message(f'Project Submission Confirmation',  # Email subject
                      sender='guideselection.cse@sathyabama.ac.in',  # Replace with your email address
                      recipients=[mailId1, mailId2])  # Replace with the recipient's email address
        msg.html = f"""
        <html>
        <body>
            <p>Dear {collection_data['name']} and {collection_data['p2name']},</p>
            <p>We are writing to inform you that we have received your project submission successfully. Thank you for your effort and contribution.</p>
            <b>Project Details:</b><br/>
            <ul>
            <li>Project Id - {teamiId}</li>
            <li>Project Name - {collection_data["projectTitle"]}</li>
            <li>Project Domain - {collection_data["projectDomain"]}</li>
            <li>Project Description - {collection_data["projectDesc"]}</li>
            <li>Guide Name - {collection_data["selectedGuide"]}</li>
            </ul><br/>
            
            <ul>
            <b>Login Credentials:</b><br/>
            <li>Project Id - {teamiId}</li>
            <li>Password - {password}</li>
            </ul><br/>
            <p>Your guide will review your project thoroughly and get back to you with feedback.
            </p><br/><br/><br/>
            <p>Best Regards,</p>
            <p>School of Computing,</p>
            <p>Sathyabama Institute of Science & Technology</p>
        </body>
        </html>
        """

        mail.send(msg)
        return jsonify({"Is_Email_sent":"true"})
    except Exception as e:
        print(e)
        return jsonify({"Is_Email_sent":"false","message": "Collection created and data inserted successfully!", "inserted_id": str(inserted_data.inserted_id)})


    





@app.route('/update_data', methods=['PUT'])
def updateLoginData():
    data = request.json  # Assuming the request data is in JSON format
    # Extract data from the request JSON
    collection_name = data.get('collection_name')
    filter_data = data.get('filter_data')
    updated_data = data.get('updated_data')

    # Update the data in the collection
    collection = db[collection_name]
    result = collection.update_one(filter_data, {'$set': updated_data})

    if result.modified_count > 0:
        return jsonify({"message": "Data updated successfully!"})
    else:
        return jsonify({"message": "No matching data found for update."}), 404
    



# @app.route('/update_vacancies_data', methods=['PUT'])
def update_vacancies_data(collection_name, filter_data, updated_data):
    data = request.json  # Assuming the request data is in JSON format
    # Extract data from the request JSON
    # collection_name = data.get('collection_name')
    # filter_data = data.get('filter_data')
    # updated_data = data.get('updated_data')

    collection = db[collection_name]
    # document = collection.find_one(filter_data)
    # if document:
    #     if "allStudents" in document:
    #         document["allStudents"].append(studentEmail)
    #     else:
    #         document["allStudents"] = [studentEmail]
    # updated_data["allStudents"] = document["allStudents"]


    # print(filter_data, updated_data)

    # Update the data in the collection
    
    result = collection.update_one(filter_data, {'$set': updated_data})

    if result.modified_count > 0:
        return jsonify({"message": "Data updated successfully!"})
    else:
        return jsonify({"message": "No matching data found for update."}), 404



# Function to acquire a lock
def acquire_lock(guide_mail_id):
    lock_collection = db["lock_collection"]
    try:
        lock_collection.insert_one({"mailId": guide_mail_id})
        return True
    except DuplicateKeyError:
        return False
# Function to release a lock
def release_lock(guide_mail_id):
    lock_collection = db["lock_collection"]
    lock_collection.delete_one({"mailId": guide_mail_id})
# print(acquire_lock("dean.computing@sathyabama.ac.in"))

@app.route('/add_registered_data', methods=['PUT'])
def add_registered_data():

    data = request.json
    email = data.get('email')
    users_collection = db.registeredUsers
    guideMailId = data.get("guideMailId")
    

    collection = db.facultylist
    filter = {'University EMAIL ID':guideMailId}
    result = collection.find_one(filter)
    # print(result)
    if result:
        # Check if registration lock is set for the guide
        while not acquire_lock(guideMailId):
            time.sleep(1)  # Wait for a short period
            # Check again after waiting
        # print(email, "--Acquired Lock")

        result = collection.find_one(filter)
        if result['TOTAL BATCHES']>0:
            try:
                # Start a client session
                with client.start_session() as session:
                    # Start a transaction
                    
                    with session.start_transaction():

                    # Perform the critical operation
                        new_user = data
                        users_collection.insert_one(new_user, session=session)
                        if data.get("update_vacancies_data"):
                            update_vacancies_data("facultylist", { "University EMAIL ID": guideMailId }, {"TOTAL BATCHES": result['TOTAL BATCHES']-1 } )
                    # Commit the transaction
                    # session.commit_transaction()
                        # Release the lock when done
                        
                        # print(email, "--Realesed Lock")
                
                return jsonify({'message': 'User registered successfully'}), 201
            except DuplicateKeyError as e:
                # session.abort_transaction()
                return jsonify({"error": "Email already registered"})
            except InvalidOperation as e:
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                return jsonify({"error": "An error occurred during registration","exception":e})
            finally:
                # Release the lock when done
                release_lock(guideMailId)
                # print(email, "--Realesed Lock")
        else:
            release_lock(guideMailId)
            return jsonify({'message': 'No Vacancies'})


@app.route("/rollback_registered_data", methods=["POST"])
def rollback_registered_data():
    data = request.json
    collection = db.registeredUsers
    delete_result = collection.delete_many({"email":data.get("email")})

    # collection = db.facultylist
    # filter = {'University EMAIL ID':data.get("guideMailId")}
    # result = collection.find_one(filter)
    # update_vacancies_data("facultylist", { "University EMAIL ID": data.get("guideMailId") }, {"TOTAL BATCHES": result['TOTAL BATCHES']+1 })

    return jsonify({"deleted":"true"})



@app.route('/check_vacancies/<string:mail>', methods=['GET'])
def check_vacancies(mail):
    collection = db.facultylist
    filter = {'University EMAIL ID':mail}
    result = collection.find_one(filter)
    # print(result)
    return jsonify({"vacancies": result['TOTAL BATCHES']})


















@app.route("/check_second_mail/<string:mailid>", methods=["GET"])
def check_second_Person_mail(mailid):

    collection = db.users
    filter = {"email":mailid}
    result = collection.find_one(filter)
    print(result)

    if result:
        if result["firstTime"]:
            otp = random.randint(100000,999999)

            try:
                msg = Message("One-Time Password (OTP) for Registration",  # Email subject
                            sender='guideselection.cse@sathyabama.ac.in',  # Replace with your email address
                            recipients=[mailid])  # Replace with the recipient's email address
                # msg.body = 'This is a test email sent from Flask-Mail'  # Email body
                msg.html = f"""
                            <html>
                            <body>
                                <p>Dear {result['Full Name']},</p>
                                <p>Your One-Time Password (OTP) for registration is:</p>
                                <div style="display: flex; justify-content: center;">
                                    <h2 style="color: #007bff; font-size: 24px; font-weight: bold;">{otp}</h2>
                                </div>
                                <p>Please use this OTP to complete your registration process.</p>
                                <p>If you did not request this OTP or have any questions, please contact our support team.</p>
                                <p>Thank you for choosing to register with us.</p>
                                <br/><br/><br/>
                                <p>Best Regards,</p>
                                <p>School of Computing,</p>
                                <p>Sathyabama Institute of Science & Technology</p>
                            </body>
                            </html>
                            """

                mail.send(msg)

                return jsonify({'email':result['email'], 'firstTime':result['firstTime'] , "name":result["Full Name"], "regNo":result["regNo"], "phoneNo":result["Mobile Number"], "section":result["section"], 'otp':otp})
            except Exception as e:
                print(e)
                return jsonify({'email':result['email'], 'firstTime':result['firstTime']})
        else:
            return jsonify({'email':result['email'], 'firstTime':result['firstTime']})
    else:
        return jsonify({"data":"mail not found"})




@app.route("/update_second_user_credentials", methods=["POST"])
def update_second_user_credentials():
    data = request.json
    collection_name = data.get("collection_name")
    filter = data.get("filter_data")
    collection = db[collection_name]
    result = collection.delete_many(filter)

    return jsonify({"deleted":"true"})


@app.route("/studentLogin/getStudentData/<string:mailid>", methods=["POST"])
def getStudentdata(mailid):
    registeredStudentsData = db['registeredStudentsData']
    filter = {"mailId":mailid}
    print(filter)
    studentCompleteData = registeredStudentsData.find(filter)
    # print(studentCompleteData[0])

    # Initialize an empty list to store the results
    studentData = []
    projectDetails = []
    projectStatus = []
    documentation = []
    comments = []
    studentImage2=""
    studentImage1=""

    # Iterate over the cursor to extract data
    for student in studentCompleteData:
        # Do something with each document in the cursor
        if student["team"]:
            studentData.append({
            # "student_id": str(student["_id"]),
                "name": student["name"],
                "team":student["team"],
                "regNo":student["regNo"],
                "phoneNo":student["phoneNo"],
                "p2name":student["p2name"],
                "p2regNo":student["p2regNo"],
                "p2phoneNo":student["p2phoneNo"],
                "p2mailId":student["p2mailId"],
                "teamId":student["teamId"],
                "editProjectDetails":student["editProjectDetails"],
                "section":student["section"],
                "p2section":student["p2section"],
                "selectedGuide":student["selectedGuide"],
                "selectedGuideMailId":student["selectedGuideMailId"]


            })
            studentImage1 = student["image"]
            studentImage2 = student["p2image"]
        else:
            studentData.append({
            # "student_id": str(student["_id"]),
                "name": student["name"],
                "team":student["team"],
                "regNo":student["regNo"],
                "phoneNo":student["phoneNo"],
                "teamId":student["teamId"],
                "section":student["section"],
                "editProjectDetails":student["editProjectDetails"],
                "selectedGuide":student["selectedGuide"],
                "selectedGuideMailId":student["selectedGuideMailId"]
            })
            studentImage1 = student["image"]


        projectDetails.append({
            "projectTitle": student["projectTitle"],
            "projectDesc": student["projectDesc"],
            "projectDomain": student["projectDomain"]
        })

        projectStatus.append({
            "documentation": student["status"]["documentation"],
            "ppt": student["status"]["ppt"],
            "guideApproval": student["status"]["guideApproval"],
            "researchPaper": {
                "approval" : student["status"]["researchPaper"]["approval"],
                "communicated" : student["status"]["researchPaper"]["communicated"],
                "accepted" : student["status"]["researchPaper"]["accepted"],
                "payment" : student["status"]["researchPaper"]["payment"]
            }
        })

        documentation.append({
            "researchPaper": student["documentation"]["researchPaper"],
            "documentation": student["documentation"]["documentation"],
            "ppt": student["documentation"]["ppt"]
        })


        comments.append(student["comments"])

    guideFilter = {"University EMAIL ID":studentData[0]["selectedGuideMailId"]}
    result = db['facultylist'].find(guideFilter)
    guideImage=""
    for r in result:
        guideImage=r["IMAGE"]




    return jsonify({    
                        "studentData":studentData,
                        "projectDetails":projectDetails,
                        "projectStatus":projectStatus,
                        "documentation":documentation,
                        "guideImage":guideImage,
                        "comments":comments[0],
                        "studentImage1":studentImage1,
                        "studentImage2":studentImage2,
                    })



@app.route("/studentLogin/updateProjectDetails/<string:mailid>", methods=["POST"])
def updateProjectDetails(mailid):
    updatedData = request.json
    registeredStudentsData = db['registeredStudentsData']
    filter = {"mailId":mailid}
    print(filter)
    updatedResult = registeredStudentsData.update_one(filter, {"$set":updatedData})
    updatedResult = registeredStudentsData.update_one(filter, {"$set":{"editProjectDetails":False}})

    if updatedResult.modified_count==1:
        return jsonify({"message":"Success"})
    else:
        return jsonify({'message': 'Fail'})

@app.route("/staffLogin/check/<string:mailId>/<string:password>", methods=["GET"])
def checkStaffLogin(mailId, password):
    facultycredentials = db["facultycredentials"]
    filter = {"mailId": mailId}
    result = facultycredentials.find_one(filter)
    print(result)
    if result:
        token = generate_token(mailId)
        if str(password)==result["password"]:
            return jsonify({"is_account_available":"true", "Is_Password_Correct":"true", "token":token  })
        else:
            return jsonify({"is_account_available":"true", "Is_Password_Correct":"false" })
    else:
        return jsonify({"is_account_available":"false", "Is_Password_Correct":"false" })


@app.route("/staffLogin/getStudentsData/<string:mailid>", methods=["POST"])
def getStudentsdata(mailid):

    facultylist = db["facultylist"]
    filter = {"University EMAIL ID": mailid}
    allStudentMailIds = []
    guide = facultylist.find(filter)
    guideImg=""
    for g in guide:
        print(g["allStudents"])
        allStudentMailIds = g["allStudents"]
        guideImg=g["IMAGE"]

    allStudentsData = []
    registeredStudentsData = db['registeredStudentsData']

    for studentMail in allStudentMailIds:
        filter = {"mailId":studentMail}
        studentData = registeredStudentsData.find(filter)
        for student in studentData:
            if student["team"]:
                allStudentsData.append({
                    "team":student["team"],
                    "projectId":student["teamId"],
                    "studentOneImg":student["image"],
                    "studentTwoImg":student["p2image"],
                    "regNoOne":student["regNo"],
                    "studentOne":student["name"],
                    "regNoTwo":student["p2regNo"],
                    "studentTwo":student["p2name"],
                    "section":student["section"],
                    "p2section":student["p2section"],
                    "projectTitle":student["projectTitle"],
                    "projectDomain":student["projectDomain"]})
            else:
                 allStudentsData.append({
                    "team":student["team"],
                    "projectId":student["teamId"],
                    "studentOneImg":student["image"],
                    "regNoOne":student["regNo"],
                    "studentOne":student["name"],
                    "section":student["section"],
                    "projectTitle":student["projectTitle"],
                    "projectDomain":student["projectDomain"]})
    

    

    return jsonify({"message":"fetched successfully", "allStudentsData":allStudentsData, "guideImg":guideImg })



@app.route("/staffLogin/getProfileData/profile_details/<string:teamid>", methods=["POST"])
def getTeamdetails(teamid):
    registeredStudentsData = db['registeredStudentsData']
    filter = {"teamId": teamid}
    team_data = registeredStudentsData.find_one(filter)
    if not team_data:
        return jsonify({"error": "Team not found"}), 404

    studentdetailsone = []
    studentdetailstwo = []

    projectdetails = []
    guidedetails = []


    projectdetails.append({
        "title": team_data["projectTitle"],
        "desc": team_data["projectDesc"],
        "domain": team_data["projectDomain"],
        "projectApproval":team_data["editProjectDetails"]
    })

    guidedetails.append({
        "projectId": team_data["teamId"],
        "guideName": team_data["selectedGuide"],
        "guideMaidId": team_data["selectedGuideMailId"]
    })


    if team_data["team"]:
        studentdetailsone.append({
            "imgOne":team_data["image"],
            "fullNameOne": team_data["name"],
            "team": team_data["team"],
            "regNoOne": team_data["regNo"],
            "secOne": team_data["section"],
            "emailOne": team_data["mailId"],
            "mobileNoOne": team_data["phoneNo"],
        })
        studentdetailstwo.append({
            "team": team_data["team"],            
            "fullNameTwo": team_data["p2name"],
            "regNoTwo": team_data["p2regNo"],
            "mobileNoTwo": team_data["p2phoneNo"],
            "emailTwo": team_data["p2mailId"],
            "secTwo": team_data["p2section"],
            "imgTwo":team_data["p2image"]
        })
        return jsonify({
        "studentDetailsOne": studentdetailsone[0],
        "studentDetailsTwo" : studentdetailstwo[0],
        "projectdetails": projectdetails[0],
        "guidedetails": guidedetails[0],
    })

    else:
        studentdetailsone.append({
            "fullNameOne": team_data["name"],
            "team": team_data["team"],
            "regNoOne": team_data["regNo"],
            "emailOne": team_data["mailId"],
            "mobileNoOne": team_data["phoneNo"],
            "secOne": team_data["section"],
            "imgOne":team_data["image"]
        })

        return jsonify({
            "studentDetailsOne": studentdetailsone[0],
            "projectdetails": projectdetails[0],
            "guidedetails": guidedetails[0],
        })
    

@app.route("/staffLogin/getProfileData/<string:teamid>", methods=["POST"])
def get_profile_data(teamid):
    # print(request.json)
    registeredStudentsData = db['registeredStudentsData']
    filter = {"teamId":teamid}
    profileCompleteData = registeredStudentsData.find(filter)


    # Initialize an empty list to store the results
    projectDetails = []
    projectMarks = []
    links=[]
    documentation=[]
    ppt=[]
    researchPaper=[]
    guideApproval=[]
    isChecked = []
    comments = []


   
    for team in profileCompleteData:
        
        if team["team"]:
            projectDetails.append({
                  "studentOneImg":team["image"],
                "studentOneName": team["name"],
                "team":team["team"],
                "studentOneRegNo":team["regNo"],
                "studentOneSection":team["section"],
               
                "studentTwoImg":team["p2image"],
                "studentTwoName":team["p2name"],
                "studentTwoRegNo":team["p2regNo"],
                "studentTwoSection":team["p2section"],
                 "projectId":team["teamId"],
                "projectTitle":team["projectTitle"],
                "projectDomain":team["projectDomain"],
                
            })
        else:
            projectDetails.append({
                "studentOneImg":team["image"],
                "studentOneName": team["name"],
                "team":team["team"],
                "studentOneRegNo":team["regNo"],
                "studentOneSection":team["section"],
                "projectId":team["teamId"],
                "projectTitle":team["projectTitle"],
                "projectDomain":team["projectDomain"]
            })
        if team["team"]:
            projectMarks.append({
                 "studentOneMarks":team["marks"],
                 "studentTwoMarks":team["p2marks"]
                 })
        else:
             projectMarks.append({
                 "studentOneMarks":team["marks"]
                 })
        


        isChecked.append({
            "researchPaper": {
                "communicated" : team["status"]["researchPaper"]["communicated"],
                "accepted" : team["status"]["researchPaper"]["accepted"],
                "paymentDone" : team["status"]["researchPaper"]["payment"]
            }
        })


        documentation.append({
            "documentation": team["status"]["documentation"]
            })
        ppt.append({
             "ppt": team["status"]["ppt"]
            })
        researchPaper.append({ 
            "researchPaper": {
                 "approval" : team["status"]["researchPaper"]["approval"]
            }
        })
        guideApproval.append({
            "guideApproval": team["editProjectDetails"]
            })
        

        links.append({
            "researchPaper": team["documentation"]["researchPaper"],
            "documentation": team["documentation"]["documentation"],
            "ppt": team["documentation"]["ppt"]
        })


        comments.append(team["comments"])

 



    return jsonify({    
                        "projectDetails":projectDetails[0],
                        "projectMarks":projectMarks[0],
                        "links":links[0],
                        "isChecked":isChecked[0],
                        "documentation":documentation[0],
                        "researchPaper":researchPaper[0],
                        "ppt":ppt[0],
                        "guideApproval":guideApproval[0],
                        "comments":comments[0]
                    })



@app.route("/staffLogin/updateProjectDetails/<string:teamid>", methods=["POST"])
def updateProjectDetailsStatus(teamid):
    updatedData = request.json
    registeredStudentsData = db['registeredStudentsData']
    filter = {"teamId": teamid}

    approval_status = updatedData.get("approvalStatus", "")

    # updatedResult = registeredStudentsData.update_one(filter, {"$set": updatedData})

    if approval_status == "approved":
        updatedResult = registeredStudentsData.update_one(filter, {"$set": {"editProjectDetails": False}})
    elif approval_status == "declined":
        updatedResult = registeredStudentsData.update_one(filter, {"$set": {"editProjectDetails": True}})
    else:
        pass

    if updatedResult.modified_count == 1:
        return jsonify({"message": "Success"})
    else:
        return jsonify({"message": "Fail"})

    






@app.route("/staffLogin/profiledetails/updatestatusDetails/<string:teamid>", methods=["POST"])
def updatestatusDetails(teamid):
    today_date = datetime.now().strftime('%d-%m-%Y')
    data = request.json
    print(data) 
    status = {
        "documentation": data["editedDocumentationApproval"],
        "ppt": data["editedPptApproval"],
        "guideApproval": data["editedGuideApproval"],
        "researchPaper": {
            "approval": data["editedResearchApproval"],
            "communicated": data["editedCommunicationApproval"],
            "accepted": data["editedAcceptedApproval"],
            "payment": data["editedPaymentApproval"]
        }
    }

    if status["documentation"]==False:
        try:
            print("execute")
            col = db['registeredStudentsData']
            doc = col.find_one({"teamId":teamid})
            details = doc["documentation"]
            details["documentation"] = ""
            col.update_one({"teamId":teamid}, {"$set": {"documentation": details}})
        except:
            pass

    if status["ppt"]==False:
        try:
            print("execute")
            col = db['registeredStudentsData']
            doc = col.find_one({"teamId":teamid})
            details = doc["documentation"]
            details["ppt"] = ""
            col.update_one({"teamId":teamid}, {"$set": {"documentation": details}})
        except:
            pass

    if status["researchPaper"]==False:
        try:
            print("execute")
            col = db['registeredStudentsData']
            doc = col.find_one({"teamId":teamid})
            details = doc["documentation"]
            details["researchPaper"] = ""
            col.update_one({"teamId":teamid}, {"$set": {"documentation": details}})
        except:
            pass


    registeredStudentsData = db['registeredStudentsData']
    filter = {"teamId": teamid}
    comment = {
        today_date: data.get("editedComments", ""),
    }

    try:
        if comment[today_date]=="":
            pass
        else:
            registeredStudentsData.update_one(
            filter,
            {"$push": {"comments": comment}},
        )

        # Update status and push comment to the 'comments' array
        registeredStudentsData.update_one(
            filter,
            {"$set": {"status": status}}
        )

        # Update marks based on the condition
        filter = {"teamId":teamid}

        size = registeredStudentsData.find_one(filter)
        if size and size.get("team"):
            marks = {"marks": data.get("editedStudentOneMarks"), "p2marks": data.get("editedStudentTwoMarks")}
        else:
            marks = {"marks": data.get("editedStudentOneMarks")}

        # Update the document with the new marks
        registeredStudentsData.update_one(filter, {"$set": marks})


        return jsonify({"message": "Success"})
    except:
        return jsonify({"message": "Fail"})




# Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'Credentials.json'

# Specify the folder ID where you want to upload the file
FOLDER_ID = '1u0t5YKNrHOIDFISlShezgIINcSJDkF9S'


# @app.route("/upload", methods=["POST"])
# def upload():
#     data = request.files.get("ppt")

@app.route('/studentLogin/uploadppt/<string:teamid>', methods=['PUT'])
def upload_ppt_file(teamid):
    data = request.form
    teamId = data.get("teamId")
    file = request.files.get("ppt")
    
        # Define the directory to save the file
    upload_dir = f'/path/to/save/'
    
    # Create the directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)

    try:
        
        # Save the file to the directory
        file_path_to_upload = os.path.join(upload_dir, f'{teamId}_ppt_{secure_filename(file.filename)}')
        file.save(file_path_to_upload)

        # Upload file to Google Drive
        file_name = os.path.basename(file_path_to_upload)
        file_id = driveAPI.upload_file_to_drive(file_path_to_upload, file_name, FOLDER_ID, SCOPES, SERVICE_ACCOUNT_FILE)

        # Get the file link
        ppt_file_link = f'https://drive.google.com/file/d/{file_id}'

        print(teamid)
        filter = {"teamId":teamid}
        collection = db["registeredStudentsData"]
        doc = collection.find_one(filter)
        doc["documentation"]["ppt"] = ppt_file_link
        result = collection.update_one(filter, {"$set": {"documentation":doc["documentation"]}})


        # Cleanup: Delete the temporary file (if needed)
        os.remove(file_path_to_upload)

        if result:
            return jsonify({'message': 'Success'})
        else:
            return jsonify({'message': 'Fail'})
    except:
        return jsonify({'message': 'Fail'})



@app.route('/studentLogin/uploaddoc/<string:teamid>', methods=['PUT'])
def upload_researchPaper_file(teamid):
    data = request.form
    teamId = data.get("teamId")
    file = request.files.get("documentation")
    
        # Define the directory to save the file
    upload_dir = f'/path/to/save/'
    
    # Create the directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)

    try:
    
        # Save the file to the directory
        file_path_to_upload = os.path.join(upload_dir, f'{teamId}_documentation_{secure_filename(file.filename)}')
        file.save(file_path_to_upload)

        # Upload file to Google Drive
        file_name = os.path.basename(file_path_to_upload)
        file_id = driveAPI.upload_file_to_drive(file_path_to_upload, file_name, FOLDER_ID, SCOPES, SERVICE_ACCOUNT_FILE)

        # Get the file link
        documentation_file_link = f'https://drive.google.com/file/d/{file_id}'

        print(teamid)
        filter = {"teamId":teamid}
        collection = db["registeredStudentsData"]
        doc = collection.find_one(filter)
        doc["documentation"]["documentation"] = documentation_file_link
        result = collection.update_one(filter, {"$set": {"documentation":doc["documentation"]}})


        # Cleanup: Delete the temporary file (if needed)
        os.remove(file_path_to_upload)

        if result:
            return jsonify({'message': 'Success'})
        else:
            return jsonify({'message': 'Fail'})
    except:
        return jsonify({'message': 'Fail'})
    





@app.route('/studentLogin/uploadrspaper/<string:teamid>', methods=['PUT'])
def upload_doc_file(teamid):
    data = request.form
    teamId = data.get("teamId")
    file = request.files.get("researchPaper")
    
        # Define the directory to save the file
    upload_dir = f'/path/to/save/'
    
    # Create the directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)

    try:
        
        # Save the file to the directory
        file_path_to_upload = os.path.join(upload_dir, f'{teamId}_researchPaper_{secure_filename(file.filename)}')
        file.save(file_path_to_upload)

        # Upload file to Google Drive
        file_name = os.path.basename(file_path_to_upload)
        file_id = driveAPI.upload_file_to_drive(file_path_to_upload, file_name, FOLDER_ID, SCOPES, SERVICE_ACCOUNT_FILE)

        # Get the file link
        researchPaper_file_link = f'https://drive.google.com/file/d/{file_id}'

        print(teamid)
        filter = {"teamId":teamid}
        collection = db["registeredStudentsData"]
        doc = collection.find_one(filter)
        doc["documentation"]["researchPaper"] = researchPaper_file_link
        result = collection.update_one(filter, {"$set": {"documentation":doc["documentation"]}})


        # Cleanup: Delete the temporary file (if needed)
        os.remove(file_path_to_upload)
        if result:
            return jsonify({'message': 'Success'})
        else:
            return jsonify({'message': 'Fail'})
    
    except:
        return jsonify({'message': 'Fail'})



# @app.route("/test", methods=["POST"])
# def test1():
#     filter1 = {"email" : "geddadavenkatapradeep@gmail.com"}
#     c = db["users"]
#     print(c.find_one(filter1)["image"])
#     return jsonify({'message': 'Fail'})
    





if __name__ == '__main__':
    app.debug = True
    app.run()
