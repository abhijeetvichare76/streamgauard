# 🛡️ StreamGuard - Multi-Agent Fraud Detection System

> Real-time fraud prevention powered by Google Cloud AI and Confluent streaming

**🎯 Live Demo:** [Your Streamlit URL - Replace this with your actual Streamlit deployment URL]
**📹 Demo Video:** [YouTube/Vimeo URL - Add once video is uploaded]

---

## The Problem: $12.5B Fraud Crisis

Meet Betty. She's 75 years old. Last month, a scammer nearly stole her life savings using AI-generated voice cloning technology. The scammer convinced her that her grandson was in trouble and needed $5,000 immediately. Betty recognized the voice - it sounded exactly like him.

All her credentials were legitimate. She logged in from her own phone, sitting at home. She typed the amount herself and clicked "Confirm Transfer." Her bank's traditional fraud system saw nothing wrong. By the time she realized it was a scam, the money would have been gone.

**Authorized Push Payment (APP) fraud** is devastating:
- **$12.5B** in US losses (2024 FTC)
- **80%** of victims on active call with scammer (FCC)
- **77%** success rate for AI voice cloning attacks (McAfee)
- **Traditional systems fail:** All credentials are legitimate, transactions are authorized

---

## The Solution: AI Agent Swarm

StreamGuard uses **3 specialized AI agents** in a sequential pipeline to detect and prevent fraud in real-time:

**Detective Agent** → Investigates using 3 parallel tools (BigQuery)
**Judge Agent** → Applies 6-tier policy engine with explainable reasoning
**Enforcer Agent** → Autonomously creates quarantine infrastructure

**Unique Innovation:** Agents don't just detect fraud - they **create real Kafka topics, Flink SQL routes, and BigQuery connectors** dynamically. This enables infinite scalability without infrastructure bottlenecks.

---

## Architecture

![Architecture Diagram](demo/assets/aegis_architecture.png)

**Technology Stack:**
- **Google Cloud:** Vertex AI (Gemini 2.0 Flash), BigQuery, Service Accounts
- **Confluent Cloud:** Kafka, Flink SQL, Schema Registry, Managed Connectors
- **Agent Framework:** Google ADK with structured Pydantic communication
- **Infrastructure:** Terraform (10+ managed resources)
- **Demo:** Streamlit with dual-mode (Tutorial + Playground)

---

## Features

### 1. Multi-Agent Orchestration
- **Detective:** Parallel context gathering (user history, beneficiary risk analysis, session telemetry)
- **Judge:** Policy-based decisions with explainable reasoning (6-tier priority system)
- **Enforcer:** Real-time infrastructure provisioning (Kafka topics, Flink statements, BigQuery connectors)
- **Router:** Orchestrates sequential pipeline with async/await patterns
- **Liaison:** Human-facing chat interface for security analysts

### 2. Real-Time Stream Processing
- Kafka topics for transaction ingestion (`customer_bank_transfers`, `fraud_investigation_queue`)
- Flink SQL for fraud filtering (amount > $1000 triggers investigation)
- Sub-7-second end-to-end latency from detection to quarantine
- Avro schemas enforce type safety (11 registered schemas)

### 3. Structured Communication
- Pydantic models for type-safe agent messaging (`InvestigationReport`, `JudgmentDecision`)
- JSON validation with correction hints to prevent LLM hallucinations
- Policy engine comparison validates LLM decisions against deterministic rules

### 4. Production-Grade Patterns
- Error handling with exponential backoff retry logic
- Graceful degradation (fallback to BLOCK on errors - better false positive than fraud)
- Resource cleanup automation to prevent quota exhaustion
- Infrastructure as Code (Terraform) for reproducible deployments

### 5. Interactive Demo
- **Tutorial Mode:** Story-driven walkthrough of Betty's fraud scenario (7 steps)
- **Playground Mode:** Interactive testing with 4 preset fraud scenarios + custom input
- Real AI integration (Vertex AI Gemini 2.0 Flash) with simulation fallback
- Live streaming logs showing agent tool calls and reasoning

---

## Quick Start

### Prerequisites
- GCP account with Vertex AI enabled
- Confluent Cloud account
- Python 3.9+

### Setup (5 commands)
```bash
# 1. Clone repository
git clone https://github.com/[your-username]/ai-partner-catalyst.git
cd ai-partner-catalyst

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp terraform/.env.example terraform/.env
# Edit terraform/.env with your GCP and Confluent credentials

# 4. Deploy infrastructure
cd terraform && terraform init && terraform apply -auto-approve

# 5. Run agent swarm
cd .. && python scripts/run_adk_swarm.py
```

### Try the Demo
```bash
# Option 1: Local Streamlit
streamlit run demo/app.py

# Option 2: Live deployment
# Visit the live demo link above
```

---

## Data Sources (Synthetically generated)

### Confluent Cloud (Partner Platform)
- **Real-time streams:** Customer bank transfers, mobile app events
- **Processing:** Flink SQL for filtering and enrichment
- **Storage:** Kafka topics with Avro schemas for type safety
- **Connectors:** BigQuery Sink for automated table creation with schema evolution

### Google Cloud
- **BigQuery Tables:**
  - `customer_profiles`: Demographics, behavioral segments, account tenure
  - `beneficiary_graph`: Account relationships, risk scores
  - `mobile_banking_sessions`: Real-time session telemetry (typing cadence, active calls, device flags)
- **Vertex AI:** Gemini 2.0 Flash for all agent reasoning and decision-making

### Synthetic Data (For Demo)
- Banking transaction scenarios (Betty's Story, VIP cases, velocity attacks, mule networks)
- Mobile app telemetry (typing cadence, active calls, device flags)
- Seeded via `scripts/seed_*.py` utilities

**Note:** Production deployment would ingest real banking transaction streams. Synthetic data demonstrates capabilities without requiring actual financial data in the demo.

---

## Key Findings & Learnings

### Technical Discoveries

1. **Flink metadata propagation delay:** Newly created topics are invisible to Flink for ~30 seconds. Solution: Enforcer agent implements automatic 30-second delay after topic creation.

2. **Windows compatibility:** PowerShell encoding issues with Terraform JSON output required special handling. Solution: UTF-8 BOM detection and normalization.

3. **ADK session management:** `InMemorySessionService` prevents cross-agent pollution by isolating conversation contexts.

4. **Pydantic validation impact:** Structured output models reduced LLM parsing failures from 30%+ to <5%.

### Architectural Decisions

1. **Why multi-agent vs single LLM:** Specialization improves accuracy, enables parallel tool calls within Detective
2. **Why Pydantic over raw JSON:** Type safety catches schema drift before production
3. **Why hybrid AI+Rules:** LLM flexibility + rule-based auditability for compliance
4. **Why dynamic infrastructure:** Scales better than static quarantine queues

### Challenges Overcome

- **Problem:** LLM occasionally skips required tool calls
  **Solution:** Few-shot examples (3 for Detective, 6 for Judge) + validation layer with retry logic

- **Problem:** Policy mismatches between LLM and deterministic rules
  **Solution:** Policy engine comparison with warnings (not hard blocks) to allow LLM reasoning flexibility

- **Problem:** Credential management duplicated across multiple agent files
  **Solution:** Centralized `config/gcp_credentials.py` with automatic temp file cleanup via `atexit`

### Future Enhancements
- **Phase 2:** Multi-model consensus (Gemini Reasoning + Flash for different agents)
- **Phase 3:** Federated learning for edge device pre-filtering
- **Phase 4:** Self-healing policies that adapt to new attack patterns
- **Production Integration:** Connect to actual banking core systems and transaction feeds


---

## Testing

### Unit Tests
```bash
pytest tests/test_policy_engine.py -v
```

### Integration Test
```bash
# Simulate fraud alert
python scripts/simulate_flink_threat_alerts.py

# Monitor agent swarm
python scripts/run_adk_swarm.py
```

### Cleanup Test Resources
```bash
# Remove test topics, Flink statements, and BigQuery tables
python scripts/cleanup_test_resources.py
```

---

## License

MIT License - See [LICENSE](LICENSE) file

---

## Acknowledgments

Built for the **Google Cloud x Confluent AI Hackathon 2025**

**Technologies:**
- Google Cloud (Vertex AI, BigQuery, Service Accounts)
- Confluent Cloud (Kafka, Flink SQL, Schema Registry, Managed Connectors)
- Google ADK (Agent Development Kit)
- Streamlit (Interactive demo interface)

**Inspiration:**
This project was inspired by the $12.5B+ APP fraud crisis affecting elderly victims. Our goal is to show that AI agents can protect vulnerable populations in real-time through intelligent, autonomous infrastructure.

---

## Contact

[Abhijeet Vichare](https://github.com/abhijeetvichare)

