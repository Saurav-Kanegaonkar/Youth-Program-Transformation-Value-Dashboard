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
