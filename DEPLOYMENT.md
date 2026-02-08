# Deploying the Doctor Assistant

This guide provides a quick setup for deploying the Doctor Assistant application.

## Prerequisites
- **Python 3.10+** (Backend)
- **Node.js 18+** & npm (Frontend)
- **OpenAI API Key** (for backend logic)

---

## 1. Backend Setup (FastAPI)

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Set up environment variables:
    - Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    - Add your **OPENAI_API_KEY** to `backend/.env`.

5.  Run the server:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    The API will be available at `http://localhost:8000`.

---

## 2. Frontend Setup (React/Vite)

1.  Navigate to the frontend directory:
    ```bash
    cd ../frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Build for production:
    ```bash
    npm run build
    ```

4.  Serve the build (e.g., using `serve`):
    ```bash
    npm install -g serve
    serve -s dist -l 3000
    ```
    The application will be available at `http://localhost:3000`.

---

## 3. Hosting (Live URL)

### Option A: Render (Recommended for Full Stack)
1.  Push your code to GitHub.
2.  Go to [dashboard.render.com](https://dashboard.render.com/).
3.  Click **New +** -> **Blueprint**.
4.  Connect your repository.
5.  Render will auto-detect `render.yaml` and create both services.
6.  **Important**: 
    - Add `OPENAI_API_KEY` in the dashboard for the backend service.
    - Once the backend is live, copy its URL (e.g., `https://doctor-assistant-backend.onrender.com`).
    - Go to the **Variables** tab of the **frontend** service.
    - Add `VITE_API_URL` with the backend URL.
    - Trigger a manual deploy of the frontend if needed.

### Option B: Railway
1.  Install Railway CLI: `npm i -g @railway/cli`
2.  Run `railway login` then `railway init`.
3.  Run `railway up`.
4.  Set variables: `railway vars set OPENAI_API_KEY=sk-...`

### Option C: Vercel (Frontend Only)
1.  Install Vercel CLI: `npm i -g vercel`
2.  Run `vercel` in the root.
3.  Link to your existing project.
4.  Note: You will need a deployed backend URL for the frontend to work. Update `VITE_API_URL` in Vercel settings.
