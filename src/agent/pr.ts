import { Octokit } from "@octokit/rest";
import fs from "fs";
import path from "path";
import { AgentConfig } from "./config";

type PRContext = {
  owner: string;
  repo: string;
  branch: string;
};

type QualityResult = {
  coverage: number;
  checksPassed: boolean;
  reportSummary: string;
  linesChanged: number;
};

function loadPRTemplate(): string {
  const templatePath = path.join(process.cwd(), "templates", "pr-description.md");
  if (!fs.existsSync(templatePath)) {
    return "Auto-generated PR by Copilot Auto Agent.";
  }
  return fs.readFileSync(templatePath, "utf8");
}

export async function createPRForIssue(
  octokit: Octokit,
  ctx: PRContext,
  issue: any,
  quality: QualityResult,
  config?: AgentConfig
) {
  const baseBranch = (await octokit.repos.get({ owner: ctx.owner, repo: ctx.repo })).data
    .default_branch;

  const template = loadPRTemplate();

  const body = template
    .replace("{{ISSUE_NUMBER}}", String(issue.number))
    .replace("{{ISSUE_TITLE}}", issue.title)
    .replace("{{QUALITY_REPORT}}", quality.reportSummary)
    .concat(
      `\n\nCloses #${issue.number}\n\n` +
        `- Coverage: ${quality.coverage}%\n` +
        `- Checks passed: ${quality.checksPassed ? "yes" : "no"}\n`
    );

  const isComplex =
    config?.pr.draft_for_complex_changes &&
    quality.linesChanged >= (config?.pr.complex_change_threshold ?? 300);

  const { data: pr } = await octokit.pulls.create({
    owner: ctx.owner,
    repo: ctx.repo,
    title: `[Auto Agent] ${issue.title}`,
    head: ctx.branch,
    base: baseBranch,
    body,
    draft: !!isComplex,
  });

  return pr;
}
