import re

from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.schemas.report import (
    EODReport,
    FinalNarrative,
    NarrativeResponse,
    TracedFigure,
)


client = genai.Client(api_key=GEMINI_API_KEY)


# Keep these as actual double-brace strings.
# We inject them into the Gemini prompt through variables
# instead of writing {{...}} directly inside an f-string.
T_CLINIC_ID = "{{clinic_id}}"
T_REPORT_DATE = "{{report_date}}"
T_TOTAL_BILLED = "{{total_billed}}"
T_TOTAL_COLLECTED = "{{total_collected}}"
T_TOTAL_OUTSTANDING = "{{total_outstanding}}"
T_TOTAL_REFUNDS = "{{total_refunds}}"
T_COLLECTION_PERCENTAGE = "{{collection_percentage}}"
T_PEAK_HOUR_RANGE = "{{peak_hour_range}}"
T_REVENUE_AT_PEAK = "{{revenue_at_peak_hour}}"
T_TOP_QUANTITY_MEDICINE = "{{top_quantity_medicine}}"
T_TOP_QUANTITY = "{{top_quantity}}"
T_TOP_REVENUE_MEDICINE = "{{top_revenue_medicine}}"
T_TOP_REVENUE = "{{top_revenue}}"


ALLOWED_TOKENS = {
    T_CLINIC_ID: "clinic_id",
    T_REPORT_DATE: "report_date",
    T_TOTAL_BILLED: "reconciliation.total_billed_paise",
    T_TOTAL_COLLECTED: "reconciliation.total_collected_paise",
    T_TOTAL_OUTSTANDING: "reconciliation.total_outstanding_paise",
    T_TOTAL_REFUNDS: "reconciliation.total_refunds_paise",
    T_COLLECTION_PERCENTAGE: "reconciliation.collection_percentage",
    T_PEAK_HOUR_RANGE: "analytics.peak_hour_range",
    T_REVENUE_AT_PEAK: "analytics.revenue_by_hour[peak_hour].revenue_paise",
    T_TOP_QUANTITY_MEDICINE:
        "analytics.top_medicines_by_quantity[0].drug_name",
    T_TOP_QUANTITY:
        "analytics.top_medicines_by_quantity[0].quantity",
    T_TOP_REVENUE_MEDICINE:
        "analytics.top_medicines_by_revenue[0].drug_name",
    T_TOP_REVENUE:
        "analytics.top_medicines_by_revenue[0].revenue_paise",
}


def format_rupees(paise: int) -> str:
    return f"₹{paise / 100:,.2f}"


def format_percentage(value: float) -> str:
    return f"{value:.1f}%"


def format_hour_range(hour: int) -> str:
    start = hour % 12 or 12

    end_hour = (hour + 1) % 24
    end = end_hour % 12 or 12

    start_suffix = "am" if hour < 12 else "pm"
    end_suffix = "am" if end_hour < 12 else "pm"

    return f"{start}{start_suffix}–{end}{end_suffix}"


def calculate_collection_percentage(
    report: EODReport,
) -> float:
    billed = report.reconciliation.total_billed_paise
    collected = report.reconciliation.total_collected_paise

    if billed <= 0:
        return 0.0

    return (
        report.reconciliation.total_collected_paise
        / billed
    ) * 100


def get_peak_data(report: EODReport):
    analytics = report.analytics

    if (
        analytics.peak_hour is None
        or not analytics.revenue_by_hour
    ):
        return None, None

    peak_hour = analytics.peak_hour

    peak_revenue = next(
        (
            item.revenue_paise
            for item in analytics.revenue_by_hour
            if item.hour == peak_hour
        ),
        None,
    )

    return peak_hour, peak_revenue


def get_token_values(
    report: EODReport,
) -> dict[str, str]:

    reconciliation = report.reconciliation
    analytics = report.analytics

    values = {
        T_CLINIC_ID: report.clinic_id,
        T_REPORT_DATE: report.report_date,

        T_TOTAL_BILLED:
            format_rupees(
                reconciliation.total_billed_paise
            ),

        T_TOTAL_COLLECTED:
            format_rupees(
                reconciliation.total_collected_paise
            ),

        T_TOTAL_OUTSTANDING:
            format_rupees(
                reconciliation.total_outstanding_paise
            ),

        T_TOTAL_REFUNDS:
            format_rupees(
                reconciliation.total_refunds_paise
            ),

        T_COLLECTION_PERCENTAGE:
            format_percentage(
                calculate_collection_percentage(report)
            ),
    }

    peak_hour, peak_revenue = get_peak_data(report)

    if peak_hour is not None and peak_revenue is not None:
        values[T_PEAK_HOUR_RANGE] = format_hour_range(
            peak_hour
        )

        values[T_REVENUE_AT_PEAK] = format_rupees(
            peak_revenue
        )

    if analytics.top_medicines_by_quantity:
        top_quantity = (
            analytics.top_medicines_by_quantity[0]
        )

        values[T_TOP_QUANTITY_MEDICINE] = (
            top_quantity.drug_name
        )

        values[T_TOP_QUANTITY] = str(
            top_quantity.quantity
        )

    if analytics.top_medicines_by_revenue:
        top_revenue = (
            analytics.top_medicines_by_revenue[0]
        )

        values[T_TOP_REVENUE_MEDICINE] = (
            top_revenue.drug_name
        )

        values[T_TOP_REVENUE] = format_rupees(
            top_revenue.revenue_paise
        )

    return values


def build_prompt(report: EODReport) -> str:

    report_json = report.model_dump_json(indent=2)

    return f"""
You are writing a concise end-of-day WhatsApp-style
billing summary for a clinic owner.

IMPORTANT:
You are NOT responsible for calculating any numbers.

Python has already calculated every metric.

You MUST preserve the exact placeholder tokens below.
NEVER replace a placeholder with a number.
NEVER calculate a number yourself.

Write the message in this style:

Good evening! Here's today's summary for {T_CLINIC_ID}
({T_REPORT_DATE}):

{T_TOTAL_BILLED} billed, {T_TOTAL_COLLECTED} collected
({T_COLLECTION_PERCENTAGE}).

{T_TOTAL_OUTSTANDING} is still outstanding.

Busiest hour: {T_PEAK_HOUR_RANGE}, with
{T_REVENUE_AT_PEAK} in revenue.

Top mover by quantity:
{T_TOP_QUANTITY_MEDICINE} ({T_TOP_QUANTITY} units).

Top by revenue:
{T_TOP_REVENUE_MEDICINE} ({T_TOP_REVENUE}).

If refunds exist:
{T_TOTAL_REFUNDS} was refunded today.

If refunds are zero:
No refunds were recorded today.

Finish with:

Note: cost data wasn't available today, so this is revenue,
not profit — flagging rather than estimating.

SUCCESS

STRICT RULES:

- Preserve every {{token}} exactly as written.
- Never replace tokens with actual numbers.
- Never output paise values such as 319000 or 317200.
- Never calculate percentages.
- Never calculate revenue.
- Never invent visit counts.
- Never claim profit.
- Never describe refunds as revenue.
- Keep the message concise.
- Use short paragraphs.
- Do not use markdown tables.
- End with SUCCESS.

If there are no transactions, write a short zero-activity
summary instead, while still using the available tokens.

DETERMINISTIC REPORT:

{report_json}

Return ONLY JSON matching the requested schema.
"""


def build_fallback_template(
    report: EODReport,
) -> str:

    r = report.reconciliation
    a = report.analytics

    values = get_token_values(report)

    billed = r.total_billed_paise
    refunds = r.total_refunds_paise

    # Empty day
    if (
        billed == 0
        and r.total_collected_paise == 0
        and r.total_outstanding_paise == 0
        and refunds == 0
        and not a.revenue_by_hour
    ):
        return (
            f"Good evening! Here's today's summary for "
            f"{T_CLINIC_ID} ({T_REPORT_DATE}):\n\n"
            f"No billing transactions were recorded today.\n\n"
            f"No revenue or refunds were recorded today.\n\n"
            f"Note: cost data wasn't available today, so this "
            f"is revenue, not profit — flagging rather than "
            f"estimating.\n\n"
            f"SUCCESS"
        )

    # Refund-only day
    if (
        billed == 0
        and refunds > 0
    ):
        return (
            f"Good evening! Here's today's summary for "
            f"{T_CLINIC_ID} ({T_REPORT_DATE}):\n\n"
            f"No billing transactions were recorded today.\n\n"
            f"{T_TOTAL_REFUNDS} was refunded today.\n\n"
            f"No revenue-generating transactions were "
            f"recorded today.\n\n"
            f"Note: cost data wasn't available today, so this "
            f"is revenue, not profit — flagging rather than "
            f"estimating.\n\n"
            f"SUCCESS"
        )

    # Normal billing day
    return (
        f"Good evening! Here's today's summary for "
        f"{T_CLINIC_ID} ({T_REPORT_DATE}):\n\n"

        f"{T_TOTAL_BILLED} billed, "
        f"{T_TOTAL_COLLECTED} collected "
        f"({T_COLLECTION_PERCENTAGE}).\n\n"

        f"{T_TOTAL_OUTSTANDING} is still outstanding.\n\n"

        f"Busiest hour: {T_PEAK_HOUR_RANGE}, "
        f"with {T_REVENUE_AT_PEAK} in revenue.\n\n"

        f"Top mover by quantity: "
        f"{T_TOP_QUANTITY_MEDICINE} "
        f"({T_TOP_QUANTITY} units).\n\n"

        f"Top by revenue: "
        f"{T_TOP_REVENUE_MEDICINE} "
        f"({T_TOP_REVENUE}).\n\n"

        f"{'No refunds were recorded today.' if refunds == 0 else T_TOTAL_REFUNDS + ' was refunded today.'}\n\n"

        f"Note: cost data wasn't available today, so this "
        f"is revenue, not profit — flagging rather than "
        f"estimating.\n\n"

        f"SUCCESS"
    )


def validate_tokens(
    template: str,
    token_values: dict[str, str],
) -> bool:

    found_tokens = set(
        re.findall(
            r"\{\{[^{}]+\}\}",
            template,
        )
    )

    unknown_tokens = (
        found_tokens - set(ALLOWED_TOKENS)
    )

    if unknown_tokens:
        raise ValueError(
            f"LLM returned unknown tokens: "
            f"{sorted(unknown_tokens)}"
        )

    missing_values = (
        found_tokens - set(token_values)
    )

    if missing_values:
        raise ValueError(
            f"LLM referenced unavailable metrics: "
            f"{sorted(missing_values)}"
        )

    return len(found_tokens) > 0


def generate_narrative(
    report: EODReport,
) -> FinalNarrative:

    prompt = build_prompt(report)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NarrativeResponse,
            temperature=0.2,
        ),
    )

    template = None

    if response.text:
        try:
            result = NarrativeResponse.model_validate_json(
                response.text
            )

            candidate = result.narrative_template

            token_values = get_token_values(report)

            # Gemini must return placeholders.
            # If it doesn't, use our deterministic grounded
            # template rather than displaying ungrounded numbers.
            if validate_tokens(
                candidate,
                token_values,
            ):
                template = candidate

        except Exception:
            template = None

    # Guaranteed safe fallback.
    if template is None:
        template = build_fallback_template(report)

    token_values = get_token_values(report)

    validate_tokens(
        template,
        token_values,
    )

    traced_figures = []

    for token, source in ALLOWED_TOKENS.items():

        if token not in template:
            continue

        display_value = token_values[token]

        traced_figures.append(
            TracedFigure(
                token=token,
                display_value=display_value,
                source=source,
            )
        )

        template = template.replace(
            token,
            display_value,
        )

    return FinalNarrative(
        narrative=template,
        traced_figures=traced_figures,
    )