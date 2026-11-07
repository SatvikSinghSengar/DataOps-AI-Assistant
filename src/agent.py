
import json
import ollama

from dataops_tools import (
    run_dataops_pipeline,
    get_dataops_report
)


# ==========================================
# 1. MODEL CONFIGURATION
# ==========================================

MODEL_NAME = "qwen3:1.7b"

OLLAMA_OPTIONS = {
    "num_ctx": 2048,
    "num_predict": 768,
    "temperature": 0
}


# ==========================================
# 2. SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are DataOps AI Assistant, an intelligent DataOps analyst.

Your responsibility is to analyze data pipeline execution,
data quality issues, investigation findings, and business impact.

STRICT ACCURACY RULES:

1. Always use actual data returned by Python tools.
2. Never invent issue counts, severity levels, or pipeline results.
3. Preserve exact severity assigned by the validator:
   CRITICAL, WARNING, or other reported values.
4. Never classify WARNING as CRITICAL.
5. Distinguish between failed validation rules,
   affected records, critical failed rules, and critical issue counts.
6. Issue counts from different rules may overlap.
7. Treat possible causes as hypotheses, not confirmed root causes.
8. Do not recommend deleting or modifying records without
   sufficient business context.
9. If information is unavailable, explicitly state that.
10. Never claim pipeline execution unless a Python tool confirms it.

REPORT INTERPRETATION:

- Missing CustomerID may affect customer-level analytics.
- Missing Description may affect product identification.
- Duplicate transactions require investigation before removal.
- Negative UnitPrice requires pricing investigation.
- Zero UnitPrice may represent legitimate promotional transactions.
- Negative quantities and cancelled invoices may represent returns.

VALIDATION REPORT RESPONSE:

When explaining a validation report, provide:

1. Dataset overview.
2. Overall validation status.
3. Three important findings ranked by severity and impact.
4. Actual issue counts and reported severity.
5. Recommended investigation actions.
6. Short business impact summary.

Use simple professional language.
Keep responses below 250 words.
Be concise, accurate, and evidence-based.

EXECUTION REPORT RULES:

1. Pipeline execution SUCCESS does not mean data quality SUCCESS.
2. Never infer data quality from execution status.
3. Never invent execution metrics or affected record counts.
4. Do not add recommendations unless requested.
5. Follow the requested output format.
6. Do not append unsolicited business impact summaries.
7. If information is unavailable, explicitly state that.
"""


# ==========================================
# 3. TOOL DEFINITIONS
# ==========================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_dataops_pipeline",
            "description": (
                "Execute the complete DataOps pipeline including "
                "profiling, validation, investigation and "
                "business impact analysis."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataops_report",
            "description": (
                "Retrieve a generated DataOps JSON report."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "report_name": {
                        "type": "string",
                        "enum": [
                            "profile",
                            "validation",
                            "investigation",
                            "business_impact",
                            "execution"
                        ],
                        "description": "The report to retrieve."
                    }
                },
                "required": ["report_name"]
            }
        }
    }
]


# ==========================================
# 4. PYTHON TOOL EXECUTION
# ==========================================

def execute_tool(tool_name, arguments):

    if tool_name == "run_dataops_pipeline":
        return run_dataops_pipeline()

    elif tool_name == "get_dataops_report":

        report_name = arguments.get("report_name", "")

        return get_dataops_report(report_name)

    return {
        "status": "FAILED",
        "error": f"Unknown tool: {tool_name}"
    }


# ==========================================
# 5. DETERMINISTIC EXECUTION REPORT FORMATTER
# ==========================================

def format_execution_report(tool_result):

    # Verify report retrieval
    if tool_result.get("status") != "SUCCESS":

        return (
            "Execution Report: FAILED\n"
            f"Error: {tool_result.get('error', 'Report unavailable')}"
        )

    # Extract actual report from nested data field
    report = tool_result.get("data", {})

    if not report:
        return "Execution report data is unavailable."

    overall_status = report.get(
        "overall_status",
        "Not available"
    )

    total_duration = report.get("total_duration_seconds")

    if total_duration is None:
        total_duration_text = "Not available in the report"
    else:
        total_duration_text = f"{total_duration:.2f} seconds"

    output = [
        f"Execution Status: {overall_status}",
        f"Total Duration: {total_duration_text}",
        "",
        "Pipeline Module Status:"
    ]

    execution_results = report.get("execution_results", [])

    if not execution_results:
        output.append("Module execution details unavailable.")

    for result in execution_results:

        step = result.get("step", "Unknown module")

        status = result.get(
            "status",
            "Not available"
        )

        duration = result.get("duration_seconds")

        if duration is None:
            duration_text = "Duration unavailable"
        else:
            duration_text = f"{duration:.2f}s"

        output.append(
            f"- {step}: {status} ({duration_text})"
        )

    return "\n".join(output)


# ==========================================
# 6. AI AGENT
# ==========================================

def ask_agent(user_query):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    try:

        # First LLM call: determine whether a tool is required
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            options=OLLAMA_OPTIONS
        )

        message = response["message"]

        tool_calls = message.get("tool_calls") or []

        # No tool call: return normal AI response
        if not tool_calls:

            return message.get(
                "content",
                "No response generated."
            )

        messages.append(message)

        # Execute requested Python tools
        for tool_call in tool_calls:

            tool_name = tool_call["function"]["name"]

            arguments = tool_call["function"].get(
                "arguments",
                {}
            )

            print(f"\nExecuting tool: {tool_name}")

            tool_result = execute_tool(
                tool_name,
                arguments
            )

            # Direct Python formatting for execution report
            if (
                tool_name == "get_dataops_report"
                and arguments.get("report_name") == "execution"
            ):

                return format_execution_report(tool_result)

            # Send other tool results to the LLM
            messages.append({
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(tool_result)
            })

        # Second LLM call: interpret other tool results
        final_response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            options=OLLAMA_OPTIONS
        )

        return final_response["message"]["content"]

    except Exception as error:

        return (
            "Agent execution error: "
            f"{type(error).__name__}: {str(error)}"
        )


# ==========================================
# 7. APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":

    print("\n====================================")
    print("       DATAOPS AI ASSISTANT")
    print("====================================")

    print("\nChecking existing validation report...")

    report = get_dataops_report("validation")

    if report.get("status") != "SUCCESS":

        print(
            "Report retrieval failed:",
            report.get("error")
        )

        raise SystemExit(1)

    print("Existing validation report loaded successfully.")

    print("\nAgent is ready. Type 'exit' to stop.")

    while True:

        try:

            user_query = input("\nYou: ").strip()

            if user_query.lower() in ["exit", "quit"]:

                print("DataOps AI Assistant stopped.")
                break

            if not user_query:
                continue

            print("\nAgent is processing your request...")

            answer = ask_agent(user_query)

            print("\nDataOps AI Assistant:")
            print(answer)

        except (KeyboardInterrupt, EOFError):

            print("\nDataOps AI Assistant stopped.")
            break
