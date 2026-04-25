# Docker Setup

Create a `.env` file at the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
VITE_API_BASE_URL=http://localhost:8000
```

Run the full app:

```bash
docker compose up --build
```

URLs:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
