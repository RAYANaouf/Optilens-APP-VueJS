import frappe

@frappe.whitelist()
def get_warehouse_stock_levels(company, warehouses, item_groups=None, search=None):
    """Get stock levels for multiple warehouses and items"""
    try:
        if isinstance(warehouses, str):
            warehouses = frappe.parse_json(warehouses)
        
        if isinstance(item_groups, str):
            item_groups = frappe.parse_json(item_groups)

        if not warehouses:
            return []

        filters = {"disabled": 0}
        
        if item_groups and len(item_groups) > 0:
            filters["item_group"] = ["in", item_groups]

        if search:
            filters["item_name"] = ["like", f"%{search}%"]

        # Fetch items
        items = frappe.get_all("Item",
            filters=filters,
            fields=["name", "item_name"],
            order_by="item_name asc",
            limit=100
        )

        if search and not items:
            # Try searching by item_code if no items found by name
            items = frappe.get_all("Item",
                filters={"name": ["like", f"%{search}%"], "disabled": 0},
                fields=["name", "item_name"],
                order_by="item_name asc",
                limit=100
            )

        if not items:
            return []

        item_codes = [d.name for d in items]

        # Fetch stock levels from Bin
        bin_data = frappe.get_all("Bin",
            filters={
                "item_code": ["in", item_codes],
                "warehouse": ["in", warehouses]
            },
            fields=["item_code", "warehouse", "actual_qty"]
        )

        # Structure data for the table
        stock_map = {}
        for item in items:
            stock_map[item.name] = {
                "item_code": item.name,
                "item_name": item.item_name,
                "balances": {wh: 0 for wh in warehouses},
                "total": 0
            }

        for bin in bin_data:
            if bin.item_code in stock_map:
                qty = float(bin.actual_qty or 0)
                stock_map[bin.item_code]["balances"][bin.warehouse] = qty
                stock_map[bin.item_code]["total"] += qty

        # Convert back to list and sort by name
        result = list(stock_map.values())
        result.sort(key=lambda x: x["item_name"])

        return result

    except Exception:
        frappe.log_error(title="get_warehouse_stock_levels error", message=frappe.get_traceback())
        return []
