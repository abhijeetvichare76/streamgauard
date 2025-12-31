"""Policy engine for StreamGuard fraud detection.

This module provides a rule-based policy engine that can be tested independently
and configured without modifying agent code.
"""
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from config.models import InvestigationReport, JudgmentDecision, Decision


class PolicyPriority(int, Enum):
    """Policy priorities (lower number = higher priority)."""
    CRITICAL_FRAUD = 1
    REPEAT_OFFENDERS = 2
    FIRST_TIME = 3
    NEW_ACCOUNT = 4
    VIP_PROTECTION = 5
    LOW_RISK = 6


@dataclass
class PolicyRule:
    """A single policy rule definition."""
    priority: PolicyPriority
    name: str
    condition: Callable[[InvestigationReport], bool]
    decision: Decision
    human_override_allowed: bool
    confidence_range: tuple[int, int]  # (min, max)
    action_required_template: str

    def matches(self, investigation: InvestigationReport) -> bool:
        """Check if this policy's conditions are met."""
        try:
            return self.condition(investigation)
        except Exception as e:
            print(f"Policy {self.name} condition check failed: {e}")
            return False

    def generate_reasoning(self, investigation: InvestigationReport) -> str:
        """Generate reasoning text for this policy application."""
        if self.priority == PolicyPriority.CRITICAL_FRAUD:
            if investigation.security_flags.get('active_voice_call'):
                return "Active voice call detected during transaction triggers Policy 1 CRITICAL FRAUD. This overrides all other considerations."
            else:
                return f"Transaction risk level is CRITICAL ({investigation.risk_score}/100), triggering Policy 1 CRITICAL FRAUD."

        elif self.priority == PolicyPriority.REPEAT_OFFENDERS:
            count = investigation.user_profile.previous_violations
            return f"User has {count} previous violation(s), triggering Policy 2 REPEAT OFFENDERS. Pattern of fraudulent behavior requires immediate blocking."

        elif self.priority == PolicyPriority.FIRST_TIME:
            return f"First-time offender with clean record and no critical fraud signals triggers Policy 3 FIRST-TIME CLEAN. Transaction approved with enhanced monitoring (amount: ${investigation.risk_score * 50:.2f} est.)."

        elif self.priority == PolicyPriority.NEW_ACCOUNT:
            age = investigation.beneficiary_analysis.account_age_hours
            return f"Beneficiary account created {age:.1f} hours ago (< 24 hours) triggers Policy 4 NEW ACCOUNT requiring human review."

        elif self.priority == PolicyPriority.VIP_PROTECTION:
            tenure = investigation.user_profile.account_tenure_days
            years = tenure / 365.25
            return f"User has tenure > 5 years ({years:.1f} years) triggering Policy 5 VIP PROTECTION. Escalating instead of blocking due to long-standing relationship."

        elif self.priority == PolicyPriority.LOW_RISK:
            return f"Transaction shows {investigation.risk_level.value} risk level ({investigation.risk_score}/100) with no critical fraud indicators. Policy 6 LOW RISK approves transaction for normal processing."

        return f"Policy {self.priority} ({self.name}) applied."

    def generate_action_required(self, investigation: InvestigationReport) -> str:
        """Generate action required text for this policy."""
        return self.action_required_template.format(
            transaction_id=investigation.transaction_id,
            user_id=investigation.user_profile.user_id,
            risk_score=investigation.risk_score
        )


# Policy Condition Functions

def _is_critical_fraud(investigation: InvestigationReport) -> bool:
    """Policy 1: CRITICAL FRAUD - Active call OR CRITICAL risk level."""
    return (
        investigation.security_flags.get('active_voice_call', False) or
        investigation.risk_level.value == "CRITICAL"
    )


def _is_repeat_offender(investigation: InvestigationReport) -> bool:
    """Policy 2: REPEAT OFFENDERS - 1 or more previous violations."""
    return investigation.user_profile.previous_violations >= 1


def _is_first_time_clean(investigation: InvestigationReport) -> bool:
    """Policy 3: FIRST-TIME CLEAN - 0 violations, no critical fraud signals.

    Note: All transactions reaching this point are already > $1000 (filtered by Flink).
    This policy gives first-time offenders benefit of the doubt for amounts between
    $1000-$5000 if they have clean records and no other red flags.

    Only applies if:
    - No previous violations
    - NOT a new account (Policy 4 handles that)
    - NOT a VIP customer (Policy 5 handles that)
    - NOT critical fraud (Policy 1 handles that)
    """
    # Exclude cases handled by higher-priority policies
    is_new_account_case = _is_new_account(investigation)
    is_vip_case = _is_vip_customer(investigation)

    return (
        investigation.user_profile.previous_violations == 0 and
        not is_new_account_case and
        not is_vip_case
    )


def _is_new_account(investigation: InvestigationReport) -> bool:
    """Policy 4: NEW ACCOUNT - Beneficiary account < 24 hours old."""
    age_hours = investigation.beneficiary_analysis.account_age_hours
    return age_hours is not None and age_hours < 24


def _is_vip_customer(investigation: InvestigationReport) -> bool:
    """Policy 5: VIP PROTECTION - Tenure > 5 years (1825 days)."""
    tenure = investigation.user_profile.account_tenure_days
    return tenure is not None and tenure > 1825


def _is_low_risk(investigation: InvestigationReport) -> bool:
    """Policy 6: LOW RISK - Catch-all for genuinely safe transactions.

    This policy approves transactions that don't trigger any higher-priority
    policies and have LOW or MEDIUM risk levels.
    """
    # If none of the stricter policies matched, approve LOW/MEDIUM risk
    return investigation.risk_level.value in ["LOW", "MEDIUM"]


# Policy Definitions

POLICIES = [
    PolicyRule(
        priority=PolicyPriority.CRITICAL_FRAUD,
        name="Critical Fraud Detection",
        condition=_is_critical_fraud,
        decision=Decision.BLOCK,
        human_override_allowed=False,
        confidence_range=(95, 100),
        action_required_template="Immediately block transaction and notify fraud team for investigation",
    ),
    PolicyRule(
        priority=PolicyPriority.REPEAT_OFFENDERS,
        name="Repeat Offender Blocking",
        condition=_is_repeat_offender,
        decision=Decision.BLOCK,
        human_override_allowed=True,
        confidence_range=(90, 95),
        action_required_template="Block transaction and flag account for closure review",
    ),
    PolicyRule(
        priority=PolicyPriority.FIRST_TIME,
        name="First-Time Clean Record",
        condition=_is_first_time_clean,
        decision=Decision.SAFE,
        human_override_allowed=True,
        confidence_range=(70, 85),
        action_required_template="Allow transaction to proceed with enhanced monitoring",
    ),
    PolicyRule(
        priority=PolicyPriority.NEW_ACCOUNT,
        name="New Account Escalation",
        condition=_is_new_account,
        decision=Decision.ESCALATE_TO_HUMAN,
        human_override_allowed=True,
        confidence_range=(60, 75),
        action_required_template="Escalate to fraud analyst for verification of beneficiary legitimacy",
    ),
    PolicyRule(
        priority=PolicyPriority.VIP_PROTECTION,
        name="VIP Customer Protection",
        condition=_is_vip_customer,
        decision=Decision.ESCALATE_TO_HUMAN,
        human_override_allowed=True,
        confidence_range=(50, 70),
        action_required_template="Contact VIP customer via verified phone number to confirm transaction intent",
    ),
    PolicyRule(
        priority=PolicyPriority.LOW_RISK,
        name="Low Risk Approval",
        condition=_is_low_risk,
        decision=Decision.SAFE,
        human_override_allowed=False,
        confidence_range=(80, 95),
        action_required_template="Transaction approved - proceed with normal processing",
    ),
]


class PolicyEngine:
    """Rule-based policy engine for fraud detection decisions."""

    def __init__(self, policies: list[PolicyRule] = None):
        """Initialize policy engine with optional custom policies.

        Args:
            policies: List of PolicyRule objects (defaults to POLICIES)
        """
        self.policies = policies or POLICIES
        # Sort by priority (lower number = higher priority)
        self.policies.sort(key=lambda p: p.priority.value)

    def evaluate(self, investigation: InvestigationReport) -> Optional[PolicyRule]:
        """Evaluate investigation against policies and return first matching policy.

        Args:
            investigation: The investigation report to evaluate

        Returns:
            The first matching PolicyRule, or None if no policies match
        """
        for policy in self.policies:
            if policy.matches(investigation):
                return policy
        return None

    def make_decision(self, investigation: InvestigationReport) -> JudgmentDecision:
        """Make a decision based on policy evaluation.

        Args:
            investigation: The investigation report to evaluate

        Returns:
            A JudgmentDecision object

        Raises:
            ValueError: If no policies match (shouldn't happen with current policy set)
        """
        matched_policy = self.evaluate(investigation)

        if not matched_policy:
            # Fallback (should never happen with Policy 6 LOW_RISK as catch-all)
            # Default to SAFE with manual review flag if somehow no policies matched
            return JudgmentDecision(
                decision=Decision.SAFE,
                policy_applied=6,
                reasoning="No specific policy matched (unexpected) - defaulting to SAFE with manual review recommendation",
                action_required="Flag for manual review to ensure policy coverage is complete",
                human_override_allowed=True,
                confidence=50,
                transaction_id=investigation.transaction_id,
                risk_score=investigation.risk_score
            )

        # Calculate confidence within the policy's range
        min_conf, max_conf = matched_policy.confidence_range
        # Higher risk score = higher confidence
        confidence = min_conf + int((investigation.risk_score / 100) * (max_conf - min_conf))
        confidence = max(min_conf, min(max_conf, confidence))  # Clamp to range

        return JudgmentDecision(
            decision=matched_policy.decision,
            policy_applied=matched_policy.priority.value,
            reasoning=matched_policy.generate_reasoning(investigation),
            action_required=matched_policy.generate_action_required(investigation),
            human_override_allowed=matched_policy.human_override_allowed,
            confidence=confidence,
            transaction_id=investigation.transaction_id,
            risk_score=investigation.risk_score
        )

    def add_policy(self, policy: PolicyRule) -> None:
        """Add a new policy to the engine.

        Args:
            policy: The PolicyRule to add
        """
        self.policies.append(policy)
        self.policies.sort(key=lambda p: p.priority.value)

    def remove_policy(self, priority: PolicyPriority) -> bool:
        """Remove a policy by priority.

        Args:
            priority: The priority of the policy to remove

        Returns:
            True if policy was removed, False if not found
        """
        original_len = len(self.policies)
        self.policies = [p for p in self.policies if p.priority != priority]
        return len(self.policies) < original_len


# Singleton instance
_policy_engine = None

def get_policy_engine() -> PolicyEngine:
    """Get the singleton policy engine instance."""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine
