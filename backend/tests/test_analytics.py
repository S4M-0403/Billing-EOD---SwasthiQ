from app.schemas.billing import BillingRecord
from app.services.analytics import calculate_analytics


def test_analytics():

    records = [
        BillingRecord(
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
            amount_paid_paise=10000,
            discount_paise=0,
            is_refund=False,
        ),
        BillingRecord(
            clinic_id="CLINIC-1",
            visit_id="VISIT-2",
            timestamp="2026-07-27T11:00:00Z",
            doctor_id="DOC-1",
            line_items=[
                {
                    "drug_name": "AMOXICILLIN",
                    "qty": 3,
                    "unit_price_paise": 6000,
                }
            ],
            payment_mode="upi",
            amount_paid_paise=18000,
            discount_paise=0,
            is_refund=False,
        ),
    ]

    report = calculate_analytics(records)

    assert report.peak_hour == 11

    assert report.revenue_by_hour[0].revenue_paise == 10000
    assert report.revenue_by_hour[1].revenue_paise == 18000

    assert report.top_medicines_by_quantity[0].drug_name == "AMOXICILLIN"
    assert report.top_medicines_by_quantity[0].quantity == 3

    assert report.top_medicines_by_revenue[0].drug_name == "AMOXICILLIN"
    assert report.top_medicines_by_revenue[0].revenue_paise == 18000