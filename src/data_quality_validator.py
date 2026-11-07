
import json
from datetime import date, datetime

import pandas as pd

from data_profiler import DATA_FILE, REPORT_DIR


def validate_data():
    print("Loading dataset for quality validation...")

    df = pd.read_excel(DATA_FILE, engine="openpyxl")

    results = []

    def add_check(rule_id, rule_name, severity, issue_count, description):
        results.append({
            "rule_id": rule_id,
            "rule_name": rule_name,
            "severity": severity,
            "status": "FAIL" if issue_count > 0 else "PASS",
            "issue_count": int(issue_count),
            "description": description
        })

    # DQ001: Missing CustomerID
    add_check(
        "DQ001",
        "Missing CustomerID",
        "WARNING",
        df["CustomerID"].isna().sum(),
        "CustomerID is missing. Transaction may still be valid."
    )

    # DQ002: Missing Description
    add_check(
        "DQ002",
        "Missing Description",
        "WARNING",
        df["Description"].isna().sum(),
        "Product description is missing."
    )

    # DQ003: Duplicate transactions
    add_check(
        "DQ003",
        "Duplicate transactions",
        "WARNING",
        df.duplicated().sum(),
        "Exact duplicate rows were detected."
    )

    # DQ004: Negative UnitPrice
    add_check(
        "DQ004",
        "Negative UnitPrice",
        "CRITICAL",
        (df["UnitPrice"] < 0).sum(),
        "UnitPrice is negative and requires investigation."
    )

    # DQ005: Zero UnitPrice
    add_check(
        "DQ005",
        "Zero UnitPrice",
        "WARNING",
        (df["UnitPrice"] == 0).sum(),
        "UnitPrice is zero. Verify whether this is intentional."
    )

    # DQ006: Invalid InvoiceDate
    parsed_dates = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )

    add_check(
        "DQ006",
        "Invalid InvoiceDate",
        "CRITICAL",
        parsed_dates.isna().sum(),
        "InvoiceDate is missing or cannot be interpreted as a date."
    )

    # DQ007: Zero Quantity
    add_check(
        "DQ007",
        "Zero Quantity",
        "WARNING",
        (df["Quantity"] == 0).sum(),
        "Quantity is zero and requires investigation."
    )

    # Business observations: not automatically treated as failures
    business_observations = [
        {
            "name": "Negative quantity records",
            "record_count": int((df["Quantity"] < 0).sum()),
            "interpretation": (
                "May represent returns or credit transactions. "
                "Do not automatically classify as invalid."
            )
        },
        {
            "name": "Cancelled invoices",
            "record_count": int(
                df["InvoiceNo"].astype(str).str.startswith("C").sum()
            ),
            "interpretation": (
                "Invoice numbers beginning with C indicate "
                "cancellations in this dataset."
            )
        }
    ]

    failed_checks = sum(
        1 for check in results if check["status"] == "FAIL"
    )

    critical_issues = sum(
        check["issue_count"]
        for check in results
        if check["severity"] == "CRITICAL"
    )

    report = {
        "dataset_name": "UCI Online Retail",
        "total_records": len(df),
        "total_checks": len(results),
        "failed_checks": failed_checks,
        "critical_issue_count": critical_issues,
        "overall_status": (
            "ATTENTION_REQUIRED" if failed_checks > 0 else "PASS"
        ),
        "validation_results": results,
        "business_observations": business_observations
    }

    output_file = REPORT_DIR / "data_quality_report.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, default=str)

    print("\n========== DATA QUALITY RESULTS ==========")

    for check in results:
        print(
            f'{check["rule_id"]} | '
            f'{check["status"]} | '
            f'{check["issue_count"]} issues | '
            f'{check["rule_name"]}'
        )

    print("\nOverall status:", report["overall_status"])
    print("Report saved at:", output_file)


if __name__ == "__main__":
    validate_data()
