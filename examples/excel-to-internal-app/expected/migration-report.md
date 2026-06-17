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

## Data Quality

- `customer_id`: blanks `0`, unique values `2`
- `name`: blanks `0`, unique values `2`
- `signup_date`: blanks `0`, unique values `2`
- `monthly_fee`: blanks `0`, unique values `2`
- `active`: blanks `0`, unique values `2`

## Permissions

- Admin: create, update, delete, export, and manage roles.
- Operator: create and update records; export only with approval.
- Viewer: read-only access to approved records.

## Suggested App Screens

- List view with filters for high-volume daily work.
- Detail/edit view with validation messages for each inferred field.
- Import review screen that blocks promotion until blanks and duplicates are accepted.

## Next Steps

- Review field names and types before importing production data.
- Resolve blank required fields before using the generated schema in production.
- Add permissions and audit logging before exposing this as an internal app.
