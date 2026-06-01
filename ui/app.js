const scenarios = [
  {
    id: "main-registration",
    title: "AI + Data Science",
    status: "success",
    statusLabel: "registered",
    question:
      "Tôi muốn đăng ký môn AI và Data Science, kiểm tra còn chỗ không và học phí tổng cộng?",
    baseline:
      "Bạn có thể đăng ký AI và Data Science nếu còn slot trên portal. Học phí sẽ phụ thuộc số tín chỉ và loại sinh viên, nên bạn nên kiểm tra lại trên hệ thống đăng ký trước khi xác nhận.",
    react:
      "AI3010-01 còn 4 chỗ và DATA3020-02 còn 3 chỗ. Với sinh viên 2A202600713, tổng học phí và phí ước tính là 19,150,000 VND. Agent đã đăng ký thành công AI3010-01 và DATA3020-02 sau khi xác nhận thanh toán.",
    baselineTrace: [
      {
        label: "system prompt",
        content:
          "You are a helpful course registration chatbot. Answer from general advising knowledge. Do not call tools.",
      },
      {
        label: "user prompt",
        content:
          "Tôi muốn đăng ký môn AI và Data Science, kiểm tra còn chỗ không và học phí tổng cộng?",
      },
      {
        label: "tool usage",
        content: "No tools called. The baseline cannot verify live slots, tuition category, or registration status.",
      },
    ],
    reactTrace: [
      {
        thought: "Need official seat data before answering.",
        action: 'check_slots({"course_query":["AI","Data Science"]})',
        observation:
          '{"ok":true,"courses":[{"course_code":"AI3010","sections":[{"section_id":"AI3010-01","available_seats":4,"availability_status":"available"}]},{"course_code":"DATA3020","sections":[{"section_id":"DATA3020-02","available_seats":3,"availability_status":"available"}]}]}',
      },
      {
        thought: "Seats are available, now calculate tuition for the student.",
        action:
          'get_tuition({"course_code":["AI3010","DATA3020"],"student_id":"2A202600713"})',
        observation:
          '{"ok":true,"student_name":"Hai Dang Minh","tuition_category":"domestic","estimated_total":19150000,"currency":"VND"}',
      },
      {
        thought: "Before registration, validate academic and schedule constraints.",
        action:
          'check_prerequisites({"student_id":"2A202600713","course_codes":["AI3010","DATA3020"]})',
        observation:
          '{"ok":true,"missing_prerequisites":[],"eligible_courses":["AI3010","DATA3020"]}',
      },
      {
        thought: "Check whether the selected sections overlap with current schedule.",
        action:
          'detect_conflicts({"student_id":"2A202600713","section_ids":["AI3010-01","DATA3020-02"]})',
        observation: '{"ok":true,"conflicts":[],"selected_sections_are_compatible":true}',
      },
      {
        thought: "All checks passed, proceed with confirmed registration.",
        action:
          'register({"student_id":"2A202600713","section_ids":["AI3010-01","DATA3020-02"],"confirm_payment":true})',
        observation:
          '{"ok":true,"registration_status":"registered","registered_sections":["AI3010-01","DATA3020-02"],"errors":[]}',
      },
    ],
  },
  {
    id: "waitlist",
    title: "Full ML course",
    status: "warning",
    statusLabel: "waitlist",
    question: "ML4010 còn chỗ không? Nếu hết chỗ thì tôi nên làm gì?",
    baseline:
      "ML4010 có thể đã gần đầy vì đây là môn nâng cao. Bạn nên vào portal kiểm tra lại và cân nhắc đăng ký waitlist hoặc chọn môn khác.",
    react:
      "ML4010-01 đang closed, không còn open seat để đăng ký trực tiếp. Agent khuyến nghị chọn môn thay thế hoặc liên hệ registrar nếu cần override; không tự đăng ký vì tool trả về trạng thái không khả dụng.",
    baselineTrace: [
      {
        label: "system prompt",
        content:
          "Answer as a normal chatbot. If uncertain, suggest checking the portal.",
      },
      {
        label: "user prompt",
        content: "ML4010 còn chỗ không? Nếu hết chỗ thì tôi nên làm gì?",
      },
      {
        label: "tool usage",
        content: "No tools called. The answer is useful but not grounded in section status.",
      },
    ],
    reactTrace: [
      {
        thought: "Need availability for ML4010.",
        action: 'check_slots({"course_query":"ML4010"})',
        observation:
          '{"ok":true,"courses":[{"course_code":"ML4010","availability_status":"unavailable","sections":[{"section_id":"ML4010-01","available_seats":0,"status":"closed"}]}]}',
      },
      {
        thought: "Closed section means registration should not be attempted.",
        action:
          'register({"student_id":"2A202600713","section_ids":["ML4010-01"],"confirm_payment":true})',
        observation:
          '{"ok":false,"registration_status":"failed","errors":["ML4010-01 is not available for registration."]}',
      },
    ],
  },
  {
    id: "cancelled",
    title: "Cancelled capstone",
    status: "blocked",
    statusLabel: "blocked",
    question: "Đăng ký Data Science Capstone giúp tôi được không?",
    baseline:
      "Bạn có thể thử đăng ký Data Science Capstone nếu đủ điều kiện tiên quyết. Nếu hệ thống không cho đăng ký, hãy liên hệ cố vấn học tập.",
    react:
      "DS4990-01 đang ở trạng thái cancelled, nên agent không đăng ký. Đây là case cần fallback: đề xuất môn thay thế hoặc chuyển sang Registrar/Academic Advising.",
    baselineTrace: [
      {
        label: "system prompt",
        content: "Give helpful registration guidance without database access.",
      },
      {
        label: "user prompt",
        content: "Đăng ký Data Science Capstone giúp tôi được không?",
      },
      {
        label: "tool usage",
        content: "No tools called. The baseline may miss the cancelled status.",
      },
    ],
    reactTrace: [
      {
        thought: "Capstone availability must be checked first.",
        action: 'check_slots({"course_query":"Data Science Capstone"})',
        observation:
          '{"ok":true,"courses":[{"course_code":"DS4990","availability_status":"unavailable","sections":[{"section_id":"DS4990-01","status":"cancelled"}]}]}',
      },
      {
        thought: "Cancelled course should trigger fallback, not registration.",
        action:
          'register({"student_id":"2A202600713","section_ids":["DS4990-01"],"confirm_payment":true})',
        observation:
          '{"ok":false,"registration_status":"failed","errors":["DS4990-01 is not available for registration."]}',
      },
    ],
  },
  {
    id: "international",
    title: "International tuition",
    status: "success",
    statusLabel: "priced",
    question:
      "Tính học phí AI cho sinh viên quốc tế 2A202601102 và xem còn slot không.",
    baseline:
      "Sinh viên quốc tế thường có mức học phí cao hơn sinh viên trong nước. Bạn nên kiểm tra bảng phí chính thức để biết tổng tiền chính xác.",
    react:
      "AI3010-01 còn 4 chỗ. Với sinh viên quốc tế 2A202601102, học phí AI3010 ước tính là 13,300,000 VND gồm 12,600,000 VND học phí cơ bản và 700,000 VND phí môn học.",
    baselineTrace: [
      {
        label: "system prompt",
        content:
          "Explain tuition policy at a high level. Do not access structured data.",
      },
      {
        label: "user prompt",
        content:
          "Tính học phí AI cho sinh viên quốc tế 2A202601102 và xem còn slot không.",
      },
      {
        label: "tool usage",
        content: "No tools called. The baseline cannot apply the student's tuition category exactly.",
      },
    ],
    reactTrace: [
      {
        thought: "Need AI availability first.",
        action: 'check_slots({"course_query":"AI"})',
        observation:
          '{"ok":true,"courses":[{"course_code":"AI3010","sections":[{"section_id":"AI3010-01","available_seats":4,"availability_status":"available"}]}]}',
      },
      {
        thought: "Use student_id to apply international tuition rate.",
        action: 'get_tuition({"course_code":"AI3010","student_id":"2A202601102"})',
        observation:
          '{"ok":true,"student_name":"Alex Park","tuition_category":"international","courses":[{"course_code":"AI3010","base_tuition":12600000,"fees":{"lab_fee":500000,"material_fee":200000},"estimated_total":13300000}],"currency":"VND"}',
      },
    ],
  },
  {
    id: "finance-hold",
    title: "Finance hold",
    status: "blocked",
    statusLabel: "escalate",
    question:
      "Sinh viên 2A202600999 muốn đăng ký AI3010-01, xử lý giúp tôi.",
    baseline:
      "Nếu tài khoản sinh viên có vấn đề tài chính, bạn nên liên hệ phòng tài chính trước khi đăng ký. Sau đó có thể quay lại đăng ký môn AI.",
    react:
      "Agent không đăng ký AI3010-01 vì sinh viên 2A202600999 đang bị FINANCE_BALANCE hold. Đây là human escalation path: chuyển sang Finance/Bursar để gỡ hold trước khi đăng ký.",
    baselineTrace: [
      {
        label: "system prompt",
        content:
          "Give safe advising guidance. Mention office escalation if there may be holds.",
      },
      {
        label: "user prompt",
        content: "Sinh viên 2A202600999 muốn đăng ký AI3010-01, xử lý giúp tôi.",
      },
      {
        label: "tool usage",
        content: "No tools called. The baseline cannot confirm the exact hold code.",
      },
    ],
    reactTrace: [
      {
        thought: "Check whether requested section exists and has open seats.",
        action: 'check_slots({"course_query":"AI3010"})',
        observation:
          '{"ok":true,"courses":[{"course_code":"AI3010","sections":[{"section_id":"AI3010-01","available_seats":4,"availability_status":"available"}]}]}',
      },
      {
        thought: "Try registration to validate account-level constraints.",
        action:
          'register({"student_id":"2A202600999","section_ids":["AI3010-01"],"confirm_payment":true})',
        observation:
          '{"ok":false,"registration_status":"failed","errors":["Student account status is blocked.","Registration blocked by holds: FINANCE_BALANCE."]}',
      },
    ],
  },
];

const state = {
  activeScenarioId: scenarios[0].id,
  mode: "react",
};

const scenarioList = document.querySelector("#scenarioList");
const conversation = document.querySelector("#conversation");
const composer = document.querySelector("#composer");
const userInput = document.querySelector("#userInput");
const messageTemplate = document.querySelector("#messageTemplate");
const resetDemo = document.querySelector("#resetDemo");

function formatTraceSections(sections) {
  return sections
    .map(
      (section) => `
        <div class="trace-section">
          <div class="trace-label">${section.label}</div>
          <pre class="trace-text">${escapeHtml(formatTraceValue(section.content))}</pre>
        </div>
      `,
    )
    .join("");
}

function prettyJson(raw) {
  try {
    return JSON.stringify(typeof raw === "string" ? JSON.parse(raw) : raw, null, 2);
  } catch {
    return raw;
  }
}

function formatTraceValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return prettyJson(value);
  return JSON.stringify(value, null, 2);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderScenarios() {
  scenarioList.innerHTML = scenarios
    .map(
      (scenario, index) => `
        <button
          class="scenario-button ${scenario.id === state.activeScenarioId ? "active" : ""}"
          type="button"
          data-scenario-id="${scenario.id}"
        >
          <strong>${index + 1}. ${scenario.title}</strong>
          <span>${scenario.question}</span>
          <span class="scenario-status ${scenario.status}">${scenario.statusLabel}</span>
        </button>
      `,
    )
    .join("");
}

function formatApiTrace(trace = []) {
  if (!trace.length) {
    return formatTraceSections([{ label: "trace", content: "No trace returned." }]);
  }

  return trace
    .map((item, index) => {
      if (item.type === "step") {
        return `
          <div class="trace-step">
            <div class="trace-label">step ${item.step || index + 1}</div>
            <pre class="trace-text">${escapeHtml(item.thought || item.llm_output || "")}</pre>
            <div class="trace-label">action</div>
            <pre class="trace-json">${escapeHtml(formatTraceValue(item.action || "No action parsed."))}</pre>
            <div class="trace-label">observation</div>
            <pre class="trace-json">${escapeHtml(formatTraceValue(item.observation || ""))}</pre>
          </div>
        `;
      }

      if (item.type === "final") {
        return formatTraceSections([
          {
            label: "final answer",
            content: item.final_answer || item.llm_output || "",
          },
        ]);
      }

      return formatTraceSections([
        {
          label: item.type || `trace ${index + 1}`,
          content: item.content || item,
        },
      ]);
    })
    .join("");
}

function createPendingMessage(question) {
  const clone = messageTemplate.content.cloneNode(true);
  const turn = clone.querySelector(".chat-turn");

  turn.dataset.mode = state.mode;
  turn.querySelector(".user-bubble").textContent = question;
  turn.querySelector(".assistant-bubble").textContent = "Đang gọi AI và tools...";
  turn.querySelector(".assistant-mode").textContent = state.mode === "react" ? "ReAct" : "Baseline";
  turn.querySelector(".assistant-mode").classList.add(state.mode);
  turn.querySelector(".trace-content").innerHTML = formatTraceSections([
    {
      label: "status",
      content: "Waiting for /chat response.",
    },
  ]);

  conversation.appendChild(clone);
  conversation.scrollTop = conversation.scrollHeight;
  return turn;
}

async function callChatApi(message, mode) {
  const response = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, mode }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `Request failed with status ${response.status}`);
  }
  return payload;
}

async function sendMessage(question) {
  const scenario = inferScenarioFromQuestion(question);
  state.activeScenarioId = scenario.id;
  renderScenarios();

  const turn = createPendingMessage(question);
  try {
    const payload = await callChatApi(question, state.mode);
    turn.querySelector(".assistant-bubble").textContent = payload.answer;
    turn.querySelector(".trace-content").innerHTML = formatApiTrace(payload.trace);
  } catch (error) {
    turn.querySelector(".assistant-bubble").textContent =
      "Không gọi được AI backend. Kiểm tra terminal chạy FastAPI và biến môi trường.";
    turn.querySelector(".trace-content").innerHTML = formatTraceSections([
      {
        label: "error",
        content: error.message,
      },
    ]);
  } finally {
    conversation.scrollTop = conversation.scrollHeight;
  }
}

function selectScenario(id) {
  const scenario = scenarios.find((item) => item.id === id) || scenarios[0];
  state.activeScenarioId = scenario.id;
  userInput.value = scenario.question;
  renderScenarios();
}

function inferScenarioFromQuestion(question) {
  const normalized = question.toLowerCase();
  if (normalized.includes("finance") || normalized.includes("2a202600999")) {
    return scenarios.find((scenario) => scenario.id === "finance-hold");
  }
  if (normalized.includes("international") || normalized.includes("quốc tế")) {
    return scenarios.find((scenario) => scenario.id === "international");
  }
  if (normalized.includes("capstone") || normalized.includes("ds4990")) {
    return scenarios.find((scenario) => scenario.id === "cancelled");
  }
  if (normalized.includes("ml4010") || normalized.includes("machine learning")) {
    return scenarios.find((scenario) => scenario.id === "waitlist");
  }
  return scenarios.find((scenario) => scenario.id === state.activeScenarioId) || scenarios[0];
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".mode-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.mode === mode);
  });
}

scenarioList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-scenario-id]");
  if (!button) return;
  selectScenario(button.dataset.scenarioId);
});

document.querySelectorAll(".mode-tab").forEach((tab) => {
  tab.addEventListener("click", () => setMode(tab.dataset.mode));
});

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = userInput.value.trim();
  if (!question) return;
  sendMessage(question);
});

resetDemo.addEventListener("click", () => {
  conversation.innerHTML = "";
  selectScenario(scenarios[0].id);
  setMode("react");
});

renderScenarios();
selectScenario(scenarios[0].id);
