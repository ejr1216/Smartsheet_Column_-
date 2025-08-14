import smartsheet

# ===== Configuration =====
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"  # Replace with your API token
SHEET_ID = 1234567890123456          # Replace with your sheet ID

# ===== Connect to Smartsheet =====
smartsheet_client = smartsheet.Smartsheet(ACCESS_TOKEN)

# Optional: Enable logging for debugging
smartsheet_client.errors_as_exceptions(True)

# ===== Get all columns =====
sheet = smartsheet_client.Sheets.get_sheet(SHEET_ID)

print(f"Columns for sheet '{sheet.name}':")
for col in sheet.columns:
    print(f"- {col.title} (ID: {col.id}, Type: {col.type})")