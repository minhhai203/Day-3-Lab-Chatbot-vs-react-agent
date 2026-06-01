# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Đặng Minh Hải
- **Student ID**: 2A202600713
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

My main contribution was implementing and connecting the CoursePilot registration tools into a ReAct-style agent for the VinUniversity course registration use case. I focused on making the agent answer registration questions using structured tool outputs instead of guessing from the prompt alone.

- **Modules Implementated**:
  - `data/course_registration_mock.json`: designed mock student/course/registration data for the lab scenario.
  - `src/tools/check_slots_tools.py`: implemented the `check_slots` tool for course lookup and seat availability.
  - `src/tools/get_tuition_tools.py`: implemented the `get_tuition` tool for domestic/international tuition calculation.
  - `src/tools/register_tools.py`: implemented the `register` tool for final registration, waitlist handling, payment confirmation, account holds, prerequisite checks, and time conflicts.
  - `src/tools/course_registration_tools.py`: kept a clean tool registry while leaving each tool in its own file.
  - `src/agent/agent.py`: connected the tools to the ReAct loop through `Thought -> Action -> Observation -> Final Answer`.
  - `tests/`: added/maintained tests for the agent loop and registration tools.

- **Code Highlights**:
  - ReAct prompt construction in `src/agent/agent.py` lines 21-47 lists available tools and enforces the output format.
  - Agent loop in `src/agent/agent.py` lines 49-105 repeatedly calls the LLM, parses an action, executes a tool, appends the observation, and stops on `Final Answer`.
  - Action parsing in `src/agent/agent.py` lines 113-135 supports JSON action arguments such as `Action: check_slots({"course_query": ["AI", "Data Science"]})`.
  - Tool execution in `src/agent/agent.py` lines 146-180 filters accepted arguments, logs `TOOL_CALL` / `TOOL_RESULT`, and returns structured `TOOL_NOT_FOUND` errors.
  - `check_slots` in `src/tools/check_slots_tools.py` lines 109-169 returns course sections, available seats, waitlist seats, and course-level availability.
  - `get_tuition` in `src/tools/get_tuition_tools.py` lines 88-161 calculates per-course fees and total estimated tuition.
  - `register` in `src/tools/register_tools.py` lines 84-204 validates the student, payment confirmation, holds, prerequisites, time conflicts, seat status, and waitlist status.

- **Documentation**:
  - The tool registry exposes the course registration tools to the agent in `src/tools/course_registration_tools.py`.
  - The ReAct loop receives user input, decides which tool to call, and uses each observation as the next input context. This is the key difference from the chatbot baseline: instead of answering in one shot, the agent can progressively ground the answer with real course data.
  - The main successful flow is: `check_slots -> get_tuition -> register`, which answers the user’s question about AI and Data Science availability, total tuition, and registration status.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**:
  During testing, the agent attempted to call a hallucinated tool named `search_course`, even though the available tool inventory only contained course registration tools such as `check_slots`, `get_tuition`, and `register`.

- **Log Source**:
  Source: `logs/2026-06-01.log`, around lines 61-64.

```text
AGENT_STEP: Thought: I will try a tool name that is not in the inventory.
Action: search_course({"query": "AI"})
TOOL_ERROR: {"ok": false, "error_code": "TOOL_NOT_FOUND", "message": "Tool search_course not found."}
AGENT_STEP: Thought: The observation says TOOL_NOT_FOUND...
Final Answer: The first attempt failed because the agent hallucinated search_course.
```

- **Diagnosis**:
  The failure came from the model choosing a semantically reasonable but invalid tool name. This was mostly a prompt/tool-spec problem: the model understood that it needed course lookup, but the tool inventory was not constrained strongly enough in that trace.

- **Solution**:
  I tightened the system prompt and tool descriptions so the agent is explicitly told to use the provided tool names and raw JSON inside `Action(...)`. I also kept defensive error handling in `_execute_tool`, so an unknown tool returns a structured `TOOL_NOT_FOUND` error instead of crashing. This made the failure visible in logs and allowed the next reasoning step to recover by saying the correct tool should be `check_slots`.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**:
   The `Thought` block helped the agent decompose one broad request into smaller decisions: first check seats, then calculate tuition, then attempt registration. A direct chatbot can sound helpful, but it tends to answer from general policy. The ReAct agent exposes why it is calling each tool, so the final answer is easier to trust and debug.

2. **Reliability**:
   The agent can perform worse than the chatbot when the model produces malformed actions or invents a tool name. In those cases, a simple chatbot may still give a safe generic answer faster. The agent also costs more tokens because each observation is appended back into the prompt. For high-stakes actions like registration, I still prefer the agent because its mistakes are traceable.

3. **Observation**:
   Observations changed the next step directly. For example, after `check_slots` returned available sections for AI and Data Science, the agent knew it could move to `get_tuition`. After `get_tuition` returned `19,150,000 VND`, the agent could proceed to `register`. When the observation was `TOOL_NOT_FOUND`, the agent had evidence that the previous action was invalid and could explain the failure instead of inventing a result.

---

## IV. Future Improvements (5 Points)

- **Scalability**:
  Replace the mock JSON file with real SIS / registrar APIs, and separate longer-running registration actions into asynchronous jobs with clear pending/success/failure states.

- **Safety**:
  Add schema validation for every tool input and require explicit confirmation before final registration. For production, I would also add a supervisor check for sensitive actions such as registration, payment, prerequisite waivers, and account holds.

- **Performance**:
  Cache read-only tool results such as course metadata and tuition rules. If the tool inventory grows, use tool routing or retrieval so the model sees only the tools relevant to the current task.

- **Product Quality**:
  Split `register` into smaller tools such as `check_prerequisites` and `detect_conflicts` if the team wants more transparent traces. This would make the demo clearer because each validation step would appear as a separate ReAct action.

---

> [!NOTE]
> This report is for the individual contribution of Đặng Minh Hải (`2A202600713`) in the CoursePilot Registration Assistant lab.
