# Financial Advisory AI Agents

Two AI agents for personal finance, built during my AI engineering internship at Upstride.

Each agent follows the same pattern: deterministic Python tools do the math, the LLM reasons and communicates. Numbers are always verifiable. The LLM never estimates.

# describing this project like I'm talking to you

Two AI agents that calculate your exact debt repayment strategy and life insurance coverage gap — built with CrewAI, GPT-4o-mini, and Pydantic.

---

## Agents

| Agent | Tools | Tests |
|---|---|---|
| Debt Management | 3 | 17 |
| Insurance Coverage Gap Analyzer | 2 | 13 |

**30 tests. All passing.**

---

## Agent 1 — Debt Management

Helps users build a debt repayment strategy and improve their CIBIL credit score.

**Tool 1 — Debt Payoff Optimizer**  
Runs both avalanche (highest rate first) and snowball (smallest balance first) simulations using month-by-month amortization. Returns both plans side-by-side with total interest paid and months to debt-free, then recommends based on the user's profile.

**Tool 2 — Debt Consolidation Analyzer**  
Given a list of debts and one or more consolidation loan options, calculates whether consolidation saves money after fees. Always flags the behavioral risk of re-accumulating debt on cleared lines.

**Tool 3 — Credit Score Improvement Planner**  
Encodes CIBIL's four scoring factors — payment history (35%), utilization (30%), credit age (15%), hard inquiries (10%) — into a prioritized action plan with timeline estimates. No live CIBIL API required.

**Guardrails:** no lender recommendations, no legal advice, no guaranteed outcomes, SEBI disclaimer on every response.

---

## Agent 2 — Insurance Coverage Gap Analyzer

Calculates how much life insurance a user actually needs and shows the gap in rupees.

Uses the DIME method — the standard framework used by IRDAI-registered financial advisors:

```
Required coverage = Debts + Income replacement + Mortgage + Education goals
Gap = Required coverage − Existing coverage
```

**Tool 1 — Coverage Need Calculator**  
Runs the DIME formula. Retirement age defaults to 60. Education goal is configurable per child. Returns a full breakdown of each component.

**Tool 2 — Coverage Gap Analyzer**  
Compares the required coverage against all existing policies (term plan + employer group cover + LIC). Returns a risk classification and priority action.

```
critically_underinsured   existing < 50% of need
moderately_underinsured   gap exists, manageable
adequately_covered        existing matches need
over_insured              existing exceeds need
```

When a gap exists, the agent outputs `HANDOFF:wealth_retirement` — a signal for the orchestration layer to pass the gap amount into retirement planning.

**Guardrails:** no insurer recommendations, no premium promises, IRDAI disclaimer on every response.

---

## Stack

- **CrewAI** — agent framework and tool orchestration  
- **GPT-4o-mini** — reasoning and response generation  
- **Pydantic v2** — input/output validation for every tool  
- **pytest** — unit tests on pure logic before LLM connection  
- **Python 3.13**

---

## Structure

```
backend/
├── agents/
│   ├── debt_management/
│   │   ├── schemas/models.py        ← Pydantic contracts
│   │   ├── tools/
│   │   │   ├── debt_payoff_optimizer.py
│   │   │   ├── debt_consolidation_analyzer.py
│   │   │   ├── credit_score_planner.py
│   │   │   ├── tool1_wrapper.py     ← CrewAI @tool decorators
│   │   │   ├── tool2_wrapper.py
│   │   │   └── tool3_wrapper.py
│   │   ├── tests/                   ← 17 unit tests
│   │   └── agent.py
│   └── insurance_coverage/
│       ├── schemas/models.py
│       ├── tools/
│       │   ├── coverage_need_calculator.py
│       │   ├── gap_analyzer.py
│       │   ├── tool1_wrapper.py
│       │   └── tool2_wrapper.py
│       ├── tests/                   ← 13 unit tests
│       └── agent.py
└── requirements.txt
```
---

## Challenges & what I learned

### LLM tool chaining doesn't guarantee value passing

The insurance agent originally had two separate CrewAI tools — one to calculate
required coverage, another to analyze the gap. The plan was for the LLM to take
the `total_required_coverage` from Tool 1 and pass it as `required_coverage` into
Tool 2.

In practice, the LLM passed `0` instead of the actual value. Every time. The gap
came back negative and Sneha (a critically underinsured user) was classified as
over-insured.

The fix: merge both tools into a single Python wrapper. The DIME calculation and
gap analysis both run inside one function call, so there's no value to pass between
tools — the math chains internally in Python, not through the LLM.

The lesson: never trust the LLM to carry a number between tool calls when the
second tool's correctness depends on it. If two operations are logically sequential,
make them one tool.

### CrewAI's `list[dict]` tool signature causes silent schema failures

The debt payoff optimizer originally accepted `debts: list[dict]` as its parameter.
CrewAI passes this to the LLM as part of the tool schema, and the LLM consistently
passed `[{}]` — an empty dict — instead of filling in the fields.

The error message was a Pydantic validation failure, which the LLM retried five
more times with the same broken input before hitting `max_iter`.

The fix: change the parameter to `debts_json: str` and accept a JSON string instead.
The docstring includes a full example of what the JSON should look like. The LLM
constructs the string correctly when given a concrete example.

The lesson: for complex nested inputs, a JSON string with an example in the docstring
is more reliable than a typed list. The LLM reads the docstring example, not the
type annotation.

---

## Setup

```bash
git clone https://github.com/rmagdaleena2508-01/financial-advisory-agents.git
cd financial-advisory-agents

python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\Activate.ps1       # Windows

pip install -r backend/requirements.txt

cp .env.example .env
# Add your OpenAI API key to .env
```

---

## Run

```bash
cd backend

# Debt Management Agent
python -m agents.debt_management.agent

# Insurance Coverage Gap Analyzer
python -m agents.insurance_coverage.agent
```

---

## Test

```bash
cd backend

python -m pytest agents/ -v
# expected: 30 passed
```

---

## How it's built

The build sequence is the same for every tool:

1. Pydantic schema — define inputs and outputs
2. Pure Python function — implement the logic, no LLM
3. Unit tests — verify the math before connecting anything
4. CrewAI wrapper — expose the function as an `@tool`
5. Agent assembly — role, goal, backstory, guardrails
6. End-to-end test — talk to the full agent

Tools are tested independently of the LLM. If the math is wrong, tests catch it before the agent ever runs.

---

## Built by

**R. Magdaleena** — AI Engineer Intern, Upstride  
[linkedin.com/in/rmagdaleena-aiengineer](https://linkedin.com/in/rmagdaleena-aiengineer) · [rmagdaleena.xyz](https://rmagdaleena.xyz) · [github.com/rmagdaleena2508-01](https://github.com/rmagdaleena2508-01)

*Part of a multi-agent AI financial advisory system built for the Indian market.*
