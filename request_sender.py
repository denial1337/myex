import requests
from pydantic import BaseModel
url = 'http://127.0.0.1:8000/api/TLST/'
r = requests.get(url)

data = {'quatity' : 10, 'dir' : 'buy'}

session = requests.Session()
reg = session.post(url, json = data)

#pr = requests.post(url, json=data)

#exec(open('request_sender.py').read())
#requests.post()