from pydantic import BaseModel


class PaymentModeReport(BaseModel):
    billed_paise: int
    collected_paise: int
    outstanding_paise: int
    refunds_paise: int


class ReconciliationReport(BaseModel):
    total_billed_paise: int
    total_collected_paise: int
    total_outstanding_paise: int
    total_refunds_paise: int
    by_payment_mode: dict[str, PaymentModeReport]


class HourlyRevenue(BaseModel):
    hour: int
    revenue_paise: int


class MedicineQuantity(BaseModel):
    drug_name: str
    quantity: int


class MedicineRevenue(BaseModel):
    drug_name: str
    revenue_paise: int


class AnalyticsReport(BaseModel):
    revenue_by_hour: list[HourlyRevenue]
    peak_hour: int | None
    top_medicines_by_quantity: list[MedicineQuantity]
    top_medicines_by_revenue: list[MedicineRevenue]

class EODReport(BaseModel):
    clinic_id: str
    report_date: str

    reconciliation: ReconciliationReport
    analytics: AnalyticsReport

class TracedFigure(BaseModel):
    token: str
    display_value: str
    source: str


class NarrativeResponse(BaseModel):
    narrative_template: str


class FinalNarrative(BaseModel):
    narrative: str
    traced_figures: list[TracedFigure]