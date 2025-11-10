import io, os, requests
from PIL import Image

# Create a small RGB image in memory
img = Image.new('RGB', (128, 128), color=(120, 180, 240))
buf = io.BytesIO()
img.save(buf, format='PNG')
buf.seek(0)

# POST to /steganography/hide
files = {'image': ('cover.png', buf.getvalue(), 'image/png')}
data = {'message': 'hello from test'}
try:
    r = requests.post('http://127.0.0.1:5000/steganography/hide', files=files, data=data, timeout=30)
    print('HIDE status:', r.status_code, 'content-type:', r.headers.get('content-type'))
    print('HIDE len:', len(r.content))
    if r.ok and r.headers.get('content-type','').startswith('image/'):
        with open('test_stego.png', 'wb') as f:
            f.write(r.content)
        print('Saved test_stego.png')
    else:
        print('HIDE body (truncated):', r.text[:500])
except Exception as e:
    print('HIDE error:', e)

# Rewind buffer and try /steganalysis/analyze
buf.seek(0)
try:
    r2 = requests.post('http://127.0.0.1:5000/steganalysis/analyze', files={'image': ('cover.png', buf.getvalue(), 'image/png')}, timeout=30)
    print('ANALYZE status:', r2.status_code, r2.text[:500])
except Exception as e:
    print('ANALYZE error:', e)

# If hide succeeded, feed to /steganography/extract
try:
    if 'test_stego.png' in os.listdir('.'):
        with open('test_stego.png', 'rb') as f:
            r3 = requests.post('http://127.0.0.1:5000/steganography/extract', files={'image': ('stego.png', f.read(), 'image/png')}, timeout=30)
        print('EXTRACT status:', r3.status_code, r3.text[:500])
except Exception as e:
    print('EXTRACT error:', e)
