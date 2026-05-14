# Architecture

Hive Industrial Sentinel is organized around three layers.

## Intelligence Layer

The agent orchestrator accepts operator prompts, checks safety policy, reads telemetry, calculates
risk, retrieves manual evidence, and produces an operational answer. The first implementation is
Gemini-ready through an OpenAI-compatible client, with deterministic local fallback for demo
reliability.

## Connectivity Layer

The `his.agents.tools` module exposes MCP-compatible tool contracts:

- `read_telemetry(asset_id, window_minutes)`
- `risk_assessment(snapshot)`
- `query_manual(question, top_k)`
- `policy_check(prompt, proposed_action)`

A formal MCP server can wrap these functions later without changing the core business logic.

## Governance Layer

The local policy evaluator mirrors Lobster Trap-style ingress and egress rules. It blocks alarm
override, forced overload, prompt injection, and unsafe model recommendations while writing JSONL
audit events.

When Lobster Trap is running as a reverse proxy, the Gemini client can route through it by setting
`LOBSTER_TRAP_ENABLED=true` and `LOBSTER_TRAP_BASE_URL`.
