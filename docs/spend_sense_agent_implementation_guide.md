# SpendSense Agent – Implementation Guide

## 1. Project Overview

**Agent Name:** SpendSense Agent
**Track:** Personal & Self‑Improvement Agents (Track 1)
**Aligned SDGs:**

- SDG 1 – No Poverty
- SDG 8 – Decent Work & Economic Growth
- SDG 10 – Reduced Inequalities

### Problem Statement

Many individuals struggle with everyday financial decisions such as purchases, savings, and budgeting. Most tools are either too complex or give unsafe financial advice. SpendSense Agent helps users evaluate spending decisions using simple rules + AI reasoning, while remaining non‑advisory, explainable, and ethical.

### What This Agent Is (and Is Not)

- [INCLUDED] A decision-support agent
- [INCLUDED] Scenario and risk analysis tool
- [EXCLUDED] Not a financial advisor
- [EXCLUDED] No investment, tax, or credit advice

---

## 2. Core Use Case

**User question:**
> “Can I afford this purchase without breaking my budget?”

The agent:

1. Analyzes income, expenses, and savings goals
2. Applies rule‑based checks
3. Uses AI to reason about trade‑offs
4. Returns a risk‑scored recommendation with explanation

---

## 3. System Architecture (Judge‑Friendly)

```
[CLI / Web UI]
        ↓
[Input Validation Layer]
        ↓
[Rule Engine]
        ↓
[AI Reasoning Module]
        ↓
[Decision + Explanation Output]
```

### Component Responsibilities

| Component | Responsibility |
|---------|---------------|
| UI / CLI | Collect user inputs, display results |
| Validation Layer | Check required fields, data types |
| Rule Engine | Deterministic budget & risk checks |
| AI Module | Natural language reasoning & alternatives |
| Output Layer | Structured JSON + explanation |

---

## 4. Input & Output Schema

### Input Schema (JSON)

```json
{
  "monthly_income": number,
  "fixed_expenses": number,
  "savings_goal": number,
  "planned_purchase": {
    "item": string,
    "cost": number
  }
}
```

### Output Schema (JSON)

```json
{
  "decision": "Low Risk | Medium Risk | High Risk",
  "confidence_score": number,
  "explanation": string,
  "alternatives": [string]
}
```

---

## 5. Rule Engine (Non‑AI Logic)

### Rules Implemented

1. **Disposable Income**

```
disposable = income - fixed_expenses - savings_goal
```

1. **Risk Thresholds**

| Condition | Risk Level |
|--------|------------|
| purchase ≤ 30% of disposable | Low |
| 30–60% of disposable | Medium |
| > 60% of disposable | High |

1. **Hard Stops**

- If disposable ≤ 0 → auto High Risk
- If cost > income → refuse with explanation

These rules ensure **predictability and safety**.

---

## 6. AI Reasoning Module

### Purpose of AI

AI is used **only** to:

- Explain results in plain language
- Suggest safer alternatives
- Add contextual reasoning

### Example Prompt Structure

**System Prompt:**
> You are a budgeting decision assistant. You must not give financial, tax, or investment advice. You explain risks and alternatives clearly and conservatively.

**User Prompt (Generated):**
> User disposable income: $150. Planned purchase: $300. Risk level: High. Explain why and suggest alternatives.

### Guardrails

- Refuse investment, loan, or tax questions
- Always include disclaimer
- Never output commands like “buy” or “don’t buy”

---

## 7. Confidence & Risk Scoring

### Confidence Score Logic

```
confidence = min(1.0, purchase_cost / max(disposable, 1))
```

Mapped to:

- 0.0–0.4 → Low Risk
- 0.4–0.7 → Medium Risk
- 0.7–1.0 → High Risk

This makes scoring **transparent and explainable**.

---

## 8. Error Handling & Validation

### Validation Checks

- Missing fields
- Negative values
- Non‑numeric inputs

### Error Output Example

```json
{
  "error": "Monthly income must be greater than 0"
}
```

---

## 9. Demo Options (Choose One)

### Option A – CLI (Fastest)

- Python or Go
- Prompt user step‑by‑step
- Output JSON + explanation

### Option B – Simple Web UI

- Single page form
- Submit → display results
- No auth, no database

CLI is **100% acceptable** for judging.

---

## 10. Marketplace Readiness

### Required Assets

- Agent name & description
- Input/output schema
- Working demo
- README

### README Must Include

- Problem statement
- SDG alignment
- Architecture diagram
- AI usage explanation
- Trade‑offs & limitations

---

## 11. Trade‑offs & Limitations (Be Honest)

- No real banking integration
- Estimates only
- Short‑term budgeting focus
- Relies on user‑provided data

Judges reward honesty here.

---

## 12. Estimated Build Timeline (< 40 Hours)

| Task | Time |
|----|----|
| Design & schemas | 4 hrs |
| Rule engine | 6 hrs |
| AI integration | 8 hrs |
| CLI / UI | 6 hrs |
| Testing & validation | 6 hrs |
| Documentation | 6 hrs |

---

## 13. Final Note

This agent is intentionally simple, explainable, and safe. Its strength is not intelligence — it’s **clarity, restraint, and real‑world usability**.

Build less. Explain more. Ship on time.
