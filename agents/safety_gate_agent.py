from typing import Dict, Any
from state import CommerceState
from razorpay_client import RazorpayTestClient
from audit_logger import AuditLogger
from config import MAX_ALLOWED_DISCOUNT_PCT, MAX_TRANSACTION_INR

class SafetyGateAgent:
    def __init__(self, razorpay_client: RazorpayTestClient):
        self.rzp_client = razorpay_client
        self.audit_logger = AuditLogger()

    def process(self, state: CommerceState) -> Dict[str, Any]:
        """
        Gates financial rules and executes order creation on Razorpay.
        Includes graceful error recovery if discount policies are violated.
        """
        original_total = state.get("original_total", 0.0)
        proposed_total = state.get("final_total", original_total)
        proposed_discount = state.get("discount_applied_pct", 0.0)
        
        effective_discount = proposed_discount
        effective_total = proposed_total
        fallback_occurred = False
        fallback_reason = ""
        
        # Policy Check 1: Discount Violation Handling (Graceful Fallback)
        if proposed_discount > MAX_ALLOWED_DISCOUNT_PCT:
            fallback_occurred = True
            fallback_reason = (
                f"Proposed discount ({proposed_discount}%) exceeded hard policy limit ({MAX_ALLOWED_DISCOUNT_PCT}%)."
            )
            # Safe Fallback Strategy: Cap discount at maximum policy limit
            effective_discount = MAX_ALLOWED_DISCOUNT_PCT
            effective_total = original_total * (1 - (effective_discount / 100.0))
            
            override_entry = self.audit_logger.log_event(
                agent="Financial_Safety_Gate",
                action="policy_override_discount_capped",
                details={
                    "proposed_discount_pct": proposed_discount,
                    "capped_discount_pct": effective_discount,
                    "original_total": original_total,
                    "adjusted_total": effective_total,
                    "reason": fallback_reason
                },
                status="OVERRIDDEN"
            )
            state_audit = state.get("audit_trail", []) + [override_entry]
        else:
            state_audit = state.get("audit_trail", [])

        # Policy Check 2: Hard Transaction Cap Violation
        if effective_total > MAX_TRANSACTION_INR:
            rejection_entry = self.audit_logger.log_event(
                agent="Financial_Safety_Gate",
                action="gate_reject_transaction",
                details={
                    "effective_total": effective_total,
                    "max_allowed_inr": MAX_TRANSACTION_INR
                },
                status="REJECTED"
            )
            return {
                "gate_passed": False,
                "error_message": f"Transaction of INR {effective_total} exceeds absolute cap of INR {MAX_TRANSACTION_INR}.",
                "audit_trail": state_audit + [rejection_entry]
            }

        # Safe Execution: Create Order via Razorpay Client
        rzp_response = self.rzp_client.create_order(
            amount_in_inr=effective_total,
            receipt=f"rcpt_{int(datetime.datetime.now().timestamp())}",
            notes={
                "applied_discount_pct": str(effective_discount),
                "fallback_triggered": str(fallback_occurred)
            }
        )

        if rzp_response.get("success"):
            exec_entry = self.audit_logger.log_event(
                agent="Financial_Safety_Gate",
                action="create_razorpay_order",
                details={
                    "order_id": rzp_response["order_id"],
                    "charged_amount": effective_total,
                    "discount_applied_pct": effective_discount,
                    "fallback_applied": fallback_occurred,
                    "currency": "INR"
                },
                status="APPROVED"
            )
            return {
                "gate_passed": True,
                "final_total": effective_total,
                "discount_applied_pct": effective_discount,
                "razorpay_order_id": rzp_response["order_id"],
                "order_status": rzp_response["status"],
                "error_message": fallback_reason if fallback_occurred else None,
                "audit_trail": state_audit + [exec_entry]
            }
        else:
            failure_entry = self.audit_logger.log_event(
                agent="Financial_Safety_Gate",
                action="create_razorpay_order",
                details={"error": rzp_response.get("error")},
                status="FAILED"
            )
            return {
                "gate_passed": False,
                "error_message": f"Razorpay API Error: {rzp_response.get('error')}",
                "audit_trail": state_audit + [failure_entry]
            }