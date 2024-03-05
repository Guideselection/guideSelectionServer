
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_mail import Mail, Message
from pymongo.errors import InvalidOperation, DuplicateKeyError
import random
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
import os
from werkzeug.utils import secure_filename
import random
import string


SCOPES = ['https://www.googleapis.com/auth/drive.file']


from google.oauth2 import service_account
# from googleapiclient.discovery import build

def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        'Credentials.json',  # Update with your service account file path
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return creds


import csv

def get_entire_row(file_path, row_number):
    try:
        # Open the CSV file
        with open(file_path, 'r', newline='') as csvfile:
            # Create a CSV reader object
            csv_reader = csv.reader(csvfile)

            # Skip to the specified row
            for _ in range(row_number - 1):
                next(csv_reader)

            # Read the specified row
            row_data = next(csv_reader)

            # Assuming the first row contains headers
            with open(file_path, 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                headers = next(csv_reader)

            # Create a dictionary with headers as keys and row data as values
            row_dict = dict(zip(headers, row_data))

            # print(row_dict)
            return row_dict

    except Exception as e:
        print(f"An error occurred: {e}")



def get_google_drive_link(service, file_name):
    # Search for the file by name
    folder_name = "All Students Images"
    folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    folder_results = service.files().list(q=folder_query, fields="files(id)").execute()
    folders = folder_results.get('files', [])
    
    if not folders:
        print(f"No folder found with the name '{folder_name}' in Google Drive.")
        return None

    folder_id = folders[0]['id']
    query = f"name contains '{file_name}' and '{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id,webViewLink)").execute()
    files = results.get('files', [])

    if not files:
        print(f"No file found with the name starting with '{file_name}' in the folder '{folder_name}'.")
        return None

    file_id = files[0]['id']
    web_view_link = files[0]['webViewLink']

    return web_view_link




creds = authenticate()
service = build('drive', 'v3', credentials=creds)
# print(get_google_drive_link(service, 41111354))








db = client.SIST_Courses

# faild = []
# def insertSectionToStudentDocument(regNo, section):
#     try:
#         collection = db["users"]
#         res = collection.update_one({"regNo":regNo}, {"$set":{"section":section}})
#         if res:
#             pass
#         else:
#             faild.append(regNo)
#     except:
#         faild.append(regNo)

# Example usage

failed = []
def insertImagesToStudentDocument(regNo, image):
    try:
        collection = db["users"]
        res = collection.update_one({"regNo":regNo}, {"$set":{"image":image}})
        if res:
            pass
        else:
            failed.append(regNo)
    except:
        failed.append(regNo)


# file_path = 'updatedstudentdetails.csv'
# for i in range(10,1484):
#     row_number = i  # Change this to the desired row number

#     stData = get_entire_row(file_path, row_number)
#     print(stData["regNo"])
#     regNo = stData["regNo"]
#     image = get_google_drive_link(service, regNo)
#     insertImagesToStudentDocument(int(regNo), image)

# # print(faild)
# print(failed)



# Flask==2.0.1
# requests==2.26.0
# gunicorn==20.1.0
# blinker==1.6.2
# click==8.1.4
# colorama==0.4.6
# dnspython==2.3.0
# Flask-Cors==4.0.0
# Flask-Mail==0.9.1
# itsdangerous==2.1.2
# Jinja2==3.1.2
# MarkupSafe==2.1.3
# PyJWT==2.7.0
# pymongo==4.4.0
# Werkzeug==2.0.1



