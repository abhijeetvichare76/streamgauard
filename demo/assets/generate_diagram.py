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
    "dpi": "400",  # Balanced resolution for web viewing
    "splines": "polyline",  # Curved edges for better label placement (try "ortho" or "polyline" for alternatives)
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

        # Flow - with cohesive labels using smaller fonts and thicker lines
        tx_topic >> Edge(label="Stream", fontsize="9", penwidth="2.0") >> flink_filter
        flink_filter >> Edge(label="Suspicious Txs", color="red", fontsize="9", penwidth="2.5") >> investigation_topic

    # Layer 2: Agent Intelligence Layer
    with Cluster("Agent Intelligence Layer (Google ADK)"):

        # Detective Agent with tools
        with Cluster("Detective Agent\n(Investigation)", graph_attr={"bgcolor": "#e8f4f8"}):
            detective = Functions("Detective\n+ Few-Shot Examples")

            # Detective's tool outputs (represented as data stores)
            tool1 = Datastore("User History\nTool")
            tool2 = Datastore("Beneficiary Risk\nTool")
            tool3 = Datastore("Session Context\nTool")

            # Parallel tool calls - using xlabel for numbered labels
            detective >> Edge(xlabel="1", style="dotted", color="blue", fontsize="9", penwidth="1.5") >> tool1
            detective >> Edge(xlabel="2", style="dotted", color="blue", fontsize="9", penwidth="1.5") >> tool2
            detective >> Edge(xlabel="3", style="dotted", color="blue", fontsize="9", penwidth="1.5") >> tool3

        # Validation Layer
        with Cluster("Validation & Policy", graph_attr={"bgcolor": "#f8f4e8"}):
            pydantic = React("Pydantic\nValidation")
            policy_engine = React("Policy Engine\n(Rules-Based)")

        # Judge Agent
        with Cluster("Judge Agent\n(Decision)", graph_attr={"bgcolor": "#f8e8f4"}):
            judge = Functions("Judge\n+ Policy Examples")

        # Enforcer Agent
        enforcer = Functions("Enforcer\n(Execution)")

        # Agent Flow with structured communication - cohesive labels
        investigation_topic >> Edge(label="Threat Data", style="bold", fontsize="9", penwidth="2.5") >> detective

        detective >> Edge(label="JSON Output\n(InvestigationReport)", color="green", fontsize="9", penwidth="2.0") >> pydantic
        pydantic >> Edge(label="Validated", color="green", fontsize="9", penwidth="2.0") >> judge

        judge >> Edge(label="JSON Output\n(JudgmentDecision)", color="orange", fontsize="9", penwidth="2.0") >> policy_engine
        policy_engine >> Edge(label="Validated Decision", color="orange", fontsize="9", penwidth="2.0") >> enforcer

    # Layer 3: Data Layer (Google Cloud Platform)
    with Cluster("Google Cloud Platform (Data Layer)"):
        with Cluster("BigQuery (Data Warehouse)"):
            # Context tables for Detective tools
            context_tables = BigQuery("Context Tables\nProfiles | Graph | Sessions")

            # Audit tables for decisions
            audit_tables = BigQuery("Audit Tables\nDecisions | Logs | Metrics")

            # Tool connections to BigQuery - using headlabel for precise positioning
            tool1 >> Edge(headlabel="Query", style="dashed", labeldistance="0.5", labelangle="-30", fontsize="9") >> context_tables
            tool2 >> Edge(headlabel="Query", style="dashed", labeldistance="0.5", labelangle="-30", fontsize="9") >> context_tables
            tool3 >> Edge(headlabel="Query", style="dashed", labeldistance="0.5", labelangle="-30", fontsize="9") >> context_tables

            # Enforcer writes audit logs
            enforcer >> Edge(label="Write Logs", color="gray", fontsize="9", penwidth="1.5") >> audit_tables

    # Layer 4: Enforcement Actions
    with Cluster("Enforcement Actions"):
        quarantine = Kafka("Quarantine Topic\n(Blocked Txs)")
        safe_queue = Kafka("Safe Queue\n(Approved Txs)")
        escalation = Kafka("Escalation Topic\n(Human Review)")

        # Enforcer provisions to different queues based on decision - cohesive labels
        enforcer >> Edge(label="BLOCK", color="red", fontsize="9", penwidth="2.5") >> quarantine
        enforcer >> Edge(label="SAFE", color="green", fontsize="9", penwidth="2.5") >> safe_queue
        enforcer >> Edge(label="ESCALATE", color="purple", fontsize="9", penwidth="2.5") >> escalation

    # Legend - using HTML table with visual arrow examples
    with Cluster("Legend", graph_attr={
        "bgcolor": "#f9f9f9",
        "style": "filled,rounded",
        "margin": "12"
    }):
        # Import Node for creating HTML table legend
        from diagrams import Node as GraphNode

        legend = GraphNode(
            label="""<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="white">
                <TR><TD COLSPAN="2" BGCOLOR="#dddddd"><B>Legend</B></TD></TR>
                <TR><TD COLSPAN="2" BGCOLOR="#eeeeee"><B>Edge Colors</B></TD></TR>
                <TR><TD><FONT COLOR="red">●━━━●</FONT></TD><TD ALIGN="LEFT">Block/Error</TD></TR>
                <TR><TD><FONT COLOR="green">●━━━●</FONT></TD><TD ALIGN="LEFT">Safe/Approved</TD></TR>
                <TR><TD><FONT COLOR="purple">●━━━●</FONT></TD><TD ALIGN="LEFT">Escalate</TD></TR>
                <TR><TD><FONT COLOR="blue">●━━━●</FONT></TD><TD ALIGN="LEFT">Tool Calls</TD></TR>
                <TR><TD><FONT COLOR="gray">●━━━●</FONT></TD><TD ALIGN="LEFT">Audit/Logging</TD></TR>
                <TR><TD COLSPAN="2" BGCOLOR="#eeeeee"><B>Edge Styles</B></TD></TR>
                <TR><TD>●━━━●</TD><TD ALIGN="LEFT">Primary Flow</TD></TR>
                <TR><TD>●┈┈┈●</TD><TD ALIGN="LEFT">Tool/Dotted</TD></TR>
                <TR><TD>●╌╌╌●</TD><TD ALIGN="LEFT">Query/Dashed</TD></TR>
                <TR><TD><B>●━━━●</B></TD><TD ALIGN="LEFT">Input/Bold</TD></TR>
            </TABLE>
            >""",
            shape="plaintext"
        )

print("Diagram generated successfully at demo/assets/aegis_architecture.png")
print("Enhanced with: Structured communication, Policy engine, Tool calls, Validation")
