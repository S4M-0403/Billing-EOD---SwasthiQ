from pydantic import ValidationError

from app.schemas.billing import BillingRecord


class BillingValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Billing log validation failed")


def parse_billing_log(data: list) -> list[BillingRecord]:
    if not isinstance(data, list):
        raise BillingValidationError([
            {
                "index": None,
                "error": "Billing log must be a JSON array"
            }
        ])

    records = []
    errors = []

    # Validate each individual record
    for index, row in enumerate(data):
        try:
            record = BillingRecord.model_validate(row)
            records.append(record)

        except ValidationError as exc:
            errors.append({
                "index": index,
                "errors": exc.errors()
            })

    # If any individual records failed validation,
    # reject the entire billing log.
    if errors:
        raise BillingValidationError(errors)

    # A billing file must contain records
    # from exactly one clinic.
    clinic_ids = {record.clinic_id for record in records}

    if len(clinic_ids) > 1:
        raise BillingValidationError([
            {
                "index": None,
                "error": (
                    "Billing log must contain records "
                    "from a single clinic."
                )
            }
        ])

    # visit_id must be unique within the file.
    visit_ids = [record.visit_id for record in records]

    duplicates = {
        visit_id
        for visit_id in visit_ids
        if visit_ids.count(visit_id) > 1
    }

    if duplicates:
        raise BillingValidationError([
            {
                "index": None,
                "error": (
                    f"Duplicate visit_id values: "
                    f"{sorted(duplicates)}"
                )
            }
        ])

    return records