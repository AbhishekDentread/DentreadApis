import zipfile
import requests
from bs4 import BeautifulSoup
from azure.storage.blob import BlobServiceClient, ContentSettings
from .models import Users,Patient,Organisation,ServiceOrder,IOSFile,OtherImageFile, Push_Meta_Data , Pushed_File_Data
from datetime import datetime
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
import pydicom
import sys


def patient_info_form_htmlfile(zip_file_path, extensions):
    files_with_extensions = ''
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        for file_info in zip_file.infolist():
            filename = file_info.filename
            if '.' in filename:
                file_name, extension = filename.split('.', 1)
                if extension in extensions:
                    html_content = zip_file.read(filename)
                    soup = BeautifulSoup(html_content, 'html.parser')
                    patient_name_tags = soup.find_all('font')

                    if len(patient_name_tags) >= 4:
                        patient_name = patient_name_tags[3].text
                        ds = patient_name[9:]
                        pn = ds.replace(',', '')
                        print(pn)
                        files_with_extensions = pn
    return files_with_extensions


def get_patient_name(ParentPatient):
    patientname = ''
    url = 'http://127.0.0.1:8042/patients/' + ParentPatient
    username = 'dentread'
    password = 'dentread'

    response = requests.get(url, auth=(username, password))
    response.raise_for_status()
    data = response.json()
    Patient_name = data['MainDicomTags']['PatientName']
    Patient_name = Patient_name.replace('^', ' ')
    patientname = Patient_name
    return patientname


def get_stl_files(zip_file_path, extensions):
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


def dicomfilesavedata(patient_name, userid ,org, parentpatient, parentstudy, studyinstanceuid):
    print('comming org id',org)
    try:
        Patient_re = Push_Meta_Data.objects.get(patiant=patient_name, orgid=org)
        print('Patient_re1010',Patient_re)
    except Exception as e:
        Patient_re = Push_Meta_Data(patiant = patient_name, orgid=org, userid=userid)
        Patient_re.save()
        print('Patient_re1111',Patient_re)

    try:
        get_order = Pushed_File_Data.objects.get(parentpatienintances=parentpatient, parentstudy=parentstudy, stydyinstanceUID=studyinstanceuid)
        get_order.parentpatienintances = parentpatient
        get_order.parentstudy = parentstudy
        get_order.stydyinstanceUID = studyinstanceuid
        get_order.save()
        print('get_order1010',get_order)
    except Exception as e:
        serviceorder_create = Pushed_File_Data.objects.create(parentpatienintances = parentpatient, parentstudy = parentstudy, stydyinstanceUID=studyinstanceuid,
                                                    pmd_data=Patient_re)
        serviceorder_create.save()
        print('serviceorder_create1111',serviceorder_create)
        return serviceorder_create.id


def stlfilesave(patient, org, filename, filesize , userid):
    try:
        patientobj = Push_Meta_Data.objects.get(patiant=patient, orgid=org)

    except Exception as e:
        patientobj = Push_Meta_Data(patiant=patient, orgid=org, userid=userid)
        patientobj.save()
    pushedfile = Pushed_File_Data.objects.create(filename=filename,filesize = filesize, pmd_data = patientobj)
    pushedfile.save()
    return pushedfile.id


def OtherFiles(peteintname, org, filename, filesize, userid):
    try:
        patientobj = Push_Meta_Data.objects.get(name=peteintname)

    except Exception as e:
        patientobj = Push_Meta_Data(patiant=peteintname, orgid=org, userid=userid)
        patientobj.save()

    file_name_with_timezone = f'{formatted_datetime}_{filename}'
    Pusheddata = Pushed_File_Data.objects.create(filename=file_name_with_timezone,filesize = filesize,pmd_data=patientobj)
    Pusheddata.save()
    return Pusheddata.id

import uuid

def azure_connection(file_obj, petient, org, file_extension, userid):
    unique_identifier = str(uuid.uuid4())[:8]
    ids = []
    print('petient data',petient)
    print('azure connect',file_obj)
    print('azure connect',type(file_obj))
    blob_service_client = BlobServiceClient.from_connection_string(
            f"DefaultEndpointsProtocol=https;AccountName=dentreadstorage;AccountKey=D+0JUNhnESDOErn3cSOcDA645vLmxaF7RqPwR7RYWwd5aosXxNYkALlkWYS/1WAROESDe1nn76Eg+ASt9vYCqQ==;EndpointSuffix=core.windows.net"
        )
    container_name = 'dentread-blob'

    if isinstance(file_obj, list):
        for file_info in file_obj:
            file_name, extension, file_size, file_object = file_info
            print('file_object12',file_object)
            print('file_object12',type(file_object))

            file_with_time = file_name + str(formatted_datetime) + '.' + extension

            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_with_time)
            blob_client.upload_blob(file_object)
            stlfile = stlfilesave(petient, org, file_with_time, file_size, userid)
            ids.append(stlfile)
        return ids
    else:
        file_name = file_obj.name
        filesize = file_obj.size
        file_name_with_timezone = f'{formatted_datetime}_{os.path.splitext(file_name)[0]}_{unique_identifier}{file_extension}'
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name_with_timezone)
        print('file_name_with_timezone',file_name_with_timezone)
        blob_client.upload_blob(file_obj)
        print('file_object15',file_obj)
        print('file_object15',type(file_obj))
        print('file_name_with_timezone11',file_name_with_timezone)

        otherfile = OtherFiles(petient,org,file_name_with_timezone,filesize, userid)
        return otherfile


# def check_dicom_files_in_zip(file_obj):
#     dicom_extensions = ['.dcm', '.ima', '.dicom']
#
#     with zipfile.ZipFile(file_obj, 'r') as zip_file:
#         for name in zip_file.namelist():
#             if any(name.lower().endswith(ext) for ext in dicom_extensions):
#                 with zip_file.open(name) as file:
#                     try:
#                         dicom_file = pydicom.dcmread(file)
#                         print(f"{name} is a valid DICOM file.")
#                         print('dicom_file length', len(dicom_file))
#                         return True
#                     except pydicom.errors.DicomError:
#                         print(f"{name} is not a valid DICOM file.")
#     return False


def check_dicom_files_in_zip(zip_filepath):
    dicom_extensions = ['.dcm', '.ima', '.dicom']
    found_dicom_files = False
    with zipfile.ZipFile(zip_filepath, 'r') as zip_file:
        for name in zip_file.namelist():
            if any(name.lower().endswith(ext) for ext in dicom_extensions):
                with zip_file.open(name) as file:
                    try:
                        dicom_file = pydicom.dcmread(file)
                        print(f"{name} is a valid DICOM file.")
                        print('DICOM file length:', len(dicom_file))
                        found_dicom_files = True
                    except pydicom.errors.InvalidDicomError:
                        print(f"{name} is not a valid DICOM file.")
            elif name.lower().endswith('.zip'):
                nested_zip_filepath = os.path.join(zip_filepath, name)
                zip_file.extract(name)
                found_dicom_files |= check_dicom_files_in_zip(name)
                os.remove(name)
    return found_dicom_files

import os
def checkfileextension(file):
    file_name = file.name
    file_extension = os.path.splitext(file_name)[1].lower()
    if file_extension == ".zip":
        return file_extension
    elif file_extension in [".jpg", ".jpeg", ".png",".pdf",".html",".htm"]:
        return file_extension


















