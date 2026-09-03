from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field

class CartItem(BaseModel):
    sku: str
    name: str
    quantity: int
    unit_price: float

class AuditEntry(BaseModel):
    timestamp: str
    agent: str
    action: str
    details: Dict[str, Any]
    status: str  # APPROVED, REJECTED, OVERRIDDEN

class CommerceState(TypedDict):
    # Conversation & Intent
    messages: List[Dict[str, str]]
    user_query: str
    intent: str  # "catalog_query", "checkout", "upsell_accepted"
    
    # Cart & Pricing Data
    cart: List[Dict[str, Any]]
    suggested_cross_sells: List[Dict[str, Any]]
    discount_applied_pct: float
    original_total: float
    final_total: float
    
    # Razorpay Transaction State
    razorpay_order_id: Optional[str]
    order_status: Optional[str]
    
    # Financial Safety & Audit
    audit_trail: List[Dict[str, Any]]
    gate_passed: bool
    error_message: Optional[str]