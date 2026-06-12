"""
Upload router – handles bank statement CSV ingestion.

Endpoints:
    POST /upload/statement  – Upload and parse a CSV bank statement.
    GET  /upload/files      – List previously uploaded files.
"""

from datetime import datetime
from io import StringIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Transaction
from backend.schemas import FileUploadResponse
from backend.services import file_storage
from backend.services.llm_service import categorize_transactions

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/statement", response_model=FileUploadResponse)
def upload_statement(
    file: UploadFile = File(...),
    user_id: int = Query(default=1, description="Owner user ID"),
    db: Session = Depends(get_db),
) -> FileUploadResponse:
    """Upload a CSV bank statement and import its transactions.

    The CSV is expected to have the columns **Date**, **Description**,
    **Amount**, and **Type** (``credit`` or ``debit``).  Column matching
    is case-insensitive and leading/trailing whitespace is stripped.

    Transactions are optionally categorized using the LLM if a
    ``GEMINI_API_KEY`` is configured.
    """
    if not file.filename or not (file.filename.lower().endswith(".csv") or file.filename.lower().endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only CSV or PDF files are accepted.")

    # ── Save file to disk ───────────────────────────────────────────
    try:
        saved_path = file_storage.save_upload(file, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # ── Read and parse CSV ──────────────────────────────────────────
    file.file.seek(0)  # rewind after save
    try:
        if file.filename.lower().endswith(".csv"):
            raw = file.file.read().decode("utf-8")
            df = pd.read_csv(StringIO(raw))
        elif file.filename.lower().endswith(".pdf"):
            import pdfplumber
            df_list = []
            with pdfplumber.open(file.file) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table and len(table) > 1:
                        # Ensure headers don't have newlines
                        headers = [str(h).replace('\n', ' ') if h else '' for h in table[0]]
                        df_list.append(pd.DataFrame(table[1:], columns=headers))
            if not df_list:
                raise ValueError("No tabular data found in the PDF.")
            df = pd.concat(df_list, ignore_index=True)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse file: {exc}",
        )

    # Normalise column names.
    df.columns = df.columns.str.strip().str.lower()

    # Map common variations to standard names
    col_mapping = {}
    for col in df.columns:
        if "amount" in col:
            col_mapping[col] = "amount"
        elif "date" in col:
            col_mapping[col] = "date"
        elif "description" in col or "narration" in col or "particulars" in col:
            col_mapping[col] = "description"
        elif "type" in col or "cr/dr" in col:
            col_mapping[col] = "type"
            
    df = df.rename(columns=col_mapping)

    required_cols = {"date", "description", "amount", "type"}
    missing = required_cols - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"File is missing required columns: {', '.join(sorted(missing))}. "
                   f"Found columns: {', '.join(df.columns.tolist())}",
        )

    # Drop rows with all-NaN values and coerce types.
    df = df.dropna(how="all")
    amount_str = df["amount"].astype(str).str.replace('−', '-').str.replace(',', '').str.replace(' ', '')
    amount_str = amount_str.str.replace(r'[^\d\.\-\+]', '', regex=True)
    df["amount"] = pd.to_numeric(amount_str, errors="coerce").fillna(0)
    df["type"] = df["type"].astype(str).str.strip().str.lower()
    df["description"] = df["description"].astype(str).str.strip()

    # ── Optional: categorize via LLM ────────────────────────────────
    txn_dicts = [
        {
            "description": row["description"],
            "amount": row["amount"],
            "transaction_type": row["type"],
        }
        for _, row in df.iterrows()
    ]

    try:
        categories = categorize_transactions(txn_dicts)
    except Exception:
        categories = ["Other"] * len(txn_dicts)

    # ── Persist transactions ────────────────────────────────────────
    imported = 0
    for idx, (_, row) in enumerate(df.iterrows()):
        try:
            parsed_date = pd.to_datetime(row["date"], dayfirst=True).date()
        except Exception:
            parsed_date = datetime.utcnow().date()

         # FOOLPROOF: Determine debit/credit mathematically if amount has a negative sign
        raw_amount = row["amount"]
        if raw_amount < 0:
            txn_type = "debit"
        else:
            txn_type = row["type"] if row["type"] in ("credit", "debit") else "debit"

        transaction = Transaction(
            user_id=user_id,
            date=parsed_date,
            description=row["description"],
            amount=abs(row["amount"]),
            category=categories[idx] if idx < len(categories) else "Other",
            transaction_type=txn_type,
            source_file=saved_path,
        )
        db.add(transaction)
        imported += 1

    db.commit()

    return FileUploadResponse(
        filename=file.filename or "unknown",
        transactions_imported=imported,
        message=f"Successfully imported {imported} transactions.",
    )


@router.get("/files")
def list_uploaded_files(
    user_id: int = Query(default=1, description="Owner user ID"),
) -> list[dict]:
    """List all files previously uploaded by a user."""
    return file_storage.list_uploads(user_id)
