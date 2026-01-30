# SpendSense: Intelligent Personal Budgeting Decision Agent

> A non-advisory financial decision-support system that helps individuals evaluate purchase decisions using rule-based logic, confidence scoring, and AI-powered reasoning.

## 🎯 Problem Statement

Many people struggle with purchasing decisions because they lack clear frameworks for evaluating affordability. They may ask:

- "Can I afford this?"
- "Is this a risky purchase?"
- "What are my alternatives?"

Current solutions are either too simplistic (simple yes/no) or overly complex (requiring financial expertise). **SpendSense** bridges this gap by providing a **structured, transparent decision-support system** that explains the financial reasoning behind recommendations without crossing into financial advice.

## 🌍 Sustainable Development Goal Alignment

SpendSense advances **three core UN Sustainable Development Goals**:

### SDG 1: No Poverty

- Helps low-income individuals make informed spending decisions
- Prevents unnecessary debt accumulation
- Promotes financial awareness and control

### SDG 8: Decent Work and Economic Growth

- Empowers personal financial management
- Reduces financial stress that impacts workplace productivity
- Contributes to economic stability through responsible consumption

### SDG 10: Reduced Inequalities

- Provides equitable access to financial decision-support (no paywall required)
- Works without specialized financial knowledge
- Transparent algorithms ensure no discriminatory decision-making

## 🏗️ Architecture Overview

SpendSense implements a **five-layer decision pipeline**:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                               │
│  (Income, Expenses, Savings, Item, Cost)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  1️⃣  INPUT VALIDATION LAYER                                │
│  - Type checking, range validation                          │
│  - Numerical consistency verification                       │
│  - Early error detection                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2️⃣  RULE ENGINE (Deterministic)                           │
│  - Calculate disposable income                              │
│  - Check hard stops (unaffordable, exceeds income)         │
│  - Assess risk level (Low/Medium/High)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3️⃣  CONFIDENCE SCORER                                     │
│  - Calculate confidence score (0.0 - 1.0)                  │
│  - Map to risk level percentages                           │
│  - Percentage of disposable income                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4️⃣  AI REASONING LAYER (Claude)                           │
│  - Generate personalized explanations                       │
│  - Suggest alternatives                                     │
│  - Enforce non-advisory guardrails                          │
│  - Fallback to rule-based explanations if API fails        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5️⃣  DECISION ENGINE (Orchestration)                       │
│  - Coordinate all components                                │
│  - Generate final report                                    │
│  - Format JSON output                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   JSON REPORT                               │
│  (Status, Financial Analysis, Risk Assessment,             │
│   AI Reasoning, Final Decision)                            │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. **Input Validation Layer** (`src/validation.py`)

Ensures all inputs are valid before processing.

**Test Coverage**: 40 tests

#### 2. **Rule Engine** (`src/rule_engine.py`)

Implements deterministic, explainable financial rules:

- Disposable Income = Monthly Income - Fixed Expenses - Savings Goal
- Risk Levels: LOW (≤30%), MEDIUM (30-60%), HIGH (>60%)
- Hard Stops: Insufficient disposable income or purchase ≥ income

**Test Coverage**: 34 tests

#### 3. **Confidence Scorer** (`src/scoring.py`)

Quantifies purchase feasibility with confidence scores (0.0-1.0)

**Test Coverage**: 39 tests

#### 4. **AI Reasoning Layer** (`src/ai_reasoning.py`)

Generates human-readable explanations via Claude API with fallback mode

**Test Coverage**: 28 tests

#### 5. **Decision Engine** (`src/decision_engine.py`)

Orchestrates all components into professional reports

**Test Coverage**: 20 tests

## 📊 Risk Assessment Framework

| Risk Level | Disposable % | Recommendation |
|------------|--------------|-----------------|
| 🟢 LOW | ≤30% | Can proceed safely |
| 🟡 MEDIUM | 30-60% | Consider alternatives |
| 🔴 HIGH | >60% | Evaluate carefully |
| ⛔ HARD STOP | Any | Cannot recommend |

## 🔧 Technical Stack

- **Language**: Python 3.13
- **AI/LLM**: Claude API (Anthropic SDK)
- **Testing**: pytest (178 tests, 100% passing)
- **Data Validation**: Pydantic
- **HTTP Framework**: FastAPI

## 📦 Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: Set API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## 🚀 Usage

### Interactive Mode

```bash
python -m src.cli
```

### Quick Evaluation

```bash
python -m src.cli --quick \
  --income 5000 \
  --expenses 1500 \
  --savings 500 \
  --item "Laptop" \
  --cost 1200
```

### JSON Mode

```bash
python -m src.cli --json input.json > output.json
```

## 🛡️ Non-Advisory Guardrails

**SpendSense does NOT provide:**

- Financial advice (buy/don't buy recommendations)
- Investment guidance
- Tax or credit advice

**SpendSense DOES provide:**

- Rule-based affordability analysis
- Transparent confidence scoring
- Risk assessment frameworks
- Alternative suggestions

> This is not financial advice. SpendSense provides decision support only.

## 🧪 Testing & Verification

```bash
# All tests
python -m pytest tests/ -v

# Specific component
python -m pytest tests/test_validation.py -v
```

### Test Coverage

- **178 total tests**, 100% passing
- Input Validation: 40 tests
- Rule Engine: 34 tests
- Confidence Scoring: 39 tests
- AI Reasoning: 28 tests
- Decision Engine: 20 tests
- CLI Interface: 17 tests

## 💡 Key Design Decisions

### 1. Rule-Based + AI Enhancement

- ✅ Explainable and reproducible
- ❌ Less personalized than pure AI

### 2. Hard Stops (Auto-Rejection)

- ✅ Prevents impossible recommendations
- ❌ Less flexible for edge cases

### 3. Disposable Income Model

- ✅ Simple and transparent
- ❌ Ignores debt and irregular expenses

### 4. No Financial Advice

- ✅ Avoids regulatory issues
- ❌ Less immediately actionable

## 🔐 Data Privacy & Security

- No data storage (in-memory only)
- No data transmission unless API key provided
- Open source (fully transparent)
- No tracking or analytics

## 📈 Future Roadmap

1. Budget tracking over time
2. Multi-goal optimization
3. Category spending analysis
4. Savings optimization
5. REST API layer
6. Mobile app
7. Privacy-preserving ML patterns

## 🤝 Contributing

Contributions welcome! Areas of interest:

- Improved alternative suggestions
- Additional risk assessment factors
- Better fallback explanations
- UI/UX improvements

## 📝 License

MIT License

## 🙏 Acknowledgments

- UN Sustainable Development Goals
- Anthropic Claude
- Pydantic
- Pytest

---

**SpendSense**: Making financial decisions transparent, accessible, and empowering.

*"Not a financial advisor. Just clearer thinking about your money."*
