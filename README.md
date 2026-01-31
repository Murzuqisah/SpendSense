# SpendSense: Intelligent Personal Budgeting Decision Agent

> A non-advisory financial decision-support system that helps individuals evaluate purchase decisions using rule-based logic, confidence scoring, and AI-powered reasoning.

## Problem Statement

Many people struggle with purchasing decisions because they lack clear frameworks for evaluating affordability. SpendSense bridges this gap by providing a structured, transparent decision-support system that explains the financial reasoning behind recommendations without crossing into financial advice.

## Sustainable Development Goal Alignment

SpendSense advances three core UN Sustainable Development Goals:

- **SDG 1: No Poverty** - Helps low-income individuals make informed spending decisions
- **SDG 8: Decent Work and Economic Growth** - Empowers personal financial management
- **SDG 10: Reduced Inequalities** - Provides equitable access to financial decision-support

## Features

- **Multi-Item Purchase Evaluation** - Analyze single or multiple items in one evaluation
- **Rule-Based Risk Assessment** - Transparent LOW/MEDIUM/HIGH risk classification
- **AI-Powered Insights** - Structured analysis with OpenAI integration
- **User Authentication** - Secure login and registration system
- **Responsive Design** - Modern UI with earthy color palette
- **Real-Time Validation** - Instant feedback on form inputs
- **Alternative Suggestions** - AI-generated alternatives for each purchase

## Architecture

```txt
User Input → Validation → Rule Engine → Confidence Scorer → AI Reasoning → Decision Report
```

### Risk Assessment Framework

| Risk Level | Disposable % | Recommendation |
|------------|--------------|----------------|
| LOW     | ≤30%         | Can proceed safely |
| MEDIUM  | 30-60%       | Consider alternatives |
| HIGH    | >60%         | Evaluate carefully |
| STOP    | Any          | Cannot recommend |

## Technical Stack

- **Backend**: Python 3.13, Flask 3.0
- **AI/LLM**: OpenAI API (gpt-4o-mini) with structured outputs
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Authentication**: Werkzeug password hashing
- **Validation**: Pydantic models

## Installation

### Prerequisites

- Python 3.13+
- OpenAI API key

### Setup

```bash
# Clone repository
git clone https://github.com/Murzuqisah/SpendSense.git
cd SpendSense

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage

### Quick Start

```bash
# Using the start script
./start.sh

# Or manually
source .venv/bin/activate
export $(cat .env | xargs)
python run_web.py
```

Then visit: <http://127.0.0.1:5000>

### First Time Use

1. **Register** - Create an account with username and password
2. **Dashboard** - View your financial decision companion
3. **New Evaluation** - Enter financial details and items to purchase
4. **Add Items** - Click "Add Another Item" for multiple purchases
5. **Analyze** - Get instant risk assessment and AI insights
6. **Review** - See alternatives and recommendations

## Example Usage

**Scenario:**

- Monthly Income: KSH 50,000
- Fixed Expenses: KSH 15,000
- Savings Goal: KSH 5,000
- Items: Laptop (KSH 12,000)

**Result:**

- Disposable Income: KSH 30,000
- Risk Level: LOW (40% of disposable)
- Confidence: 40%
- AI provides structured analysis with alternatives

## Non-Advisory Guardrails

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

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_decision_engine.py -v


# Run Dockerfile

docker build -t spendsense .
docker run -p 5000:5000 --env-file .env spendsense
```

## Project Structure

```txt
SpendSense/
├── src/
│   ├── ai_reasoning.py      # OpenAI integration with structured outputs
│   ├── decision_engine.py   # Main orchestration logic
│   ├── rule_engine.py       # Deterministic financial rules
│   ├── scoring.py           # Confidence scoring
│   ├── validation.py        # Input validation
│   └── web_app.py          # Flask application
├── templates/               # HTML templates
│   ├── base.html
│   ├── landing.html
│   ├── dashboard.html
│   ├── index.html          # Evaluation form
│   ├── results.html        # Decision report
│   └── login.html
├── static/
│   └── style.css           # Styling with earthy palette
├── tests/                  # Test suite
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── run_web.py            # Application entry point
```

## UI Features

- **Earthy Color Palette**: Olive leaf, black forest, cornsilk, sunlit clay, copperwood
- **Dynamic Forms**: Add/remove multiple purchase items
- **Real-Time Validation**: Visual feedback (green/red borders)
- **Loading States**: Progress indicators during analysis
- **Responsive Design**: Mobile-friendly layout
- **Structured Results**: Clear risk analysis, considerations, and alternatives

## Security & Privacy

- Password hashing with Werkzeug
- Session-based authentication
- No persistent financial data storage
- Environment-based API key management
- Input validation and sanitization

## Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DEBUG=True
PORT=5000
```

## Future Roadmap

- [ ] Budget tracking over time
- [ ] Multi-goal optimization
- [ ] Category spending analysis
- [ ] Export reports to PDF
- [ ] Mobile app
- [ ] Database integration for history
- [ ] Multi-currency support

## Contributing

Contributions welcome! Areas of interest:

- Improved alternative suggestions
- Additional risk assessment factors
- UI/UX improvements
- Test coverage expansion

## License

MIT License

## Acknowledgments

- UN Sustainable Development Goals
- OpenAI API
- Flask Framework
- Pydantic

---

**SpendSense**: Making financial decisions transparent, accessible, and empowering.

*"Not a financial advisor. Just clearer thinking about your money."*
