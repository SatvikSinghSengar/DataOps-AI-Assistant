
import pandas as pd
import json
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Original dataset location
DATA_FILE = BASE_DIR / "data" / "Online_Retail.xlsx"

# Output directory
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def profile_retail_data():

    print("Reading Online Retail dataset...")

    df = pd.read_excel(
        DATA_FILE,
        engine="openpyxl"
    )

    print("Dataset loaded successfully.")

    # Basic dataset information
    total_rows = len(df)
    total_columns = len(df.columns)

    # Missing values
    missing_values = {
        col: int(count)
        for col, count in df.isnull().sum().items()
        if count > 0
    }

    # Duplicate records
    duplicate_records = int(df.duplicated().sum())

    # Numeric statistics
    numeric_summary = {}

    for col in ["Quantity", "UnitPrice"]:
        numeric_summary[col] = {
            "minimum": float(df[col].min()),
            "maximum": float(df[col].max()),
            "mean": round(float(df[col].mean()), 2)
        }

    # Business-level observations
    negative_quantity = int((df["Quantity"] < 0).sum())
    zero_price = int((df["UnitPrice"] == 0).sum())
    negative_price = int((df["UnitPrice"] < 0).sum())

    cancelled_invoices = int(
        df["InvoiceNo"]
        .astype(str)
        .str.startswith("C")
        .sum()
    )

    # Date information
    invoice_dates = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    # Generate profile
    report = {
        "dataset_name": "UCI Online Retail",
        "total_rows": total_rows,
        "total_columns": total_columns,
        "columns": list(df.columns),
        "data_types": {
            col: str(dtype)
            for col, dtype in df.dtypes.items()
        },
        "missing_values": missing_values,
        "duplicate_records": duplicate_records,
        "numeric_summary": numeric_summary,
        "negative_quantity_records": negative_quantity,
        "zero_price_records": zero_price,
        "negative_price_records": negative_price,
        "cancelled_invoice_records": cancelled_invoices,
        "invalid_invoice_dates": int(invoice_dates.isna().sum()),
        "unique_customers": int(df["CustomerID"].nunique()),
        "unique_products": int(df["StockCode"].nunique()),
        "unique_countries": int(df["Country"].nunique()),
        "date_range": {
            "start": str(invoice_dates.min()),
            "end": str(invoice_dates.max())
        }
    }

    # Display report
    print("\n========== DATA PROFILE ==========")
    print(json.dumps(report, indent=4))

    # Save report
    output_file = REPORT_DIR / "retail_data_profile.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nProfile saved successfully:")
    print(output_file)


if __name__ == "__main__":

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    profile_retail_data()
