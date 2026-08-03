import time
import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

start = time.time()
while time.time() - start < 180:
    try:
        print("Polling...")
        req = urllib.request.Request(
            'https://fitna-backend-production.up.railway.app/api/v1/admin/seed_db_now/',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
            print('Success:', r.read().decode())
            break
    except urllib.error.HTTPError as e:
        print('HTTP Error:', e.code, e.reason)
        # 502 Bad Gateway means server isn't up
    except Exception as e:
        print('Waiting...', e)
    time.sleep(10)
