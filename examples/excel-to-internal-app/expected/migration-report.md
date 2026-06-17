# Migration Report: Customer CRM

- Source CSV: `examples/excel-to-internal-app/sample_data/customers.csv`
- Target table: `customer_crm`
- Rows inspected: `2`

## Inferred Fields

- `customer_id` -> `INTEGER`
- `name` -> `TEXT`
- `signup_date` -> `DATE`
- `monthly_fee` -> `REAL`
- `active` -> `TEXT`

## Next Steps

- Review field names and types before importing production data.

