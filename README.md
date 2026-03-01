# Deceiving Siren

> **Audio & Video Steganography Platform** — Hide any file inside audio and video data using LSB encoding and spectrogram embedding.

<p align="center">
  <img src="docs/banner.png" alt="Deceiving Siren Banner" width="800" />
</p>

---

##  Features

| Capability | Description |
|---|---|
| **LSB Audio Steganography** | Hide any file inside a WAV/FLAC audio file using Least Significant Bit encoding |
| **Spectrogram Embedding** | Encode images/data into the frequency domain — visible only when viewing the spectrogram |
| **Video Steganography** | Extract the audio track from a video, embed hidden data, and remux it back |
| **Multi-Format Output** | Export as WAV, FLAC (lossless — data preserved) or MP3, OGG (lossy — with warning) |
| **Drag & Drop UI** | Cyberpunk-themed interface with drag-and-drop file upload (80MB limit) |
| **WebGL Visualizations** | Real-time waveform and spectrogram viewers powered by wavesurfer.js |
| **Dockerized Deployment** | Full Docker Compose setup with Flask, Next.js, and Nginx |

---

##  Architecture

```
┌──────────────────┐         ┌──────────────────┐
│   Next.js App    │  HTTP   │   Flask API      │
│   (Port 3000)    │ ──────► │   (Port 5000)    │
│                  │         │                  │
│  • Cyberpunk UI  │         │  • LSB Engine    │
│  • WebGL Viz     │         │  • Spectrogram   │
│  • Drag & Drop   │         │  • Video Extract │
│  • Format Select │         │  • Format Conv.  │
└──────────────────┘         └──────────────────┘
         │                            │
         └──────── Nginx (:80) ───────┘
```

---

##  Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- Or: **Python 3.11+**, **Node.js 20+**, **ffmpeg**

### With Docker Compose

```bash
git clone https://github.com/your-username/Deceiving_Siren.git
cd Deceiving_Siren
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

Open [http://localhost](http://localhost) in your browser.

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

##  Project Structure

```
Deceiving_Siren/
├── .github/workflows/      # CI/CD pipelines
│   ├── ci.yml              # Lint + test on push/PR
│   └── deploy.yml          # Build & push Docker images
├── backend/
│   ├── app/
│   │   ├── __init__.py     # Flask app factory
│   │   ├── config.py       # Configuration
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Steganography engines
│   │   └── utils/          # Helpers
│   ├── tests/              # pytest test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── wsgi.py
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router pages
│   │   └── components/     # Reusable UI components
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker/
│   ├── docker-compose.yml
│   └── nginx.conf
├── .gitignore
├── .env.example
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/encode` | LSB-encode a payload into an audio file |
| `POST` | `/api/decode` | Extract hidden data from a steganographic audio file |
| `POST` | `/api/encode-spectrogram` | Hide an image in an audio spectrogram |
| `POST` | `/api/decode-spectrogram` | Extract the spectrogram as a PNG image |
| `POST` | `/api/encode-video` | Hide data in a video's audio track |
| `POST` | `/api/decode-video` | Extract hidden data from a video's audio |
| `GET`  | `/api/health` | Health check |

---

## ⚠️ Format Warning

> **Lossy formats (MP3, OGG)** destroy hidden data during compression.
> Always use **WAV or FLAC** if you need to preserve the embedded message.

---

##  License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  <strong>🧜‍♀️ Deceiving Siren</strong> — What you hear is not what it seems.
</p>
