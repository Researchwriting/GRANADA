# GRANADA
Smart Grant Writing and Donor Matching System for NGOs, Researchers, and Institutions. Automates proposal generation, SDG tagging, logframes, budgets, and maps open donor calls in real time.

## Development

Build the stack using Docker Compose:

```bash
docker-compose up --build
```

The backend will be available at `http://localhost:8000` and the frontend at `http://localhost:3000`.

To run the FastAPI server locally without Docker:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

Install dependencies and run in development mode:

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
