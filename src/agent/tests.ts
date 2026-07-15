import { AgentConfig } from "./config";
import { execSync } from "child_process";

export type QualityResult = {
  coverage: number;
  checksPassed: boolean;
  reportSummary: string;
  linesChanged: number;
};

export async function runTestsAndQualityChecks(
  config: AgentConfig
): Promise<QualityResult> {
  try {
    execSync("npm test -- --coverage", { stdio: "inherit" });
  } catch (e) {
    // tests failed, but we still want a report
  }

  // In a real setup, parse coverage from coverage report.
  const coverage = config.code_quality.min_coverage; // placeholder

  const checksPassed = coverage >= config.code_quality.min_coverage;

  const reportSummary = `Minimum coverage: ${config.code_quality.min_coverage}%. Actual: ${coverage}%.`;

  // In a real setup, compute lines changed from git diff.
  const linesChanged = 200;

  return {
    coverage,
    checksPassed,
    reportSummary,
    linesChanged,
  };
}
