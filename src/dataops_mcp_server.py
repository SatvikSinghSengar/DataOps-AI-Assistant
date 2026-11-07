
from mcp.server.fastmcp import FastMCP

from dataops_tools import (
    run_dataops_pipeline,
    get_dataops_report,
)

mcp = FastMCP("DataOps AI Assistant")


@mcp.tool()
def execute_dataops_pipeline() -> dict:
    """
    Execute the complete DataOps pipeline:
    data profiling, data quality validation,
    AI investigation, and business impact analysis.

    Returns the actual execution status and module results.
    """
    try:
        return run_dataops_pipeline()
    except Exception as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
        }


@mcp.tool()
def retrieve_dataops_report(report_name: str) -> dict:
    """
    Retrieve an existing DataOps report.

    Valid report names:
    profile, validation, investigation,
    business_impact, execution.
    """
    allowed_reports = {
        "profile",
        "validation",
        "investigation",
        "business_impact",
        "execution",
    }

    if report_name not in allowed_reports:
        return {
            "status": "ERROR",
            "error": "Invalid report name",
            "allowed_reports": sorted(allowed_reports),
        }

    try:
        return get_dataops_report(report_name)
    except Exception as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
