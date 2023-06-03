# from django.test import TestCase
#
import zipfile
import requests
from bs4 import BeautifulSoup


def fun1():
    with open(r"C:\Users\abhis\OneDrive\Desktop\Rx_125915304.html", 'r') as file:
        # Read the contents of the file
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all span tags with class "patient-name"
        patient_name_tags = soup.find_all('font')

        if len(patient_name_tags) >= 4:
            patient_name = patient_name_tags[3].text
            ds = patient_name[9:]
            pn = ds.replace(',','')
            print(pn)
fun1()




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
                    files_with_extensions.append((file_name, extension))
    return files_with_extensions

# Example usage
# zip_file_path = r"C:\Users\abhis\Downloads\iTero_Export_125915304 1.zip"
#
# target_extensions = ['stl']  # Example extensions to check
#
# files_with_extensions = Get_stl_files(zip_file_path, target_extensions)
#
# print("Files with target extensions in the ZIP file:")
# for file_name, extension in files_with_extensions:
#     dn = file_name + '.'+extension
#     print(file_name, dn)