from jose import jwt

SECRET_KEY_JWT='0e1d13e66b155b4dcc565566705c019a2c14c4f1c875d96cc77048afb4e6274'
ALGORITHM='HS256'

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzM1MDU3OTA4LCJleHAiOjE3MzUwNjA2MDgsInNjb3BlIjoiYWNjZXNzX3Rva2VuIn0.Es-Ej_7qNcJvMXKtVe0DLg4v2OR26AUH1NxDxoWx_ZM'

payload = jwt.decode(token, SECRET_KEY_JWT, algorithms=['HS256'])
print(f"Decoded payload: {payload}")