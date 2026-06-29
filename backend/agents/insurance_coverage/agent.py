from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
from .tools.tool1_wrapper import insurance_coverage_gap_analyzer_tool
from .tools.tool2_wrapper import coverage_gap_analyzer_tool

load_dotenv()

llm = LLM(model="gpt-4o-mini", temperature=0.3)

BACKSTORY = """
You are an empathetic insurance advisor on the Nemi Wealth platform,
serving Indian users who need to understand their life insurance coverage gap.

Your personality:
- Warm and clear. Insurance is confusing for most users. Simplify without dumbing down.
- Precise. You use tools for ALL calculations. Never estimate numbers mentally.
- India-aware. You understand term plans, LIC policies, employer group cover, IRDAI.
- Honest. If someone is critically underinsured, say so clearly but without panic.

How you work:
- Call the Insurance Coverage Gap Analyzer tool with ALL inputs at once.
- The tool handles the DIME calculation and gap analysis internally.
- Present the results clearly — required coverage, existing coverage,
  gap in rupees, risk level, and action steps.
- Always include the handoff question when handoff_triggered is true.



Hard rules you never break:
1. Never recommend specific insurance companies or products by name.
2. Never promise specific premium amounts — these vary by age, health, and insurer.
3. Never advise on claims processes or policy disputes — refer to IRDAI or insurer.
4. Always remind users that employer group cover ends when they leave the job.
5. Always end with the standard disclaimer.
6. When handoff is triggered say:
   "Would you like me to factor this gap into your retirement plan?"
   Then output: HANDOFF:wealth_retirement

Disclaimer to always include:
This is educational guidance based on the information you have provided.
It is not regulated insurance advice. Consult an IRDAI-registered insurance
advisor before purchasing any policy.
"""

insurance_coverage_agent = Agent(
    role="Insurance Coverage Advisor",
    goal=(
        "Help users understand exactly how much life insurance they need, "
        "calculate their current coverage gap in rupees, and guide them "
        "on closing that gap — with clarity, empathy, and mathematical precision."
    ),
    backstory=BACKSTORY,
   # In the Agent definition:
    tools=[
    insurance_coverage_gap_analyzer_tool,
    ],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=6,
)


def chat_with_insurance_agent(user_message: str) -> str:
    task = Task(
        description=user_message,
        agent=insurance_coverage_agent,
        expected_output=(
            "A clear response showing required coverage, existing coverage, "
            "gap in rupees, risk level, priority action steps, "
            "handoff trigger if applicable, and the standard disclaimer."
        )
    )
    crew = Crew(
        agents=[insurance_coverage_agent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
    print("\n=== Insurance Coverage Gap Analyzer — Test Run ===\n")

    queries = [
        # INS_001 — Arjun Nair — full flow
        (
            "I am Arjun, 34 years old. I earn Rs.1.2 lakh per month. "
            "I have a spouse and one child aged 4. "
            "I have a home loan of Rs.35 lakh, personal loan of Rs.2 lakh, "
            "and credit card debt of Rs.25,000. "
            "My child's education goal is Rs.25 lakh. I want to retire at 60. "
            "I currently have a Rs.50 lakh term plan, Rs.10 lakh employer cover, "
            "and Rs.5 lakh LIC policy. "
            "How much life insurance do I need and what is my coverage gap?"
        ),

        # INS_002 — Sneha Kulkarni — zero coverage case
        (
            "I am Sneha, 29 years old. I earn Rs.75,000 per month. "
            "I have a spouse but no children yet. "
            "I have a personal loan of Rs.1.5 lakh, car loan of Rs.4 lakh, "
            "and credit card debt of Rs.12,000. No home loan. "
            "I want to retire at 58. "
            "I have no term plan. Only Rs.5 lakh employer group cover. "
            "What is my insurance gap?"
        ),

        # INS_003 — Vikram Bhat — high income, still underinsured
        (
            "I am Vikram, 45 years old. I earn Rs.3 lakh per month. "
            "I have a spouse and 2 children aged 12 and 15. "
            "Home loan Rs.80 lakh, car loan Rs.12 lakh. No other debts. "
            "Education goal Rs.20 lakh per child. I want to retire at 55. "
            "I have a Rs.1 crore term plan and Rs.20 lakh LIC policy. "
            "Am I adequately covered?"
        ),
    ]

    for i, query in enumerate(queries, 1):
        print(f"--- Query {i} ---")
        print(f"USER: {query}\n")
        response = chat_with_insurance_agent(query)
        print(f"AGENT: {response}\n")