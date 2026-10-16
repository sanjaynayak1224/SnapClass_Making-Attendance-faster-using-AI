<p align="center">
  <img src="https://i.ibb.co/YTYGn5qV/logo.png" alt="SnapClass Logo" width="120" />
</p>

<h1 align="center">SnapClass &mdash; Making Attendance Faster Using AI</h1>

<p align="center">
  An intelligent classroom attendance system combining multi-face computer vision and sequential voice biometrics to mark full-class attendance in seconds.
</p>

<p align="center">
  <a href="https://snapclass-take-attendance-using-ai.streamlit.app/"><img src="https://img.shields.io/badge/Live%20App-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit" alt="Live App"></a>
  <a href="https://snap-class-landing-page-self.vercel.app/"><img src="https://img.shields.io/badge/Showcase-Vercel%20Landing%20Page-black?style=for-the-badge&logo=vercel" alt="Showcase Website"></a>
  <a href="https://github.com/sanjaynayak1224/SnapClass_Landing_Page"><img src="https://img.shields.io/badge/Frontend%20Repo-Landing%20Page-5865F2?style=for-the-badge&logo=github" alt="Landing Page Repo"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Database-Supabase%20Postgres-3ECF8E?style=for-the-badge&logo=supabase" alt="Supabase">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License">
</p>

---

## 📌 Table of Contents

- [Quick Links](#-quick-links)
- [Why I Built SnapClass](#-why-i-built-snapclass)
- [How It Works](#-how-it-works)
  - [1. Multi-Face Recognition from Classroom Photos](#1-multi-face-recognition-from-classroom-photos)
  - [2. Sequential Voice ID Roll-Call](#2-sequential-voice-id-roll-call)
  - [3. QR Code & Instant Course Onboarding](#3-qr-code--instant-course-onboarding)
  - [4. Zero-Password Student Portal](#4-zero-password-student-portal)
- [System Architecture](#-system-architecture)
- [Database Schema (Supabase PostgreSQL)](#-database-schema-supabase-postgresql)
- [Project Structure](#-project-structure)
- [Local Setup & Installation](#-local-setup--installation)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Installation](#step-by-step-installation)
  - [Setting Up Supabase Secrets](#setting-up-supabase-secrets)
- [User Walkthrough](#-user-walkthrough)
  - [For Teachers](#for-teachers)
  - [For Students](#for-students)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)
- [Deploying to Streamlit Cloud](#-deploying-to-streamlit-cloud)
- [Related Repositories](#-related-repositories)
- [Author](#-author)
- [License](#-license)

---

## 🔗 Quick Links

- **Live Streamlit Application:** [https://snapclass-take-attendance-using-ai.streamlit.app/](https://snapclass-take-attendance-using-ai.streamlit.app/)
- **Showcase Landing Page (Vercel):** [https://snap-class-landing-page-self.vercel.app/](https://snap-class-landing-page-self.vercel.app/)
- **Landing Page GitHub Repository:** [sanjaynayak1224/SnapClass_Landing_Page](https://github.com/sanjaynayak1224/SnapClass_Landing_Page)
- **Core Application GitHub Repository:** [sanjaynayak1224/SnapClass_Making-Attendance-faster-using-AI](https://github.com/sanjaynayak1224/SnapClass_Making-Attendance-faster-using-AI)

---

## 💡 Why I Built SnapClass

In almost every college lecture, the first 10 to 15 minutes are wasted on roll call. A professor stands at the podium reading out 60 to 80 names one by one, or hands around a physical sign-in sheet that invariably gets passed around for proxy signatures. Wall-mounted biometric scanners aren't much better—they create massive bottleneck queues outside the classroom door before every lecture.

I wanted to solve this cleanly from both sides:

1. **For Teachers:** Allow an instructor to take attendance simply by snapping 1 or 2 wide-angle photos of the room with their phone or laptop camera, or recording a 15-second audio clip of students saying "Present".
2. **For Students:** Give them a friction-free experience. No forgotten passwords—students log in with their face, join classes instantly using QR codes, and track their attendance percentages in real time.

That is how SnapClass was born. It is built entirely in Python using Streamlit for the reactive user interface, dlib and scikit-learn for facial feature extraction and classification, Resemblyzer for deep speaker verification, and Supabase PostgreSQL for cloud persistence.

---

## 🧠 How It Works

SnapClass combines two independent biometric modalities (vision and speech) alongside automated course enrollment. Here is the technical breakdown of each component:

### 1. Multi-Face Recognition from Classroom Photos

```text
Classroom Photo(s) 
       │
       ▼
dlib Frontal Face Detector (HOG + Linear SVM)
       │
       ▼
68-Point Facial Landmark Predictor (Shape Predictor)
       │
       ▼
dlib ResNet Deep Metric Model ──► 128-Dimensional Face Descriptor Vector
       │
       ▼
Scikit-Learn SVC Classifier (Linear Kernel, Balanced Weights) ──► Candidate Student ID
       │
       ▼
Euclidean Distance Threshold Guard (norm <= 0.6) ──► Verified Present / Unknown
```

- **Face Detection & Descriptors (`src/pipelines/face_pipeline.py`):**
  When a teacher uploads classroom photos, `dlib` scans the full resolution image using its frontal face detector. For every face located, a 68-point shape predictor aligns the facial landmarks, and dlib's ResNet face recognition model calculates a 128-dimensional embedding vector.
- **Classification & Verification:**
  A Support Vector Classifier (`SVC`) trained on all enrolled students predicts which student matches each detected vector. To prevent false positives (such as an unknown visitor being labeled as an enrolled student), the pipeline calculates the Euclidean distance between the detected face and the candidate's stored training embeddings. Only matches with a distance score <= 0.6 are marked **Present**.
- **Performance Optimization:**
  Heavy deep learning models and the trained SVM classifier are cached in memory using `@st.cache_resource`. When a new student registers, the cache is automatically invalidated and the model retrains instantly.

---

### 2. Sequential Voice ID Roll-Call

```text
Classroom Audio (.wav / .mp3)
       │
       ▼
Librosa Audio Loader (Resampled to 16,000 Hz)
       │
       ▼
Librosa Voice Activity Detection (effects.split, top_db=30, min duration > 0.5s)
       │
       ▼
Resemblyzer VoiceEncoder (Pretrained Deep LSTM) ──► 256-Dimensional Speaker Embedding
       │
       ▼
Cosine Similarity Dot Product (np.dot >= 0.65) vs Enrolled Student Voice Embeddings
       │
       ▼
Identified Student Match + Confidence Score
```

- **Audio Preprocessing (`src/pipelines/voice_pipeline.py`):**
  The instructor records classroom audio while students call out "Present" one after another. The audio buffer is resampled to 16 kHz using `librosa`.
- **Speech Segmentation (Voice Activity Detection):**
  `librosa.effects.split` isolates speech bursts based on a 30 dB relative silence threshold, filtering out background desk noise and short coughs (< 0.5 seconds).
- **Speaker Embedding & Cosine Matching:**
  Each isolated utterance is passed into `resemblyzer.VoiceEncoder`, generating a 256-dimensional speaker vector. The pipeline computes the cosine similarity (dot product of normalized vectors) against stored voice embeddings of enrolled students in that subject. If the top similarity score clears the 0.65 threshold, that student is tagged as present.

---

### 3. QR Code & Instant Course Onboarding

```text
Teacher creates Course (e.g. CS101) ──► Generates Unique Join URL & QR Code (Segno)
                                                    │
                                                    ▼
Student scans QR Code with phone ──► Launches app.py with ?join-code=CS101
                                                    │
                                                    ▼
If logged in ──► auto_enroll_dialog() confirms enrollment in 1 click!
```

- When a teacher creates a course, SnapClass uses `segno` to generate a high-resolution QR code encoding `https://snapclass-take-attendance-using-ai.streamlit.app/?join-code=<SUBJECT_CODE>`.
- The teacher can project the QR code onto the classroom screen or copy the link directly into a group chat.
- When students scan the code, Streamlit parses the query parameter `join-code`, automatically opens the confirmation dialog, and enrolls them into the course roster.

---

### 4. Zero-Password Student Portal

- **Frictionless Login:** Students open the student portal and look into their webcam. The AI scans the camera feed, locates their face, and compares the embedding against the database. If recognized, they are logged in immediately without typing passwords.
- **Dynamic Onboarding:** If a face is not recognized, the interface automatically presents a registration card. The student enters their name, captures their face descriptor from the camera, and optionally records a short voice sample ("I am present, my name is John"). The system stores the biometrics in Supabase, retrains the SVM classifier, and signs them in.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          SnapClass Ecosystem                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌───────────────────────┐                         ┌──────────────────────┐
│  Showcase / Marketing │                         │  Core Attendance App │
│  (Flask on Vercel)    │                         │  (Streamlit Cloud)   │
│  snap-class-landing-  │                         │  snapclass-take-     │
│  page-self.vercel.app │                         │  attendance-using-ai │
└───────────────────────┘                         └──────────┬───────────┘
                                                             │
                  ┌──────────────────────────────────────────┴───────────────┐
                  ▼                                                          ▼
        ┌───────────────────┐                                      ┌───────────────────┐
        │  Teacher Portal   │                                      │  Student Portal   │
        │  - Bcrypt Login   │                                      │  - FaceID Login   │
        │  - Manage Courses │                                      │  - Face/Voice Reg │
        │  - Photo Scan     │                                      │  - View Stats     │
        │  - Voice Rollcall │                                      │  - QR Auto-Enroll │
        │  - Review & Save  │                                      └───────────────────┘
        └─────────┬─────────┘                                                │
                  │                                                          │
                  └──────────────────────────┬───────────────────────────────┘
                                             ▼
                               ┌───────────────────────────┐
                               │  Biometric AI Pipelines   │
                               │  - dlib + 128-d ResNet    │
                               │  - Scikit-Learn SVM       │
                               │  - Resemblyzer + Librosa  │
                               └─────────────┬─────────────┘
                                             ▼
                               ┌───────────────────────────┐
                               │     Supabase Database     │
                               │  (PostgreSQL + Realtime)  │
                               └───────────────────────────┘
```

---

## 🗄️ Database Schema (Supabase PostgreSQL)

SnapClass runs on Supabase (PostgreSQL). Below is the complete relational structure ready to execute in the Supabase SQL Editor:

```sql
-- 1. Teachers Table
CREATE TABLE teachers (
    teacher_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Students Table (stores 128-d face & 256-d voice embedding vectors)
CREATE TABLE students (
    student_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    face_embedding JSONB,
    voice_embedding JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Subjects Table
CREATE TABLE subjects (
    subject_id BIGSERIAL PRIMARY KEY,
    subject_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    section TEXT NOT NULL,
    teacher_id BIGINT REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Course Enrollment Junction Table
CREATE TABLE subject_students (
    id BIGSERIAL PRIMARY KEY,
    subject_id BIGINT REFERENCES subjects(subject_id) ON DELETE CASCADE,
    student_id BIGINT REFERENCES students(student_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(subject_id, student_id)
);

-- 5. Attendance Session Logs Table
CREATE TABLE attendance_logs (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT REFERENCES students(student_id) ON DELETE CASCADE,
    subject_id BIGINT REFERENCES subjects(subject_id) ON DELETE CASCADE,
    timestamp TEXT NOT NULL,
    is_present BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📂 Project Structure

```text
Snapclass/
├── .streamlit/
│   └── secrets.toml              # Supabase URL & Key configuration (git-ignored)
├── src/
│   ├── components/               # Modular UI dialogs and visual widgets
│   │   ├── dialog_add_photos.py          # Modal: Capture via webcam or upload photos
│   │   ├── dialog_attendance_results.py  # Modal: Review & edit present/absent table
│   │   ├── dialog_auto_enroll.py         # Modal: One-click QR join confirmation
│   │   ├── dialog_create_subject.py      # Modal: Create new course (code, name, section)
│   │   ├── dialog_enroll_subject.py      # Modal: Manual subject code enrollment
│   │   ├── dialog_share_subject.py       # Modal: Generates QR code and join link
│   │   ├── dialog_voice_attendance.py    # Modal: Record & analyze classroom voice audio
│   │   ├── footer.py                     # Branded footer layouts
│   │   ├── header.py                     # Branded navigation header & logo
│   │   └── subject_card.py               # Custom styled card for courses and statistics
│   ├── database/                 # Database connection & query helper functions
│   │   ├── config.py             # Supabase client initialization from secrets
│   │   └── db.py                 # Full CRUD operations for teachers, students, logs
│   ├── pipelines/                # Machine learning and biometrics pipelines
│   │   ├── face_pipeline.py      # dlib face detection, 128-d descriptors, SVM classifier
│   │   └── voice_pipeline.py     # Librosa VAD segmentation, Resemblyzer voice embeddings
│   ├── screens/                  # Main user role screens
│   │   ├── home_screen.py        # Landing role selection (Teacher vs Student)
│   │   ├── student_screen.py     # FaceID login, biometric registration, student stats
│   │   └── teacher_screen.py     # Teacher auth, attendance tabs, subject management
│   └── ui/
│       └── base_layout.py        # CSS injections, Google Fonts, theme colors & buttons
├── static/
│   └── img/
│       └── logo.png              # SnapClass logo asset
├── .gitignore                    # Environment & cache ignore rules
├── app.py                        # Streamlit main entry point & query router
├── README.md                     # Comprehensive project documentation
└── requirements.txt              # Production Python package dependencies
```

---

## 🚀 Local Setup & Installation

Follow these steps to run SnapClass on your local development machine:

### Prerequisites
- **Python 3.10 to 3.12** installed (Python 3.11 is recommended for smooth `dlib` compatibility).
- A free **Supabase** project ([supabase.com](https://supabase.com/)).
- A working webcam and microphone.

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/sanjaynayak1224/SnapClass_Making-Attendance-faster-using-AI.git
cd SnapClass_Making-Attendance-faster-using-AI
```

#### 2. Create and Activate a Virtual Environment
```bash
# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install CMake and dlib
`dlib` contains native C++ extensions. Depending on your platform:

- **Windows:**
  The prebuilt wheel is specified in `requirements.txt`:
  ```bash
  pip install dlib-bin
  ```
- **macOS:**
  ```bash
  brew install cmake
  pip install dlib
  ```
- **Ubuntu / Debian Linux:**
  ```bash
  sudo apt-get update
  sudo apt-get install -y build-essential cmake libopenblas-dev liblapack-dev libx11-dev
  pip install dlib
  ```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note on `face_recognition_models`:**
> `requirements.txt` fetches `face_recognition_models` directly from GitHub:
> ```bash
> pip install git+https://github.com/ageitgey/face_recognition_models
> ```

#### 5. Configure Supabase Secrets
Create a `.streamlit/secrets.toml` file in the root directory:

```bash
mkdir .streamlit
```

Add your Supabase URL and Key inside `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-supabase-service-or-anon-key"
```

*(You can retrieve these from your Supabase Dashboard under Project Settings > API).*

#### 6. Run the Application
```bash
streamlit run app.py
```

Open your browser at:
```text
http://localhost:8501
```

---

## 📋 User Walkthrough

### For Teachers

1. **Sign Up / Login:** Open the Teacher Portal, create a profile or log in with your username and password.
2. **Create a Subject:** Go to **Manage Subjects > Create a new Subject**. Enter course code (e.g. `CS101`), course title, and section.
3. **Distribute Join Code:** Click **Share Code** on the course card. Display the generated QR code on the projector or copy the link for students to enroll.
4. **Take Attendance via Photo:**
   - Go to **Take Attendance**, select the course, and click **Add photos**.
   - Snap photos with your webcam or upload wide shots of the room.
   - Click **Run Face Analysis**.
   - A verification modal displays all enrolled students with detection status and source photo tags. Review and click **Confirm and Save**.
5. **Take Attendance via Voice:**
   - Click **Use Voice Attendance**.
   - Start recording and have students say "Present" one by one.
   - Click **Analyze Audio**. Review the matched students and click **Confirm and Save**.
6. **Review Logs:** Navigate to **Attendance Records** to view historical attendance tallies and export records.

---

### For Students

1. **Login via Face:** Open the Student Portal and look at your camera. The system scans and recognizes your face instantly.
2. **First-Time Registration:** If your face is not recognized yet:
   - Type your full name.
   - Take a clear snapshot to register your face embedding.
   - *(Optional)* Record a quick phrase ("I am present, my name is...") to register your voice biometrics.
   - Click **Create Account**. You are now registered and logged in!
3. **Enroll in a Course:**
   - Scan your teacher's QR code or click their join link, then click **Yes Enroll Now!**.
   - Or click **Enroll in subject** on your dashboard and enter the subject code manually.
4. **Check Attendance:** View your course cards to see total classes held and classes attended.

---

## 🔧 Troubleshooting & FAQs

### 1. `dlib` fails to install
If `pip install dlib` throws build errors:
- On Windows: run `pip install dlib-bin` instead of compiling from source.
- On Linux: ensure `build-essential` and `cmake` are installed (`sudo apt install cmake`).
- On macOS: run `xcode-select --install` and `brew install cmake`.

### 2. Camera or Microphone not working in Streamlit
Modern browsers only grant camera and audio access over secure contexts (`https://` or `http://localhost`). If accessing from another device on your local network, use `localhost` or deploy behind SSL. Also verify your browser permissions for the site.

### 3. Face not recognized or low accuracy
- Ensure classroom photos are well-lit.
- Students should register their initial profile facing the camera in a reasonably lit room without extreme backlighting.
- The Euclidean threshold is set to `0.6` in `face_pipeline.py`. If you want a more lenient matching for grainy cameras, you can adjust `resemblance_threshold = 0.65`.

### 4. Audio Voice Roll-Call not recognizing voices
- Ensure the microphone is close enough to clearly record student responses.
- In `voice_pipeline.py`, the energy splitting threshold is set to `top_db=30`. If your classroom has louder ambient noise, adjust `top_db=25` or `top_db=20` to better isolate distinct voice segments.

---

## ☁️ Deploying to Streamlit Cloud

To host your own version of SnapClass on Streamlit Community Cloud:

1. Fork or push this repository to your GitHub account.
2. Log in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **"New app"**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. In **Advanced settings > Secrets**, paste your Supabase keys:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-supabase-key"
   ```
5. Click **Deploy**. Streamlit Cloud will automatically install dependencies from `requirements.txt` and launch your live app!

---

## 🔗 Related Repositories

- **Marketing Landing Page Repository:** [sanjaynayak1224/SnapClass_Landing_Page](https://github.com/sanjaynayak1224/SnapClass_Landing_Page)
- **Hosted Landing Page:** [https://snap-class-landing-page-self.vercel.app/](https://snap-class-landing-page-self.vercel.app/)

---

## 👤 Author

**Sanjay S Nayak**
- GitHub: [@sanjaynayak1224](https://github.com/sanjaynayak1224)
- Live App: [SnapClass on Streamlit](https://snapclass-take-attendance-using-ai.streamlit.app/)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). Feel free to fork, customize, and deploy it for your school, college, or university!
