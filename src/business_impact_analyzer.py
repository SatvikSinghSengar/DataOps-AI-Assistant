
import json
from pathlib import Path
from datetime import datetime, timezone


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"

INPUT_FILE = REPORT_DIR / "ai_investigation_report.json"
OUTPUT_FILE = REPORT_DIR / "business_impact_report.json"


# --------------------------------------------------
# 2. Business impact knowledge base
# --------------------------------------------------

BUSINESS_IMPACT_RULES = {
    "DQ001": {
        "impact_area": "Customer Analytics",
        "priority": "HIGH",
        "business_impact": (
            "Missing CustomerID values may reduce the accuracy of "
            "customer segmentation, customer purchase history and "
            "customer lifetime value analysis."
        ),
        "affected_business_functions": [
            "Customer segmentation",
            "Customer behavior analysis",
            "Customer lifetime value reporting"
        ]
    },

    "DQ002": {
        "impact_area": "Product Analytics",
        "priority": "MEDIUM",
        "business_impact": (
            "Missing product descriptions may affect product identification, "
            "product-level reporting and catalog analysis."
        ),
        "affected_business_functions": [
            "Product reporting",
            "Product catalog analysis",
            "Product performance dashboards"
        ]
    },

    "DQ003": {
        "impact_area": "Financial and Transaction Reporting",
        "priority": "HIGH",
        "business_impact": (
            "Duplicate transactions may inflate transaction counts "
            "and potentially distort revenue and sales reporting."
        ),
        "affected_business_functions": [
            "Sales reporting",
            "Revenue analytics",
            "Transaction reconciliation"
        ]
    },

    "DQ004": {
        "impact_area": "Pricing and Financial Reporting",
        "priority": "CRITICAL",
        "business_impact": (
            "Negative UnitPrice values may distort pricing analysis "
            "and financial calculations if they are not legitimate "
            "business adjustments."
        ),
        "affected_business_functions": [
            "Revenue reporting",
            "Pricing analytics",
            "Financial reconciliation"
        ]
    },

    "DQ005": {
        "impact_area": "Revenue and Product Analytics",
        "priority": "MEDIUM",
        "business_impact": (
            "Zero-priced transactions may affect revenue calculations "
            "and product performance reporting. They may also represent "
            "legitimate promotional or complimentary items."
        ),
        "affected_business_functions": [
            "Revenue analytics",
            "Promotional analysis",
            "Product performance reporting"
        ]
    }
}


# --------------------------------------------------
# 3. Calculate percentage of affected records
# --------------------------------------------------

def calculate_affected_percentage(issue_count, total_records):

    if total_records == 0:
        return 0.0

    return round((issue_count / total_records) * 100, 2)


# --------------------------------------------------
# 4. Analyze individual business impact
# --------------------------------------------------

def analyze_business_impact(result, total_records):

    rule_id = result["rule_id"]

    knowledge = BUSINESS_IMPACT_RULES.get(rule_id)

    if not knowledge:
        return None

    issue_count = result["issue_count"]

    return {
        "rule_id": rule_id,
        "rule_name": result["rule_name"],
        "severity": result["severity"],
        "issue_count": issue_count,
        "affected_percentage": calculate_affected_percentage(
            issue_count,
            total_records
        ),
        "impact_area": knowledge["impact_area"],
        "business_priority": knowledge["priority"],
        "business_impact": knowledge["business_impact"],
        "affected_business_functions": (
            knowledge["affected_business_functions"]
        ),
        "root_cause_verified": False
    }


# --------------------------------------------------
# 5. Generate executive summary
# --------------------------------------------------

def generate_executive_summary(impacts, total_records):

    critical_count = sum(
        1 for item in impacts
        if item["business_priority"] == "CRITICAL"
    )

    high_count = sum(
        1 for item in impacts
        if item["business_priority"] == "HIGH"
    )

    medium_count = sum(
        1 for item in impacts
        if item["business_priority"] == "MEDIUM"
    )

    highest_priority = max(
        impacts,
        key=lambda item: {
            "CRITICAL": 3,
            "HIGH": 2,
            "MEDIUM": 1,
            "LOW": 0
        }.get(item["business_priority"], 0),
        default=None
    )

    if highest_priority:
        top_issue = (
            f"{highest_priority['rule_name']} "
            f"({highest_priority['issue_count']} records)"
        )
    else:
        top_issue = "No business-impact issues identified."

    return {
        "dataset_size": total_records,
        "identified_business_impact_areas": len(impacts),
        "critical_priority_issues": critical_count,
        "high_priority_issues": high_count,
        "medium_priority_issues": medium_count,
        "highest_priority_issue": top_issue,
        "overall_assessment": (
            "Business review is required before approving this dataset."
            if critical_count or high_count
            else "No high-priority business impact identified."
        ),
        "interpretation_note": (
            "Affected percentages are calculated independently for each "
            "rule. Records may overlap across rules, so percentages must "
            "not be added together."
        )
    }


# --------------------------------------------------
# 6. Main execution
# --------------------------------------------------

def generate_business_impact_report():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Investigation report not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        investigation = json.load(file)

    total_records = investigation["total_records"]

    impacts = []

    for result in investigation["investigation_results"]:

        if result["validation_status"] != "FAIL":
            continue

        impact = analyze_business_impact(
            result,
            total_records
        )

        if impact:
            impacts.append(impact)

    impacts.sort(
        key=lambda item: {
            "CRITICAL": 3,
            "HIGH": 2,
            "MEDIUM": 1,
            "LOW": 0
        }.get(item["business_priority"], 0),
        reverse=True
    )

    executive_summary = generate_executive_summary(
        impacts,
        total_records
    )

    output = {
        "report_type": "Business Impact Analysis",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_name": investigation["dataset_name"],
        "executive_summary": executive_summary,
        "business_impact_results": impacts,
        "pipeline_recommendation": (
            investigation["pipeline_recommendation"]
        )
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nBUSINESS IMPACT ANALYSIS COMPLETED")
    print("-----------------------------------")
    print(f"Dataset records: {total_records}")
    print(f"Impact areas identified: {len(impacts)}")
    print(
        "Critical priorities:",
        executive_summary["critical_priority_issues"]
    )
    print(
        "High priorities:",
        executive_summary["high_priority_issues"]
    )
    print(
        "Medium priorities:",
        executive_summary["medium_priority_issues"]
    )

    print("\nHighest priority issue:")
    print(executive_summary["highest_priority_issue"])

    print("\nOverall assessment:")
    print(executive_summary["overall_assessment"])

    print(f"\nReport saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_business_impact_report()
