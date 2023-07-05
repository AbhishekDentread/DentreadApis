import sys

from django.shortcuts import render
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model()
from apiron import Timeout
import jwt
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from api.tests import *
from datetime import datetime,timedelta
from orthanc_rest_client import Orthanc
from requests.auth import HTTPBasicAuth
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


blob_service_client = BlobServiceClient.from_connection_string(
                    f"DefaultEndpointsProtocol=https;AccountName=dentreadstorage;AccountKey=D+0JUNhnESDOErn3cSOcDA645vLmxaF7RqPwR7RYWwd5aosXxNYkALlkWYS/1WAROESDe1nn76Eg+ASt9vYCqQ==;EndpointSuffix=core.windows.net"
                )


class AuthView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'contact': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['password']
        ),
        responses={
            200: openapi.Response(
                description='Successful login',
                examples={
                    'application/json': {
                        'status': True,
                        'message': 'You are logged in',
                        'token': 'your_token',
                        'payload': {
                            'id': 'user_id',
                            'email': 'user_email',
                            'exp': 'expiration_date',
                            'iat': 'issued_at_date'
                        }
                    }
                }
            ),
            400: openapi.Response(
                description='Unauthorized request',
                examples={
                    'application/json': {
                        'status': False,
                        'message': 'Unauthorized request',
                        'token': '',
                        'payload': ''
                    }
                }
            )
        }
    )
    def post(self, request):
        print('yesss authentication4')
        response = {
            'status': False,
            'message': 'Something went wrong',
            'token': '',
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
                payload = {'id': user.id,'email':user.email, 'exp': datetime.utcnow() + timedelta(days=7), 'iat': datetime.utcnow()}
                token = jwt.encode(payload, 'secret', algorithm='HS256')
                print('token len',len(token))

                response['status'] = True
                response['token'] = token
                response['message'] = 'you are logged in'
            else:
                response['message'] = 'Unauthorized request.'
                raise Exception('Unauthorized request.')

        except Exception as e:
            response['message'] = str(e)
        return Response(response)


class UploadFileView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE),
            },
            required=['file']
        ),
        responses={
            200: openapi.Response(
                description='File uploaded successfully',
                examples={
                    'application/json': {
                        'message': 'File uploaded successfully',
                        'filename': 'uploaded_file_name'
                    }
                }
            ),
            400: openapi.Response(
                description='Failed to upload file',
                examples={
                    'application/json': {
                        'message': 'Failed to upload file'
                    }
                }
            )
        }
    )
    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        auth = request.META.get('HTTP_AUTH')
        print('auth data',type(auth))


        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except Exception as e:
            return Response({'error': 'token expired'}, status=status.HTTP_400_BAD_REQUEST)


        userobj = Users.objects.get(id=payload['id'])
        org = Organisation.objects.get(id=userobj.orgid_id)
        print('org data',org.uniquekey)

        if str(org.uniquekey) != str(auth):
            print('Unauthorized access')
            return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)

        print('org check',org)


        print(payload)
        if 'file' not in request.FILES:
            return Response({'error': 'No file found in the request.'}, status=status.HTTP_400_BAD_REQUEST)
        file_obj = request.FILES['file']

        file_extension = checkfileextension(file_obj)
        if file_extension in [".jpg", ".jpeg", ".png", ".pdf", ".html", ".htm"]:
            print('checkextension4567', file_extension)
            print('yess other file working and loading')
            otherisd = azure_connection(file_obj, 'test petientname', org,file_extension, payload['id'])
            if otherisd:
                request.session['fileid'] = otherisd


            return Response(
                {'message': 'File uploaded successfully to Azure Server.',
                 'filename': file_obj.name,'id':request.session.get('fileid')})
        elif file_extension == ".zip":
            try:
                file_path = file_obj.temporary_file_path()
                print('file_obj', type(file_obj))
                t = Timeout(read_timeout=1000, connection_timeout=1000)
                dicom_file = check_dicom_files_in_zip(file_path)
                print('dicom_file', dicom_file)
            except Exception as e:
                return Response({"message":"This File is not allowed"})



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
                            parent_patient = i.get('ParentPatient', None)
                            print('parent_patient', parent_patient)
                            parent_study = i.get('ParentStudy', None)
                            instance = i.get('ID', None)
                            print('instance_id12345', instance)
                            print('parent_study', parent_study)
                            for i in parent_patient:
                                i = parent_patient
                                print('iiii', i)
                            for j in parent_study:
                                j = parent_study
                                print('jjjjj', j)
                            tag = orthanc.get_study(j)
                            data = tag.get('MainDicomTags', None)
                            study_instanceuid = data.get('StudyInstanceUID')
                            Patient_name = get_patient_name(parent_patient)
                            print('Patient_name12', Patient_name)

                            fileid = dicomfilesavedata(Patient_name,payload['id'], org, parent_patient, parent_study, study_instanceuid)
                            print('data', fileid)

                            if fileid:
                                request.session['fileid'] = fileid

                            tag = orthanc.get_study(j)
                            data = tag.get('MainDicomTags', None)
                            study_instanceuid = data.get('StudyInstanceUID')
                            print('study_instanceuid', study_instanceuid)

                        return Response(
                            {'message': 'File uploaded successfully to Orthanc server.', 'filename': file_obj.name, "id":request.session.get('fileid')})
                    try:
                        patient_info = patient_info_form_htmlfile(file_obj, 'html')
                        print('Patient119900', patient_info)
                        if patient_info:
                            stl_data = get_stl_files(file_obj,
                                                     '.stl, .obj, .ply, .fbx, .dae, .3ds, .blend, .dxf, .step, .stp, .igs, .iges, .x3d, .vrml, .amf, .gltf, .glb, .usdz, .3mf, .wrl')
                            azure_files = azure_connection(stl_data, patient_info, org,file_extension, payload['id'])
                            if azure_files:
                                request.session['fileid'] = azure_files
                                print('azure_files', azure_files)

                            return Response(
                                {'message': 'File uploaded successfully to Azure Server.', 'filename': file_obj.name,'id':request.session.get('fileid')})
                    except Exception as e:
                        return Response({'error': f'Error occurred during file upload: {str(e)}'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except pydicom.errors.InvalidDicomError:
                    return Response({'error': 'Invalid file.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': "failed to upload file"})
        else:
            return Response({'message': "This file format is not allowed"})

class DownloanFileView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='type',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='Type of file to download',
                enum=[1, 2, 3],
            ),
            openapi.Parameter(
                name='id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='ID of the file to download',
            ),
        ],
        responses={
            200: openapi.Response(
                description='File downloaded successfully',
                content={
                    'application/octet-stream': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary',
                        }
                    }
                }
            ),
            400: openapi.Response(
                description='Failed to download file',
                examples={
                    'application/json': {
                        'message': 'Failed to download file'
                    }
                }
            )
        }
    )
    def get(self, request):
        data = request.data

        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except Exception as e:
            return Response({'error': 'token expired'}, status=status.HTTP_400_BAD_REQUEST)
        userobj = Users.objects.get(id=payload['id'])
        org = Organisation.objects.get(id=userobj.orgid_id)

        if data.get('type') == 1 or data.get('type') == 3:
            try:

                print('org lation',org)
                container_name = 'dentread-blob'
                if data.get('type') == 1:
                    print('going ....')
                    file_record = Pushed_File_Data.objects.get(id=data.get('id'), pmd_data__orgid_id=org)
                elif data.get('type') == 3:
                    file_record = Pushed_File_Data.objects.get(id=data.get('id'), pmd_data__orgid_id=org)
                    print('file_record',file_record)
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_record.filename)
                download_stream = blob_client.download_blob()
                response = HttpResponse(download_stream.readall(),
                                        content_type=blob_client.get_blob_properties().content_settings.content_type)
                response['Content-Disposition'] = f'attachment; filename="{file_record.filename}"'
                print('response file name', response['Content-Disposition'])
                return response
            except Exception as e:
                return Response({'status': False, 'message': 'download failed'})

        elif data.get('type') == 2:
            print('yess work')
            line_item = Pushed_File_Data.objects.get(id=data.get('id'), pmd_data__orgid_id=org)
            print('line_item',line_item)
            url = 'http://127.0.0.1:8042/studies/' + str(line_item.parentstudy) + '/archive'
            print('url',url)
            auth = HTTPBasicAuth('dentread', 'dentread')
            response = requests.get(url, auth=auth)
            print('working fine but')
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
                return Response({'message':'Failed to download file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'message':'Failed to download file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def apidocuments(request):
    return render(request,'apidocuments.html')










