# Deployment Guide: Pitch Perfect AI

Because your project has two distinct parts with very different requirements, we need a **Split Deployment Strategy**.

### 🏗 Architecture
1.  **Frontend (Next.js)** → Deployed on **Vercel** (Best for Next.js, free).
2.  **Backend (FastAPI + AI Models)** → Deployed on **Render** or **Railway** (Required because AI models are too large/heavy for Vercel).

---

## Part 1: Deploying the Backend (Do this first)

The backend needs a server with enough RAM to load the AI models (PyTorch/Transformers). **Vercel cannot host this backend** because the file size matches (approx 1GB+) exceed Vercel's 250MB limit.

### Option A: Render (Easiest)
1.  Push your latest code to GitHub.
2.  Sign up at [render.com](https://render.com/).
3.  Click **New +** → **Web Service**.
4.  Connect your GitHub repo (`Prabhav1437/pitch_perfect`).
5.  Configure the service:
    *   **Root Directory**: `.` (leave empty or dot)
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
    *   **Instance Type**: Select **Starter** or higher (Free tier might fail due to RAM limits for AI models. You likely need at least 2GB RAM).
6.  Click **Deploy Web Service**.
7.  **Copy your Backend URL** (e.g., `https://pitch-perfect-api.onrender.com`) once active.

### Option B: Railway (Better Performance)
1.  Sign up at [railway.app](https://railway.app/).
2.  Click **New Project** → **Deploy from GitHub repo**.
3.  Railway will auto-detect Python.
4.  Go to **Settings** → **Generate Domain** to get your URL.

---

## Part 2: Deploying the Frontend (Vercel)

Now that you have a live backend URL, let's deploy the UI.

1.  **Prepare Frontend for Production**:
    *   We need to tell the frontend where the backend lives.
    *   Create a file `.env.local` (local) and ensure your code uses an Environment Variable.

2.  **Update `page.tsx`**:
    *   Change the hardcoded fetch URL to use an environment variable.
    *   *I will update this code for you in the next step.*

3.  **Deploy to Vercel**:
    1.  Go to [vercel.com](https://vercel.com/) and sign up/login.
    2.  Click **Add New...** → **Project**.
    3.  Import your `pitch_perfect` repository.
    4.  **Important**: Edit the **Root Directory**.
        *   Click "Edit" next to Root Directory and select `frontend`.
    5.  **Environment Variables**:
        *   Add a new variable:
            *   Key: `NEXT_PUBLIC_API_URL`
            *   Value: `YOUR_BACKEND_URL_FROM_PART_1` (e.g., `https://pitch-perfect-api.onrender.com`)
            *   *Note: Do not add a trailing slash `/` at the end.*
    6.  Click **Deploy**.

---

## Part 3: Troubleshooting

### CORS Errors
If your frontend says "Network Error" or "CORS Error", you need to update `main.py` in your backend to allow the Vercel domain.

**In `main.py`**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Model Loading Timouts
AI models take time to load. On the first request (cold start), the backend might take 30-60 seconds.
*   **Fix**: Use a service that keeps the server active (Render paid plans or Railway).
