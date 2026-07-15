export type MetricEvent =
  | "issues_processed"
  | "prs_created"
  | "fixes_merged"
  | "features_implemented"
  | "avg_resolution_time"
  | "coverage_delta";

export function recordMetric(event: MetricEvent, value?: number | string) {
  // For now, just log. Could be pushed to a dashboard or artifact.
  console.log(`[metrics] ${event}: ${value ?? 1}`);
}
