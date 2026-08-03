import urllib.request

files = [
    'http://127.0.0.1:8000/videos/Screen_Recording_2024-12-31_160638.mp4',
    'http://127.0.0.1:8000/audio/debwong1951-tsunami-test-siren-431947.mp3',
    'http://127.0.0.1:8000/photos/5960980390409342627.jpg',
    'http://127.0.0.1:8000/documents/pdf-test_1AnXwqU.pdf',
]
for url in files:
    try:
        r = urllib.request.urlopen(url)
        ct = r.headers.get('Content-Type', 'unknown')
        filename = url.split('/')[-1]
        print(f'OK {r.status} {ct} -> {filename}')
    except Exception as e:
        print(f'FAIL {url}: {e}')
