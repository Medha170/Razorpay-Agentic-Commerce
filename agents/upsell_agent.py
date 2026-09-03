import datetime
from typing import Dict, Any
from state import CommerceState
from catalog_service import CatalogService

class UpsellAgent:
    def __init__(self, catalog_service: CatalogService):
        self.catalog = catalog_service

    def process(self, state: CommerceState) -> Dict[str, Any]:
        """Analyzes active cart and injects cross-sell recommendations or bundle discounts."""
        cart = state.get("cart", [])
        if not cart:
            return {}
        
        primary_sku = cart[0]["sku"]
        product = self.catalog.get_product_by_sku(primary_sku)
        
        suggested_cross_sells = []
        applied_discount = 0.0
        
        if product and "eligible_cross_sells" in product:
            for cross_sku in product["eligible_cross_sells"]:
                cross_prod = self.catalog.get_product_by_sku(cross_sku)
                if cross_prod:
                    suggested_cross_sells.append(cross_prod)
            
            # Dynamic bundle promotion (10% discount)
            applied_discount = 10.0  
        
        original_total = state.get("original_total", 0.0)
        discounted_total = original_total * (1 - (applied_discount / 100.0))
        
        audit_log = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "agent": "Upsell_Growth_Agent",
            "action": "evaluate_dynamic_cross_sell",
            "details": {
                "primary_sku": primary_sku,
                "suggested_skus": [p["sku"] for p in suggested_cross_sells],
                "proposed_discount_pct": applied_discount
            },
            "status": "APPROVED"
        }
        
        return {
            "suggested_cross_sells": suggested_cross_sells,
            "discount_applied_pct": applied_discount,
            "final_total": discounted_total,
            "audit_trail": state.get("audit_trail", []) + [audit_log]
        }