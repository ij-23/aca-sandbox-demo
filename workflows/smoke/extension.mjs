// Trusted workflow delivered only to a disposable, service-provided Copilot disk.
import { appendFileSync } from "node:fs";
import { setTimeout as delay } from "node:timers/promises";
import { defineWorkflow, joinSession } from "@github/copilot-sdk/extension";

const workflow = defineWorkflow({
  meta: {
    name: "aca-viability-smoke",
    description: "Deterministic preparation, real Copilot AI, result-based branch and SDK file polling.",
    phases: [{ title: "Prepare" }, { title: "Agent" }, { title: "Verify" }],
    argsSchema: {
      type: "object",
      required: ["nonce"],
      properties: { nonce: { type: "string" } },
    },
    limits: { maxConcurrentSubagents: 1, maxTotalSubagents: 2, timeoutSeconds: 180 },
  },
  run: async (ctx) => {
    const nonce = ctx.args.nonce;
    if (typeof nonce !== "string" || !/^[a-f0-9]{32}$/.test(nonce)) {
      throw new Error("Invalid smoke nonce");
    }
    const steps = [];
    const emit = (step, status) => {
      appendFileSync("smoke-events.jsonl", JSON.stringify({
        timestamp: new Date().toISOString(), workflow_run_id: ctx.runId, nonce, step, status,
      }) + "\n");
      ctx.log(`${step}: ${status}`);
    };
    ctx.phase("Prepare");
    let start = Date.now();
    const prepared = await ctx.step("prepare-v1", async () => {
      emit("prepare", "running");
      const sum = [2, 3].reduce((a, b) => a + b, 0);
      // Explicit observation window to test retrieval before command completion.
      // This is a real bounded wait, not simulated AI activity.
      await delay(3000, undefined, { signal: ctx.signal });
      emit("prepare", "passed");
      return { sum, observation_window_ms: 3000 };
    });
    steps.push({ step: "prepare", status: "passed", duration_ms: Date.now() - start, result: prepared });
    ctx.phase("Agent");
    start = Date.now();
    emit("agent", "running");
    const answer = await ctx.agent(
      `Return only JSON with nonce "${nonce}", answer "pong", and sum equal to 2 + 3. Do not use tools or inspect files.`,
      {
        label: "credential-and-agent-check",
        schema: {
          type: "object", required: ["nonce", "answer", "sum"],
          properties: { nonce: { type: "string" }, answer: { type: "string" }, sum: { type: "number" } },
        },
      },
    );
    const valid = answer !== null && typeof answer === "object"
      && answer.nonce === nonce && answer.answer === "pong" && answer.sum === prepared.sum;
    emit("agent", valid ? "passed" : "failed");
    // Persist only validated trusted output; never echo an unexpected agent response.
    steps.push({ step: "agent", status: valid ? "passed" : "failed", duration_ms: Date.now() - start,
      result: valid ? { nonce, answer: "pong", sum: answer.sum } : null });
    ctx.phase("Verify");
    start = Date.now();
    const decision = await ctx.step("verify-v1", () => {
      emit("verify", "running");
      const branch = valid ? "verified" : "rejected";
      emit("verify", valid ? "passed" : "failed");
      return { branch, reason: valid ? "agent_matches_deterministic_result" : "agent_result_mismatch" };
    });
    steps.push({ step: "verify", status: valid ? "passed" : "failed", duration_ms: Date.now() - start, result: decision });
    return { nonce, workflow_run_id: ctx.runId, answer: valid ? "pong" : null,
      sum: prepared.sum, branch: decision.branch, steps };
  },
});

await joinSession({ workflows: [workflow] });
