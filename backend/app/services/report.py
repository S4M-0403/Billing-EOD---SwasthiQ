import re

from app.schemas.billing import BillingRecord
from app.schemas.report import EODReport
from app.services.analytics import calculate_analytics
from app.services.reconciliation import calculate_reconciliation


def generate_eod_report(
    records: list[BillingRecord],
    filename: str | None = None,
) -> EODReport:

    reconciliation = calculate_reconciliation(records)
    analytics = calculate_analytics(records)

    # Empty billing day
    if not records:
        report_date = "Unknown"

        if filename:
            match = re.search(
                r"\d{4}-\d{2}-\d{2}",
                filename,
            )

            if match:
                report_date = match.group(0)

        return EODReport(
            clinic_id="Unknown",
            report_date=report_date,
            reconciliation=reconciliation,
            analytics=analytics,
        )

    clinic_id = records[0].clinic_id
    report_date = records[0].timestamp.date().isoformat()

    return EODReport(
        clinic_id=clinic_id,
        report_date=report_date,
        reconciliation=reconciliation,
        analytics=analytics,
    )