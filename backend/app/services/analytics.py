from collections import defaultdict

from app.schemas.billing import BillingRecord
from app.schemas.report import (
    AnalyticsReport,
    HourlyRevenue,
    MedicineQuantity,
    MedicineRevenue,
)


def calculate_analytics(
    records: list[BillingRecord],
) -> AnalyticsReport:

    revenue_by_hour = defaultdict(int)
    medicine_quantity = defaultdict(int)
    medicine_revenue = defaultdict(int)

    for record in records:

        # Refunds are not treated as medicine sales.
        if record.is_refund:
            continue

        hour = record.timestamp.hour

        billed = (
            sum(
                item.qty * item.unit_price_paise
                for item in record.line_items
            )
            - record.discount_paise
        )

        revenue_by_hour[hour] += billed

        for item in record.line_items:
            medicine_quantity[item.drug_name] += item.qty
            medicine_revenue[item.drug_name] += (
                item.qty * item.unit_price_paise
            )

    hourly_data = [
        HourlyRevenue(
            hour=hour,
            revenue_paise=revenue,
        )
        for hour, revenue in sorted(revenue_by_hour.items())
    ]

    peak_hour = None

    if revenue_by_hour:
        peak_hour = max(
            revenue_by_hour,
            key=revenue_by_hour.get,
        )

    quantity_ranking = sorted(
        medicine_quantity.items(),
        key=lambda item: (-item[1], item[0]),
    )

    revenue_ranking = sorted(
        medicine_revenue.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return AnalyticsReport(
        revenue_by_hour=hourly_data,
        peak_hour=peak_hour,
        top_medicines_by_quantity=[
            MedicineQuantity(
                drug_name=name,
                quantity=quantity,
            )
            for name, quantity in quantity_ranking[:5]
        ],
        top_medicines_by_revenue=[
            MedicineRevenue(
                drug_name=name,
                revenue_paise=revenue,
            )
            for name, revenue in revenue_ranking[:5]
        ],
    )