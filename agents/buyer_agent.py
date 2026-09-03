import datetime
from typing import Dict, Any
from state import CommerceState
from catalog_service import CatalogService

class BuyerAgent:
    def __init__(self, catalog_service: CatalogService):
        self.catalog = catalog_service

    def process(self, state: CommerceState) -> Dict[str, Any]:
        """Interprets buyer query, matches items against catalog, and builds initial cart."""
        query = state.get("user_query", "")
        matching_products = self.catalog.search_products(query)
        
        cart = state.get("cart", [])
        if matching_products and not cart:
            top_item = matching_products[0]
            cart.append({
                "sku": top_item["sku"],
                "name": top_item["name"],
                "quantity": 1,
                "unit_price": top_item["price"]
            })
        
        original_total = sum(item["unit_price"] * item["quantity"] for item in cart)
        
        audit_log = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "agent": "A2A_Buyer_Agent",
            "action": "catalog_lookup_and_cart_build",
            "details": {
                "query": query,
                "matches_found": len(matching_products),
                "cart_items": [item["sku"] for item in cart]
            },
            "status": "APPROVED"
        }
        
        return {
            "cart": cart,
            "original_total": original_total,
            "final_total": original_total,
            "audit_trail": state.get("audit_trail", []) + [audit_log]
        }