# 🚀 SentixVision: Couture Intelligence Platform

SentixVision is a distributed, real-time computer vision platform tailored for the **couture and high-end fashion industry**. By leveraging edge AI and a microservices architecture, it transforms raw camera feeds from ateliers and boutiques into actionable workplace intelligence.

It helps managers answer: *"Who is currently at the cutting table?", "Is the team morale high?", and "Who is our top Artisan today?"*

---

## ✨ Key Features

- **👗 Industry-Specific Zones**: Pre-configured analysis for *Cutting Table*, *Sewing Station*, and *QC Zones*.
- **👁️ Live AI Dashboard**: Real-time 20+ FPS tracking using YOLOv8 and ByteTrack.
- **😊 Emotion & Sentiment**: Integrated Facial Expression Recognition (FER) via DeepFace to monitor workshop atmosphere.
- **🏆 Artisan Performance**: Automated scoring based on zone presence and positive engagement.
- **📺 High-Stability MJPEG Stream**: Custom MJPEG bridge ensuring a flicker-free live feed in the browser.
- **🏗️ Distributed Architecture**: Separated FastAPI backend for heavy AI compute and a premium Streamlit frontend for visualization.

---

## ⚡ Quick Start (Docker)

The easiest way to run SentixVision is using Docker Compose.

### 1. Clone & Setup
```bash
git clone https://github.com/ThamiBa/SentixVision.git
cd SentixVision
cp .env.example .env
```

### 2. Launch Services
```bash
docker compose up -d --build
```

### 3. Access the Platform
- **Dashboard**: [http://localhost:8501](http://localhost:8501)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Direct Stream**: [http://localhost:5002/stream](http://localhost:5002/stream)

---

## 🏗️ Architecture & Stack

SentixVision uses a modern, high-performance stack:

| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Frontend** | Dashboard | **Streamlit** (Custom Bauhaus/Premium UI) |
| **API** | SaaS Backend | **FastAPI** (Async Processing) |
| **Compute** | AI Engine | **YOLOv8** + **ByteTrack** |
| **Emotion** | Facial Analysis | **DeepFace** (VGG-Face) |
| **Database** | Persistence | **PostgreSQL** + **TimescaleDB** |
| **Caching** | Message Bus | **Redis** |
| **Streaming** | Video Bridge | **Custom MJPEG + OpenCV** |

---

## ⚙️ Configuration (.env)

Edit the `.env` file to customize your deployment:

```env
SECRET_KEY=your_secure_random_key
API_URL=http://backend:8000
DATABASE_URL=postgresql://user:pass@db:5432/sentix
REDIS_URL=redis://redis:6379/0
```

---

## 🎯 Artisan Scoring Algorithm

The platform gamifies productivity by identifying the "Artisan of the Day" using a weighted impact score:

$$Score = (Time_{Zone} \times 1.0) + (Emotion_{Positive} \times 5.0)$$

*We prioritize workplace happiness: positive engagement is weighted 5x higher than simple physical presence.*

---

## 🛠️ Debugging & Camera Sources

- **Webcam**: Use `0` in the URL input.
- **Demo Mode**: Type `DUMMY` to trigger the internal atelier simulator.
- **IP Cameras**: Supports RTSP, HTTP, and RTMP streams.
    - *Example*: `rtsp://admin:password@192.168.1.100:554/stream1`

---

## 📜 License
MIT License - Developed for the Couture Industry.
