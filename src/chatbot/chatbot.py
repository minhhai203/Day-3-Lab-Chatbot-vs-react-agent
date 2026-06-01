import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.core.gemini_provider import GeminiProvider

SYSTEM_PROMPT = """You are a helpful and professional university registration advisor at Green Valley University.
Your role is to assist students with all course registration-related questions and problems.

UNIVERSITY REGISTRATION POLICIES:
- Registration periods: Early registration for seniors (90+ credits) opens 6 weeks before semester start. Juniors (60-89 credits) open 5 weeks before. Sophomores (30-59 credits) open 4 weeks before. Freshmen (0-29 credits) open 3 weeks before.
- Add/Drop deadline: Students may add or drop courses without academic penalty during the first two weeks of each semester.
- Late withdrawal: After week 2 and before week 10, students may withdraw with a "W" grade. No withdrawals are permitted after week 10.
- Maximum credit load: Students may enroll in a maximum of 18 credits per semester. Overload requests (up to 21 credits) require a GPA of 3.5+ and department advisor approval.
- Minimum credit load: Full-time status requires 12 credits per semester. Part-time students may enroll in 1-11 credits.
- Waitlist: If a course is full, students may join the waitlist. Waitlisted students are automatically enrolled if a seat opens before the end of week 1.
- Prerequisites: Students must have completed all listed prerequisites before enrolling. Prerequisite waivers require written approval from the course instructor and department chair.
- Holds: Registration holds (financial, academic, advising) must be resolved before a student can register. Contact the appropriate office to clear holds.
- Tuition payment: A 50% deposit is due within 72 hours of registration. Full payment is due by the end of week 2 of the semester.

COMMON REGISTRATION ISSUES & SOLUTIONS:
- "Time conflict" error: Two courses share overlapping meeting times. Choose an alternative section or a different course.
- "Prerequisite not met" error: You have not completed the required prerequisite courses. Contact the instructor for a waiver if you have equivalent experience.
- "Course full / section closed": Join the waitlist through the student portal. Monitor your university email for seat-opening notifications.
- "Registration hold": Log into the student portal to identify the hold type, then contact the responsible office (Bursar for financial holds, Academic Affairs for academic holds, Advising Center for advising holds).
- "Permission required": Some courses need instructor or department consent. Email the instructor with your name, student ID, and reason for requesting permission.
- System login issues: Clear browser cache, try a different browser, or contact the IT Help Desk at it-help@greenvalley.edu or (555) 010-1234.

KEY CONTACTS:
- Registrar's Office: registrar@greenvalley.edu | (555) 010-1000 | Open Mon-Fri 8 AM - 5 PM
- Bursar's Office (tuition/fees): bursar@greenvalley.edu | (555) 010-1100
- Academic Advising Center: advising@greenvalley.edu | (555) 010-1200
- IT Help Desk: it-help@greenvalley.edu | (555) 010-1234
- Student Portal: https://portal.greenvalley.edu

BEHAVIOR GUIDELINES:
- Always be polite, patient, and empathetic — registration can be stressful for students.
- Ask clarifying questions if the student's problem is unclear (e.g., ask for the course name, error message, or student standing).
- Provide step-by-step guidance when explaining how to perform an action in the student portal.
- If a problem requires action from a specific office, tell the student exactly which office to contact and how.
- Do not guess at policies. If you are unsure, advise the student to contact the Registrar's Office directly.
- Keep responses concise and friendly. Use bullet points or numbered steps when listing instructions.
"""


class UniversityRegistrationChatbot:
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash"):
        self.llm = GeminiProvider(model_name=model_name, api_key=api_key)
        self.history: List[Dict[str, str]] = []

    def _build_prompt(self, user_message: str) -> str:
        """Format conversation history + new user message into a single prompt string."""
        lines = []
        for turn in self.history:
            role = "Student" if turn["role"] == "user" else "Advisor"
            lines.append(f"{role}: {turn['content']}")
        lines.append(f"Student: {user_message}")
        lines.append("Advisor:")
        return "\n".join(lines)

    def chat(self, user_message: str) -> str:
        prompt = self._build_prompt(user_message)
        result = self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)
        response = result["content"].strip()

        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": response})
        return response

    def reset(self):
        self.history = []


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment or .env file.")
        sys.exit(1)

    chatbot = UniversityRegistrationChatbot(api_key=api_key)

    print("=" * 60)
    print("  Green Valley University — Course Registration Advisor")
    print("=" * 60)
    print("Hello! I'm your registration advisor. How can I help you")
    print("with course registration today?")
    print("(Type 'quit' to exit, 'reset' to start a new conversation)")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! Good luck with your registration!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\nAdvisor: Thank you for visiting. Good luck with your registration!")
            break

        if user_input.lower() == "reset":
            chatbot.reset()
            print("\nAdvisor: Conversation reset. How can I help you?")
            continue

        print("\nAdvisor: ", end="", flush=True)
        response = chatbot.chat(user_input)
        print(response)


if __name__ == "__main__":
    main()
