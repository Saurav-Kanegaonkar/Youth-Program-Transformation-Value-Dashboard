const state = await fetch("analysis/outputs/app_payload.json").then((response) => response.json());

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});
const number = new Intl.NumberFormat("en-US");
const percent = (value, digits = 0) => `${(value * 100).toFixed(digits)}%`;

let activeMarket = "All markets";

function scoreClass(score) {
  if (score >= 72) return "high";
  if (score >= 56) return "medium";
  return "low";
}

function renderMetrics() {
  const { portfolio } = state;
  const metrics = [
    ["Active students", number.format(portfolio.active_students), `${portfolio.sites} sites`],
    ["Readiness", portfolio.avg_readiness_score, `${percent(portfolio.avg_attendance_rate, 1)} attendance`],
    ["Open data checks", number.format(portfolio.open_quality_checks), "SQL controls"],
    ["Value at stake", currency.format(portfolio.value_at_stake_usd), `${portfolio.initiatives_scored} initiatives`],
  ];

  document.querySelector("#metric-grid").innerHTML = metrics
    .map(
      ([label, value, detail]) => `
        <article class="metric-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${detail}</em>
        </article>
      `
    )
    .join("");
}

function renderHero() {
  const topSite = state.site_readiness[0];
  const topInitiative = state.initiative_scorecard[0];
  const topScenario = state.scenario_forecast[0];

  document.querySelector("#decision-title").textContent =
    `${topSite.site_name} needs a BVT review before the next management readout`;
  document.querySelector("#decision-copy").textContent =
    `${topSite.market} has the highest modeled transformation pressure: ${topSite.priority_score} priority, ${topSite.readiness_score} readiness, ${percent(topSite.attendance_rate, 1)} attendance, and ${topSite.open_quality_checks} open data-quality checks. Pair the site review with ${topInitiative.workstream.toLowerCase()} and use the ${topScenario.scenario_name.toLowerCase()} scenario as the management option.`;
  document.querySelector("#decision-tags").innerHTML = [
    `${topSite.program_model}`,
    `${topSite.data_system}`,
    `${currency.format(topSite.value_at_stake_usd)} value at stake`,
  ]
    .map((tag) => `<span>${tag}</span>`)
    .join("");
}

function renderMarkets() {
  const maxPriority = Math.max(...state.market_rollup.map((row) => row.avg_priority_score));
  document.querySelector("#market-count").textContent = `${state.market_rollup.length} markets`;
  document.querySelector("#market-list").innerHTML = state.market_rollup
    .map(
      (market) => `
        <article class="rank-row">
          <div>
            <b>${market.market}</b>
            <span>${market.sites} sites, ${number.format(market.active_students)} students</span>
          </div>
          <strong>${market.avg_priority_score}</strong>
          <div class="progress-track" aria-hidden="true">
            <i style="width:${(market.avg_priority_score / maxPriority) * 100}%"></i>
          </div>
          <small>${currency.format(market.value_at_stake_usd)} value at stake</small>
        </article>
      `
    )
    .join("");
}

function renderToolMix() {
  const maxRequests = Math.max(...state.tool_mix.map((row) => row.requests));
  document.querySelector("#tool-count").textContent = `${state.portfolio.requirements_traced} requirements`;
  document.querySelector("#tool-mix").innerHTML = state.tool_mix
    .map(
      (row) => `
        <article class="bar-row">
          <div>
            <b>${row.tool}</b>
            <span>${row.requests} requests</span>
          </div>
          <div class="progress-track" aria-hidden="true">
            <i style="width:${(row.requests / maxRequests) * 100}%"></i>
          </div>
        </article>
      `
    )
    .join("");
}

function renderMarketFilter() {
  const markets = ["All markets", ...new Set(state.site_readiness.map((row) => row.market))];
  document.querySelector("#market-filter").innerHTML = markets
    .map((market) => `<option value="${market}">${market}</option>`)
    .join("");
  document.querySelector("#market-filter").addEventListener("change", (event) => {
    activeMarket = event.target.value;
    renderSiteTable();
  });
}

function renderSiteTable() {
  const rows = state.site_readiness.filter((row) => activeMarket === "All markets" || row.market === activeMarket).slice(0, 12);
  document.querySelector("#site-table").innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>
            <b>${row.site_name}</b>
            <span>${row.market}, ${row.program_model}</span>
          </td>
          <td><span class="score-pill ${scoreClass(row.priority_score)}">${row.priority_score}</span></td>
          <td>${row.readiness_score}</td>
          <td>${percent(row.attendance_rate, 1)}</td>
          <td>
            <b>${percent(row.data_completeness_rate, 1)}</b>
            <span>${row.open_quality_checks} open</span>
          </td>
          <td>${row.next_action}</td>
        </tr>
      `
    )
    .join("");
}

function renderInitiatives() {
  document.querySelector("#initiative-grid").innerHTML = state.initiative_scorecard
    .slice(0, 6)
    .map(
      (row) => `
        <article class="initiative-card">
          <div>
            <span>${row.workstream}</span>
            <h3>${row.initiative_name}</h3>
          </div>
          <dl>
            <div><dt>Score</dt><dd>${row.initiative_score}</dd></div>
            <div><dt>Value</dt><dd>${currency.format(row.expected_value_usd)}</dd></div>
            <div><dt>Phase</dt><dd>${row.phase}</dd></div>
          </dl>
          <p>${row.site_name} · ${row.project_methodology} · ${row.recommended_pm_action}</p>
        </article>
      `
    )
    .join("");
}

function renderRequirements() {
  document.querySelector("#requirement-count").textContent = `${state.requirement_matrix.length} high-risk`;
  document.querySelector("#requirement-list").innerHTML = state.requirement_matrix
    .slice(0, 10)
    .map(
      (row) => `
        <article class="requirement-card">
          <div>
            <b>${row.decision_need}</b>
            <span>${row.stakeholder_group} · ${row.site_name}</span>
          </div>
          <dl>
            <div><dt>Tool</dt><dd>${row.tool_target}</dd></div>
            <div><dt>Priority</dt><dd>${row.priority}</dd></div>
            <div><dt>Risk</dt><dd>${row.delivery_risk_score}</dd></div>
          </dl>
          <p>${row.acceptance_criteria}</p>
        </article>
      `
    )
    .join("");
}

function renderQuality() {
  const maxOpen = Math.max(...state.quality_mix.map((row) => row.open_checks));
  document.querySelector("#quality-count").textContent = `${state.portfolio.open_quality_checks} open`;
  document.querySelector("#quality-list").innerHTML = state.quality_mix
    .map(
      (row) => `
        <article class="quality-card">
          <div>
            <b>${row.source_system}</b>
            <span>${number.format(row.defect_count)} defects</span>
          </div>
          <strong>${row.open_checks}</strong>
          <div class="progress-track" aria-hidden="true">
            <i style="width:${(row.open_checks / maxOpen) * 100}%"></i>
          </div>
          <small>${percent(row.defect_rate, 1)} defect rate</small>
        </article>
      `
    )
    .join("");
}

function renderScenarios() {
  document.querySelector("#scenario-count").textContent = `${state.scenario_forecast.length} forecasts`;
  document.querySelector("#scenario-grid").innerHTML = state.scenario_forecast
    .slice(0, 9)
    .map(
      (row) => `
        <article class="scenario-card">
          <div>
            <span>${row.scenario_name}</span>
            <h3>${row.site_name}</h3>
          </div>
          <strong>${currency.format(row.annualized_value_usd)}</strong>
          <dl>
            <div><dt>Attendance</dt><dd>${percent(row.projected_attendance_rate, 1)}</dd></div>
            <div><dt>Coverage</dt><dd>${percent(row.projected_staff_coverage_rate, 1)}</dd></div>
            <div><dt>Students</dt><dd>${row.weekly_students_gained}</dd></div>
          </dl>
        </article>
      `
    )
    .join("");
}

function bindTabs() {
  const sections = {
    cockpit: document.querySelector("#cockpit"),
    queue: document.querySelector("#queue"),
    requirements: document.querySelector("#requirements"),
    scenarios: document.querySelector("#scenarios"),
  };
  document.querySelectorAll(".view-tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".view-tab").forEach((tab) => tab.classList.remove("active"));
      button.classList.add("active");
      sections[button.dataset.view].scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

renderHero();
renderMetrics();
renderMarkets();
renderToolMix();
renderMarketFilter();
renderSiteTable();
renderInitiatives();
renderRequirements();
renderQuality();
renderScenarios();
bindTabs();
