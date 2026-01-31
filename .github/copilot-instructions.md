# SpendSense AI Agent Instructions

## Project Overview

SpendSense is a **non-advisory financial decision-support system** that evaluates purchase affordability through a deterministic rule-based pipeline enhanced with AI reasoning. It serves individuals making informed spending decisions without crossing into financial advice.

**Key Philosophy**: Transparent, explainable decisions with clear guardrails against financial advisory language.

## Architecture: The Decision Pipeline

The system follows a strict sequential pipeline (see `src/decision_engine.py`):

```
Input → Validation → Rule Engine → Confidence Scorer → AI Reasoning → JSON Report
```

**Component responsibilities:**
- **`src/validation.py`**: Type checking, range validation, numerical consistency
- **`src/rule_engine.py`**: Deterministic disposable income calculation and hard-stop detection
- **`src/scoring.py`**: Confidence score quantification (0.0–1.0 scale)
- **`src/ai_reasoning.py`**: OpenAI API integration for explanations and alternatives
- **`src/decision_engine.py`**: Orchestrates all components, returns comprehensive JSON report

**Critical insight**: Each component outputs structured data that feeds the next. Validation failures halt the pipeline immediately; the engine never proceeds with invalid data.

## Risk Assessment Rules

SpendSense implements three risk tiers based on **purchase cost as % of disposable income**:

| Risk Level | Disposable % | Recommendation |
|-----------|--------------|----------------|
| **LOW** | ≤30% | Can proceed safely |
| **MEDIUM** | 30–60% | Consider alternatives |
| **HIGH** | >60% | Evaluate carefully |
| **STOP** | Any | Hard stops: negative disposable or cost > monthly income |

**File reference**: [src/rule_engine.py](src/rule_engine.py#L31-L39)

## Web Application Structure

Flask app in `src/web_app.py` uses:
- **Session-based auth**: In-memory `users` dict with Werkzeug password hashing (non-production)
- **Fallback mode**: Gracefully runs with rule-based decisions only if `OPENAI_API_KEY` absent
- **Responsive UI**: Templates in `templates/`, styled with `static/style.css`

**Key routes**: `/`, `/login`, `/register`, `/dashboard`, `/evaluate` (POST)

## Testing & Quality Assurance

- **Test-driven development**: All 178 tests pass; each module has comprehensive test suite
- **Test location**: [tests/](tests/) (e.g., `test_decision_engine.py` for orchestration)
- **Running tests**: `pytest` (coverage includes edge cases, boundary conditions, hard stops)
- **No tests modify state**: Tests are isolated, use in-memory fixtures, never touch `.env`

**Common patterns**:
- Test files mirror source structure: `src/X.py` → `tests/test_X.py`
- Validation tests include type mismatches, negative values, zero checks
- Rule engine tests verify threshold boundaries (29.9%, 30%, 60%, 60.1%)

## Development Workflows

### Local Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY to .env
```

### Running the Application
```bash
./start.sh          # Uses .env and runs Flask on localhost:5000
# OR manually:
export $(cat .env | xargs)
python run_web.py --host 127.0.0.1 --port 5000
```

### Debugging
- Enable Flask debug mode: `python run_web.py --debug`
- Logs configured in `src/decision_engine.py` and components via `logging` module
- Add temporary `logger.info()` statements for step-by-step trace

## Code Conventions & Patterns

### Error Handling
- **ValidationError**: Raised by `InputValidator` for invalid input; caught in `decision_engine.evaluate()`
- **API failures**: `AIReasoning` catches OpenAI exceptions, returns fallback explanations
- **Responses**: Always return structured JSON with `status` ("success" or "error") and detailed error messages

### Naming Conventions
- **Variables**: Use descriptive names (`monthly_income`, `disposable_income`, not `m_i`, `d_i`)
- **Methods**: Descriptive verbs (`validate_amount()`, `calculate_disposable_income()`, `check_hard_stops()`)
- **Enums**: PascalCase (`RiskLevel.LOW`, `TransactionType.EXPENSE`)

### Type Hints
- All functions include return type hints (required in new code)
- Use `Optional[]` for nullable fields, `Dict[str, Any]` for JSON-like objects
- Example: `def evaluate_purchase(income: float, ...) -> Dict[str, Any]:`

### Logging
- Use `logger.info()` for workflow steps, `logger.error()` for failures
- Log at component entry points: "Step 1: Validating input...", "Step 2: Running rule engine..."

## Integration Points & Dependencies

### External APIs
- **OpenAI API** (`gpt-4o-mini`): Called via `src/ai_reasoning.py::AIReasoning.generate_explanation()`
  - Requires `OPENAI_API_KEY` in `.env`
  - **Critical**: System prompt in `SYSTEM_PROMPT` constant enforces exact budget logic and JSON-only output
  - Returns strictly JSON-formatted responses: `{"decision": "...", "confidence_score": ..., "explanation": "...", "alternatives": [...]}`
  - Graceful fallback to rule-based mode via `_get_fallback_json_response()` if API fails or unavailable
  - Low temperature (0.5) ensures deterministic, rule-compliant responses

### Configuration
- **`.env` file**: Contains `OPENAI_API_KEY`, `SECRET_KEY` (Flask); generated from `.env.example`
- **`requirements.txt`**: Flask, OpenAI client, Pydantic, pytest, python-dotenv

### Database (Planned)
- Currently uses in-memory user storage (see `web_app.py` line ~20: `users = {}`)
- Future: Replace with persistent storage (PostgreSQL, MongoDB)

## Key Files to Know

- **Entry points**: `run_web.py` (Flask), `src/__main__.py` (FastAPI prototype)
- **Decision logic**: `src/decision_engine.py` (orchestrator), `src/rule_engine.py` (rules)
- **Web interface**: `src/web_app.py` (Flask routes), `templates/` (HTML)
- **Tests**: `tests/test_decision_engine.py` (orchestration), `tests/test_rule_engine.py` (rules)
- **Docs**: `docs/IMPLEMENTATION_SUMMARY.md` (phase breakdown), `README.md` (quick start)

## When Adding Features

1. **Preserve the pipeline**: Never bypass validation or rule engine
2. **Add tests first**: Use TDD; tests validate the new feature before implementation
3. **Update error messages**: Ensure clarity for end users
4. **Check hard stops**: New rules should respect the hard-stop framework (negative disposable, cost > income)
5. **Maintain non-advisory tone**: Avoid phrases like "you should" or "we recommend"; use "Consider..." or "High risk detected"

## Non-Advisory Guardrails (Critical)

All AI-generated text must:
- Avoid "should", "must", "will" (prescriptive language)
- Never suggest specific investments or financial products
- Frame outputs as "decision support", not "advice"
- Include disclaimers: "This is not financial advice"

**File with guardrails**: `src/ai_reasoning.py` (system prompt enforces this)

### Agent System Prompt

The AI agent uses a strict deterministic system prompt defined in `src/ai_reasoning.py` (see `SYSTEM_PROMPT` constant). This prompt:
- Enforces the exact budget logic: `disposable_income = income - expenses - savings_goal`
- Requires JSON-only responses with `decision`, `confidence_score`, `explanation`, `alternatives`
- Implements risk thresholds: LOW (≤30%), MEDIUM (30-60%), HIGH (>60%)
- Prevents financial advice, investment recommendations, and loan suggestions
- Handles fallback gracefully when API fails

**Key constraint**: Agents must ALWAYS respond with valid JSON only—no markdown, commentary, or additional text.
