# Free-Tier Deployment Guide

This guide will walk you through deploying SkillProbe completely for free using **Render** for the backend (FastAPI) and **Vercel** for the frontend (React).

---

## Part 1: Backend Deployment (Render)

We are using Render because their free tier allows native Python web services and background threads without complex serverless configurations.

1. **Sign up / Log in to Render**
   - Go to [render.com](https://render.com) and log in with your GitHub account.

2. **Create the Web Service using `render.yaml`**
   - We have already included a `render.yaml` file in the root of the project. This makes deployment essentially one-click.
   - On the Render dashboard, click **New** -> **Blueprint**.
   - Connect your GitHub repository.
   - Render will detect the `render.yaml` file and automatically configure the build commands, start commands, and Python versions.
   - Click **Apply**.

3. **Add your Gemini API Key**
   - Once the service is created, go to the **Environment** tab in your Render dashboard for the new Web Service.
   - Add a new secret environment variable:
     - **Key:** `GEMINI_API_KEY`
     - **Value:** `<your-actual-google-gemini-api-key>`
   - *Note: Do not commit your real key to GitHub!*

4. **Get your Backend URL**
   - Wait for the build to finish (this takes about 2-3 minutes).
   - Render will give you a live URL, usually looking like `https://skillprobe-backend-xxxx.onrender.com`.
   - Copy this URL! You need it for Part 2.

---

## Part 2: Frontend Deployment (Vercel)

We use Vercel because it provides the fastest global CDN for React/Vite SPAs.

1. **Sign up / Log in to Vercel**
   - Go to [vercel.com](https://vercel.com) and log in with your GitHub account.

2. **Import the Project**
   - Click **Add New...** -> **Project**.
   - Select your GitHub repository.

3. **Configure the Project**
   - In the Vercel deployment configuration, set the **Framework Preset** to **Vite**.
   - Set the **Root Directory** to `frontend` (crucial: you must edit this from the default root).
   - Open the **Environment Variables** section and add:
     - **Name:** `VITE_API_BASE_URL`
     - **Value:** `<the render URL you copied in Part 1>` (e.g., `https://skillprobe-backend-xxxx.onrender.com`)
   
4. **Deploy**
   - Click **Deploy**. Vercel will build the frontend using the rules defined in `frontend/vercel.json`.
   - Vercel will give you a live URL (e.g., `https://skillprobe-frontend.vercel.app`).

---

## Part 3: Securing CORS (Final Step)

Right now, your backend on Render is allowing requests from `*` (anywhere). To be secure and prevent others from using your API (and your Gemini credits), you should restrict it to your Vercel frontend.

1. Go back to the **Render Dashboard** -> Your Web Service -> **Environment**.
2. Find the `CORS_ORIGINS` variable.
3. Change its value from `*` to your new Vercel domain:
   - Example: `https://skillprobe-frontend.vercel.app`
4. Save the changes. Render will quickly restart the service.


