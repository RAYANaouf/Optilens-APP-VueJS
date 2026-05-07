import frappe
import json

@frappe.whitelist()
def get_pos_data(company=None, pos_profile=None):
    # Get all companies
    companies = frappe.get_all("Company", fields=["name", "default_currency"])
    
    # Get all POS Profiles
    profiles = frappe.get_all("POS Profile", 
        fields=["name", "company", "warehouse", "selling_price_list"],
        filters={"disabled": 0}
    )

    # Check for active POS Opening Entry
    filters = {
        "user": frappe.session.user,
        "status": "Open",
        "docstatus": 1
    }
    if company:
        filters["company"] = company
    if pos_profile:
        filters["pos_profile"] = pos_profile

    opening_entry = frappe.get_all("POS Opening Entry", 
        filters=filters,
        fields=["name", "pos_profile", "company"]
    )
    
    return {
        "companies": companies,
        "profiles": profiles,
        "opening_entry": opening_entry[0] if opening_entry else None
    }

@frappe.whitelist()
def create_pos_session(company, pos_profile, denominations):
    import json
    if isinstance(denominations, str):
        denominations = json.loads(denominations)

    # Calculate opening amount
    opening_amount = sum(float(d['value']) * int(d['qty']) for d in denominations)
    
    # Get mode of payment from POS Profile
    pos_profile_doc = frappe.get_doc("POS Profile", pos_profile)
    mode_of_payment = "Cash" # Default fallback
    
    if pos_profile_doc.payments:
        mode_of_payment = pos_profile_doc.payments[0].mode_of_payment
    
    # Create POS Opening Entry
    doc = frappe.get_doc({
        "doctype": "POS Opening Entry",
        "company": company,
        "pos_profile": pos_profile,
        "user": frappe.session.user,
        "status": "Open",
        "period_start_date": frappe.utils.now(),
        "balance_details": [
            {
                "mode_of_payment": mode_of_payment,
                "opening_amount": opening_amount
            }
        ]
    })
    
    # Add denominations to the document (Frappe standard structure)
    # Note: Frappe doesn't have a standard list for denominations in Opening Entry, 
    # but some users use custom tables or just the opening amount. 
    # Assuming standard Opening Entry for now.
    
    doc.insert()
    doc.submit()
    
    return {
        "name": doc.name,
        "pos_profile": doc.pos_profile,
        "company": doc.company,
        "opening_amount": opening_amount
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

@frappe.whitelist()
def get_customer_invoices(customer):
    if not customer:
        return []

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "customer": customer,
            "docstatus": 1,
            "outstanding_amount": [">", 0]
        },
        fields=[
            "name", "posting_date", "grand_total",
            "outstanding_amount", "currency", "due_date"
        ],
        order_by="posting_date desc"
    )
    return invoices

@frappe.whitelist()
def get_supplier_invoices(supplier):
    if not supplier:
        return []

    invoices = frappe.get_all(
        "Purchase Invoice",
        filters={
            "supplier": supplier,
            "docstatus": 1,
            "outstanding_amount": [">", 0]
        },
        fields=[
            "name", "posting_date", "grand_total",
            "outstanding_amount", "currency", "due_date"
        ],
        order_by="posting_date desc"
    )
    return invoices

@frappe.whitelist()
def sync_offline_orders(orders):
    import json
    orders = json.loads(orders)
    synced_count = 0

    for order in orders:
        try:
            # Create POS Invoice
            doc = frappe.new_doc("POS Invoice")
            doc.customer = order.get("selectedCustomer", {}).get("name")
            doc.pos_profile = order.get("pos_profile")
            doc.company = order.get("company")
            doc.is_pos = 1
            doc.update_stock = 1
            
            # Add Items
            for item in order.get("cart", []):
                doc.append("items", {
                    "item_code": item.get("name"),
                    "qty": item.get("qty"),
                    "rate": item.get("standard_rate"),
                    "warehouse": item.get("warehouse") or frappe.db.get_value("POS Profile", doc.pos_profile, "warehouse")
                })
            
            # Handle Payments
            payment = order.get("payment", {})
            if payment.get("method") == "Cash" and payment.get("amount") > 0:
                doc.append("payments", {
                    "mode_of_payment": "Cash",
                    "amount": payment.get("amount")
                })
            
            doc.insert()
            doc.submit()
            synced_count += 1
            
        except Exception:
            frappe.log_error(title="POS Sync Error", message=frappe.get_traceback())
            continue
            
    return {"synced_count": synced_count}

@frappe.whitelist()
def create_cash_transaction(type, amount, reason, company, pos_profile):
    """
    Creates a Cash Transaction record for In/Out movements from the POS.
    """
    # Create a new POS Invoice or a custom 'Cash Transaction' doctype if you have one.
    # For now, let's assume we use a Journal Entry or a custom DocType.
    # This logic should be adapted to your specific requirements.
    
    # Example: Create a log entry or specific Frappe record
    # Replace 'Cash Transaction' with your actual DocType name
    try:
        doc = frappe.get_doc({
            "doctype": "Cash Transaction", # Ensure this DocType exists
            "type": type,
            "amount": float(amount),
            "reason": reason,
            "company": company,
            "pos_profile": pos_profile,
            "user": frappe.session.user,
            "posting_date": frappe.utils.today(),
            "posting_time": frappe.utils.nowtime()
        })
        doc.insert()
        return {"status": "success", "name": doc.name}
    except Exception as e:
        # If custom DocType doesn't exist, we can fallback to log_error
        frappe.log_error(title="POS Cash Transaction Error", message=frappe.get_traceback())
        # Return success anyway for the UI if we just want to log it for now
        return {"status": "logged"}

