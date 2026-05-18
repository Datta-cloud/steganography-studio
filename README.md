# 🔐 Steganography Studio

> Hide and extract secret messages in images and audio using LSB (Least Significant Bit) steganography — with a clean web UI, QR code output, and live deployment on Render.

**Live Demo → [steganography-studio.onrender.com](https://steganography-studio.onrender.com)**  
**GitHub → [Datta-cloud/steganography-studio](https://github.com/Datta-cloud/steganography-studio)**

---

## ✨ Features

- **Image Steganography** — Encode a secret text message into any PNG/JPG image; decode it back with a single click
- **Audio Steganography** — Hide and extract messages inside WAV audio files using LSB on raw frame bytes
- **QR Code Output** — Decoded messages are instantly rendered as a scannable QR code alongside the text
- **Delimiter-based termination** — Uses a `####` sentinel so extraction stops cleanly without reading noise
- **Minimal, responsive UI** — Dark-themed interface built with vanilla HTML/CSS; works on mobile and desktop

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Steganography | LSB algorithm (custom implementation) |
| Image processing | Pillow (PIL) |
| Audio processing | Python `wave` module |
| QR code generation | `qrcode` library |
| Frontend | HTML, CSS (vanilla) |
| Deployment | Render (free tier) |

---



## ⚙️ How It Works

### Image — Encode
1. Converts the message + delimiter to a binary bit string
2. Iterates over pixels row by row, replacing the LSB of the Red channel with one message bit per pixel
3. Returns the modified image as a downloadable PNG

### Image — Decode
1. Reads the LSB of the Red channel from each pixel in sequence
2. Groups bits into 8-bit characters, building the message until the `####` delimiter is found
3. Displays the recovered text and generates a QR code

### Audio — Encode / Decode
Same LSB approach, but applied to raw WAV frame bytes instead of pixel values. Works on uncompressed PCM WAV files only.


## 🖼 Usage

### Encode a message into an image
1. Go to the **Encode Image** card
2. Upload any PNG or JPG file
3. Type your secret message
4. Click **Encode & Download** — a `stego.png` file is downloaded

### Decode a message from an image
1. Go to the **Decode Image** card
2. Upload the encoded `stego.png`
3. Click **Decode Message** — the hidden text and its QR code appear on screen

### Audio works the same way — use a `.wav` file

---

## ⚠️ Limitations

- Image capacity: ~1 bit per pixel → a 100×100 image holds ~1,250 characters max
- Audio: message length must be ≤ total number of audio frame bytes
- Audio input must be uncompressed PCM WAV (MP3/AAC not supported)
- No encryption — messages are hidden, not encrypted. Add AES if needed for production



## 👤 Author

**Dattatray Hadke**  
B.Tech — AI & Data Science, VIIT Pune  
[GitHub](https://github.com/Datta-cloud) 
