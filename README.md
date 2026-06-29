\# Financial Advisory Agents



Production-grade AI agents for personal finance, built with CrewAI and GPT-4o-mini.

Developed as part of an AI Engineering internship at Upstride.



\---



\## Overview



This repository contains two specialized financial advisory agents built for

the Nemi Wealth platform. Each agent uses deterministic Python tools for all

calculations — the LLM handles reasoning and communication, the LLM will never handle math.



|       Agents                    |   Tools   | Tests |         Status          |

|---------------------------------|-----------|-------|-------------------------|

| Debt Management Agent           | 3         | 17    | Production-ready        |

| Insurance Coverage Gap Analyzer | 2         | 13    | Production-ready        |



\*\*Total: 2 agents · 5 tools · 30 unit tests · all passing\*\*



\---



\## Agent 1 — Debt Management Agent



Helps users understand their debt situation, build a repayment strategy,

and improve their CIBIL credit score.



\### Tools



\*\*Tool 1: Debt Payoff Optimizer\*\*

Simulates avalanche (highest interest rate first) and snowball

(smallest balance first) repayment strategies using month-by-month

amortization math. Returns both strategies side-by-side with total

interest paid, months to debt-free, and a recommendation based on

the user's debt profile.



\*\*Tool 2: Debt Consolidation Analyzer\*\*

Compares multiple consolidation loan options against the user's

current repayment path. Calculates net savings after processing fees.

Always includes a behavioral warning about re-accumulating debt

on cleared credit lines.



\*\*Tool 3: Credit Score Improvement Planner\*\*

Encodes CIBIL scoring logic across four factors — payment history (35%),

credit utilization (30%), credit age (15%), and hard inquiries (10%).

Returns a prioritized action plan with timeline estimates and projected

score range. Works from user-provided data only — no live CIBIL API.



\### Example interaction


User: I have a credit card with Rs.1.5 lakh at 36% and a personal loan



of Rs.3 lakh at 14%. I can pay Rs.5000 extra per month.



What is my best strategy?



Agent: \[calls Debt Payoff Optimizer]

Avalanche method: debt-free in 26 months, Rs.90,971 total interest.

Recommendation: Avalanche — pay credit card first at 36%.

Once cleared, redirect Rs.7,500 + Rs.5,000 to personal loan.




### Guardrails

\- Never recommends specific banks or lenders by name

\- Never advises on bankruptcy or legal proceedings

\- Never promises guaranteed score improvements

\- Always ends with SEBI disclaimer



\---



\## Agent 2 — Insurance Coverage Gap Analyzer



Calculates how much life insurance a user needs using the DIME method

and identifies the exact gap in rupees between their need and current coverage.



\### DIME Method

Required Coverage = D + I + M + E

D = Debts (non-mortgage: personal loan, car loan, credit card)



I = Income replacement (annual income × years to retirement)



M = Mortgage (home loan outstanding)



E = Education (goal per child × number of children)

Gap = Required Coverage − Existing Coverage



\### Tools



\*\*Tool 1: Coverage Need Calculator\*\*

Runs the DIME formula with India-specific defaults.

Retirement age defaults to 60 if not specified.

Education goal is configurable per child.



\*\*Tool 2: Coverage Gap Analyzer\*\*

Compares required coverage from Tool 1 against all existing policies

(term plan + employer group cover + LIC/traditional policies).

Returns risk classification and priority action.



Risk classifications:

\- `critically\_underinsured` — existing covers less than 50% of need

\- `moderately\_underinsured` — gap exists but manageable

\- `adequately\_covered` — existing matches need

\- `over\_insured` — existing exceeds need



\### Inter-agent handoff

When a coverage gap is detected, the agent outputs:
HANDOFF:wealth\_retirement



This signal passes the gap amount to the Wealth \& Retirement agent

for integration into retirement planning and wealth projection.



\### Example interaction


User: I am Sneha, 29. I earn Rs.75,000/month. Spouse, no children.



Personal loan Rs.1.5L, car loan Rs.4L. Want to retire at 58.



Only Rs.5L employer group cover. What is my gap?



Agent: \[calls Insurance Coverage Gap Analyzer]



Required coverage: Rs.2,66,62,000

Existing coverage: Rs.5,00,000



Gap: Rs.2,61,62,000

Risk: Critically underinsured (2% of need covered)

Action: Buy a pure term plan immediately.

Note: Employer group cover ends when you leave the job.

Would you like me to factor this into your retirement plan?

HANDOFF:wealth\_retirement



\### Guardrails

\- Never recommends specific insurance companies or products

\- Never promises specific premium amounts

\- Always includes IRDAI compliance disclaimer

\- Works from user-provided data only — no live insurance API



\---



\## Tech Stack



|      Layer      |     Technology        |

|-----------------|-----------------------|

| Agent framework |      CrewAI           |

| LLM             |  GPT-4o-mini (OpenAI) |

| Data validation |      Pydantic v2      |

| Testing         |       pytest          |

| Language        |     Python 3.13       |



\---



\## Project Structure





financial-advisory-agents/



├── backend/



│   ├── agents/



│   │   ├── debt\_management/



│   │   │   ├── schemas/models.py        # Pydantic data contracts



│   │   │   ├── tools/



│   │   │   │   ├── debt\_payoff\_optimizer.py



│   │   │   │   ├── debt\_consolidation\_analyzer.py



│   │   │   │   ├── credit\_score\_planner.py



│   │   │   │   ├── tool1\_wrapper.py     # CrewAI tool wrappers



│   │   │   │   ├── tool2\_wrapper.py



│   │   │   │   └── tool3\_wrapper.py



│   │   │   ├── tests/                   # 17 unit tests



│   │   │   └── agent.py                 # Agent assembly



│   │   └── insurance\_coverage/



│   │       ├── schemas/models.py



│   │       ├── tools/



│   │       │   ├── coverage\_need\_calculator.py



│   │       │   ├── gap\_analyzer.py



│   │       │   ├── tool1\_wrapper.py



│   │       │   └── tool2\_wrapper.py



│   │       ├── tests/                   # 13 unit tests



│   │       └── agent.py



│   └── requirements.txt



├── .env.example



├── .gitignore



└── README.md

\---



\## Setup



```bash

\# Clone the repo

git clone https://github.com/rmagdaleena2508-01/financial-advisory-agents.git

cd financial-advisory-agents



\# Create virtual environment

python -m venv venv



\# Activate (Windows)

venv\\Scripts\\Activate.ps1



\# Activate (Mac/Linux)

source venv/bin/activate



\# Install dependencies

pip install -r backend/requirements.txt



\# Set up environment

cp .env.example .env

\# Edit .env and add your OpenAI API key

```



\---



\## Running the Agents



```bash

cd backend



\# Run Debt Management Agent

python -m agents.debt\_management.agent



\# Run Insurance Coverage Gap Analyzer

python -m agents.insurance\_coverage.agent

```



\---



\## Running Tests



```bash

cd backend



\# All tests

python -m pytest agents/ -v



\# Debt Management tests only

python -m pytest agents/debt\_management/tests/ -v



\# Insurance Coverage tests only

python -m pytest agents/insurance\_coverage/tests/ -v

```



Expected output:

30 passed in X.XXs



\---



\## Design Principles



\*\*Tools do the math. LLM does the reasoning.\*\*

Every number in every response comes from a deterministic Python function,

not from the LLM. This means outputs are verifiable, testable, and consistent.



\*\*Build sequence discipline.\*\*

Pydantic schemas → pure Python logic → unit tests (all passing)

→ CrewAI wrappers → agent assembly → end-to-end testing.

Never skip a step.



\*\*Guardrails are non-negotiable.\*\*

Financial advisory is regulated in India. Every agent has explicit

hard refusal rules in the system prompt and always includes

appropriate disclaimers (SEBI / IRDAI).



\---



\## Built By



\*\*R. Magdaleena\*\* — AI Engineer Intern at Upstride

\[LinkedIn](https://linkedin.com/in/rmagdaleena-aiengineer) ·

\[Portfolio](https://rmagdaleena.xyz) ·

\[GitHub](https://github.com/rmagdaleena2508-01)



\---



\*Part of a Wealth fintech platform — a multi-agent AI financial advisory system serving Indian users.\*




