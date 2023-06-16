from django.shortcuts import redirect, render
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
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Users
from Apiproject.settings import SECRET_KEY
import jwt
import requests
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Users,Patient,Organisation,ServiceOrder,IOSFile,OtherImageFile

import requests
import json
import requests
from django.core.exceptions import ObjectDoesNotExist
from api.tests import Get_Patient_Name,Get_stl_files,Azure_Connection,Dicomfiledatasave,Stlfilesave,Get_jpgpng_files,OtherFiles,Patient_Info_form_htmlfile,check_dicom_files_in_zip,checkfileextensions,is_file_object
from datetime import datetime,timedelta
from orthanc_rest_client import Orthanc
from requests.auth import HTTPBasicAuth


blob_service_client = BlobServiceClient.from_connection_string(
                    f"DefaultEndpointsProtocol=https;AccountName=dentreadstorage;AccountKey=D+0JUNhnESDOErn3cSOcDA645vLmxaF7RqPwR7RYWwd5aosXxNYkALlkWYS/1WAROESDe1nn76Eg+ASt9vYCqQ==;EndpointSuffix=core.windows.net"
                )

class AuthenticateView(APIView):
    print('yesss authentication')
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

            if user:
                payload = {'id': user.id,'email':user.email, 'exp': datetime.utcnow() + timedelta(minutes=100), 'iat': datetime.utcnow()}
                token = jwt.encode(payload, 'secret', algorithm='HS256')
                response['status'] = True
                response['token'] = token
                response['message'] = 'User logged in'
            else:
                response['message'] = 'Unauthorized request.'
                raise Exception('Unauthorized request.')

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

        userobj = Users.objects.get(id=payload['id'])
        org = Organisation.objects.get(id=userobj.orgid_id)
        print(payload)

        if 'file' not in request.FILES:
            return Response({'error': 'No file found in the request.'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES['file']
        print('true or false', is_file_object(file_obj))


        checkextension = checkfileextensions(file_obj)
        if checkextension in [".jpg", ".jpeg", ".png", ".pdf", ".html", ".htm"]:
            print('checkextension4567', checkextension)
            print('yess other file working and loading')
            Azure_Connection(file_obj, 'test petientname', org)
            return Response(
                {'message': 'File uploaded successfully to Azure Server.',
                 'filename': file_obj.name})
        elif checkextension == ".zip":
            file_path = file_obj.temporary_file_path()
            print('file_obj', type(file_obj))
            t = Timeout(read_timeout=1000, connection_timeout=1000)
            dicom_file = check_dicom_files_in_zip(file_path)
            print('dicom_file', dicom_file)

            if file_obj:
                print('running for dicom file')
                print('file obj here', file_obj)
                try:
                    if dicom_file == True:
                        print('running for 0000009', dicom_file)
                        auth = HTTPBasicAuth('dentread', 'dentread')
                        print('not running 777')
                        orthanc = Orthanc('http://127.0.0.1:8042', auth=auth, warn_insecure=False)
                        print('welll 7878', orthanc)
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

                            data = Dicomfiledatasave(Patient_name, org, ParentPatient, ParentStudy, StudyInstanceUID)
                            print('data', data)
                            tag = orthanc.get_study(j)
                            data = tag.get('MainDicomTags', None)
                            StudyInstanceUID = data.get('StudyInstanceUID')
                            print('StudyInstanceUID', StudyInstanceUID)
                        return Response(
                            {'message': 'File uploaded successfully to Orthanc server.', 'filename': file_obj.name})

                    try:
                        Patient11 = Patient_Info_form_htmlfile(file_obj, 'html')
                        print('Patient119900', Patient11)
                        if Patient11:
                            stl_data = Get_stl_files(file_obj,
                                                     '.stl, .obj, .ply, .fbx, .dae, .3ds, .blend, .dxf, .step, .stp, .igs, .iges, .x3d, .vrml, .amf, .gltf, .glb, .usdz, .3mf, .wrl')
                            azure_files = Azure_Connection(stl_data, Patient11, org)
                            print('azure_files', azure_files)
                            return Response(
                                {'message': 'File uploaded successfully to Azure Server.', 'filename': file_obj.name})

                    except Exception as e:
                        return Response({'error': f'Error occurred during file upload: {str(e)}'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                except pydicom.errors.InvalidDicomError:
                    return Response({'error': 'Invalid file.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': "failed to upload file"})
        else:
            return Response({'message': "file not accepted"})


class DownloanFile(APIView):
    def get(self, request):
        data = request.data
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except Exception as e:
            return Response({'error': 'token expired'}, status=status.HTTP_400_BAD_REQUEST)

        if data.get('type') == 1 or data.get('type') == 3:
            try:
                userobj = Users.objects.get(id=payload['id'])
                org = Organisation.objects.get(id=userobj.orgid_id)
                print(payload)
                container_name = 'dentread-blob'
                if data.get('type') == 1:
                    file_record = IOSFile.objects.get(id=399, orgid=130)
                elif data.get('type') == 3:
                    file_record = OtherImageFile.objects.get(id=53, orgid=130)
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_record.fileName)
                download_stream = blob_client.download_blob()
                response = HttpResponse(download_stream.readall(),
                                        content_type=blob_client.get_blob_properties().content_settings.content_type)
                response['Content-Disposition'] = f'attachment; filename="{file_record.fileName}"'
                print('response file name', response['Content-Disposition'])
                return response
            except Exception as e:
                return Response({'status': False, 'message': 'download failed'})

        elif data.get('type') == 2:
            line_item = ServiceOrder.objects.get(id=5774, orgid=130)
            url = 'http://127.0.0.1:8042/studies/' + str(line_item.ParentStudy) + '/archive'
            auth = HTTPBasicAuth('dentread', 'dentread')
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                response_headers = response.headers
                # Extract the filename from the Content-Disposition header, if available
                content_disposition = response_headers.get('content-disposition')
                if content_disposition:
                    file_name = content_disposition.split('filename=')[1].strip('"')
                else:
                    file_name = 'downloaded_file.dcm'  # Default filename if content-disposition is not provided
                # Create a new HttpResponse object
                http_response = Response(content_type=response_headers['content-type'])
                # Set the content-disposition header for the response
                http_response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                # Write the file content to the response
                http_response.content = response.content
                return http_response
            else:
                return Response('Failed to download file.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response('Failed to download file.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)




































# #ttest codes
# from datetime import datetime
# current_datetime = datetime.now()
# formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
#
# # File Upload Functions
# def uploadLabData(id, pk, f):
#     usr = Users.objects.get(id=id)
#     org = Organisation.objects.get(id=usr.orgid_id)
#     service_order = ServiceOrder.objects.get(id=pk)
#     file_name = f.name
#     # blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
#     # blob_client.upload_blob(f)
#     blob_service_client = BlobServiceClient.from_connection_string(
#             f"DefaultEndpointsProtocol=https;AccountName=dentreadstorage;AccountKey=D+0JUNhnESDOErn3cSOcDA645vLmxaF7RqPwR7RYWwd5aosXxNYkALlkWYS/1WAROESDe1nn76Eg+ASt9vYCqQ==;EndpointSuffix=core.windows.net"
#         )
#     container_name = 'dentread-blob'
#     file_with_time = file_name + str(formatted_datetime)
#
#     print('yess here uploaded')
#
#     blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_with_time)
#     blob_client.upload_blob(f)
#     sfile = IOSFile(file=f, fileName=f.name, repid=service_order.id, orgid=org, size=f.size, pid=service_order.pid)
#     sfile.save()
#
# from datetime import date, datetime
# def uploadOtherImage(id, pk, file):
#     usr = Users.objects.get(id=id)
#     org = Organisation.objects.get(id=usr.orgid_id)
#     service_order = ServiceOrder.objects.get(id = pk)
#     file_name = file.name
#     blob_service_client = BlobServiceClient.from_connection_string(
#             f"DefaultEndpointsProtocol=https;AccountName=dentreadstorage;AccountKey=D+0JUNhnESDOErn3cSOcDA645vLmxaF7RqPwR7RYWwd5aosXxNYkALlkWYS/1WAROESDe1nn76Eg+ASt9vYCqQ==;EndpointSuffix=core.windows.net"
#         )
#     container_name = 'dentread-blob'
#
#     file_with_time = file_name + str(formatted_datetime)
#     print('yess here upload other')
#
#     blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_with_time)
#     blob_client.upload_blob(file)
#     print('yess here upload other2323')
#
#     sfile = OtherImageFile(file = file, thumbnail = file, repid = service_order.id, orgid = org, fileName = file.name, size = file.size, pid = service_order.pid, date = date.today())
#     sfile.save()
#
#
# from apiron import Timeout
# import threading
# import zipfile
# class UploadDcm(threading.Thread):
#     def __init__(self, f, pk):
#         self.f = f.read()
#         self.pk = pk
#         threading.Thread.__init__(self)
#     def run(self):
#         t = Timeout(read_timeout=1000, connection_timeout=1000)
#         from orthanc_rest_client import Orthanc
#         from requests.auth import HTTPBasicAuth
#         auth = HTTPBasicAuth('dentread', 'dentread')
#         orthanc = Orthanc(settings.ORTHANC_UPLOAD_URL, auth=auth, warn_insecure=False)
#         ort = orthanc.add_instance(self.f, timeout_spec=t)
#         for i in ort:
#             ParentPatient = i.get('ParentPatient', None)
#             ParentStudy = i.get('ParentStudy', None)
#             instance = i.get('ID', None)
#             Path = i.get('Path', None)
#             for i in ParentPatient:
#                 i = ParentPatient
#             for j in ParentStudy:
#                 j = ParentStudy
#             for k in instance:
#                 k = instance
#             for l in Path:
#                 l = Path
#
#             tag = orthanc.get_study(j)
#             data = tag.get('MainDicomTags', None)
#             StudyInstanceUID = data.get('StudyInstanceUID')
#             service_order = ServiceOrder.objects.get(id=self.pk)
#             service_order.ParentPatient = i
#             service_order.ParentStudy = j
#             service_order.StudyInstanceUID = StudyInstanceUID
#             service_order.upload = "uploaded"
#             service_order.instance = k
#             service_order.Path = l
#             service_order.save()
#             if service_order.instance != None:
#                 auth = HTTPBasicAuth('dentread', 'dentread')
#                 url = 'http://demo.dentread.com:8042' + '/instances/' + str(service_order.instance) + '/preview'
#                 params = {"quality": 100}
#                 headers = {
#                 "Content-Type": "image/jpeg",
#                 }
#                 response = requests.get(url, headers=headers, auth = auth, params=params)
#                 a = str(service_order.name)
#                 filename = a.replace(" ", "_")
#                 sink_path = 'static/dicomThumb/'+filename
#                 try:
#                     if response.status_code == 200:
#                         data = response.content
#                         with open(str(sink_path)+".png", "wb") as f:
#                             f.write(response.content)
#                             f.close()
#                         service_order.thumbnail = sink_path + '.png'
#                         service_order.save()
#                 except Exception as e:
#                     print(e)
#
#
# def uploadDcmFile(pk, file):
#     service_order = ServiceOrder.objects.get(id = pk)
#     service_order.file = file.name
#     service_order.size = file.size
#     service_order.save()
#     UploadDcm(file, pk).start()
#
# # detect the file from the Zip
# def checkTheFile(file):
#     my_ext_first = ['.stl', '.obj', '.ply', '.fbx', '.dae', '.3ds', '.blend', '.dxf', '.step', '.stp', '.igs', '.iges', '.x3d', '.vrml', '.amf', '.gltf', '.glb', '.usdz', '.3mf', '.wrl']
#     my_ext_second = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.ico', '.webp', '.jp2']
#     result_ext  = ''
#     file_name = file.name
#     with zipfile.ZipFile(file, 'r') as zip_file:
#
#         for file_info in zip_file.infolist():
#             filename = file_info.filename
#             print('filename here',filename)
#             file_size = file_info.file_size
#             if any(filename.endswith(ext) for ext in my_ext_first):
#                 result_ext = 'iosFile'
#             elif file_name.endswith(tuple(my_ext_second)):
#                 result_ext = 'otherImageFile'
#             else:
#                 result_ext = 'dicomFile'
#     return result_ext
#
#
#
# class UploadFiles(APIView):
#     def post(self, request):
#         try:
#             token = request.META.get('HTTP_AUTHORIZATION')
#             payload = jwt.decode(token, 'secret', algorithm=['HS256'])
#         except Exception as e:
#             return Response({'error': 'token expired'}, status=status.HTTP_400_BAD_REQUEST)
#         f = request.FILES['file']
#         usr = Users.objects.get(id=payload['id'])
#         org = Organisation.objects.get(id=usr.orgid_id)
#         patient = Patient(name = 'Latest_Patient' + str(org.orgname), orgid = org, locate = org.orgname, gender = 'select', age = 0)
#         patient.save()
#         service_order = ServiceOrder(orgid = org, pid = patient.id, locate = org.orgname, gender = patient.gender , age = patient.age, refpt_orgid = org.id)
#         service_order.save()
#         if f:
#             f_ext = checkTheFile(f)
#             print('check images f_ext',f_ext)
#             if f_ext == 'iosFile':
#                 uploadLabData(payload['id'],service_order.id, f)
#                 return Response({"message":"file successfully uploaded on azure server"})
#             elif f_ext == 'otherImageFile':
#                 uploadOtherImage(payload['id'],service_order.id, f)
#                 return Response({"message":"file successfully uploaded on azure server"})
#             else:
#                 uploadDcmFile(service_order.id, f)
#                 return Response({"message":"file successfully uploaded on orthanc server "})
#         else:
#             return Response({'error': 'Please choose a file first.'}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"message":"something went wrong"})



