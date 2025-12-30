# StreamGuard Playground

Interactive fraud scenario testing interface for the StreamGuard Aegis demo.

## Features

- **4 Preset Scenarios**: Classic Coaching, Velocity Attack, Mule Network, VIP Edge Case
- **Real AI Agents**: Uses actual Vertex AI Gemini for Detective and Judge reasoning (when credentials available)
- **BigQuery Integration**: Inserts test data into real BigQuery tables
- **Simulated Confluent**: Shows infrastructure that would be created without API calls
- **Single-Page Layout**: Everything visible at once, no wizard navigation

## File Structure

```
playground/
├── __init__.py                  # Module initialization
├── presets.py                   # 4 fraud scenario definitions
├── bigquery_operations.py       # INSERT into BigQuery tables
├── investigator.py              # Wrap Detective+Judge with callbacks
├── simulated_enforcer.py        # Fake Confluent actions
└── components.py                # UI components (cards, logs, etc.)
```

## How It Works

### 1. User Flow

```
Select Preset → Customize Fields → Click "Run Investigation" → Watch Live Results
```

### 2. Data Flow

```
Form Inputs → BigQuery INSERT → Detective Agent → Judge Agent → Enforcer Simulation
```

### 3. Backend Processing

**Phase 1: Data Insertion**
- Inserts customer profile to `customer_profiles` table
- Inserts beneficiary to `beneficiary_graph` table
- Inserts session context to `mobile_banking_sessions` table

**Phase 2: Investigation (Real AI)**
- Detective queries BigQuery using tools
- Gemini analyzes context and builds risk assessment
- Judge applies policy rules and makes decision

**Phase 3: Enforcement (Simulated)**
- Shows Kafka topics that would be created
- Shows Flink routing that would be deployed
- Shows BigQuery connectors that would be configured
- All visual only - no real API calls to Confluent

## Preset Scenarios

### Classic Coaching
- **Signal**: Active voice call during transaction
- **User**: Elderly, 10-year tenure
- **Beneficiary**: Brand new account (2 hours old)
- **Expected**: BLOCK (Policy 1: Voice Call Override)

### Velocity Attack
- **Signal**: Rooted device, extremely fast typing
- **User**: Young adult, tech savvy
- **Beneficiary**: Established account
- **Expected**: HOLD (Policy 3: First-time + Low Amount)

### Mule Network
- **Signal**: Repeat offender
- **Beneficiary**: High-risk, flagged device
- **Expected**: BLOCK (Policy 2: Repeat Offender)

### VIP Edge Case
- **Signal**: Ambiguous risk signals
- **User**: 20-year premium customer
- **Expected**: ESCALATE_TO_HUMAN (Policy 5: VIP Protection)

## Environment Setup

### With Real GCP (Recommended)

1. Set environment variables:
```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_SERVICE_ACCOUNT_KEY="/path/to/key.json"
```

2. Or use Streamlit secrets (for deployment):
```toml
# .streamlit/secrets.toml
GCP_PROJECT_ID = "your-project-id"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
# ... rest of service account JSON
```

### Without GCP (Simulation Mode)

The playground automatically detects missing credentials and falls back to simulation mode:
- BigQuery inserts are simulated with logs
- Agent reasoning uses plausible canned responses based on input signals
- Warning banner displays at top of page

## Code Examples

### Running Investigation

```python
from playground.investigator import PlaygroundInvestigator, SimulatedInvestigator
from playground.bigquery_operations import check_gcp_available

# Check if real mode available
if check_gcp_available():
    investigator = PlaygroundInvestigator(on_event=log_callback)
else:
    investigator = SimulatedInvestigator(on_event=log_callback)

# Run investigation
result = investigator.investigate_sync(transaction_data)
# Returns: {"investigation": "...", "judgment": "..."}
```

### Simulating Enforcement

```python
from playground.simulated_enforcer import simulate_enforcement

enforcement = simulate_enforcement(
    user_id="betty_senior",
    decision="BLOCK",
    on_progress=log_callback
)
# Returns: {"decision": "BLOCK", "resources_created": [...], "actions_taken": [...]}
```

## Deployment

See `../../../MANUAL_DEPLOYMENT.md` for Streamlit Community Cloud deployment instructions.

## Notes

- All BigQuery inserts use the `playground_` prefix to avoid conflicts
- Transaction IDs use format: `pg_tx_YYYYMMDD_HHMMSS_XXXX`
- Session IDs use format: `pg_sess_XXXXXXXX`
- Simulated resources are never actually created in Confluent
