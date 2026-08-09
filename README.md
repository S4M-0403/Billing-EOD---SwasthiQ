# SwasthiQ — EOD Billing Intelligence

SwasthiQ is an AI-powered end-of-day billing intelligence system for clinics.

It takes a clinic billing JSON log, validates the records, performs deterministic financial reconciliation and analytics, and generates a concise AI-assisted end-of-day summary with traceable figures.

## What it does

- Validates billing records using Pydantic
- Detects malformed records
- Ensures a billing log belongs to a single clinic
- Detects duplicate visit IDs
- Calculates total billed amount
- Calculates collected and outstanding amounts
- Separately handles refunds
- Breaks reconciliation down by payment mode
- Calculates revenue by hour
- Identifies the peak revenue hour
- Finds top medicines by quantity
- Finds top medicines by revenue
- Generates a human-readable Gemini summary
- Grounds figures in the deterministic report
- Displays the source of figures used by the AI narrative
- Handles empty billing days gracefully

## Architecture

```text
                    Billing JSON
                         |
                         v
              +---------------------+
              | FastAPI / Pydantic  |
              | Validation Layer    |
              +----------+----------+
                         |
                         v
              +---------------------+
              | Deterministic       |
              | Billing Analysis    |
              +----------+----------+
                         |
             +-----------+-----------+
             |                       |
             v                       v
       Reconciliation            Analytics
             |                       |
             +-----------+-----------+
                         |
                         v
                 Structured EOD
                     Report
                         |
                         v
                  Gemini API
                         |
                         v
                Narrative Template
                         |
                         v
                Token Validation
                         |
                         v
              Grounded Final Narrative
                         |
              +----------+----------+
              |                     |
              v                     v
        AI Summary UI        Traced Figures

Key design decision: deterministic financial calculations

Gemini is not trusted to calculate financial figures.

All financial calculations are performed by the backend first.

The AI receives the deterministic report and generates a narrative using approved metric placeholders.

For example:

{{total_billed}}
{{total_collected}}
{{total_outstanding}}
{{peak_hour}}
{{top_quantity}}
{{top_revenue}}

The backend then replaces these placeholders with values from the deterministic report.

This means a number displayed in the AI summary can be traced back to its source field.

Example:

₹3,190.00
        |
        v
reconciliation.total_billed_paise

The AI therefore provides language and summarization, while Python remains responsible for financial correctness.

Empty and invalid data handling

An empty billing file is treated as a valid zero-transaction day.

Malformed records are rejected before they reach the AI layer.

For example, if a billing record is missing a required field such as payment_mode, validation fails with a structured error instead of allowing Gemini to process incomplete data.

Tech Stack
Backend
Python
FastAPI
Pydantic
Google Gemini API
Uvicorn
Frontend
React
TypeScript
Vite
Tailwind CSS
Recharts
React Router
Project Structure
SwasthiQ/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── sample-data/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   │
│   └── package.json
│
├── README.md
└── .gitignore
Running locally
Backend

From the project root:

cd backend

Create a virtual environment:

python -m venv venv

Windows:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Create a .env file:

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

Start the API:

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
Frontend

Open another terminal:

cd frontend
npm install
npm run dev

The frontend will be available at:

http://localhost:5173
Environment Variables

Backend:

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

Frontend:

VITE_API_URL=

Secrets such as the Gemini API key must never be committed to the repository.

Testing

The application was tested against:

Refund-only day

Expected behavior:

Zero billing
Zero collection
Refunds shown separately
No revenue chart
No medicine rankings
Empty day

Expected behavior:

Zero billing
Zero collection
Zero outstanding
Zero refunds
Clear empty-state UI
No hallucinated analytics
Valid transaction data

Expected behavior:

Reconciliation populated
Revenue-by-hour analytics populated
Peak hour identified
Medicine rankings populated
Gemini narrative generated
Figures displayed with traceability
Malformed data

Expected behavior:

Validation fails
HTTP 422 response
Error shown in the frontend
Gemini is not called
Previous report state is cleared
Example grounded narrative
Good evening! Here's today's summary for CLN-KNP-014 (27 Jul):

₹3,190.00 billed, ₹3,172.00 collected (99.4%).

₹18.00 is still outstanding.

Busiest hour: 1pm–2pm, with ₹760.00 in revenue.

Top mover by quantity: OMEPRAZOLE (18 units).

Top by revenue: ATORVASTATIN (₹1,200.00).

No refunds were recorded today.

Note: cost data wasn't available today, so this is revenue,
not profit — flagging rather than estimating.
API

The backend exposes endpoints for:

Health checks
Billing validation
Billing analysis
AI-assisted billing analysis

Interactive API documentation is available through FastAPI Swagger at /docs.

Notes

The project intentionally keeps financial computation deterministic and separates it from natural-language generation.

This architecture reduces the risk of hallucinated financial figures while still using an LLM where it provides the most value: converting structured billing analytics into a concise, human-readable end-of-day summary.