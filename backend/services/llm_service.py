"""
LLM service layer – wraps Mistral AI via LangChain.

All public functions in this module are **synchronous** because
FastAPI will run them in a thread-pool when called from async endpoints.
If the ``MISTRAL_API_KEY`` is not configured, functions gracefully
return sensible fallback values so the rest of the app still works.
"""

from __future__ import annotations

import json
import logging
import math
from typing import Any

from backend.config import settings

logger = logging.getLogger(__name__)

# ── Risk weights for asset types (0 = lowest risk, 10 = highest) ────
ASSET_RISK_WEIGHTS: dict[str, float] = {
    "fixed_deposit": 1.0,
    "ppf": 1.5,
    "gold": 3.0,
    "mutual_fund": 5.0,
    "equity": 7.0,
    "crypto": 9.0,
}

# ── LLM singleton ──────────────────────────────────────────────────────


def get_llm():
    """Return a cached ``ChatMistralAI`` instance.

    Uses the *mistral-small-latest* model for fast, cost-effective responses.
    Returns ``None`` when no API key is configured.
    """
    if not settings.MISTRAL_API_KEY:
        logger.warning("MISTRAL_API_KEY is not set – LLM features are disabled.")
        return None

    from langchain_mistralai import ChatMistralAI

    return ChatMistralAI(
        model="mistral-small-latest",
        api_key=settings.MISTRAL_API_KEY,
        temperature=0.3,
    )


def _invoke_llm(prompt: str, fallback: str = "LLM is not configured.") -> str:
    """Helper: invoke the LLM with *prompt* and return the text content.

    If the LLM is unavailable, *fallback* is returned instead.
    """
    llm = get_llm()
    if llm is None:
        return fallback
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as exc:  # pragma: no cover
        logger.exception("LLM invocation failed: %s", exc)
        return f"Error generating response: {exc}"


# ═══════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════


def categorize_transactions(transactions: list[dict]) -> list[str]:
    """Categorize a batch of transactions using the LLM.

    Args:
        transactions: List of dicts, each with at least ``description``
            and ``amount`` keys.

    Returns:
        A list of category strings in the same order as *transactions*.
        Possible categories: Food, Transport, Shopping, Bills,
        Entertainment, Health, Investment, Income, Transfer, Other.
    """
    if not transactions:
        return []

    categories_list = (
        "Food, Transport, Shopping, Bills, Entertainment, Health, "
        "Investment, Income, Transfer, Other"
    )

    # Build a compact description list for the prompt.
    txn_lines = "\n".join(
        f"{i + 1}. {t.get('description', 'N/A')} | Amount: {t.get('amount', 0)} | "
        f"Type: {t.get('transaction_type', 'unknown')}"
        for i, t in enumerate(transactions)
    )

    prompt = (
        "You are a financial transaction categorizer. "
        f"Categorize each transaction into exactly one of: {categories_list}.\n\n"
        "Transactions:\n"
        f"{txn_lines}\n\n"
        "Return ONLY a valid JSON array of category strings in the same order. "
        "Example: [\"Food\", \"Transport\", \"Bills\"]\n"
        "Do not include any other text."
    )

    raw = _invoke_llm(prompt, fallback="[]")

    # Parse the JSON response.
    try:
        # Strip markdown code-fence wrappers if the model returns them.
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]  # remove opening fence line
            cleaned = cleaned.rsplit("```", 1)[0]  # remove closing fence
        parsed = json.loads(cleaned)
        if isinstance(parsed, list) and len(parsed) == len(transactions):
            return [str(c) for c in parsed]
    except (json.JSONDecodeError, IndexError, ValueError):
        logger.warning("Failed to parse LLM categories – falling back to 'Other'.")

    return ["Other"] * len(transactions)


def generate_spending_insights(summary: dict[str, Any]) -> str:
    """Generate natural-language spending insights from aggregated data.

    Args:
        summary: A dict containing keys like ``total_income``,
            ``total_expense``, ``category_breakdown``, etc.

    Returns:
        A markdown-formatted string with spending insights.
    """
    prompt = (
        "You are an expert personal-finance advisor. "
        "Analyze the following spending summary and provide 3-5 actionable insights.\n\n"
        f"Total Income: ₹{summary.get('total_income', 0):,.2f}\n"
        f"Total Expenses: ₹{summary.get('total_expense', 0):,.2f}\n"
        f"Net Savings: ₹{summary.get('net', 0):,.2f}\n"
        f"Transaction Count: {summary.get('transaction_count', 0)}\n"
        f"Category Breakdown: {json.dumps(summary.get('category_breakdown', {}), indent=2)}\n\n"
        "Be concise, specific, and encouraging. Use bullet points."
    )

    return _invoke_llm(
        prompt,
        fallback=(
            "• Your total income is ₹{inc:,.2f} and expenses are ₹{exp:,.2f}.\n"
            "• Configure your MISTRAL_API_KEY for personalised AI insights."
        ).format(
            inc=summary.get("total_income", 0),
            exp=summary.get("total_expense", 0),
        ),
    )


def generate_savings_advice(summary: dict[str, Any], goals: list[dict]) -> str:
    """Generate savings recommendations considering goals.

    Args:
        summary: Spending summary dict.
        goals: List of goal dicts (``name``, ``target_amount``,
            ``current_amount``, ``deadline``, ``priority``).

    Returns:
        Natural-language savings advice.
    """
    goals_text = "\n".join(
        f"- {g.get('name', 'Goal')}: target ₹{g.get('target_amount', 0):,.2f}, "
        f"saved ₹{g.get('current_amount', 0):,.2f}, "
        f"priority={g.get('priority', 'medium')}, deadline={g.get('deadline', 'N/A')}"
        for g in goals
    ) or "No goals set yet."

    prompt = (
        "You are a personal-finance advisor specializing in savings strategies.\n\n"
        f"Monthly Income: ₹{summary.get('total_income', 0):,.2f}\n"
        f"Monthly Expenses: ₹{summary.get('total_expense', 0):,.2f}\n"
        f"Net Savings: ₹{summary.get('net', 0):,.2f}\n\n"
        f"Financial Goals:\n{goals_text}\n\n"
        "Provide 3-5 specific, actionable recommendations to help this person "
        "increase savings and reach their goals faster. Be practical and concise."
    )

    return _invoke_llm(
        prompt,
        fallback="Configure your MISTRAL_API_KEY to receive personalised savings advice.",
    )


def chat_response(message: str, context: str) -> str:
    """Generate a conversational AI response with financial context.

    Args:
        message: The user's latest message.
        context: A string containing recent financial context (balances,
            goals, transaction summaries, etc.) to ground the response.

    Returns:
        The assistant's reply.
    """
    prompt = (
        "You are a friendly, knowledgeable AI financial advisor named WealthBot. "
        "Use the following context about the user's finances to answer accurately. "
        "If the question is not finance-related, you may answer briefly but steer "
        "the conversation back to finance.\n\n"
        f"--- User Financial Context ---\n{context}\n"
        f"--- End Context ---\n\n"
        f"User: {message}\n\n"
        "Respond helpfully and concisely."
    )

    return _invoke_llm(
        prompt,
        fallback=(
            "I'm your AI wealth advisor, but my language model is not configured yet. "
            "Please set the MISTRAL_API_KEY environment variable to enable AI features."
        ),
    )


def calculate_risk_score(portfolio: list[dict]) -> dict[str, Any]:
    """Calculate a portfolio risk score using deterministic math.

    The score is a weighted average of per-asset risk weights (scaled 0–10)
    based on the current market value of each holding.  The LLM is used
    **only** to explain the score in plain English.

    Args:
        portfolio: List of dicts with keys ``asset_type``,
            ``quantity``, ``current_price``.

    Returns:
        A dict with ``risk_score`` (float 0–10), ``risk_level`` (str),
        ``asset_allocation`` (dict), and ``explanation`` (str).
    """
    if not portfolio:
        return {
            "risk_score": 0.0,
            "risk_level": "N/A",
            "asset_allocation": {},
            "explanation": "No portfolio data available to calculate risk.",
        }

    # ── Deterministic calculation ───────────────────────────────────
    total_value = 0.0
    type_values: dict[str, float] = {}

    for asset in portfolio:
        value = asset.get("quantity", 0) * asset.get("current_price", 0)
        atype = asset.get("asset_type", "other")
        type_values[atype] = type_values.get(atype, 0.0) + value
        total_value += value

    if total_value == 0:
        return {
            "risk_score": 0.0,
            "risk_level": "N/A",
            "asset_allocation": {},
            "explanation": "Portfolio has zero market value.",
        }

    # Weighted risk score.
    weighted_sum = sum(
        ASSET_RISK_WEIGHTS.get(atype, 5.0) * val
        for atype, val in type_values.items()
    )
    risk_score = round(weighted_sum / total_value, 2)

    # Asset allocation percentages.
    asset_allocation = {
        atype: round((val / total_value) * 100, 2)
        for atype, val in type_values.items()
    }

    # Risk level label.
    if risk_score <= 3:
        risk_level = "Conservative"
    elif risk_score <= 5:
        risk_level = "Moderate"
    elif risk_score <= 7:
        risk_level = "Aggressive"
    else:
        risk_level = "Very Aggressive"

    # ── LLM explanation ─────────────────────────────────────────────
    explanation_prompt = (
        "You are a financial risk analyst. A user's portfolio has a risk score "
        f"of {risk_score}/10 ({risk_level}). "
        f"Their asset allocation is: {json.dumps(asset_allocation)}. "
        "In 2-3 sentences, explain what this risk level means for the user "
        "and suggest one actionable adjustment if appropriate."
    )

    explanation = _invoke_llm(
        explanation_prompt,
        fallback=(
            f"Your portfolio risk score is {risk_score}/10 ({risk_level}). "
            "Configure your MISTRAL_API_KEY for a detailed explanation."
        ),
    )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "asset_allocation": asset_allocation,
        "explanation": explanation,
    }
