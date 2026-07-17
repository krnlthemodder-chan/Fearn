import { Octokit } from "@octokit/rest";
import { AgentConfig } from "./config";

export async function runNightly(octokit: Octokit, config: AgentConfig) {
  if (!config.schedule.nightly.enabled) return;

  // Example: list open issues and process those with auto labels
  // In practice, you might limit count or filter by updated_at.
  const { data: issues } = await octokit.issues.listForRepo({
    owner: process.env.GITHUB_REPOSITORY?.split("/")[0] || "",
    repo: process.env.GITHUB_REPOSITORY?.split("/")[1] || "",
    state: "open",
  });

  // You could call processIssue for each, or run optimizations, dependency updates, etc.
  console.log(`Nightly run: found ${issues.length} open issues.`);
}
