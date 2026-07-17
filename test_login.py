
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import re

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

req1 = urllib.request.Request('http://127.0.0.1:8001/django-admin/login/')
res1 = opener.open(req1)
html = res1.read().decode('utf-8')

match = re.search(r'name=.csrfmiddlewaretoken. value=.(.*?).>', html)
csrf_token = match.group(1) if match else ''
print('Got CSRF token:', csrf_token[:10] + '...')

data = urllib.parse.urlencode({
    'username': 'superadmin',
    'password': 'Admin1234',
    'csrfmiddlewaretoken': csrf_token,
    'next': '/django-admin/'
}).encode('utf-8')

req2 = urllib.request.Request('http://127.0.0.1:8001/django-admin/login/', data=data, method='POST')
req2.add_header('Referer', 'http://127.0.0.1:8001/django-admin/login/')
req2.add_header('User-Agent', 'Mozilla/5.0')

try:
    res2 = opener.open(req2)
    print('Final URL:', res2.geturl())
    print('Status Code:', res2.getcode())
    final_html = res2.read().decode('utf-8')
    if 'Veuillez compl' in final_html or 'Please enter the correct' in final_html:
        print('LOGIN FAILED! Form error present in HTML.')
    else:
        print('LOGIN SUCCEEDED! No form errors found.')
except Exception as e:
    print('Exception:', e)

