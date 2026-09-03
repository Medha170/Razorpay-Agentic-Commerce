import os
import razorpay
from typing import Dict, Any, Optional

class RazorpayTestClient:
    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        # Fallback to environment variables if not passed
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID", "rzp_test_mock_key")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET", "rzp_test_mock_secret")
        
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def create_order(self, amount_in_inr: float, currency: str = "INR", receipt: str = "rcpt_001", notes: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Creates a Razorpay Order.
        Note: Razorpay API expects amount in sub-units (paise for INR).
        """
        amount_in_paise = int(amount_in_inr * 100)
        
        payload = {
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": receipt,
            "notes": notes or {"created_by": "AgenticCommerceEngine"}
        }
        
        try:
            order = self.client.order.create(data=payload)
            return {
                "success": True,
                "order_id": order["id"],
                "amount": order["amount"] / 100,
                "currency": order["currency"],
                "status": order["status"],
                "raw": order
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def fetch_order(self, order_id: str) -> Dict[str, Any]:
        try:
            order = self.client.order.fetch(order_id)
            return {"success": True, "order": order}
        except Exception as e:
            return {"success": False, "error": str(e)}