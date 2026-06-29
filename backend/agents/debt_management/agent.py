from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
from .tools.tool1_wrapper import debt_payoff_optimizer_tool
from .tools.tool2_wrapper import debt_consolidation_analyzer_tool
from .tools.tool3_wrapper import credit_score_planner_tool

load_dotenv()

llm = LLM(model="gpt-4o-mini", temperature=0.3)

BACKSTORY = """
You are an empathetic debt counselor on the Nemi Wealth platform,
serving Indian users who are trying to become debt-free.

Your personality:
- Warm and non-judgmental. Many users feel shame about debt. Acknowledge stress first.
- Precise. You use tools for ALL numbers. You never estimate or calculate mentally.
- India-aware. Amounts in rupees. You understand EMI, CIBIL, SIP, EPF, 80C.
- Honest. If consolidation does not save money, say so clearly.

Hard rules you never break:
1. Never recommend specific banks or lenders by name.
2. Never advise on bankruptcy or legal proceedings — refer to a lawyer.
3. Never promise guaranteed score improvements or debt forgiveness.
4. Never claim to know a user's live CIBIL score — work only from what they tell you.
5. Always end every response with the disclaimer below.
6. When a question is about investing, tax planning, or retirement say:
   "This falls under our Investment or Wealth advisor's expertise."
   Then output: HANDOFF:<agent_name> where agent_name is one of:
   personal_finance, investment_advisory, wealth_retirement.

Disclaimer to always include at the end of every response:
This is educational guidance based on the information you have provided.
It is not regulated financial advice. For personalised advice please consult
a SEBI-registered financial advisor or a certified credit counselor.
"""

debt_management_agent = Agent(
    role="Personal Debt Counselor",
    goal=(
        "Help users understand their complete debt picture, build a practical "
        "repayment strategy, and improve their credit score with empathy, "
        "mathematical precision, and honest guidance."
    ),
    backstory=BACKSTORY,
    tools=[
        debt_payoff_optimizer_tool,
        debt_consolidation_analyzer_tool,
        credit_score_planner_tool,
    ],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=6,
)


def chat_with_agent(user_message: str) -> str:
    task = Task(
        description=user_message,
        agent=debt_management_agent,
        expected_output=(
            "A clear, empathetic response with specific numbers from tools, "
            "prioritized action steps, and the standard disclaimer."
        )
    )
    crew = Crew(
        agents=[debt_management_agent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
    print("\n=== Debt Management Agent — Test Run (Mock User Data) ===\n")

    queries = [
        # USR_003 — Anjali Verma — Tool 1: Debt Payoff Optimizer
        (
            "My name is Anjali. I have a personal loan of Rs.80,000 at 14.5% interest "
            "with EMI of Rs.4,500 and 20 months remaining. I also have credit card debt "
            "of Rs.8,000 — I pay Rs.2,000 minimum monthly on it. The credit card charges "
            "36% interest. I can squeeze out Rs.2,000 extra per month. "
            "Which debt should I pay first and what is my best strategy?"
        ),

        # USR_001 — Priya Sharma — Tool 2: Debt Consolidation Analyzer
        (
            "I am Priya. I have credit card debt of Rs.15,000 at 36% interest and I pay "
            "Rs.2,000 minimum monthly with 8 months remaining. My income is Rs.1,50,000 "
            "per month. A bank offered me a personal loan at 12% to clear my credit card "
            "debt with 1% processing fee over 12 months. Is consolidation worth it?"
        ),

        # USR_003 — Anjali Verma — Tool 3: Credit Score Improvement Planner
        (
            "I am Anjali, 26 years old. My CIBIL score is around 680. "
            "I use about 70% of my credit card limit. I missed one EMI last month "
            "on my personal loan. My oldest account is about 2 years old and I "
            "recently applied for one loan. How do I improve my credit score? "
            "I want to buy a home in 3 years and need a good score for the loan."
        ),
    ]

    for i, query in enumerate(queries, 1):
        print(f"--- Query {i} ---")
        print(f"USER: {query}\n")
        response = chat_with_agent(query)
        print(f"AGENT: {response}\n")