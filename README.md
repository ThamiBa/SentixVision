# 🚀 SentixVision: Workplace Intelligence Platform

SentixVision is a real-time computer vision dashboard that transforms camera feeds into actionable business intelligence. It helps managers answer: *"Who is working?", "Are customers happy?", and "Who is the Worker of the Day?"*

## ⚡ Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/YourUsername/SentixVision.git
cd SentixVision

# Install dependencies (requires Python 3.10+)
pip install -r requirements.txt

# Post-install: DeepFace may download weights (500MB+) on first run.
```

### 2. Run Application
```bash
streamlit run app.py
```

### 3. Camera Connection
- **Webcam**: Enter `0` in the sidebar.
- **IP Camera (RTSP)**: ` http://192.168.11.100:8080/onvif/device_service`
- **Android (IP Webcam)**: `http://192.168.1.XX:8080/video`
- **iOS (EpocCam)**: Use `0` or virtual driver ID.

---

## 🏗️ Architecture & Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Dashboard UI, State Management, Sidebar Config |
| **AI Core** | YOLOv8 + ByteTrack | Object Detection (Person) & Multi-Object Tracking |
| **Emotion** | DeepFace (FER) | Facial Expression Recognition (Happy, Angry, Neutral) |
| **Zone Logic** | OpenCV | Polymer-based spatial analysis (Worker vs Customer zones) |
| **Data Viz** | Built-in Metrics | Real-time counters and calculated KPIs |

**Pattern**: Producer-Consumer (Threaded)
- **Producer**: `FrameCapture` (Retries, Connection Management)
- **Queue**: `st.session_state.frame_queue` (Maxsize 30)
- **Consumer**: `AI Processor` (Tracking -> Emotion -> Logic -> Annotation)

---

## 🎯 "Worker of the Day" Algorithm
A gamified metric to identify top performers.
```python
Score = (Time_in_Zone_Frames * 1.0) + (Positive_Emotion_Frames * 5.0)
```
*Workers are rewarded more for being happy/pleasant (5x multiplier) than just being present.*

---

## 🤖 Prompt Strategy
**Copy-paste this prompt to instruct another AI to iterate on this codebase:**

```markdown
ACT: Expert CV Engineer. CONTEXT: SentixVision (Streamlit+YOLO+DeepFace).
GOAL: Optimize/Refactor 'app.py' maintaining these constraints:
1. MUST: Producer-Consumer threaded pattern.
2. MUST: 5-retry connection logic in Producer.
3. MUST: YOLOv8 tracking with 'bytetrack.yaml'.
4. MUST: 'worker_scores' state logic (Time + 5*Happy).
5. MUST: Visual Alerts for 'Angry' in Consumer Zone.
6. MUST: Single-file structure (12 sections).
7. SHOULD: Keep Dark Theme CSS.
8. MUST NOT: Blocking operations in UI thread.
CURRENT STATE: Functional MVP. 
TASK: [Insert specific request here, e.g., 'Add database persistence']
```

---

## 📊 Modes & Performance
- **Analytics Mode**: Counts unique IDs, calculates dwell time.
- **Security Mode**: Alerts on "Angry" customers or intrusion.
- **Target Performance**: ~15-20 FPS on CPU (due to skip-frame Emotion analysis).
