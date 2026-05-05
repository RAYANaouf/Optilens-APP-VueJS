import frappe
import json

@frappe.whitelist()
def get_pos_data():
    # Get all companies
    companies = frappe.get_all("Company", fields=["name", "default_currency"])
    
    # Get all POS Profiles
    profiles = frappe.get_all("POS Profile", 
        fields=["name", "company", "warehouse", "selling_price_list"],
        filters={"disabled": 0}
    )

    # Check for active POS Opening Entry for the user
    opening_entry = frappe.get_all("POS Opening Entry", 
        filters={
            "status": "Open",
            "docstatus": 1
        },
        fields=["name", "pos_profile", "company"]
    )
    
    return {
        "companies": companies,
        "profiles": profiles,
        "opening_entry": opening_entry[0] if opening_entry else None
    }

@frappe.whitelist()
def get_item(priceLists=None, warehouse=None):
    # Convert priceLists from JSON string to Python list
    if isinstance(priceLists, str):
        priceLists = json.loads(priceLists)
    
    priceListsNames = [priceList["name"] for priceList in priceLists] if priceLists else []

    # Fetch items
    items = frappe.get_all(
        "Item",
        fields=[
            'name', 'item_name', 'image', 'brand',
            'item_group', 'description', 'stock_uom'
        ],
        filters={"disabled": 0},
        limit_page_length=100000,
        order_by="item_name ASC"
    )

    item_codes = [item["name"] for item in items]

    # Prepare price filters
    price_filters = {}
    if item_codes:
        price_filters["item_code"] = ["in", item_codes]
    if priceListsNames:
        price_filters["price_list"] = ["in", priceListsNames]

    # Fetch prices
    prices = frappe.get_all(
        "Item Price",
        fields=["item_code", "price_list", "price_list_rate", "currency", "modified"],
        filters=price_filters,
        limit_page_length=10000000
    )
    
    frappe.log_error(
        title="Debug: get_item() Info",
        message=f"""
            Total Item Prices fetched: {len(prices)}
            Item Codes with 'FREIN' in Price List:
            {[p['item_code'] for p in prices if 'FREIN' in p['item_code'].upper()]}
        """
    )


    # Group prices by item_code
    price_map = {}
    for price in prices:
        price_map.setdefault(price["item_code"], []).append(price)

    # Fetch stock quantities (Bin)
    qty_map = {}
    pos_map = {}

    if warehouse:
        bins = frappe.get_all(
            "Bin",
            filters={
                "warehouse": warehouse,
                "item_code": ["in", item_codes],
                "actual_qty": ["!=", 0]
            },
            fields=["item_code", "actual_qty"]
        )
        for bin in bins:
            qty_map[bin["item_code"]] = bin["actual_qty"]

        # Optional: Fetch POS quantities
        pos_data = frappe.db.sql(f"""
            SELECT pii.item_code, SUM(pii.qty) AS pos_invoice_qty
            FROM `tabPOS Invoice Item` pii
            JOIN `tabPOS Invoice` pi ON pi.name = pii.parent
            WHERE pi.consolidated_invoice IS NULL
            AND pi.docstatus = 1
            AND pii.item_code IN ({', '.join(['%s'] * len(item_codes))})
            AND pii.warehouse = %s
            GROUP BY pii.item_code
        """, tuple(item_codes + [warehouse]), as_dict=True)

        for row in pos_data:
            pos_map[row["item_code"]] = row["pos_invoice_qty"]

    # Merge prices + QTY into each item
    for item in items:
        item_code = item["name"]
        item["prices"] = price_map.get(item_code, [])
        item["bin_qty"] = qty_map.get(item_code, 0)
        item["pos_invoice_qty"] = pos_map.get(item_code, 0)
        item["stock_qty"] = qty_map.get(item_code, 0) - pos_map.get(item_code, 0)

    return items
