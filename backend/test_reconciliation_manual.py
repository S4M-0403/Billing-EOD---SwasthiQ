import json

from app.schemas.billing import BillingRecord
from app.services.reconciliation import calculate_reconciliation


with open(
    "../sample-data/billing_log_2026-07-25.json",
    "r",
) as file:
    data = json.load(file)


records = [
    BillingRecord.model_validate(row)
    for row in data
]


report = calculate_reconciliation(records)

print(report.model_dump())