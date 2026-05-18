from flask import Flask, request, render_template, send_file
from PIL import Image
import io
import qrcode
import base64
import wave

app = Flask(__name__)

# ── Helpers ────────────────────────────────────────────────

DELIMITER = "####"

def text_to_bits(text):
    return ''.join(format(ord(c), "08b") for c in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    message = ""
    for byte in chars:
        if len(byte) < 8:
            break
        message += chr(int(byte, 2))
        if message.endswith(DELIMITER):
            return message[:-len(DELIMITER)]
    return message

# ── Image Steganography ────────────────────────────────────

def encode_image(image, message):
    image = image.convert("RGB")
    encoded = image.copy()
    width, height = image.size

    binary_message = text_to_bits(message + DELIMITER)
    capacity = width * height

    if len(binary_message) > capacity:
        raise ValueError(f"Message too long for this image (max ~{capacity // 8} chars).")

    index = 0
    for row in range(height):
        for col in range(width):
            if index >= len(binary_message):
                return encoded
            r, g, b = image.getpixel((col, row))
            r = (r & ~1) | int(binary_message[index])
            encoded.putpixel((col, row), (r, g, b))
            index += 1

    return encoded


def decode_image(image):
    image = image.convert("RGB")
    width, height = image.size
    bits = ""

    for row in range(height):
        for col in range(width):
            r, g, b = image.getpixel((col, row))
            bits += str(r & 1)

    return bits_to_text(bits)

# ── Audio Steganography ────────────────────────────────────

def encode_audio(audio_file, message, output_path="stego_audio.wav"):
    binary_message = text_to_bits(message + DELIMITER)

    with wave.open(audio_file, mode="rb") as audio:
        params = audio.getparams()
        frame_bytes = bytearray(audio.readframes(audio.getnframes()))

    if len(binary_message) > len(frame_bytes):
        raise ValueError("Message too long for this audio file.")

    for i, bit in enumerate(binary_message):
        frame_bytes[i] = (frame_bytes[i] & 0xFE) | int(bit)

    with wave.open(output_path, "wb") as out:
        out.setparams(params)
        out.writeframes(bytes(frame_bytes))

    return output_path


def decode_audio(audio_file):
    with wave.open(audio_file, mode="rb") as audio:
        frame_bytes = bytearray(audio.readframes(audio.getnframes()))

    bits = "".join(str(b & 1) for b in frame_bytes)
    return bits_to_text(bits)

# ── QR Code Helper ─────────────────────────────────────────

def make_qr_base64(text):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# ── Routes ─────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/encode", methods=["POST"])
def encode():
    if "image" not in request.files or not request.form.get("message"):
        return "Error: Missing image or message.", 400

    try:
        image = Image.open(request.files["image"])
        encoded_img = encode_image(image, request.form["message"])
    except ValueError as e:
        return str(e), 400

    buf = io.BytesIO()
    encoded_img.save(buf, "PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", as_attachment=True, download_name="stego.png")


@app.route("/decode", methods=["POST"])
def decode():
    if "image" not in request.files:
        return "Error: Missing image.", 400

    image = Image.open(request.files["image"])
    hidden_text = decode_image(image)
    qr_base64 = make_qr_base64(hidden_text)

    return render_template("index.html", qr_image=qr_base64, hidden_text=hidden_text)


@app.route("/encode-audio", methods=["POST"])
def encode_audio_route():
    if "audio" not in request.files or not request.form.get("message"):
        return "Error: Missing audio or message.", 400

    try:
        output_path = encode_audio(request.files["audio"], request.form["message"])
    except ValueError as e:
        return str(e), 400

    return send_file(output_path, as_attachment=True, download_name="stego_audio.wav")


@app.route("/decode-audio", methods=["POST"])
def decode_audio_route():
    if "audio" not in request.files:
        return "Error: Missing audio.", 400

    hidden_text = decode_audio(request.files["audio"])
    qr_base64 = make_qr_base64(hidden_text)

    return render_template("index.html", qr_image=qr_base64, hidden_text=hidden_text)


if __name__ == "__main__":
    app.run(debug=True)