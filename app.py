from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_mail import Mail, Message
from pymongo.errors import InvalidOperation, DuplicateKeyError
import random
import jwt
import datetime

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






def generate_token(email):
    # Define the payload for the token (you can include additional claims if needed)
    payload = {'email': email,
               'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
               }

    # Define the secret key used to sign the token
    # Make sure to keep this key secure and preferably stored in a configuration file
    secret_key = 'your-secret-key'

    # Generate the token with the payload and secret key
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return token


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

                return jsonify({"is_account_available":"true", "Is_Email_sent":"true","_id":str(id), "OTP":otp, "token":token, "token_for_first_time":tokenforfirsttime ,  "first_time":"true"})
            except Exception as e:
                print(e)
                return jsonify({"is_account_available":"true" ,"_id":str(id), "Is_Email_sent":"false", "first_time":"true"})
        else:
            return jsonify({'is_account_available': "false" , "Is_Email_sent":"false"})
    
    elif str(password)==result['password']:

        return jsonify({'is_account_available': "true", "is_password_correct":"true","_id":str(id), "token":token, "first_time":"false", "Is_Email_sent":"false"})

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





@app.route('/guidelist', methods=['GET'])
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




@app.route('/create_collection', methods=['POST'])
def create_collection():
    data = request.json  # Assuming the request data is in JSON format

    # Get the collection name and data from the request JSON
    collection_name = data.get('collection_name')
    collection_data = data.get('data')

    # Create the collection
    collection = db[collection_name]

    # Insert data into the collection
    inserted_data = collection.insert_one(collection_data)

    return jsonify({"message": "Collection created and data inserted successfully!", "inserted_id": str(inserted_data.inserted_id)})






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


@app.route('/add_registered_data', methods=['PUT'])
def add_registered_data():

    data = request.json
    email = data.get('email')
    users_collection = db.registeredUsers
    
    try:
        # Start a client session
        with client.start_session() as session:
            # Start a transaction
            
            with session.start_transaction():

            # Perform the critical operation
                new_user = data
                users_collection.insert_one(new_user, session=session)

            # Commit the transaction
            # session.commit_transaction()

        return jsonify({'message': 'User registered successfully'}), 201
    except DuplicateKeyError as e:
        # session.abort_transaction()
        return jsonify({"error": "Email already registered"})
    except InvalidOperation as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred during registration","exception":e})


@app.route("/rollback_registered_data", methods=["POST"])
def rollback_registered_data():
    data = request.json
    collection = db.registeredUsers
    result = collection.delete_many(data)

    return jsonify({"deleted":"true"})



@app.route('/checkVacancies/<string:mail>', methods=['GET'])
def check_vacancies(mail):
    collection = db.facultylist
    filter = {'University EMAIL ID':mail}
    result = collection.find_one(filter)
    # print(result)
    return jsonify({"vacancies": result['TOTAL BATCHES']})



@app.route('/update_vacancies_data', methods=['PUT'])
def update_vacancies_data():
    data = request.json  # Assuming the request data is in JSON format
    # Extract data from the request JSON
    collection_name = data.get('collection_name')
    filter_data = data.get('filter_data')
    updated_data = data.get('updated_data')

    # print(filter_data, updated_data)

    # Update the data in the collection
    collection = db[collection_name]
    result = collection.update_one(filter_data, {'$set': updated_data})

    if result.modified_count > 0:
        return jsonify({"message": "Data updated successfully!"})
    else:
        return jsonify({"message": "No matching data found for update."}), 404















@app.route("/checkSecondMail/<string:mailid>", methods=["GET"])
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

            return jsonify({'email':result['email'], 'firstTime':result['firstTime'], 'otp':otp})
        except Exception as e:
            print(e)
            return jsonify({'email':result['email'], 'firstTime':result['firstTime']})
    else:
        return jsonify({"data":"mail not found"})




@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.json
    collection_name = data.get("collection_name")
    filter = data.get("filter_data")
    collection = db[collection_name]
    result = collection.delete_many(filter)

    return jsonify({"deleted":"true"})








if __name__ == '__main__':
    app.debug = True
    app.run()
