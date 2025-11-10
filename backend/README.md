# Backend Setup

Requirements
- Python 3.10+ (3.11 recommended)
- pip

Install dependencies

1. Create a virtual environment (optional but recommended)
2. Install Python packages:
   - They are pinned in `requirements.txt`.

Environment variables

Create a `.env` file in `backend/` with:

- JWT_SECRET_KEY=change-me
- DATABASE_URI=sqlite:///stegano.db (or your DB URI)
- FIREBASE_SERVICE_ACCOUNT=full\path\to\service-account.json

Firebase Admin

Download a Firebase service account key JSON from your Firebase project settings and set `FIREBASE_SERVICE_ACCOUNT` to its absolute path. This is required for authenticated API routes like /api/history, /api/preferences, /auth/profile.

Run the server

- python app.py

Endpoints (partial)

- POST /steganography/hide (multipart: image, message) -> returns PNG (and records history if Authorization Bearer Firebase ID token is provided)
- POST /steganography/extract (multipart: image) -> returns { message }
- POST /steganalysis/analyze (multipart: image) -> returns { is_stego, confidence }
- GET /uploads/<filename> -> serves saved images
- /api/* routes require a Firebase ID token in Authorization header and a configured service account.
