# import requests
#
# def return_token():
#     url = 'http://127.0.0.1:8000/auth/'
#     email = 'angelopoulosc@gmail.com'
#     password = 'Dent@123'
#
#     data = {
#         'email': email,
#         'password': password
#     }
#
#     try:
#         response = requests.post(url, data=data)
#         response.raise_for_status()
#
#         response_data = response.json()
#         token = response_data.get('token')
#         print(f"Token: {token}")
#         return token
#     except requests.exceptions.RequestException as e:
#         print('Error connecting to the server:', e)
#
# data = return_token()
# print('Token:', data)
#
#
# def upload_file_with_token(file_path, token):
#     url = 'http://127.0.0.1:8000/uploadfile/'
#     headers = {'Authorization': token}
#
#     try:
#         with open(file_path, 'rb') as file:
#             files = {'file': file}
#             print('files01',files)
#             response = requests.post(url, files=files, headers=headers)
#             print('response code',response)
#
#             if response.status_code == 200:
#                 print('response status',response)
#                 print('File uploaded successfully.')
#             else:
#                 print('File upload failed.')
#     except requests.exceptions.RequestException as e:
#         print('Error connecting to the server:', e)
# # Example usage
# file_path = r'C:\Users\abhis\Downloads\Sarla_Paul.zip'
# token = return_token()
# upload_file_with_token(file_path, token)
#
#
#
#
#
#
#
#
#
#


import requests

def return_token():
    url = 'http://127.0.0.1:8000/auththenticate/'
    email = 'angelopoulosc@gmail.com'
    password = 'Dent@123'

    data = {
        'email': email,
        'password': password
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()

        response_data = response.json()
        token = response_data.get('token')
        print(f"Token: {token}")
        return token
    except requests.exceptions.RequestException as e:
        print('Error connecting to the server:', e)
        return None

import jwt

def upload_file_with_token(file_path, token):
    if token is None:
        print('No token available. Server not running or token retrieval failed.')
        return

    url = 'http://127.0.0.1:8000/uploadfile/'
    headers = {'Authorization': token}
    print('headers',headers)

    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files, headers=headers)
            print('response',response)

            if response.status_code == 200:
                print('File uploaded successfully.')
            else:
                print('File upload failed.')
    except requests.exceptions.RequestException as e:
        print('Error connecting to the server:', e)

# Example usage
if __name__ == '__main__':
    file_path = r'C:\Users\abhis\Downloads\logo1.png'
    token = return_token()
    upload_file_with_token(file_path, token)



