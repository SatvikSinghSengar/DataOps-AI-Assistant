# DataOps AI Assistant

An AI-assisted DataOps prototype for dataset profiling, data-quality validation, issue investigation, and business-impact analysis.

## Problem

Data engineering teams spend time manually profiling datasets, identifying quality issues, investigating anomalies, and understanding downstream business impact. This project demonstrates an automated workflow that generates structured reports.

## Features

- **Data profiling:** Row counts, column counts, data types, missing values, duplicates, and statistical summaries.
- **Data-quality validation:** Checks for missing values, duplicates, negative prices, zero prices, invalid dates, and zero quantities.
- **AI investigation:** Summarizes findings and recommends investigation priorities.
- **Business-impact analysis:** Maps data-quality issues to potential effects on financial reporting, customer analytics, and product analytics.
- **Pipeline orchestration:** Runs the complete workflow and generates consolidated execution reports.
- **MCP integration:** Exposes pipeline execution and report retrieval to compatible AI clients.

## Architecture

```text
UCI Online Retail Dataset
          |
          v
     Data Profiler
          |
          v
 Data Quality Validator
          |
          v
    AI Investigator
          |
          v
 Business Impact Analyzer
          |
          v
      JSON Reports
          ^
          |
     Orchestrator
          |
          v
       MCP Server
          |
          v
 Compatible AI Client
