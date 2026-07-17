import { Octokit } from "@octokit/rest";

export function createClient(token?: string) {
  const auth = token || process.env.GITHUB_TOKEN;
  if (!auth) {
    throw new Error("GITHUB_TOKEN is required");
  }
  return new Octokit({ auth });
}

export type IssueContext = {
  owner: string;
  repo: string;
  issueNumber: number;
};

export async function getIssue(octokit: Octokit, ctx: IssueContext) {
  const { data } = await octokit.issues.get({
    owner: ctx.owner,
    repo: ctx.repo,
    issue_number: ctx.issueNumber,
  });
  return data;
}

export async function commentOnIssue(
  octokit: Octokit,
  ctx: IssueContext,
  body: string
) {
  await octokit.issues.createComment({
    owner: ctx.owner,
    repo: ctx.repo,
    issue_number: ctx.issueNumber,
    body,
  });
}

export async function createBranchFromDefault(
  octokit: Octokit,
  owner: string,
  repo: string,
  branchName: string
) {
  const { data: repoData } = await octokit.repos.get({ owner, repo });
  const defaultBranch = repoData.default_branch;

  const { data: ref } = await octokit.git.getRef({
    owner,
    repo,
    ref: `heads/${defaultBranch}`,
  });

  await octokit.git.createRef({
    owner,
    repo,
    ref: `refs/heads/${branchName}`,
    sha: ref.object.sha,
  });

  return branchName;
}
