import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
OUTPUTS = ANALYSIS / "outputs"

random.seed(5262026)


def clamp(value, low, high):
    return max(low, min(high, value))


def pct(value):
    return f"{value * 100:.1f}%"


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n")


markets = [
    ("MKT-01", "South Bronx", "NYC", "Community school", "Salesforce + DOE extract", 0.64, 0.12),
    ("MKT-02", "Central Brooklyn", "NYC", "Beacon center", "Airtable + SIS export", 0.58, 0.10),
    ("MKT-03", "Northern Queens", "NYC", "Expanded learning", "PowerSchool export", 0.48, 0.08),
    ("MKT-04", "Upper Manhattan", "NYC", "Community school", "Google Sheets intake", 0.62, 0.13),
    ("MKT-05", "Staten Island", "NYC", "Sports partnership", "Excel tracker", 0.41, 0.07),
    ("MKT-06", "Anchorage Launch", "AK", "Pilot partner", "Partner CSV intake", 0.52, 0.15),
]

program_models = [
    ("Academic Enrichment", 0.82, 0.68, "Literacy and homework lab"),
    ("Sports and Wellness", 0.78, 0.74, "Youth fitness and team sports"),
    ("STEM and Coding", 0.73, 0.64, "STEM project studio"),
    ("Music and Arts", 0.76, 0.70, "Arts enrichment"),
    ("College and Career", 0.70, 0.60, "Career exposure and mentoring"),
]

school_levels = ["Elementary", "Middle", "High"]
owners = ["Program Ops", "Analytics", "Finance", "Site Leadership", "Partnerships"]
weeks = [f"2026-W{week:02d}" for week in range(8, 22)]


def build_sites():
    rows = []
    index = 1
    for market_id, market, state, partner_type, data_system, poverty_pressure, mobility in markets:
        site_count = 5 if state == "NYC" else 3
        for n in range(site_count):
            model, attendance_base, engagement_base, service_line = random.choice(program_models)
            level = random.choice(school_levels)
            capacity = random.randint(130, 420) if state == "NYC" else random.randint(80, 180)
            rows.append(
                {
                    "site_id": f"SITE-{index:03d}",
                    "site_name": f"{market} Youth Hub {n + 1}",
                    "market_id": market_id,
                    "market": market,
                    "state": state,
                    "school_level": level,
                    "program_model": model,
                    "service_line": service_line,
                    "enrollment_capacity": capacity,
                    "partner_type": partner_type,
                    "data_system": data_system,
                    "poverty_pressure": round(poverty_pressure, 3),
                    "student_mobility_rate": round(mobility + random.uniform(-0.02, 0.025), 3),
                    "launch_wave": "Wave 3 pilot" if state == "AK" else random.choice(["Wave 1 scale", "Wave 2 stabilize", "Wave 3 pilot"]),
                    "site_owner": random.choice(["A. Rivera", "M. Chen", "J. LaBeach", "K. Patel", "T. Williams"]),
                    "attendance_base": attendance_base,
                    "engagement_base": engagement_base,
                }
            )
            index += 1
    return rows


def build_weekly_metrics(sites):
    rows = []
    for site in sites:
        capacity = int(site["enrollment_capacity"])
        model_bias = site["attendance_base"]
        engagement_bias = site["engagement_base"]
        data_drag = {"Excel tracker": 0.065, "Google Sheets intake": 0.045, "Partner CSV intake": 0.055}.get(site["data_system"], 0.025)
        launch_drag = 0.055 if "pilot" in site["launch_wave"].lower() else 0.015
        for week_index, week in enumerate(weeks):
            seasonal_gain = week_index * random.uniform(0.001, 0.004)
            staff_coverage = clamp(random.normalvariate(0.86 - launch_drag + seasonal_gain, 0.06), 0.58, 0.99)
            attendance = clamp(
                random.normalvariate(model_bias - site["poverty_pressure"] * 0.08 - site["student_mobility_rate"] * 0.35 + seasonal_gain, 0.045),
                0.47,
                0.96,
            )
            engagement = clamp(random.normalvariate(engagement_bias + seasonal_gain - launch_drag, 0.055), 0.42, 0.95)
            completion = clamp(random.normalvariate(0.72 + (engagement - 0.65) * 0.35, 0.06), 0.38, 0.95)
            wellness = clamp(random.normalvariate(0.55 + (site["program_model"] == "Sports and Wellness") * 0.22, 0.08), 0.18, 0.93)
            data_completeness = clamp(random.normalvariate(0.93 - data_drag - launch_drag, 0.04), 0.62, 0.995)
            incident_rate = clamp(random.normalvariate(1.6 + (0.86 - staff_coverage) * 5.4 + site["student_mobility_rate"] * 2, 0.55), 0.1, 5.8)
            assessment_gain = clamp(random.normalvariate(0.07 + completion * 0.08 + engagement * 0.05, 0.025), 0.015, 0.23)
            budget_utilization = clamp(random.normalvariate(0.91 + random.uniform(-0.04, 0.06), 0.055), 0.68, 1.13)
            active_students = int(capacity * clamp(random.normalvariate(attendance + 0.08, 0.04), 0.48, 1.0))
            rows.append(
                {
                    "week": week,
                    "site_id": site["site_id"],
                    "active_students": active_students,
                    "attendance_rate": round(attendance, 3),
                    "engagement_rate": round(engagement, 3),
                    "homework_completion_rate": round(completion, 3),
                    "sports_wellness_participation_rate": round(wellness, 3),
                    "family_touchpoints": max(8, int(random.normalvariate(active_students * 0.18, 12))),
                    "staff_coverage_rate": round(staff_coverage, 3),
                    "incident_rate_per_100": round(incident_rate, 2),
                    "pre_post_assessment_gain": round(assessment_gain, 3),
                    "budget_utilization_rate": round(budget_utilization, 3),
                    "data_completeness_rate": round(data_completeness, 3),
                }
            )
    return rows


def build_initiatives(sites):
    workstreams = [
        ("Attendance Recovery", "attendance_rate", "weekly attendance lift"),
        ("Reporting Automation", "data_completeness_rate", "manual reporting hours removed"),
        ("Program Mix Optimization", "engagement_rate", "student engagement lift"),
        ("Staffing Model", "staff_coverage_rate", "coverage gap reduction"),
        ("Family Outreach", "family_touchpoints", "family engagement lift"),
        ("Sports Wellness Expansion", "sports_wellness_participation_rate", "wellness participation lift"),
    ]
    rows = []
    for idx, site in enumerate(sites, start=1):
        selected = random.sample(workstreams, 3)
        for lane_index, (workstream, metric, outcome) in enumerate(selected, start=1):
            expected_value = random.randint(42000, 190000)
            effort = random.randint(90, 420)
            phase = random.choice(["Discovery", "Design", "Pilot", "Scale", "Sustain"])
            status = random.choice(["On track", "At risk", "Blocked", "Ready for review"])
            methodology = random.choice(["Agile sprint board", "RACI tracker", "DMAIC improvement cycle", "Milestone waterfall"])
            rows.append(
                {
                    "initiative_id": f"BVT-{idx:03d}-{lane_index}",
                    "site_id": site["site_id"],
                    "workstream": workstream,
                    "initiative_name": f"{site['program_model']} {workstream.lower()} plan",
                    "target_metric": metric,
                    "expected_value_usd": expected_value,
                    "expected_outcome": outcome,
                    "effort_hours": effort,
                    "owner_team": random.choice(owners),
                    "project_methodology": methodology,
                    "phase": phase,
                    "status": status,
                    "start_week": random.choice(weeks[:5]),
                    "due_week": random.choice(weeks[7:]),
                }
            )
    return rows


def build_quality_checks(sites):
    checks = [
        ("attendance_day_completeness", "Attendance", "missing attendance dates"),
        ("duplicate_student_program_enrollment", "Enrollment", "duplicate participant rows"),
        ("assessment_score_valid_range", "Assessment", "invalid pre/post score range"),
        ("staff_roster_alignment", "Staffing", "unmatched staff schedule rows"),
        ("budget_program_code_match", "Finance", "program code mismatch"),
        ("stakeholder_request_sla", "BI requests", "stale requirement status"),
    ]
    rows = []
    idx = 1
    for site in sites:
        data_risk = {"Excel tracker": 0.085, "Google Sheets intake": 0.065, "Partner CSV intake": 0.075}.get(site["data_system"], 0.035)
        for sql_check, source, issue in checks:
            records = random.randint(450, 5200)
            defect_rate = clamp(random.normalvariate(data_risk, 0.035), 0.002, 0.22)
            defects = int(records * defect_rate)
            severity = "Critical" if defect_rate > 0.14 else "High" if defect_rate > 0.085 else "Medium" if defect_rate > 0.035 else "Low"
            rows.append(
                {
                    "check_id": f"DQ-{idx:04d}",
                    "site_id": site["site_id"],
                    "source_system": source,
                    "sql_check_name": sql_check,
                    "issue_theme": issue,
                    "severity": severity,
                    "records_checked": records,
                    "defect_count": defects,
                    "defect_rate": round(defects / records, 4),
                    "owner_team": random.choice(["Analytics", "Program Ops", "Finance Ops", "Site Leadership"]),
                    "status": random.choice(["Open", "Open", "In progress", "Resolved"]),
                }
            )
            idx += 1
    return rows


def build_requirements(sites):
    stakeholder_groups = [
        ("Executive leadership", "Monthly value scorecard", "Power BI"),
        ("Program directors", "Weekly site action queue", "Tableau"),
        ("Site coordinators", "Daily attendance exception list", "Excel"),
        ("Finance partners", "Budget variance and value realization", "SQL mart"),
        ("Partnerships", "Launch readiness and partner reporting", "Power BI"),
    ]
    rows = []
    idx = 1
    for site in sites:
        for group, need, tool in random.sample(stakeholder_groups, 3):
            priority = random.choice(["P0", "P1", "P1", "P2"])
            rows.append(
                {
                    "requirement_id": f"REQ-{idx:04d}",
                    "site_id": site["site_id"],
                    "stakeholder_group": group,
                    "decision_need": need,
                    "reporting_cadence": random.choice(["Daily", "Weekly", "Biweekly", "Monthly"]),
                    "tool_target": tool,
                    "source_system": site["data_system"],
                    "priority": priority,
                    "acceptance_criteria": random.choice(
                        [
                            "Matches source totals within 1 percent",
                            "Includes owner, due date, and exception reason",
                            "Filters by market, program model, and school level",
                            "Exports cleanly for leadership readout",
                        ]
                    ),
                    "status": random.choice(["Backlog", "In build", "In review", "Accepted"]),
                }
            )
            idx += 1
    return rows


def build_scenarios(sites):
    rows = []
    scenario_defs = [
        ("Baseline", 0.0, 0.0, 0.0, 0),
        ("Attendance push", 0.055, 0.012, 0.018, 3),
        ("BI automation", 0.018, 0.02, -0.012, 7),
        ("Staff coverage sprint", 0.025, 0.065, 0.028, 2),
        ("Wellness expansion", 0.022, 0.015, 0.035, 1),
    ]
    for site in sites:
        for scenario_name, attendance_lift, coverage_lift, cost_change, hours_saved in scenario_defs:
            rows.append(
                {
                    "scenario_id": f"{site['site_id']}-{scenario_name.lower().replace(' ', '-')}",
                    "site_id": site["site_id"],
                    "scenario_name": scenario_name,
                    "attendance_lift_pp": round(attendance_lift + random.uniform(-0.006, 0.009), 3),
                    "staff_coverage_lift_pp": round(coverage_lift + random.uniform(-0.006, 0.008), 3),
                    "cost_change_pct": round(cost_change + random.uniform(-0.006, 0.006), 3),
                    "weekly_hours_saved": max(0, round(hours_saved + random.uniform(-0.5, 1.4), 1)),
                    "confidence": round(clamp(random.normalvariate(0.73, 0.11), 0.42, 0.94), 2),
                }
            )
    return rows


def score_outputs(sites, metrics, initiatives, checks, requirements, scenarios):
    site_lookup = {row["site_id"]: row for row in sites}
    by_site_metrics = defaultdict(list)
    for row in metrics:
        by_site_metrics[row["site_id"]].append(row)

    defects_by_site = defaultdict(int)
    open_checks_by_site = defaultdict(int)
    critical_checks_by_site = defaultdict(int)
    for row in checks:
        if row["status"] != "Resolved":
            open_checks_by_site[row["site_id"]] += 1
            defects_by_site[row["site_id"]] += int(row["defect_count"])
            if row["severity"] in {"Critical", "High"}:
                critical_checks_by_site[row["site_id"]] += 1

    req_by_site = defaultdict(list)
    for row in requirements:
        req_by_site[row["site_id"]].append(row)

    scenario_by_site = defaultdict(list)
    for row in scenarios:
        scenario_by_site[row["site_id"]].append(row)

    site_readiness = []
    for site_id, rows in by_site_metrics.items():
        site = site_lookup[site_id]
        avg = {
            key: sum(float(row[key]) for row in rows) / len(rows)
            for key in [
                "attendance_rate",
                "engagement_rate",
                "homework_completion_rate",
                "sports_wellness_participation_rate",
                "staff_coverage_rate",
                "incident_rate_per_100",
                "pre_post_assessment_gain",
                "budget_utilization_rate",
                "data_completeness_rate",
            ]
        }
        active_students = round(sum(int(row["active_students"]) for row in rows) / len(rows))
        data_risk = clamp(1 - avg["data_completeness_rate"], 0, 0.45)
        operating_risk = clamp((0.82 - avg["attendance_rate"]) + (0.82 - avg["staff_coverage_rate"]) + avg["incident_rate_per_100"] / 10, 0, 1.2)
        readiness = (
            avg["attendance_rate"] * 20
            + avg["engagement_rate"] * 17
            + avg["homework_completion_rate"] * 12
            + avg["staff_coverage_rate"] * 18
            + avg["data_completeness_rate"] * 18
            + clamp(avg["pre_post_assessment_gain"] / 0.18, 0, 1) * 10
            + clamp(1 - avg["incident_rate_per_100"] / 5.5, 0, 1) * 5
        )
        value_at_stake = active_students * (0.82 - avg["attendance_rate"]) * 760 + defects_by_site[site_id] * 7
        priority_score = clamp(
            (100 - readiness) * 0.9
            + operating_risk * 30
            + data_risk * 45
            + open_checks_by_site[site_id] * 2.4
            + len([r for r in req_by_site[site_id] if r["priority"] in {"P0", "P1"}]) * 3.2,
            0,
            100,
        )
        if avg["data_completeness_rate"] < 0.88:
            next_action = "Fix SQL data controls before executive readout"
        elif avg["staff_coverage_rate"] < 0.82:
            next_action = "Run staffing coverage sprint with site leadership"
        elif avg["attendance_rate"] < 0.76:
            next_action = "Prioritize attendance recovery scenario"
        else:
            next_action = "Move to value realization tracking"
        site_readiness.append(
            {
                "site_id": site_id,
                "site_name": site["site_name"],
                "market": site["market"],
                "state": site["state"],
                "school_level": site["school_level"],
                "program_model": site["program_model"],
                "data_system": site["data_system"],
                "active_students": active_students,
                "attendance_rate": round(avg["attendance_rate"], 3),
                "engagement_rate": round(avg["engagement_rate"], 3),
                "staff_coverage_rate": round(avg["staff_coverage_rate"], 3),
                "data_completeness_rate": round(avg["data_completeness_rate"], 3),
                "incident_rate_per_100": round(avg["incident_rate_per_100"], 2),
                "pre_post_assessment_gain": round(avg["pre_post_assessment_gain"], 3),
                "open_quality_checks": open_checks_by_site[site_id],
                "critical_quality_checks": critical_checks_by_site[site_id],
                "p0_p1_requirements": len([r for r in req_by_site[site_id] if r["priority"] in {"P0", "P1"}]),
                "readiness_score": round(readiness, 1),
                "priority_score": round(priority_score, 1),
                "value_at_stake_usd": round(max(value_at_stake, 0), 0),
                "next_action": next_action,
            }
        )

    site_readiness.sort(key=lambda row: row["priority_score"], reverse=True)

    site_score_lookup = {row["site_id"]: row for row in site_readiness}
    initiative_scorecard = []
    for row in initiatives:
        site_score = site_score_lookup[row["site_id"]]
        phase_multiplier = {"Discovery": 0.76, "Design": 0.84, "Pilot": 0.93, "Scale": 1.0, "Sustain": 0.72}[row["phase"]]
        blocker = 9 if row["status"] == "Blocked" else 5 if row["status"] == "At risk" else 0
        value_density = float(row["expected_value_usd"]) / float(row["effort_hours"])
        score = clamp(site_score["priority_score"] * 0.55 + value_density * 0.035 + phase_multiplier * 15 + blocker, 0, 100)
        initiative_scorecard.append(
            {
                **row,
                "site_name": site_score["site_name"],
                "market": site_score["market"],
                "readiness_score": site_score["readiness_score"],
                "initiative_score": round(score, 1),
                "value_density_usd_per_hour": round(value_density, 1),
                "recommended_pm_action": "Escalate dependency" if row["status"] == "Blocked" else "Size next sprint" if row["phase"] in {"Design", "Pilot"} else "Track realization",
            }
        )
    initiative_scorecard.sort(key=lambda row: row["initiative_score"], reverse=True)

    scenario_forecast = []
    for site_row in site_readiness:
        for scenario in scenario_by_site[site_row["site_id"]]:
            projected_attendance = clamp(site_row["attendance_rate"] + float(scenario["attendance_lift_pp"]), 0, 0.98)
            projected_coverage = clamp(site_row["staff_coverage_rate"] + float(scenario["staff_coverage_lift_pp"]), 0, 0.99)
            weekly_students_gained = max(0, (projected_attendance - site_row["attendance_rate"]) * site_row["active_students"])
            value_gain = weekly_students_gained * 760 + float(scenario["weekly_hours_saved"]) * 52 * 38
            scenario_forecast.append(
                {
                    **scenario,
                    "site_name": site_row["site_name"],
                    "market": site_row["market"],
                    "projected_attendance_rate": round(projected_attendance, 3),
                    "projected_staff_coverage_rate": round(projected_coverage, 3),
                    "weekly_students_gained": round(weekly_students_gained, 1),
                    "annualized_value_usd": round(value_gain * (1 + float(scenario["cost_change_pct"]) * -1), 0),
                }
            )
    scenario_forecast.sort(key=lambda row: row["annualized_value_usd"], reverse=True)

    requirement_matrix = []
    for req in requirements:
        site_score = site_score_lookup[req["site_id"]]
        priority_weight = {"P0": 4, "P1": 3, "P2": 2}[req["priority"]]
        status_weight = {"Backlog": 1, "In build": 2, "In review": 3, "Accepted": 4}[req["status"]]
        delivery_risk = clamp(priority_weight * 13 + (4 - status_weight) * 8 + (100 - site_score["readiness_score"]) * 0.22, 0, 100)
        requirement_matrix.append(
            {
                **req,
                "site_name": site_score["site_name"],
                "market": site_score["market"],
                "delivery_risk_score": round(delivery_risk, 1),
            }
        )
    requirement_matrix.sort(key=lambda row: row["delivery_risk_score"], reverse=True)

    market_rollup = []
    for market in sorted({row["market"] for row in site_readiness}):
        rows = [row for row in site_readiness if row["market"] == market]
        market_rollup.append(
            {
                "market": market,
                "sites": len(rows),
                "active_students": sum(row["active_students"] for row in rows),
                "avg_readiness_score": round(sum(row["readiness_score"] for row in rows) / len(rows), 1),
                "avg_priority_score": round(sum(row["priority_score"] for row in rows) / len(rows), 1),
                "open_quality_checks": sum(row["open_quality_checks"] for row in rows),
                "value_at_stake_usd": round(sum(row["value_at_stake_usd"] for row in rows), 0),
            }
        )
    market_rollup.sort(key=lambda row: row["avg_priority_score"], reverse=True)

    quality_mix = []
    grouped_quality = defaultdict(lambda: {"open": 0, "defects": 0, "records": 0})
    for row in checks:
        bucket = grouped_quality[row["source_system"]]
        if row["status"] != "Resolved":
            bucket["open"] += 1
        bucket["defects"] += int(row["defect_count"])
        bucket["records"] += int(row["records_checked"])
    for source, values in grouped_quality.items():
        quality_mix.append(
            {
                "source_system": source,
                "open_checks": values["open"],
                "defect_rate": round(values["defects"] / values["records"], 4),
                "defect_count": values["defects"],
            }
        )
    quality_mix.sort(key=lambda row: row["open_checks"], reverse=True)

    tool_mix = Counter(req["tool_target"] for req in requirements)
    stakeholder_mix = Counter(req["stakeholder_group"] for req in requirements)

    portfolio = {
        "sites": len(sites),
        "markets": len({row["market"] for row in sites}),
        "weekly_metric_rows": len(metrics),
        "active_students": sum(row["active_students"] for row in site_readiness),
        "initiatives_scored": len(initiative_scorecard),
        "requirements_traced": len(requirements),
        "avg_readiness_score": round(sum(row["readiness_score"] for row in site_readiness) / len(site_readiness), 1),
        "avg_attendance_rate": round(sum(row["attendance_rate"] for row in site_readiness) / len(site_readiness), 3),
        "open_quality_checks": sum(row["open_quality_checks"] for row in site_readiness),
        "value_at_stake_usd": round(sum(row["value_at_stake_usd"] for row in site_readiness), 0),
        "top_market": market_rollup[0]["market"],
        "top_site": site_readiness[0]["site_name"],
    }

    app_payload = {
        "portfolio": portfolio,
        "site_readiness": site_readiness,
        "initiative_scorecard": initiative_scorecard[:18],
        "scenario_forecast": scenario_forecast[:20],
        "requirement_matrix": requirement_matrix[:18],
        "market_rollup": market_rollup,
        "quality_mix": quality_mix,
        "tool_mix": [{"tool": tool, "requests": count} for tool, count in tool_mix.most_common()],
        "stakeholder_mix": [{"stakeholder_group": group, "requests": count} for group, count in stakeholder_mix.most_common()],
    }

    return app_payload, site_readiness, initiative_scorecard, scenario_forecast, requirement_matrix


def write_analysis_docs(app_payload):
    portfolio = app_payload["portfolio"]
    top_site = app_payload["site_readiness"][0]
    top_initiative = app_payload["initiative_scorecard"][0]
    top_scenario = app_payload["scenario_forecast"][0]
    top_requirement = app_payload["requirement_matrix"][0]

    write_text(
        ANALYSIS / "executive_findings.md",
        f"""
# Executive Findings

- The modeled youth-program portfolio covers {portfolio['sites']} sites, {portfolio['markets']} markets, {portfolio['active_students']:,} active students, and {portfolio['initiatives_scored']} transformation initiatives.
- Average transformation readiness is {portfolio['avg_readiness_score']} with {portfolio['open_quality_checks']} open data-quality controls, so the portfolio is usable for leadership review but needs source-system cleanup before scaling automated reporting.
- {top_site['site_name']} is the highest BVT priority: priority score {top_site['priority_score']}, readiness {top_site['readiness_score']}, attendance {pct(top_site['attendance_rate'])}, and {top_site['open_quality_checks']} open SQL/data checks.
- The highest-scored initiative is `{top_initiative['initiative_name']}` with an initiative score of {top_initiative['initiative_score']} and ${int(top_initiative['expected_value_usd']):,} expected value.
- The strongest modeled scenario is `{top_scenario['scenario_name']}` at {top_scenario['site_name']}, with ${int(top_scenario['annualized_value_usd']):,} annualized value and {top_scenario['weekly_students_gained']} weekly students gained.
- The riskiest reporting requirement is `{top_requirement['decision_need']}` for {top_requirement['stakeholder_group']} in {top_requirement['tool_target']}; it should be resolved before the next management readout.
""",
    )

    write_text(
        ANALYSIS / "analysis_plan.md",
        """
# Analysis Plan

1. Gather stakeholder requirements by audience, reporting cadence, source system, tool target, priority, and acceptance criteria.
2. Profile weekly program operations across attendance, engagement, homework completion, sports/wellness participation, staffing coverage, incidents, assessment gains, budget utilization, and data completeness.
3. Run SQL-style data quality checks for attendance completeness, duplicate enrollments, assessment validity, staffing roster alignment, finance coding, and request SLA aging.
4. Score site readiness with weighted operational, educational-outcome, and data-trust metrics.
5. Rank transformation initiatives by site need, value density, project phase, status blockers, and expected value.
6. Model scenarios for attendance recovery, BI automation, staffing coverage, and wellness expansion.
7. Publish an executive workbench that can support Excel exports, SQL mart validation, Tableau/Power BI dashboard planning, and project-management prioritization.
""",
    )

    write_text(
        ANALYSIS / "methodology.md",
        """
# Methodology

The scoring model is intentionally transparent for interview discussion. It does not use black-box machine learning.

## Site Readiness

Readiness blends attendance, engagement, homework completion, staff coverage, data completeness, assessment lift, and incident control. The model rewards sites that can support executive reporting and penalizes sites with weak source-system reliability.

## Priority Score

Priority combines readiness gaps, operational risk, data risk, open quality checks, and high-priority stakeholder requirements. A high score means a site needs business value transformation support before the next leadership review.

## Initiative Score

Initiatives are ranked by site priority, expected-value density, project phase, and status blockers. This mirrors the practical BVT analyst task of converting messy operational signals into a focused management queue.

## Scenario Forecast

Scenarios estimate attendance lift, staff coverage lift, weekly hours saved, and annualized value. They are directional planning estimates for stakeholder conversation, not financial commitments.
""",
    )

    write_text(
        ANALYSIS / "sql_checks.sql",
        """
-- SQL control examples for the Youth Program Transformation Value Dashboard.

-- 1. Attendance completeness by site-week.
select
  site_id,
  week,
  count(*) as metric_rows,
  avg(attendance_rate) as avg_attendance_rate,
  avg(data_completeness_rate) as avg_data_completeness
from weekly_program_metrics
group by site_id, week
having avg(data_completeness_rate) < 0.90;

-- 2. Duplicate enrollment records that could inflate active-student counts.
select
  site_id,
  participant_id,
  program_model,
  count(*) as enrollment_rows
from participant_program_enrollment
group by site_id, participant_id, program_model
having count(*) > 1;

-- 3. Assessment scores outside accepted pre/post range.
select
  site_id,
  week,
  pre_score,
  post_score
from assessment_events
where pre_score not between 0 and 100
   or post_score not between 0 and 100
   or post_score < pre_score - 25;

-- 4. Open quality checks by severity for BVT management review.
select
  source_system,
  severity,
  count(*) as open_checks,
  sum(defect_count) as defect_count
from data_quality_checks
where status <> 'Resolved'
group by source_system, severity
order by open_checks desc, defect_count desc;

-- 5. Requirement traceability for BI delivery planning.
select
  stakeholder_group,
  tool_target,
  priority,
  status,
  count(*) as requirements
from stakeholder_requirements
group by stakeholder_group, tool_target, priority, status
order by priority, requirements desc;
""",
    )

    write_text(
        ROOT / "STATUS.md",
        """
# Status

- Status: upgraded through the Portfolio Artifact Upgrade Workflow.
- Role target: BVT Analyst for a youth enrichment and education program operator.
- Upgrade focus: education business value transformation, data analysis, SQL controls, Excel/Tableau/Power BI requirement traceability, project-methodology prioritization, and scenario forecasting.

## Verification

- Regenerate data and analysis: `npm run analyze`
- Serve locally: `npm start`
- Open: `http://localhost:4173`
""",
    )


def write_repository_docs():
    write_text(
        DATA / "README.md",
        """
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
""",
    )

    write_text(
        ROOT / "data_dictionary.md",
        """
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
""",
    )

    write_text(
        ROOT / "README.md",
        """
# Youth Program Transformation Value Dashboard

An interactive BVT analyst portfolio artifact for youth enrichment and education program operations. It turns synthetic source data into a stakeholder-ready operating workbench for program transformation, BI requirements, SQL data controls, and scenario forecasting.

![Executive cockpit](docs/images/cockpit.png)

Executive cockpit: summarizes portfolio readiness, active students, open data controls, value at stake, market pressure, and the next management decision.

![Transformation queue](docs/images/queue.png)

Transformation queue: ranks sites and initiatives by readiness gaps, operating risk, data trust, stakeholder demand, expected value, and project status.

![BI requirements and SQL controls](docs/images/requirements.png)

BI requirements and SQL controls: traces stakeholder decision needs to Excel, SQL mart, Tableau, and Power BI delivery targets while showing source-quality blockers.

![Scenario lab](docs/images/scenarios.png)

Scenario lab: forecasts directional value for attendance recovery, reporting automation, staffing coverage, and wellness expansion interventions.

## What This Project Is

This project models the type of work a BVT analyst in a large youth enrichment nonprofit might be asked to do: gather requirements from cross-functional stakeholders, analyze youth-program performance, identify trends and data-quality blockers, communicate recommendations, and monitor the value of implemented strategies.

The app includes four linked views:

- **Executive cockpit:** Portfolio KPIs, top site decision, market readiness, stakeholder demand, and source-quality pressure.
- **Transformation queue:** Ranked site and initiative priorities with recommended next actions.
- **BI requirements:** Requirement traceability across Excel, SQL marts, Tableau, and Power BI.
- **Scenario lab:** Directional forecasts for attendance recovery, BI automation, staffing coverage, and wellness expansion.

## Role Fit

This artifact demonstrates the core work expected in a BVT analyst role:

- Data analysis and reporting across attendance, engagement, staffing, assessment, finance, and data-completeness metrics.
- SQL quality checks for source validation and dashboard trust.
- BI delivery planning for Excel, Tableau, Power BI, and SQL mart outputs.
- Cross-functional stakeholder requirement traceability.
- Project-management methodology fields such as RACI, Agile sprint boards, DMAIC, and milestone planning.
- Education, sports, and wellness program context.

## Data

All data is deterministic synthetic data generated by `scripts/score_operating_data.py` with seed `5262026`. It is modeled on public youth-enrichment operating structures, not on private or real company performance.

Synthetic source tables include:

- `sites.csv`: 28 youth-program hubs across 5 urban markets and 1 regional pilot market. Urban site capacity ranges from 130 to 420 students. Regional pilot capacity ranges from 80 to 180 students.
- `weekly_program_metrics.csv`: 14 weeks of attendance, engagement, homework completion, sports/wellness participation, family touchpoints, staff coverage, incident rate, assessment lift, budget utilization, and data completeness.
- `transformation_initiatives.csv`: 3 BVT initiatives per site across attendance recovery, reporting automation, program mix optimization, staffing, family outreach, and sports/wellness expansion.
- `data_quality_checks.csv`: SQL-style controls for attendance completeness, duplicate enrollment, assessment validity, staffing alignment, finance coding, and BI request SLA.
- `stakeholder_requirements.csv`: reporting requirements by stakeholder group, cadence, BI tool target, source system, priority, acceptance criteria, and status.
- `scenario_assumptions.csv`: directional scenario levers for attendance lift, staff coverage lift, cost change, weekly hours saved, and confidence.

The model uses bounded normal distributions by program model, source system, launch wave, community pressure, and student mobility. Spreadsheet and partner-file source systems receive higher defect-risk assumptions than managed exports. Scenario outputs are directional planning estimates, not audited financial projections.

## Repository Map

| Path | Purpose |
| --- | --- |
| `scripts/score_operating_data.py` | Generates synthetic data, scores readiness and BVT priorities, writes analysis outputs and docs. |
| `analysis/outputs/app_payload.json` | Static app payload for the dashboard. |
| `analysis/outputs/site_readiness.csv` | Site-level readiness and priority queue. |
| `analysis/outputs/initiative_scorecard.csv` | Ranked transformation initiatives. |
| `analysis/outputs/scenario_forecast.csv` | Forecasted scenario value by site. |
| `analysis/outputs/requirement_matrix.csv` | Stakeholder BI delivery-risk queue. |
| `analysis/sql_checks.sql` | SQL examples for data completeness, defects, and requirement traceability. |
| `src/app.js` | Renders the interactive static workbench from generated JSON. |
| `src/styles.css` | Responsive dashboard styling. |

## Run Locally

```bash
npm run analyze
npm start
```

Then open `http://localhost:4173`.

## Scope

This is a static public portfolio artifact with reproducible synthetic data and transparent scoring logic. It does not connect to live student systems, finance systems, enrollment systems, BI servers, Excel workbooks, Tableau, Power BI, or production data. It shows how a BVT analyst can structure data analysis, requirement planning, SQL validation, project prioritization, scenario forecasting, and executive-ready recommendations before a production implementation.
""",
    )


def main():
    for legacy_file in [
        DATA / "daily_metrics.csv",
        DATA / "entities.csv",
        DATA / "recommended_actions.csv",
        DATA / "source_events.csv",
    ]:
        legacy_file.unlink(missing_ok=True)

    sites = build_sites()
    metrics = build_weekly_metrics(sites)
    initiatives = build_initiatives(sites)
    checks = build_quality_checks(sites)
    requirements = build_requirements(sites)
    scenarios = build_scenarios(sites)

    data_files = [
        ("sites.csv", sites, [key for key in sites[0].keys() if key not in {"attendance_base", "engagement_base"}]),
        ("weekly_program_metrics.csv", metrics, list(metrics[0].keys())),
        ("transformation_initiatives.csv", initiatives, list(initiatives[0].keys())),
        ("data_quality_checks.csv", checks, list(checks[0].keys())),
        ("stakeholder_requirements.csv", requirements, list(requirements[0].keys())),
        ("scenario_assumptions.csv", scenarios, list(scenarios[0].keys())),
    ]
    for filename, rows, fieldnames in data_files:
        clean_rows = [{key: row[key] for key in fieldnames} for row in rows]
        write_csv(DATA / filename, clean_rows, fieldnames)

    app_payload, site_readiness, initiative_scorecard, scenario_forecast, requirement_matrix = score_outputs(
        sites, metrics, initiatives, checks, requirements, scenarios
    )

    write_csv(OUTPUTS / "site_readiness.csv", site_readiness, list(site_readiness[0].keys()))
    write_csv(OUTPUTS / "priority_queue.csv", site_readiness, list(site_readiness[0].keys()))
    write_csv(OUTPUTS / "initiative_scorecard.csv", initiative_scorecard, list(initiative_scorecard[0].keys()))
    write_csv(OUTPUTS / "scenario_forecast.csv", scenario_forecast, list(scenario_forecast[0].keys()))
    write_csv(OUTPUTS / "requirement_matrix.csv", requirement_matrix, list(requirement_matrix[0].keys()))
    (OUTPUTS / "app_payload.json").write_text(json.dumps(app_payload, indent=2))
    (OUTPUTS / "summary.json").write_text(json.dumps(app_payload["portfolio"], indent=2))

    write_analysis_docs(app_payload)
    write_repository_docs()

    print(f"Scored {len(site_readiness)} sites and {len(initiative_scorecard)} initiatives.")
    print(f"Top BVT site: {site_readiness[0]['site_name']} ({site_readiness[0]['priority_score']})")
    print(f"Average readiness: {app_payload['portfolio']['avg_readiness_score']}")


if __name__ == "__main__":
    main()
