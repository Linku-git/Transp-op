# Session 55 — Trip Statistics & CO2 Screen

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-50|Session 50]]
## Complexity: Low
> Previous: [[sessions/session-54|Session 54]] | Next: [[sessions/session-56|Session 56]]

## Objective
Build a statistics screen that visualizes trip data, CO2 savings, and transport usage with interactive charts and a shareable impact card.

---

## Tasks
- [ ] Create StatisticsScreen with period selector (month / year / all time)
- [ ] Display summary cards: total trips, total distance, CO2 saved, training modules completed, quiz average score
- [ ] Create monthly trips bar chart
- [ ] Create CO2 savings trend line chart
- [ ] Create transport mode usage pie chart
- [ ] Implement "Share my impact" button that generates a shareable image card
- [ ] Calculate CO2 savings per trip compared to individual car usage

## Files to Create/Modify
- `mobile/lib/screens/statistics_screen.dart`
- `mobile/lib/widgets/stats_summary_cards.dart`
- `mobile/lib/widgets/trips_bar_chart.dart`
- `mobile/lib/widgets/co2_trend_chart.dart`
- `mobile/lib/widgets/transport_mode_pie_chart.dart`
- `mobile/lib/widgets/share_impact_card.dart`
- `mobile/lib/providers/statistics_provider.dart`
- `mobile/lib/services/statistics_service.dart`
- `mobile/lib/utils/co2_calculator.dart`

## Tests
- [ ] StatisticsScreen renders correctly with mock data
- [ ] Period filter switches between month, year, and all time
- [ ] Summary cards display correct aggregated values
- [ ] Bar chart renders monthly trip counts
- [ ] Line chart renders CO2 savings trend
- [ ] Pie chart renders transport mode distribution
- [ ] CO2 calculation produces correct values (vs individual car baseline)
- [ ] Share button generates shareable card

## Acceptance Criteria
- Statistics screen loads and displays data for the selected period
- Period selector filters all charts and summary cards accordingly
- Summary cards show total trips, distance, CO2 saved, training modules, and quiz average
- Monthly trips bar chart is interactive and labeled
- CO2 savings trend line shows progression over time
- Transport mode pie chart shows usage distribution with labels
- CO2 savings are calculated using individual car usage as baseline
- "Share my impact" generates a visually appealing card suitable for sharing
- Empty state is handled when no trip data exists

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
