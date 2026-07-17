import { Octokit } from "@octokit/rest";
import { AgentConfig } from "./config";
import { IssueContext, getIssue, commentOnIssue, createBranchFromDefault } from "./github";
import { createPRForIssue } from "./pr";
import { runTestsAndQualityChecks } from "./tests";

function hasLabel(issue: any, label: string): boolean {
  return issue.labels?.some((l: any) => l.name === label);
}

function shouldSkipIssue(config: AgentConfig, issue: any): boolean {
  return config.issues.skip_labels.some((label) => hasLabel(issue, label));
}

function shouldAutoProcess(config: AgentConfig, issue: any): boolean {
  return config.issues.auto_process_labels.some((label) => hasLabel(issue, label));
}

export async function processIssue(
  octokit: Octokit,
  config: AgentConfig,
  ctx: IssueContext
) {
  const issue = await getIssue(octokit, ctx);

  if (shouldSkipIssue(config, issue)) {
    await commentOnIssue(
      octokit,
      ctx,
      ":pause_button: Auto Agent skipped this issue due to skip labels."
    );
    return;
  }

  if (!shouldAutoProcess(config, issue)) {
    await commentOnIssue(
      octokit,
      ctx,
      ":grey_question: Auto Agent did not process this issue (no auto-process labels)."
    );
    return;
  }

  await commentOnIssue(
    octokit,
    ctx,
    ":robot: Auto Agent started processing this issue..."
  );

  const branchName = `auto-agent/issue-${ctx.issueNumber}`;

  await createBranchFromDefault(octokit, ctx.owner, ctx.repo, branchName);

  // Here you’d call Copilot / your own logic to modify code.
  // For now we assume changes are made by another step or script.

  const qualityResult = await runTestsAndQualityChecks(config);

  const pr = await createPRForIssue(
    octokit,
    {
      owner: ctx.owner,
      repo: ctx.repo,
      branch: branchName,
    },
    issue,
    qualityResult
  );

  await commentOnIssue(
    octokit,
    ctx,
    `:white_check_mark: Auto Agent created PR #${pr.number} for this issue.`
  );
}
