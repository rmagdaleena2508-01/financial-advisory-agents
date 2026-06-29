from pydantic import BaseModel
from typing import Literal
from ..schemas.models import Debt


class MonthlySnapshot(BaseModel):
    month: int
    debt_name: str
    balance_remaining: float
    payment_made: float


class DebtPlan(BaseModel):
    strategy: Literal["avalanche", "snowball"]
    months_to_debt_free: int
    total_interest_paid: float
    order_debts_paid: list[str]
    monthly_snapshots: list[MonthlySnapshot]


class OptimizerInput(BaseModel):
    debts: list[Debt]
    extra_monthly_payment: float


class OptimizerOutput(BaseModel):
    avalanche: DebtPlan
    snowball: DebtPlan
    interest_saved_by_avalanche: float
    months_difference: int
    recommendation: Literal["avalanche", "snowball"]
    recommendation_reason: str


def _simulate_payoff(
    debts: list[Debt],
    extra_monthly: float,
    strategy: Literal["avalanche", "snowball"]
) -> DebtPlan:

    balances = {d.name: d.principal_outstanding for d in debts}
    rates = {d.name: d.interest_rate_pct / 100 / 12 for d in debts}
    emis = {d.name: d.monthly_emi for d in debts}

    if strategy == "avalanche":
        priority_order = sorted(debts, key=lambda d: d.interest_rate_pct, reverse=True)
    else:
        priority_order = sorted(debts, key=lambda d: d.principal_outstanding)

    priority_names = [d.name for d in priority_order]

    month = 0
    total_interest = 0.0
    snapshots = []
    order_cleared = []
    max_months = 600

    while any(b > 0.01 for b in balances.values()) and month < max_months:
        month += 1

        interest_this_month = {}
        for name, balance in balances.items():
            if balance > 0.01:
                interest = balance * rates[name]
                interest_this_month[name] = interest
                total_interest += interest

        for name in balances:
            if balances[name] > 0.01:
                payment = min(emis[name], balances[name] + interest_this_month.get(name, 0))
                balances[name] = balances[name] + interest_this_month.get(name, 0) - payment
                balances[name] = max(0, balances[name])
                snapshots.append(MonthlySnapshot(
                    month=month,
                    debt_name=name,
                    balance_remaining=round(balances[name], 2),
                    payment_made=round(payment, 2)
                ))

        remaining_extra = extra_monthly
        for name in priority_names:
            if remaining_extra <= 0:
                break
            if balances[name] > 0.01:
                extra_applied = min(remaining_extra, balances[name])
                balances[name] -= extra_applied
                balances[name] = max(0, balances[name])
                remaining_extra -= extra_applied

        for name in priority_names:
            if balances[name] <= 0.01 and name not in order_cleared:
                order_cleared.append(name)

    return DebtPlan(
        strategy=strategy,
        months_to_debt_free=month,
        total_interest_paid=round(total_interest, 2),
        order_debts_paid=order_cleared,
        monthly_snapshots=snapshots
    )


def run_debt_payoff_optimizer(input: OptimizerInput) -> OptimizerOutput:
    if not input.debts:
        raise ValueError("At least one debt is required.")

    avalanche = _simulate_payoff(input.debts, input.extra_monthly_payment, "avalanche")
    snowball = _simulate_payoff(input.debts, input.extra_monthly_payment, "snowball")

    interest_saved = round(snowball.total_interest_paid - avalanche.total_interest_paid, 2)
    months_diff = abs(snowball.months_to_debt_free - avalanche.months_to_debt_free)

    high_interest_debts = [d for d in input.debts if d.interest_rate_pct >= 24]

    if interest_saved > 5000 and len(high_interest_debts) > 0:
        recommendation = "avalanche"
        reason = (
            f"Avalanche saves you Rs.{interest_saved:,.0f} in interest. "
            f"You have {len(high_interest_debts)} high-interest debt(s) above 24% — "
            "tackling those first has a big mathematical advantage."
        )
    elif len(input.debts) >= 4:
        recommendation = "snowball"
        reason = (
            f"With {len(input.debts)} debts, snowball builds momentum by clearing "
            f"smaller balances first. The extra interest cost vs avalanche is "
            f"Rs.{abs(interest_saved):,.0f} — a reasonable price for staying motivated."
        )
    else:
        recommendation = "avalanche"
        reason = (
            f"Avalanche is the mathematically optimal choice here, "
            f"saving you Rs.{interest_saved:,.0f} in interest over {months_diff} fewer months."
        )

    return OptimizerOutput(
        avalanche=avalanche,
        snowball=snowball,
        interest_saved_by_avalanche=interest_saved,
        months_difference=months_diff,
        recommendation=recommendation,
        recommendation_reason=reason,
    )