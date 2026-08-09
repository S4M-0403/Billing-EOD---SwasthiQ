import json

from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.narrative import generate_narrative
from app.services.parser import (
    parse_billing_log,
    BillingValidationError,
)
from app.services.report import generate_eod_report


router = APIRouter(
    prefix="/billing",
    tags=["Billing"],
)


@router.post("/validate")
async def validate_billing_log(
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()
        data = json.loads(contents)

        records = parse_billing_log(data)

        return {
            "valid": True,
            "record_count": len(records),
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not valid JSON.",
        )

    except BillingValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Billing log validation failed",
                "errors": exc.errors,
            },
        )


@router.post("/analyze")
async def analyze_billing_log(
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()
        data = json.loads(contents)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not valid JSON.",
        )

    try:
        records = parse_billing_log(data)

    except BillingValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Billing log validation failed",
                "errors": exc.errors,
            },
        )

    try:
        report = generate_eod_report(records)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return report
@router.post("/analyze-with-narrative")
async def analyze_with_narrative(
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()
        data = json.loads(contents)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not valid JSON.",
        )

    try:
        records = parse_billing_log(data)
        report = generate_eod_report(
    records,
    filename=file.filename,
)

    except BillingValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Billing log validation failed",
                "errors": exc.errors,
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    try:
        narrative = generate_narrative(report)

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Narrative generation failed.",
        )

    return {
        "report": report,
        "narrative": narrative,
    }