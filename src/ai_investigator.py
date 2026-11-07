
import json
from pathlib import Path
from datetime import datetime, timezone


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"

INPUT_FILE = REPORT_DIR / "data_quality_report.json"
OUTPUT_FILE = REPORT_DIR / "ai_investigation_report.json"


# --------------------------------------------------
# 2. Investigation knowledge base
# --------------------------------------------------

INVESTIGATION_RULES = {
    "DQ001": {
        "possible_causes": [
            "Customer information was not captured during checkout.",
            "Customer data was not available in the source transaction.",
            "Customer identification was optional for some purchases."
        ],
        "investigation_steps": [
            "Check whether missing CustomerID records are concentrated in particular countries.",
            "Compare missing CustomerID records with invoice types and transaction dates.",
            "Verify whether anonymous purchases are permitted by the business."
        ],
        "recommended_action": (
            "Preserve valid transactions. Investigate customer attribution "
            "requirements before applying any correction."
        )
    },

    "DQ002": {
        "possible_causes": [
            "Product descriptions were not populated in the source system.",
            "Product master data may be incomplete.",
            "Product information may have been lost during data extraction."
        ],
        "investigation_steps": [
            "Identify the StockCode values associated with missing descriptions.",
            "Compare missing descriptions against the product master.",
            "Check whether the missing values are concentrated in specific periods."
        ],
        "recommended_action": (
            "Enrich descriptions from an authoritative product master where possible."
        )
    },

    "DQ003": {
        "possible_causes": [
            "Duplicate transactions may have entered the source system.",
            "Data extraction or ingestion may have processed records more than once.",
            "Duplicate records may have originated from an upstream integration."
        ],
        "investigation_steps": [
            "Identify the duplicated transaction keys and exact duplicate rows.",
            "Check source extraction and ingestion logs.",
            "Determine whether duplicates are present in the original source dataset."
        ],
        "recommended_action": (
            "Verify duplicates against source records before removing them."
        )
    },

    "DQ004": {
        "possible_causes": [
            "Incorrect UnitPrice values may have originated in the source system.",
            "A data transformation or mapping error may have changed the price.",
            "Negative prices may represent exceptional business adjustments."
        ],
        "investigation_steps": [
            "Extract the two records containing negative UnitPrice values.",
            "Inspect their InvoiceNo, StockCode, Quantity and InvoiceDate.",
            "Check whether these records represent legitimate adjustments or erroneous prices.",
            "Compare the values with the original transaction records."
        ],
        "recommended_action": (
            "Treat as a critical investigation item. Do not automatically "
            "replace negative prices with zero or delete the transactions."
        )
    },

    "DQ005": {
        "possible_causes": [
            "Zero-priced items may represent promotional or complimentary products.",
            "The source system may have incomplete pricing information.",
            "A pricing transformation may have incorrectly assigned zero."
        ],
        "investigation_steps": [
            "Identify the StockCode and InvoiceNo values with zero UnitPrice.",
            "Check whether these items belong to promotional transactions.",
            "Compare zero-priced records with other transactions for the same product."
        ],
        "recommended_action": (
            "Verify business context before changing zero-priced transactions."
        )
    },

    "DQ006": {
        "possible_causes": [],
        "investigation_steps": [],
        "recommended_action": "No action required. Validation passed."
    },

    "DQ007": {
        "possible_causes": [],
        "investigation_steps": [],
        "recommended_action": "No action required. Validation passed."
    }
}


# --------------------------------------------------
# 3. Load validation report
# --------------------------------------------------

def load_validation_report():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Validation report not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        report = json.load(file)

    if "validation_results" not in report:
        raise ValueError("Missing validation_results in input report.")

    return report


# --------------------------------------------------
# 4. Investigate individual validation results
# --------------------------------------------------

def investigate_check(check):

    rule_id = check["rule_id"]
    status = check["status"]
    issue_count = check["issue_count"]

    knowledge = INVESTIGATION_RULES.get(rule_id, {
        "possible_causes": [],
        "investigation_steps": [],
        "recommended_action": "Manual investigation required."
    })

    if status == "PASS":
        investigation_status = "NO_ACTION_REQUIRED"

    elif check["severity"] == "CRITICAL":
        investigation_status = "CRITICAL_INVESTIGATION_REQUIRED"

    else:
        investigation_status = "REVIEW_RECOMMENDED"

    return {
        "rule_id": rule_id,
        "rule_name": check["rule_name"],
        "severity": check["severity"],
        "validation_status": status,
        "issue_count": issue_count,
        "observed_fact": check["description"],
        "possible_root_causes": knowledge["possible_causes"],
        "root_cause_status": (
            "HYPOTHESES_NOT_VERIFIED"
            if knowledge["possible_causes"]
            else "NOT_APPLICABLE"
        ),
        "investigation_status": investigation_status,
        "investigation_steps": knowledge["investigation_steps"],
        "recommended_action": knowledge["recommended_action"]
    }


# --------------------------------------------------
# 5. Generate overall pipeline recommendation
# --------------------------------------------------

def determine_pipeline_recommendation(results):

    critical_failures = [
        result for result in results
        if result["severity"] == "CRITICAL"
        and result["validation_status"] == "FAIL"
    ]

    warning_failures = [
        result for result in results
        if result["severity"] == "WARNING"
        and result["validation_status"] == "FAIL"
    ]

    if critical_failures:
        return {
            "decision": "HOLD_FOR_INVESTIGATION",
            "reason": (
                "Critical data-quality failures were detected. "
                "Investigate them before approving the pipeline."
            )
        }

    if warning_failures:
        return {
            "decision": "SUCCESS_WITH_WARNINGS",
            "reason": (
                "No critical failures were detected. "
                "Review warning-level issues according to business rules."
            )
        }

    return {
        "decision": "SUCCESS",
        "reason": "All data-quality checks passed."
    }


# --------------------------------------------------
# 6. Generate complete investigation report
# --------------------------------------------------

def generate_investigation():

    report = load_validation_report()

    results = [
        investigate_check(check)
        for check in report["validation_results"]
    ]

    critical_failures = sum(
        1 for result in results
        if result["severity"] == "CRITICAL"
        and result["validation_status"] == "FAIL"
    )

    warning_failures = sum(
        1 for result in results
        if result["severity"] == "WARNING"
        and result["validation_status"] == "FAIL"
    )

    investigation_report = {
        "report_type": "AI Data Quality Investigation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_name": report["dataset_name"],
        "total_records": report["total_records"],
        "validation_summary": {
            "total_checks": len(results),
            "failed_checks": sum(
                1 for result in results
                if result["validation_status"] == "FAIL"
            ),
            "critical_failed_checks": critical_failures,
            "warning_failed_checks": warning_failures
        },
        "pipeline_recommendation": (
            determine_pipeline_recommendation(results)
        ),
        "investigation_results": results,
        "business_observations": report.get(
            "business_observations", []
        ),
        "important_note": (
            "Issue counts across different rules may overlap. "
            "They must not be interpreted as unique affected records. "
            "Possible root causes are hypotheses and require verification."
        )
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            investigation_report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nDATAOPS AI INVESTIGATION COMPLETED")
    print("-----------------------------------")
    print(f"Dataset: {report['dataset_name']}")
    print(f"Total checks: {len(results)}")
    print(f"Critical failed checks: {critical_failures}")
    print(f"Warning failed checks: {warning_failures}")

    decision = investigation_report["pipeline_recommendation"]

    print(f"\nPipeline decision: {decision['decision']}")
    print(f"Reason: {decision['reason']}")

    print(f"\nInvestigation report saved: {OUTPUT_FILE}")


# --------------------------------------------------
# 7. Execution entry point
# --------------------------------------------------

if __name__ == "__main__":
    generate_investigation()
