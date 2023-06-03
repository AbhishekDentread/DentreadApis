from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.hashers import make_password
from api.models import Users
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate
import pydicom
# Create your views here.
from azure.storage.blob import BlobServiceClient, ContentSettings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
import jwt
import pydicom
from apiron import Timeout
import datetime

import jwt
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Users
from Apiproject.settings import SECRET_KEY
import jwt
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Users,Patient,Organisation,ServiceOrder,IOSFile
import requests
import json
import requests
from django.core.exceptions import ObjectDoesNotExist
from api.tests import Get_Patient_Name,Patient_Info_form_htmlfile,Get_stl_files


class AuthenticateView(APIView):
    def post(self, request):
        response = {
            'status': False,
            'message': 'Something went wrong',
            'token': '',
            'payload': ''
        }
        data = request.data
        try:
            if not (data.get('email') or data.get('contact')):
                response['message'] = 'Please enter email or contact'
                raise Exception('Please enter email or contact')

            if not data.get('password'):
                response['message'] = 'Authentication failed'
                raise Exception('Authentication failed')

            if data.get('email'):
                user = Users.objects.filter(email=data.get('email'), password=data.get('password')).first()
            else:
                user = Users.objects.filter(contact=data.get('contact'), password=data.get('password')).first()

            if user is None:
                response['message'] = 'Unauthorized request.'
                raise Exception('Unauthorized request.')

            payload = {'id': user.id,'email':user.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=100),
                       'iat': datetime.datetime.utcnow()}
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            response['status'] = True
            response['token'] = token
            response['message'] = 'User logged in'

        except Exception as e:
            response['message'] = str(e)

        return Response(response)



class OrthancUploadfile(APIView):
    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except Exception as e:
            return Response({'error': 'token expired'}, status=status.HTTP_400_BAD_REQUEST)


        print(payload)
        # Check if the 'file' key exists in the request.FILES dictionary
        if 'file' not in request.FILES:
            return Response({'error': 'No file found in the request.'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtain the uploaded file from the request
        file_obj = request.FILES['file']
        t = Timeout(read_timeout=1000, connection_timeout=1000)
        # Patient_name = Check_Html_File(file_obj, 'html')
        # print('files_with_extensions', Patient_name)

        userobj = Users.objects.get(id=payload['id'])
        org = Organisation.objects.get(id=userobj.orgid_id)
        orgname = org.orgname

        Patient_name = Patient_Info_form_htmlfile(file_obj,'html')
        if Patient_name:
            print('Patient_Info_form_htmlfile',Patient_name)
            stl_data = Get_stl_files(file_obj, 'stl,ply,obj')
            for file_name, extension in stl_data:
                filename = file_name + '.' + extension
                try:
                    Patient_re = Patient.objects.get(name=Patient_name, orgid=org)
                    Patient_re.name = Patient_name
                    Patient_re.orgid = org
                    Patient_re.locate = orgname
                    Patient_re.gender = 'select'
                    Patient_re.age = 0
                    Patient_re.save()
                    print('Patient_re', Patient_re)

                except Exception as e:
                    Patient_re = Patient(name=Patient_name, orgid=org, locate=orgname, gender='select', age=0)
                    Patient_re.save()
                    

                try:
                    iosdata = IOSFile.objects.get(orgid = org,fileName=filename)
                    iosdata.org = org
                    iosdata.fileName = filename
                    iosdata.pid = Patient_re.id
                except Exception as e:
                    IOSFile.objects.create(orgid = org,fileName=filename,pid=Patient_re.id,file=filename)

        else:
            try:
                # Read the DICOM file using pydicom
                from orthanc_rest_client import Orthanc
                from requests.auth import HTTPBasicAuth
                auth = HTTPBasicAuth('dentread', 'dentread')
                orthanc = Orthanc('http://demo.dentread.com:8042', auth=auth, warn_insecure=False)
                ort = orthanc.add_instance(file_obj.read(), timeout_spec=t)
                print('ort', ort)
                for i in ort:
                    ParentPatient = i.get('ParentPatient', None)
                    print('ParentPatient', ParentPatient)
                    ParentStudy = i.get('ParentStudy', None)
                    StudyInstanceUID = i.get('StudyInstanceUID')
                    instance = i.get('ID', None)
                    print('instance_id12345', instance)
                    print('ParentStudy', ParentStudy)
                    for i in ParentPatient:
                        i = ParentPatient
                        print('iiii', i)
                    for j in ParentStudy:
                        j = ParentStudy
                        print('jjjjj', j)
                    tag = orthanc.get_study(j)
                    data = tag.get('MainDicomTags', None)
                    StudyInstanceUID = data.get('StudyInstanceUID')
                    Patient_name = Get_Patient_Name(ParentPatient)
                    print('Patient_name12', Patient_name)



                    try:
                        Patient_re = Patient.objects.get(name=Patient_name, orgid=org)
                        Patient_re.name = Patient_name
                        Patient_re.orgid = org
                        Patient_re.locate = orgname
                        Patient_re.gender = 'select'
                        Patient_re.age = 0
                        Patient_re.save()
                        print('Patient_re', Patient_re)

                    except Exception as e:
                        Patient_re = Patient(name=Patient_name, orgid=org, locate=orgname, gender='select', age=0)
                        Patient_re.save()
                    try:
                        get_order = ServiceOrder.objects.get(ParentPatient=ParentPatient,
                                                             ParentStudy=ParentStudy,
                                                             StudyInstanceUID=StudyInstanceUID,
                                                             )
                        get_order.ParentPatient = ParentPatient
                        get_order.ParentStudy = ParentStudy
                        get_order.StudyInstanceUID = StudyInstanceUID
                        get_order.orgid = org
                        get_order.pid = Patient_re.id
                        get_order.locale = orgname
                        get_order.gender = 'select'
                        get_order.age = 0
                    except Exception as e:
                        ServiceOrder.objects.create(ParentPatient=ParentPatient,
                                                    ParentStudy=ParentStudy,
                                                    StudyInstanceUID=StudyInstanceUID,
                                                    orgid=org,
                                                    pid=Patient_re.id, locale=orgname, gender='select', age=0)
                    tag = orthanc.get_study(j)
                    data = tag.get('MainDicomTags', None)
                    StudyInstanceUID = data.get('StudyInstanceUID')
                    print('StudyInstanceUID', StudyInstanceUID)

                try:
                    if ort:
                        return Response(
                            {'message': 'File uploaded successfully to Orthanc server.', 'filename': file_obj.name, })
                    else:
                        return Response({'error': 'Failed to upload file to Orthanc server.'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                except Exception as e:
                    return Response({'error': f'Error occurred during file upload: {str(e)}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except pydicom.errors.InvalidDicomError:
                return Response({'error': 'Invalid DICOM file.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'stl data': 'stl data'})




class FileUploadView(APIView):
    def post(self, request):
        file_obj = request.FILES['file']

        # Create a BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(
            f"DefaultEndpointsProtocol=https;AccountName=dentreadstorage;AccountKey=D+0JUNhnESDOErn3cSOcDA645vLmxaF7RqPwR7RYWwd5aosXxNYkALlkWYS/1WAROESDe1nn76Eg+ASt9vYCqQ==;EndpointSuffix=core.windows.net"
        )

        # Set container name and file name
        container_name = 'demo-static-storage'
        file_name = file_obj.name

        # Get a reference to the container
        container_client = blob_service_client.get_container_client(container_name)

        # Upload the file to Azure Blob Storage
        blob_client = container_client.get_blob_client(file_name)
        blob_client.upload_blob(file_obj, overwrite=True, content_settings=ContentSettings(content_type=file_obj.content_type))

        # Return the URL of the uploaded file
        file_url = f"https://dentreadstorage.blob.core.windows.net/{container_name}/{file_name}"
        return Response({'file_url': file_url})


class FileUploader(APIView):
    def post(self,request):
        response = {
            'status': False,
            'message': 'Something went wrong',
            'token': '',
            'payload': ''
        }
        token = request.META.get('HTTP_AUTHORIZATION')
        payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        print(payload['id'])

        return Response({"token":payload,})