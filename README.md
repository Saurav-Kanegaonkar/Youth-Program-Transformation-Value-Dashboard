# Youth Program Transformation Value Dashboard

I built this because education program business value transformation and scenario tracking needs more than a dashboard: it needs a decision artifact that connects source data, analysis, and next actions.

![Youth Program Transformation Value Dashboard](docs/images/dashboard.png)

## What this project is

This project is a scorecard for education program business value transformation and scenario tracking. It uses synthetic but workflow-shaped data to rank program initiative-level risks and convert the output into stakeholder-ready recommendations.

## Data sources

- `entities.csv` - 36 program initiative records
- `daily_metrics.csv` - 5,040 daily operating rows
- `source_events.csv` - 760 event, exception, QA, and stakeholder-request records
- `recommended_actions.csv` - 220 action candidates

## Analysis outputs

- `analysis/executive_findings.md`
- `analysis/analysis_plan.md`
- `analysis/sql_checks.sql`
- `analysis/outputs/priority_queue.csv`

## Recommendation

Use the priority queue to focus stakeholder attention on the program initiative segments where performance upside, measurement risk, and operational readiness overlap.

## Run locally

```bash
python3 -m http.server 4173
```
