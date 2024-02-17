from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_mail import Mail, Message
from pymongo.errors import InvalidOperation, DuplicateKeyError
import random
import jwt
from datetime import datetime, timedelta
import time

app=Flask(__name__)
CORS(app)



app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your email server
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'pradeepgeddada31@gmail.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'dkjtxrfbelenaebn'  # Replace with your email password

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
                msg = Message(f'Your OTP is {otp}',  # Email subject
                            sender='pradeepgeddada31@gmail.com',  # Replace with your email address
                            recipients=[mailid])  # Replace with the recipient's email address
                msg.body = 'This is a test email sent from Flask-Mail'  # Email body

                mail.send(msg)

                return jsonify({"is_account_available":"true", "Is_Email_sent":"true","_id":str(id), "OTP":otp, "token":token, "token_for_first_time":tokenforfirsttime , "name":result["Full Name"], "regNo":result["regNo"], "phoneNo":result["Mobile Number"], "section":result["section"],  "first_time":"true"})
            except Exception as e:
                print(e)
                return jsonify({"is_account_available":"true" ,"_id":str(id), "Is_Email_sent":"false", "first_time":"true"})
        else:
            return jsonify({'is_account_available': "false" , "Is_Email_sent":"false"})
    
    elif str(password)==result['password']:

        # registeredStudentsData = db['registeredStudentsData']
        # filter = {"mailId":mailid}
        # print(filter)
        # studentCompleteData = registeredStudentsData.find(filter)
        # print(studentCompleteData[0])

        # # Initialize an empty list to store the results
        # studentData = []
        # projectDetails = []
        # projectStatus = []
        # documentation = []

        # # Iterate over the cursor to extract data
        # for student in studentData:
        #     # Do something with each document in the cursor
        #     if student["team"]:
        #         studentData.append({
        #         # "student_id": str(student["_id"]),
        #             "name": student["name"],
        #             "team":student["team"],
        #             "regNo":student["regNo"],
        #             "phoneNo":student["phoneNo"],
        #             "p2name":student["p2name"],
        #             "p2regNo":student["p2regNo"],
        #             "p2phoneNo":student["p2phoneNo"],
        #             "p2mailId":student["p2mailId"],
        #         })
        #     else:
        #         studentData.append({
        #         # "student_id": str(student["_id"]),
        #             "name": student["name"],
        #             "team":student["team"],
        #             "regNo":student["regNo"],
        #             "phoneNo":student["phoneNo"]
        #         })

        #     projectDetails.append({
        #         "projectTitle": student["projectTitle"],
        #         "projectDesc": student["projectDesc"],
        #         "projectDomain": student["projectDomain"]
        #     })

        #     projectStatus.append({
        #         "documentation": student["status"]["documentation"],
        #         "ppt": student["status"]["ppt"],
        #         "guideApproval": student["status"]["guideApproval"],
        #         "researchPaper": {
        #             "approval" : student["status"]["researchPaper"]["approval"],
        #             "communicated" : student["status"]["researchPaper"]["communicated"],
        #             "accepted" : student["status"]["researchPaper"]["accepted"],
        #             "payment" : student["status"]["researchPaper"]["payment"]
        #         }
        #     })

        #     documentation.append({
        #         "researchPaper": student["documentation"]["researchPaper"],
        #         "documentation": student["documentation"]["documentation"],
        #         "ppt": student["documentation"]["ppt"]
        #     })
             
        #         # Add more fields as needed
            
        



        return jsonify({'is_account_available': "true",
                            "is_password_correct":"true","_id":str(id),
                            "token":token,
                            "first_time":"false",
                            "Is_Email_sent":"false"
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
                      sender='pradeepgeddada31@gmail.com',  # Replace with your email address
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
                      sender='pradeepgeddada31@gmail.com',  # Replace with your email address
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
            <p>Our team will review your project thoroughly and get back to you with feedback.
            Thank you once again for choosing to work with us.</p><br/><br/><br/>
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
                      sender='pradeepgeddada31@gmail.com',  # Replace with your email address
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
            <p>Our team will review your project thoroughly and get back to you with feedback.
            Thank you once again for choosing to work with us.</p><br/><br/><br/>
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
        otp = random.randint(100000,999999)

        try:
            msg = Message(f'Your OTP is {otp}',  # Email subject
                        sender='pradeepgeddada31@gmail.com',  # Replace with your email address
                        recipients=[mailid])  # Replace with the recipient's email address
            msg.body = 'This is a test email sent from Flask-Mail'  # Email body

            mail.send(msg)

            return jsonify({'email':result['email'], 'firstTime':result['firstTime'] , "name":result["Full Name"], "regNo":result["regNo"], "phoneNo":result["Mobile Number"], "section":result["section"], 'otp':otp})
        except Exception as e:
            print(e)
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
    print(studentCompleteData[0])

    # Initialize an empty list to store the results
    studentData = []
    projectDetails = []
    projectStatus = []
    documentation = []
    comments = []


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
                "selectedGuide":student["selectedGuide"],
                "selectedGuideMailId":student["selectedGuideMailId"]


            })
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
                        "comments":comments[0]
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
        return jsonify({"message":"success"})

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
    for g in guide:
        print(g["allStudents"])
        allStudentMailIds = g["allStudents"]

    allStudentsData = []
    registeredStudentsData = db['registeredStudentsData']

    for studentMail in allStudentMailIds:
        filter = {"mailId":studentMail}
        studentData = registeredStudentsData.find(filter)
        for student in studentData:
            if student["team"]:
                allStudentsData.append({
                    "team":student["team"],
                    "teamId":student["teamId"],
                    "teamLeadImg":"https://thumbs.dreamstime.com/b/man-profile-cartoo…-vector-illustration-graphic-design-135443492.jpg",
                    "registerNoOne":student["regNo"],
                    "studentOne":student["name"],
                    "registerNoTwo":student["p2regNo"],
                    "studentTwo":student["p2name"],
                    "section":student["section"],
                    "projectTitle":student["projectTitle"]})
            else:
                 allStudentsData.append({
                    "team":student["team"],
                    "teamId":student["teamId"],
                    "teamLeadImg":"https://thumbs.dreamstime.com/b/man-profile-cartoo…-vector-illustration-graphic-design-135443492.jpg",
                    "registerNoOne":student["regNo"],
                    "studentOne":student["name"],
                    "section":student["section"],
                    "projectTitle":student["projectTitle"]})
    

    

    return jsonify({"message":"fetched successfully", "allStudentsData":allStudentsData })


    # registeredStudentsData = db['registeredStudentsData']
    # filter = {"mailId":mailid}
    # print(filter)
    # studentCompleteData = registeredStudentsData.find(filter)
    # print(studentCompleteData[0])

    # # Initialize an empty list to store the results
    # studentData = []
    # projectDetails = []
    # projectStatus = []
    # documentation = []


    # # Iterate over the cursor to extract data
    # for student in studentCompleteData:
    #     # Do something with each document in the cursor
    #     if student["team"]:
    #         studentData.append({
    #         # "student_id": str(student["_id"]),
    #             "name": student["name"],
    #             "team":student["team"],
    #             "regNo":student["regNo"],
    #             "phoneNo":student["phoneNo"],
    #             "p2name":student["p2name"],
    #             "p2regNo":student["p2regNo"],
    #             "p2phoneNo":student["p2phoneNo"],
    #             "p2mailId":student["p2mailId"],
    #             "selectedGuide":student["selectedGuide"],
    #             "selectedGuideMailId":student["selectedGuideMailId"]


    #         })
    #     else:
    #         studentData.append({
    #         # "student_id": str(student["_id"]),
    #             "name": student["name"],
    #             "team":student["team"],
    #             "regNo":student["regNo"],
    #             "phoneNo":student["phoneNo"],
    #             "selectedGuide":student["selectedGuide"],
    #             "selectedGuideMailId":student["selectedGuideMailId"]
    #         })

    #     projectDetails.append({
    #         "projectTitle": student["projectTitle"],
    #         "projectDesc": student["projectDesc"],
    #         "projectDomain": student["projectDomain"]
    #     })

    #     projectStatus.append({
    #         "documentation": student["status"]["documentation"],
    #         "ppt": student["status"]["ppt"],
    #         "guideApproval": student["status"]["guideApproval"],
    #         "researchPaper": {
    #             "approval" : student["status"]["researchPaper"]["approval"],
    #             "communicated" : student["status"]["researchPaper"]["communicated"],
    #             "accepted" : student["status"]["researchPaper"]["accepted"],
    #             "payment" : student["status"]["researchPaper"]["payment"]
    #         }
    #     })

    #     documentation.append({
    #         "researchPaper": student["documentation"]["researchPaper"],
    #         "documentation": student["documentation"]["documentation"],
    #         "ppt": student["documentation"]["ppt"]
    #     })

    # guideFilter = {"University EMAIL ID":studentData[0]["selectedGuideMailId"]}
    # result = db['facultylist'].find(guideFilter)
    # guideImage=""
    # for r in result:
    #     guideImage=r["IMAGE"]




    # return jsonify({    
    #                     "studentData":studentData,
    #                     "projectDetails":projectDetails,
    #                     "projectStatus":projectStatus,
    #                     "documentation":documentation,
    #                     "guideImage":guideImage
    #                 })







if __name__ == '__main__':
    app.debug = True
    app.run()
