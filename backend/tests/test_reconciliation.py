from app.schemas.billing import BillingRecord
from app.services.reconciliation import calculate_reconciliation


def test_normal_transaction():

    record = BillingRecord(
        clinic_id="CLINIC-1",
        visit_id="VISIT-1",
        timestamp="2026-07-27T10:00:00Z",
        doctor_id="DOC-1",
        line_items=[
            {
                "drug_name": "PARACETAMOL",
                "qty": 2,
                "unit_price_paise": 5000,
            }
        ],
        payment_mode="cash",
        amount_paid_paise=8000,
        discount_paise=1000,
        is_refund=False,
    )

    report = calculate_reconciliation([record])

    assert report.total_billed_paise == 9000
    assert report.total_collected_paise == 8000
    assert report.total_outstanding_paise == 1000
    assert report.total_refunds_paise == 0

def test_refund():

    record = BillingRecord(
        clinic_id="CLINIC-1",
        visit_id="VISIT-2",
        timestamp="2026-07-27T10:00:00Z",
        doctor_id="DOC-1",
        line_items=[
            {
                "drug_name": "ATORVASTATIN",
                "qty": 2,
                "unit_price_paise": 12000,
            }
        ],
        payment_mode="card",
        amount_paid_paise=-24000,
        discount_paise=0,
        is_refund=True,
    )

    report = calculate_reconciliation([record])

    assert report.total_billed_paise == 0
    assert report.total_collected_paise == 0
    assert report.total_outstanding_paise == 0
    assert report.total_refunds_paise == 24000