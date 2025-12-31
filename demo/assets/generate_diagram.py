import os
# Add Graphviz to PATH for local execution if not present
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

from diagrams import Diagram, Cluster, Edge, Node
from diagrams.onprem.queue import Kafka
from diagrams.onprem.analytics import Flink
from diagrams.gcp.analytics import BigQuery
from diagrams.gcp.compute import Functions
from diagrams.gcp.database import Datastore
from diagrams.programming.framework import React
from diagrams.generic.blank import Blank

# Create a diagram
# show=False prevents opening the file immediately
# graph_attr sets layout direction (Left to Right) and transparency
graph_attr = {
    "rankdir": "LR",
    "bgcolor": "white",
    "dpi": "350",  # Balanced resolution for web viewing
    "splines": "ortho",  # Orthogonal edges for cleaner look
    "nodesep": "0.8",
    "ranksep": "1.2"
}

with Diagram("StreamGuard Aegis Architecture (Enhanced)", show=False, filename="demo/assets/aegis_architecture", graph_attr=graph_attr):

    # Layer 1: Confluent Cloud
    with Cluster("Confluent Cloud (Real-Time Data Layer)"):
        # Kafka Topics
        tx_topic = Kafka("customer_bank_transfers\n(Input Topic)")
        investigation_topic = Kafka("fraud_investigation_queue\n(High Priority)")

        # Flink SQL
        flink_filter = Flink("Flink SQL\nFraud Detector\n(Risk Scoring)")

        # Flow
        tx_topic >> Edge(label="Stream") >> flink_filter
        flink_filter >> Edge(label="Suspicious Txs", color="red") >> investigation_topic

    # Layer 2: Agent Intelligence Layer
    with Cluster("Agent Intelligence Layer (Google ADK)"):

        # Detective Agent with tools
        with Cluster("Detective Agent\n(Investigation)", graph_attr={"bgcolor": "#e8f4f8"}):
            detective = Functions("Detective\n+ Few-Shot Examples")

            # Detective's tool outputs (represented as data stores)
            tool1 = Datastore("User History\nTool")
            tool2 = Datastore("Beneficiary Risk\nTool")
            tool3 = Datastore("Session Context\nTool")

            # Parallel tool calls
            detective >> Edge(label="1", style="dotted", color="blue") >> tool1
            detective >> Edge(label="2", style="dotted", color="blue") >> tool2
            detective >> Edge(label="3", style="dotted", color="blue") >> tool3

        # Validation Layer
        with Cluster("Validation & Policy", graph_attr={"bgcolor": "#f8f4e8"}):
            pydantic = React("Pydantic\nValidation")
            policy_engine = React("Policy Engine\n(Rules-Based)")

        # Judge Agent
        with Cluster("Judge Agent\n(Decision)", graph_attr={"bgcolor": "#f8e8f4"}):
            judge = Functions("Judge\n+ Policy Examples")

        # Enforcer Agent
        enforcer = Functions("Enforcer\n(Execution)")

        # Agent Flow with structured communication
        investigation_topic >> Edge(label="Threat Data", style="bold") >> detective

        detective >> Edge(label="JSON Output\n(InvestigationReport)", color="green") >> pydantic
        pydantic >> Edge(label="Validated", color="green") >> judge

        judge >> Edge(label="JSON Output\n(JudgmentDecision)", color="orange") >> policy_engine
        policy_engine >> Edge(label="Validated Decision", color="orange") >> enforcer

    # Layer 3: Data Layer (Google Cloud Platform)
    with Cluster("Google Cloud Platform (Data Layer)"):
        with Cluster("BigQuery (Data Warehouse)"):
            # Context tables for Detective tools
            context_tables = BigQuery("Context Tables\nProfiles | Graph | Sessions")

            # Audit tables for decisions
            audit_tables = BigQuery("Audit Tables\nDecisions | Logs | Metrics")

            # Tool connections to BigQuery
            tool1 >> Edge(label="Query", style="dashed") >> context_tables
            tool2 >> Edge(label="Query", style="dashed") >> context_tables
            tool3 >> Edge(label="Query", style="dashed") >> context_tables

            # Enforcer writes audit logs
            enforcer >> Edge(label="Write Logs", color="gray") >> audit_tables

    # Layer 4: Enforcement Actions
    with Cluster("Enforcement Actions"):
        quarantine = Kafka("Quarantine Topic\n(Blocked Txs)")
        safe_queue = Kafka("Safe Queue\n(Approved Txs)")
        escalation = Kafka("Escalation Topic\n(Human Review)")

        # Enforcer provisions to different queues based on decision
        enforcer >> Edge(label="BLOCK", color="red") >> quarantine
        enforcer >> Edge(label="SAFE", color="green") >> safe_queue
        enforcer >> Edge(label="ESCALATE", color="purple") >> escalation

    # Legend - compact format
    with Cluster("Legend", graph_attr={
        "bgcolor": "#f0f0f0",
        "style": "filled,rounded",
        "fontsize": "10",
        "labeljust": "l",
        "margin": "10"
    }):
        # Create a single node with all legend info
        from diagrams.generic.blank import Blank
        legend_text = (
            "COLORS:\n"
            "• Red = Block\n"
            "• Green = Safe/Approved\n"
            "• Purple = Escalate\n"
            "• Blue = Tool Calls\n"
            "• Gray = Audit\n\n"
            "STYLES:\n"
            "• Solid = Primary\n"
            "• Dotted = Tools\n"
            "• Dashed = Query\n"
            "• Bold = Input"
        )
        Blank(legend_text)

print("Diagram generated successfully at demo/assets/aegis_architecture.png")
print("Enhanced with: Structured communication, Policy engine, Tool calls, Validation")
