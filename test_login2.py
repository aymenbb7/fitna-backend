
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import re

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

req1 = urllib.request.Request('http://127.0.0.1:8002/django-admin/login/')
res1 = opener.open(req1)
html = res1.read().decode('utf-8')

match = re.search(r'name=.csrfmiddlewaretoken. value=.(.*?).>', html)
csrf_token = match.group(1) if match else ''

data = urllib.parse.urlencode({
    'username': 'superadmin',
    'password': 'Admin1234',
    'csrfmiddlewaretoken': csrf_token,
    'next': '/django-admin/'
}).encode('utf-8')

req2 = urllib.request.Request('http://127.0.0.1:8002/django-admin/login/', data=data, method='POST')
req2.add_header('Referer', 'http://127.0.0.1:8002/django-admin/login/')
req2.add_header('User-Agent', 'Mozilla/5.0')

try:
    res2 = opener.open(req2)
    print('Final URL:', res2.geturl())
except Exception as e:
    print('Exception:', e)

