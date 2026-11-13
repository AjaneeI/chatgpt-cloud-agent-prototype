# ChatGPT → GitHub Cloud Agent Prototype

**Stage 1: free, simulation-only, intentionally limited.** Regular ChatGPT conversations can create and label task issues with the connected GitHub integration. GitHub Actions then runs an on-demand job and writes evidence back to the issue and as an artifact. Your laptop may remain off.

No DeepSeek model is connected. This prototype does **not** run AI inference, change repository files, deploy, merge, accept shell commands, or require secrets. Stage 1 success is not proof of a later DeepSeek integration.

## Trigger from ChatGPT

1. Create a GitHub issue in this repository with an entire body consisting of the JSON object below (no Markdown fences):

    {"schema_version":1,"task":"smoke-test","mode":"B"}

2. **After** the issue exists, add the label named cloud-run-approved. The workflow triggers on the issue-label event, not on issue creation.
3. The cloud job checks the owner and payload, runs the Python unit tests, executes one simulated stage, saves report.json and report.md as a GitHub Actions artifact, and posts a result comment to the issue if successful.
4. Ask ChatGPT to inspect the issue comment or workflow logs before deciding on another task.

## Three modes, in the prototype

- **A — finish:** complete the bounded smoke test.
- **B — checkpoint:** run one stage, save results, and return CHECKPOINT_READY.
- **C — approval:** return AWAITING_APPROVAL, with no test stage executed or other action authorized.

## Security and cost

This is a **public repository**. Do not include secrets, sensitive prompts or private source code in issues or logs. The worker accepts only a fixed JSON schema and smoke-test task. Only owner-authored issues with the launch label can run the workflow. The code is CPU-only and never invokes a model API. GitHub Actions runner free usage depends on GitHub's current plan and policy. The workflow has minimal repository read access and issue-write access solely to post status; checkout disables credential persistence.

## Next phase

After the actual cloud-run evidence is reviewed, add a bounded coding-agent harness, a separately authorized DeepSeek endpoint, spending limits, checkpoints and branch-only PR generation. No automatic merges.
