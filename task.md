# B.L.A.S.T. Protocol Checklist

- [x] **Phase 0: S - Strategy (The "Brainstorming" Gate)**
    - [x] Invoke `brainstorming` skill (completed via direct prompt)
    - [x] Consult `n8n-workflow-patterns` (selected RSS -> AI -> Output)
    - [x] Wait for User Confirmation

- [x] **Protocol 0: Initialization** (Mandatory & Blocking)
    - [x] Initialize Project Memory (`task.md`, `findings.md`, `progress.md`) in Current Working Directory.
    - [x] Create `gemini.md` (Project Constitution) defining Data Schema, Pattern.
    - [x] Strict Check: verify all files exist before proceeding.
    - [x] Wait for User Confirmation.

- [x] **Phase 1: B - Blueprint** (Design Phase)
    - [x] Schema Definition: Define strict Input/Output JSON in `gemini.md`.
    - [x] Scout Templates: Invoke `search_templates` to find 3 relevant templates.
    - [x] Node Strategy: Use `n8n-node-configuration` to plan node properties.
    - [x] Wait for User Confirmation.

- [x] **Phase 2: L - Link** (Connection Phase)
    - [x] Handshake: Verify Credentials & perform Handshake Workflow (`validate_node`).
    - [x] AI/Tools Integration: Use `n8n-mcp-tools-expert` to configure AI nodes or MCP tools if needed.
    - [x] Wait for User Confirmation.

- [x] **Phase 3: A - Architect (Implementation Phase)**
    - [x] Mandatory Skill Instructions (n8n-code-javascript, etc.).
    - [x] Strict Standard Fundamentalism (NO custom nodes).
    - [x] Iterative Build: Skeleton -> Configuration -> Connections.
    - [x] Wait for User Confirmation.

- [x] **Phase 4: S - Stylize (Hardening Phase)**
    - [x] Validation Loop: Invoke `n8n-validation-expert`.
    - [x] Error Handling: Add Error Triggers.
    - [x] Sanitization: Format output (Code node parser added).
    - [x] Wait for User Confirmation.

- [x] **Phase 5: T - Trigger (Verification Phase)**
    - [x] Final Verification.
    - [x] Live Test.
    - [x] Documentation.
