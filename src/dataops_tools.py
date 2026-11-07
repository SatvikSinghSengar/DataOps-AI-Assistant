
import json
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"
ORCHESTRATOR_PATH = PROJECT_DIR / "src" / "dataops_orchestrator.py"


def run_dataops_pipeline():
    """
    Execute the complete DataOps pipeline and return its execution result.
    """

    try:
        process = subprocess.run(
            [sys.executable, str(ORCHESTRATOR_PATH)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )

        if process.returncode != 0:
            return {
                "status": "FAILED",
                "error": process.stderr,
                "output": process.stdout
            }

        report_path = REPORT_DIR / "dataops_execution_report.json"

        if not report_path.exists():
            return {
                "status": "FAILED",
                "error": "Execution report was not generated."
            }

        with open(report_path, "r", encoding="utf-8") as file:
            execution_report = json.load(file)

        return {
            "status": execution_report.get("overall_status", "UNKNOWN"),
            "execution_report": execution_report,
            "output": process.stdout
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "FAILED",
            "error": "Pipeline execution exceeded the 300-second timeout."
        }

    except Exception as error:
        return {
            "status": "FAILED",
            "error": str(error)
        }


def get_dataops_report(report_name):
    """
    Retrieve a generated DataOps JSON report.
    """

    allowed_reports = {
        "profile": "retail_data_profile.json",
        "validation": "data_quality_report.json",
        "investigation": "ai_investigation_report.json",
        "business_impact": "business_impact_report.json",
        "execution": "dataops_execution_report.json"
    }

    if report_name not in allowed_reports:
        return {
            "status": "FAILED",
            "error": "Unknown report name.",
            "available_reports": list(allowed_reports.keys())
        }

    report_path = REPORT_DIR / allowed_reports[report_name]

    if not report_path.exists():
        return {
            "status": "FAILED",
            "error": f"Report not found: {report_name}"
        }

    try:
        with open(report_path, "r", encoding="utf-8") as file:
            report_data = json.load(file)

        return {
            "status": "SUCCESS",
            "report_name": report_name,
            "data": report_data
        }

    except json.JSONDecodeError:
        return {
            "status": "FAILED",
            "error": "The report contains invalid JSON."
        }


if __name__ == "__main__":
    print("Testing DataOps Tool Interface...")

    result = run_dataops_pipeline()

    print("\nPipeline Status:", result["status"])

    if result["status"] == "SUCCESS":
        print("\nTesting report retrieval...")

        report = get_dataops_report("validation")

        print("Report Retrieval:", report["status"])
        print("Available report:", report.get("report_name"))
    else:
        print(result.get("error", "Pipeline execution failed."))
