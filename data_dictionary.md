# Data Dictionary

| Dataset | Grain | Description |
| --- | --- | --- |
| `data/sites.csv` | Site | Youth-program site metadata, market, program model, source system, launch wave, and owner. |
| `data/weekly_program_metrics.csv` | Site-week | Operating metrics used for readiness scoring and scenario analysis. |
| `data/transformation_initiatives.csv` | Initiative | Business value transformation initiatives with expected value, effort, phase, status, and project methodology. |
| `data/data_quality_checks.csv` | SQL check-site | Data-quality controls for attendance, enrollment, assessment, staffing, finance, and BI request SLA. |
| `data/stakeholder_requirements.csv` | Requirement | Reporting and decision requirements by stakeholder group, cadence, BI tool target, source system, and acceptance criteria. |
| `data/scenario_assumptions.csv` | Site-scenario | Scenario levers for attendance lift, staff coverage lift, cost change, hours saved, and confidence. |
| `analysis/outputs/site_readiness.csv` | Site | Scored readiness and BVT priority queue. |
| `analysis/outputs/initiative_scorecard.csv` | Initiative | Ranked initiative value and project action queue. |
| `analysis/outputs/scenario_forecast.csv` | Site-scenario | Scenario forecast with projected attendance, staffing, students gained, and annualized value. |
| `analysis/outputs/requirement_matrix.csv` | Requirement | Stakeholder BI requirement delivery-risk queue. |
| `analysis/outputs/app_payload.json` | Portfolio | Static application payload used by the dashboard. |
