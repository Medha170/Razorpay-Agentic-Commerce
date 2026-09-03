from langgraph.graph import StateGraph, END
from state import CommerceState
from catalog_service import CatalogService
from razorpay_client import RazorpayTestClient

from agents.buyer_agent import BuyerAgent
from agents.upsell_agent import UpsellAgent
from agents.safety_gate_agent import SafetyGateAgent

# Initialize shared dependencies
catalog_svc = CatalogService("catalog.json")
rzp_client = RazorpayTestClient()

# Instantiate modular agents
buyer_agent = BuyerAgent(catalog_svc)
upsell_agent = UpsellAgent(catalog_svc)
safety_gate = SafetyGateAgent(rzp_client)

def build_commerce_orchestrator():
    workflow = StateGraph(CommerceState)
    
    # Register agent process methods as graph nodes
    workflow.add_node("buyer_handler", buyer_agent.process)
    workflow.add_node("upsell_engine", upsell_agent.process)
    workflow.add_node("safety_gate", safety_gate.process)
    
    # Define execution graph sequence
    workflow.set_entry_point("buyer_handler")
    workflow.add_edge("buyer_handler", "upsell_engine")
    workflow.add_edge("upsell_engine", "safety_gate")
    workflow.add_edge("safety_gate", END)
    
    return workflow.compile()

if __name__ == "__main__":
    app = build_commerce_orchestrator()
    
    test_state = {
        "user_query": "I want to buy an Ergonomic Mechanical Keyboard",
        "cart": [],
        "audit_trail": []
    }
    
    result = app.invoke(test_state)
    print("--- EXECUTION COMPLETE ---")
    print(f"Razorpay Order ID: {result.get('razorpay_order_id')}")
    print(f"Gate Passed: {result.get('gate_passed')}")