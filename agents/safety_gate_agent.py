import datetime
from typing import Dict, Any
from state import CommerceState
from razorpay_client import RazorpayTestClient
from config import MAX_ALLOWED_DISCOUNT_PCT, MAX_TRANSACTION_INR

class SafetyGateAgent:
    def __init__(self, razorpay_client: RazorpayTestClient):
        self.rzp_client = razorpay_client

    def process(self, state: CommerceState) -> Dict[str, Any]:
        """Gates transaction rules and executes order creation on Razorpay."""
        final_total = state.get("final_total", 0.0)
        discount_pct = state.get("discount_applied_pct", 0.0)
        
        # Check Policy Rule 1: Discount Cap
        if discount_pct > MAX_ALLOWED_DISCOUNT_PCT:
            audit_log = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "agent": "Financial_Safety_Gate",
                "action": "gate_check_discount",
                "details": {"discount_pct": discount_pct, "max_allowed": MAX_ALLOWED_DISCOUNT_PCT},
                "status": "REJECTED"
            }
            return {
                "gate_passed": False,
                "error_message": f"Discount of {discount_pct}% exceeds allowed policy limit of {MAX_ALLOWED_DISCOUNT_PCT}%.",
                "audit_trail": state.get("audit_trail", []) + [audit_log]
            }
        
        # Check Policy Rule 2: Transaction Upper Cap
        if final_total > MAX_TRANSACTION_INR:
            audit_log = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "agent": "Financial_Safety_Gate",
                "action": "gate_check_amount",
                "details": {"amount_inr": final_total, "max_allowed": MAX_TRANSACTION_INR},
                "status": "REJECTED"
            }
            return {
                "gate_passed": False,
                "error_message": f"Total amount INR {final_total} exceeds maximum transaction limit of INR {MAX_TRANSACTION_INR}.",
                "audit_trail": state.get("audit_trail", []) + [audit_log]
            }
        
        # Execute Money Action
        rzp_response = self.rzp_client.create_order(
            amount_in_inr=final_total,
            receipt=f"rcpt_{int(datetime.datetime.now().timestamp())}",
            notes={"discount_pct": str(discount_pct)}
        )
        
        if rzp_response.get("success"):
            audit_log = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "agent": "Financial_Safety_Gate",
                "action": "create_razorpay_order",
                "details": {
                    "order_id": rzp_response["order_id"],
                    "amount": final_total,
                    "currency": "INR"
                },
                "status": "APPROVED"
            }
            return {
                "gate_passed": True,
                "razorpay_order_id": rzp_response["order_id"],
                "order_status": rzp_response["status"],
                "audit_trail": state.get("audit_trail", []) + [audit_log]
            }
        else:
            audit_log = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "agent": "Financial_Safety_Gate",
                "action": "create_razorpay_order",
                "details": {"error": rzp_response.get("error")},
                "status": "FAILED"
            }
            return {
                "gate_passed": False,
                "error_message": f"Razorpay API Error: {rzp_response.get('error')}",
                "audit_trail": state.get("audit_trail", []) + [audit_log]
            }