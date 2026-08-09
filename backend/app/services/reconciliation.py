from collections import defaultdict

from app.schemas.billing import BillingRecord
from app.schemas.report import (
    PaymentModeReport,
    ReconciliationReport,
)


def calculate_billed(record: BillingRecord) -> int:
    """
    Calculate the billed amount for a normal transaction.
    All amounts remain in paise.
    """
    gross_amount = sum(
        item.qty * item.unit_price_paise
        for item in record.line_items
    )

    return gross_amount - record.discount_paise


def calculate_reconciliation(
    records: list[BillingRecord],
) -> ReconciliationReport:

    total_billed = 0
    total_collected = 0
    total_outstanding = 0
    total_refunds = 0

    payment_data = defaultdict(
        lambda: {
            "billed": 0,
            "collected": 0,
            "outstanding": 0,
            "refunds": 0,
        }
    )

    for record in records:

        payment_mode = record.payment_mode.value

        # Refunds are handled separately.
        if record.is_refund:
            refund_amount = abs(record.amount_paid_paise)

            total_refunds += refund_amount
            payment_data[payment_mode]["refunds"] += refund_amount

            continue

        billed = calculate_billed(record)
        collected = record.amount_paid_paise
        outstanding = billed - collected

        total_billed += billed
        total_collected += collected
        total_outstanding += outstanding

        payment_data[payment_mode]["billed"] += billed
        payment_data[payment_mode]["collected"] += collected
        payment_data[payment_mode]["outstanding"] += outstanding

    by_payment_mode = {
        mode: PaymentModeReport(
            billed_paise=data["billed"],
            collected_paise=data["collected"],
            outstanding_paise=data["outstanding"],
            refunds_paise=data["refunds"],
        )
        for mode, data in payment_data.items()
    }

    return ReconciliationReport(
        total_billed_paise=total_billed,
        total_collected_paise=total_collected,
        total_outstanding_paise=total_outstanding,
        total_refunds_paise=total_refunds,
        by_payment_mode=by_payment_mode,
    )