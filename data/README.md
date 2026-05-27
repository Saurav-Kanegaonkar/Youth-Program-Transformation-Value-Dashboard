# Synthetic Data

All data is synthetic and portfolio-safe. It is shaped around youth-program operations, after-school enrichment, sports/wellness participation, stakeholder reporting, and business value transformation workflows.

The generator uses a fixed seed, `5262026`, so the portfolio can be regenerated exactly. The structure is modeled on public youth-enrichment operating patterns: school-based sites, program models, weekly attendance, enrichment engagement, staff coverage, incident tracking, family touchpoints, assessment lift, budget utilization, source-system quality, BI request intake, and intervention scenarios.

Key generation assumptions:

- Sites cover 5 urban markets and 1 regional pilot market, with 28 total youth-program hubs.
- Urban site capacity ranges from 130 to 420 students. Regional pilot capacity ranges from 80 to 180 students.
- Weekly attendance, engagement, staff coverage, assessment lift, and data completeness are drawn from bounded normal distributions by program model, source system, launch wave, community pressure, and student mobility.
- Data-quality defects are higher for spreadsheet and partner-file source systems than for managed system exports.
- Scenario forecasts apply directional lifts to attendance, staff coverage, automation hours saved, and cost change. They are planning estimates, not audited financial projections.

Generated source tables:

- `sites.csv`: site metadata, market, program model, partner type, source system, capacity, and owner.
- `weekly_program_metrics.csv`: weekly attendance, engagement, staff coverage, incident, assessment, budget, and data-completeness metrics.
- `transformation_initiatives.csv`: BVT workstream, expected value, phase, status, owner, and project methodology.
- `data_quality_checks.csv`: SQL-style source controls and defect counts.
- `stakeholder_requirements.csv`: stakeholder decision needs, BI tool target, priority, cadence, acceptance criteria, and delivery status.
- `scenario_assumptions.csv`: directional scenario levers for attendance, staffing, cost, and automation hours saved.
