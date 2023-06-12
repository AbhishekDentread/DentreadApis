# from django.test import TestCase
#
import zipfile
import requests
from bs4 import BeautifulSoup
from azure.storage.blob import BlobServiceClient, ContentSettings
from .models import Users,Patient,Organisation,ServiceOrder,IOSFile,OtherImageFile
import datetime

def Patient_Info_form_htmlfile(zip_file_path, extensions):
    files_with_extensions = ''
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        for file_info in zip_file.infolist():
            filename = file_info.filename
            if '.' in filename:
                file_name, extension = filename.split('.', 1)
                if extension in extensions:

                    html_content = zip_file.read(filename)
                    soup = BeautifulSoup(html_content, 'html.parser')

                    # Find all span tags with class "patient-name"
                    patient_name_tags = soup.find_all('font')

                    if len(patient_name_tags) >= 4:
                        patient_name = patient_name_tags[3].text
                        ds = patient_name[9:]
                        pn = ds.replace(',', '')
                        print(pn)
                        files_with_extensions = pn
    return files_with_extensions

def Get_Patient_Name(ParentPatient):
    patientname = ''
    url = 'http://demo.dentread.com:8042/patients/' + ParentPatient
    username = 'dentread'
    password = 'dentread'

    response = requests.get(url, auth=(username, password))
    response.raise_for_status()  # Raise an exception for non-2xx status codes
    data = response.json()
    Patient_name = data['MainDicomTags']['PatientName']
    Patient_name = Patient_name.replace('^', ' ')
    patientname = Patient_name
    return patientname

def Get_stl_files(zip_file_path, extensions):
    files_with_extensions = []
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        for file_info in zip_file.infolist():
            filename = file_info.filename
            if '.' in filename:
                file_name, extension = filename.split('.', 1)
                if extension in extensions:
                    file_size = file_info.file_size
                    file_object = zip_file.open(filename)
                    files_with_extensions.append((file_name, extension, file_size,file_object))
    return files_with_extensions

def Get_jpgpng_files(zip_file_path, extensions):

    files_with_extensions = []
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        for file_info in zip_file.infolist():
            filename = file_info.filename
            if '.' in filename:
                file_name, extension = filename.split('.', 1)
                if extension in extensions:
                    file_size = file_info.file_size
                    print('the JPEG story',file_name)
                    files_with_extensions.append((file_name, extension, file_size))
    return files_with_extensions   


def Dicomfiledatasave(Patient_name,org,ParentPatient,ParentStudy,StudyInstanceUID):
    try:
        Patient_re = Patient.objects.get(name=Patient_name, orgid=org)
        print('Patient_re1010',Patient_re)
    except Exception as e:
        Patient_re = Patient(name = Patient_name, orgid=org, locate=org.orgname, gender='select', age=0)
        Patient_re.save()
        print('Patient_re1111',Patient_re)
        
    try:
        get_order = ServiceOrder.objects.get(ParentPatient=ParentPatient, ParentStudy=ParentStudy, StudyInstanceUID=StudyInstanceUID)
        get_order.ParentPatient = ParentPatient
        get_order.ParentStudy = ParentStudy
        get_order.StudyInstanceUID = StudyInstanceUID
        get_order.save()
        print('get_order1010',get_order)
    except Exception as e:
        serviceorder_create = ServiceOrder.objects.create(ParentPatient = ParentPatient, ParentStudy = ParentStudy, StudyInstanceUID=StudyInstanceUID,
                                                    orgid=org, pid=Patient_re.id, locate=org.orgname, gender='select', age=0,refpt_orgid = org.id)
        serviceorder_create.repid = serviceorder_create.id
        serviceorder_create.save()
        print('serviceorder_create1111',serviceorder_create)


def Stlfilesave(Patient11,org,filename,file_size):
    try:
        Patient_re = Patient.objects.get(name=Patient11, orgid=org)
        print('Patient_re', Patient_re)
        print('Patient_re1010',Patient_re)
    except Exception as e:
        Patient_re = Patient(name=Patient11, orgid=org, locate=org.orgname, gender='select', age=0)
        Patient_re.save()
        print('Patient_re1111',Patient_re)

    serviceorder_create = ServiceOrder.objects.create(
        orgid=org,
        pid=Patient_re.id, locate=org.orgname, gender='select', age=0,refpt_orgid = org.id)  
    print('serviceorder_create1010',serviceorder_create)    

    serviceorder_create.repid = serviceorder_create.id
    serviceorder_create.save()

    IOSFile.objects.create(orgid = org,fileName=filename,pid=Patient_re.id,file=filename,repid = serviceorder_create.id,size = file_size)
    print('IOSFile1010',IOSFile)     


def OtherFiles(peteintname,org,filename,file_size):
    try:
        Patient_re = Patient.objects.get(name=peteintname)
        print('Patient_re', Patient_re)
        print('Patient_re1010',Patient_re)
    except Exception as e:
        Patient_re = Patient(name=peteintname, orgid=org, locate=org.orgname, gender='select', age=0)
        Patient_re.save()
        print('Patient_re1111',Patient_re)
    serviceorder_create = ServiceOrder.objects.create(
        orgid=org,
        pid=Patient_re.id, locate=org.orgname, gender='select', age=0,refpt_orgid = org.id)  
    print('serviceorder_create1010',serviceorder_create)
    serviceorder_create.repid = serviceorder_create.id
    serviceorder_create.save()
    OtherImageFile.objects.create(orgid = org,fileName=filename,pid=Patient_re.id,file=filename,repid = serviceorder_create.id,size = file_size)
    print('OtherImageFile',IOSFile)      


def Azure_Connection(file_obj,petient,org):
    print('petient data',petient)
    print('azure connect',file_obj)
    print('azure connect',type(file_obj))
    blob_service_client = BlobServiceClient.from_connection_string(
            f"DefaultEndpointsProtocol=https;AccountName=dentreadstorage;AccountKey=D+0JUNhnESDOErn3cSOcDA645vLmxaF7RqPwR7RYWwd5aosXxNYkALlkWYS/1WAROESDe1nn76Eg+ASt9vYCqQ==;EndpointSuffix=core.windows.net"
        )
    container_name = 'dentread-blob'
    from datetime import datetime
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(file_obj, list):
        for file_info in file_obj:
            file_name, extension, file_size, file_object = file_info
            print('file_object12',file_object)
            print('file_object12',type(file_object))

            file_with_time = file_name + str(formatted_datetime) + '.' + extension

            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_with_time)
            blob_client.upload_blob(file_object)
            Stlfilesave(petient, org, file_with_time, file_size)
    else:
        file_name = file_obj.name
        filesize = file_obj.size
        file_with_time = file_name + str(formatted_datetime)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_with_time)
        blob_client.upload_blob(file_obj)
        print('file_object15',file_obj)
        print('file_object15',type(file_obj))
        OtherFiles(petient,org,file_obj,filesize)


        
import pydicom


def check_dicom_files_in_zip(file_obj):
    dicom_extensions = ['.dcm', '.ima', '.dicom']

    with zipfile.ZipFile(file_obj, 'r') as zip_file:
        for name in zip_file.namelist():
            if any(name.lower().endswith(ext) for ext in dicom_extensions):
                with zip_file.open(name) as file:
                    try:
                        dicom_file = pydicom.dcmread(file)
                        print(f"{name} is a valid DICOM file.")
                        print('dicom_file length', len(dicom_file))
                        return True
                    except pydicom.errors.DicomError:
                        print(f"{name} is not a valid DICOM file.")
    return False

import os
def checkfileextensions(file):
    # Example usage
    file_name = file.name
    file_extension = os.path.splitext(file_name)[1].lower()

    if file_extension == ".zip":
        return file_extension

    elif file_extension in [".jpg", ".jpeg", ".png",".pdf",".html",".htm"]:
        return file_extension

import io

def is_file_object(obj):
    return isinstance(obj, io.IOBase)










