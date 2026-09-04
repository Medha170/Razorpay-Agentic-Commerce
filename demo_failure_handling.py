from orchestrator import build_commerce_orchestrator

def run_failure_scenario():
    print("==========================================================")
    print(" DEMO: EXCEEDING POLICY DISCOUNT (35% requested vs 20% max)")
    print("==========================================================")
    
    app = build_commerce_orchestrator()
    
    # Simulate state where an upstream agent set an out-of-bounds discount (35%)
    simulated_illegal_state = {
        "user_query": "I want an Ergonomic Mechanical Keyboard with VIP discount",
        "cart": [{
            "sku": "PROD-ERR-001",
            "name": "Ergonomic Mechanical Keyboard",
            "quantity": 1,
            "unit_price": 4999.0
        }],
        "original_total": 4999.0,
        "discount_applied_pct": 35.0,  # Violates 20% MAX_ALLOWED_DISCOUNT_PCT limit
        "final_total": 3249.35,
        "audit_trail": []
    }

    result = app.invoke(simulated_illegal_state)

    print("\n--- EXECUTION RESULT ---")
    print(f"Gate Passed:             {result.get('gate_passed')}")
    print(f"Razorpay Order ID:       {result.get('razorpay_order_id')}")
    print(f"Original Total:          INR {result.get('original_total')}")
    print(f"Capped Discount Applied: {result.get('discount_applied_pct')}% (Overridden from 35%)")
    print(f"Final Charged Total:     INR {result.get('final_total')}")
    print(f"Warning/Fallback Note:   {result.get('error_message')}")

    print("\n--- COMPLETE AUDIT TRAIL ---")
    for idx, log in enumerate(result.get("audit_trail", []), 1):
        print(f"\nStep {idx}:")
        print(f"  Agent:   {log['agent']}")
        print(f"  Action:  {log['action']}")
        print(f"  Status:  {log['status']}")
        print(f"  Details: {log['details']}")

if __name__ == "__main__":
    run_failure_scenario()