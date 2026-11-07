
import json
import time
from pathlib import Path

from data_profiler import profile_retail_data
from data_quality_validator import validate_data
from ai_investigator import generate_investigation
from business_impact_analyzer import generate_business_impact_report


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"


def run_dataops_pipeline():
    print("\n======================================")
    print("       DATAOPS AI ASSISTANT")
    print("======================================")

    pipeline_start = time.time()
    execution_results = []

    pipeline_steps = [
        ("Data Profiling", profile_retail_data),
        ("Data Quality Validation", validate_data),
        ("AI Investigation", generate_investigation),
        ("Business Impact Analysis", generate_business_impact_report)
    ]

    for step_name, step_function in pipeline_steps:
        print(f"\nRunning: {step_name}")

        step_start = time.time()

        try:
            step_function()

            duration = round(time.time() - step_start, 2)

            execution_results.append({
                "step": step_name,
                "status": "SUCCESS",
                "duration_seconds": duration
            })

            print(f"Status: SUCCESS ({duration} seconds)")

        except Exception as error:
            duration = round(time.time() - step_start, 2)

            execution_results.append({
                "step": step_name,
                "status": "FAILED",
                "duration_seconds": duration,
                "error": str(error)
            })

            print(f"Status: FAILED")
            print(f"Error: {error}")
            print("\nPipeline stopped due to failure.")
            break

    total_duration = round(time.time() - pipeline_start, 2)

    execution_report = {
        "pipeline_name": "DataOps AI Assistant",
        "total_duration_seconds": total_duration,
        "execution_results": execution_results,
        "overall_status": (
            "SUCCESS"
            if len(execution_results) == len(pipeline_steps)
            and all(step["status"] == "SUCCESS"
                    for step in execution_results)
            else "FAILED"
        )
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report_path = REPORT_DIR / "dataops_execution_report.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(execution_report, file, indent=4)

    print("\n======================================")
    print("       PIPELINE EXECUTION SUMMARY")
    print("======================================")

    for result in execution_results:
        print(f"{result['step']}: {result['status']}")

    print(f"\nOverall Status: {execution_report['overall_status']}")
    print(f"Total Duration: {total_duration} seconds")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    run_dataops_pipeline()
