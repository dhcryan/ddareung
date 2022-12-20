import zipfile_deflate64 as zipfile
import os
extract_path='/home/dhc4003/ddareung/data'
zipfile.ZipFile('seoul_bike18_22.zip').extractall(path=extract_path)

# import zipfile
# import os
# from zipfile import ZipFile
# import subprocess, sys
# extract_path='/home/dhc4003/ddareung/data'
# # zipfile.ZipFile('seoul_bike18_22.zip').extractall(path=extract_path)
# def Unzip(zipFile, destinationDirectory):
#     try:
#         with ZipFile(zipFile, 'r') as zipObj:
#             # Extract all the contents of zip file in different directory
#             zipObj.extractall(destinationDirectory)
#     except:
#         print("An exception occurred extracting with Python ZipFile library.")
#         print("Attempting to extract using 7zip")
#         subprocess.Popen(["7z", "e", f"{zipFile}", f"-o{destinationDirectory}", "-y"])
        
# Unzip('seoul_bike18_22.zip',extract_path)