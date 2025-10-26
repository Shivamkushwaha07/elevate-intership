
from flask import Flask, render_template, request, send_file
from PIL import Image
import io, datetime

app = Flask(__name__)

def _to_bin(data):
    return ''.join(format(byte, '08b') for byte in data)

def encode_lsb(image, message):
    image = image.convert('RGBA')
    data = list(image.getdata())
    msg_bytes = message.encode() + b'<<END>>'
    bits = _to_bin(msg_bytes)
    bit_iter = iter(bits)
    new_data = []
    for pixel in data:
        r,g,b,a = pixel
        rgb = [r,g,b]
        for i in range(3):
            try:
                bit = next(bit_iter)
                rgb[i] = (rgb[i] & ~1) | int(bit)
            except StopIteration:
                pass
        new_data.append(tuple(rgb + [a]))
    out = Image.new('RGBA', image.size)
    out.putdata(new_data)
    return out

def decode_lsb(image):
    image = image.convert('RGBA')
    data = image.getdata()
    bits = ''.join(str(c & 1) for p in data for c in p[:3])
    bytes_list = [bits[i:i+8] for i in range(0,len(bits),8)]
    msg = bytearray()
    for b in bytes_list:
        msg.append(int(b,2))
        if msg.endswith(b'<<END>>'):
            return msg[:-6].decode(errors='replace')
    return ''

@app.route('/', methods=['GET','POST'])
def index():
    extracted = None
    if request.method == 'POST':
        if 'encode' in request.form:
            file = request.files['image']
            msg = request.form['message']
            img = Image.open(file.stream)
            out = encode_lsb(img, msg)
            buf = io.BytesIO()
            out.save(buf, format='PNG')
            buf.seek(0)
            return send_file(buf, as_attachment=True, download_name='encoded.png', mimetype='image/png')
        elif 'decode' in request.form:
            file = request.files['stego_image']
            img = Image.open(file.stream)
            extracted = decode_lsb(img)
    return render_template('index.html', extracted=extracted)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
