import frappe
import json

@frappe.whitelist()
def get_pos_opening_entry(company, pos_profile):
    """
    Fetch the open POS Opening Entry for the given company, profile and current user.
    """
    if not company or not pos_profile:
        return None

    opening_entry = frappe.db.get_value(
        "POS Opening Entry",
        {
            "company": company,
            "pos_profile": pos_profile,
            "user": frappe.session.user,
            "status": "Open"
        },
        ["name", "period_start_date"],
        as_dict=True
    )
    return opening_entry

@frappe.whitelist()
def get_pos_suppliers(company):
    """
    Fetch suppliers that have the selected company in their 'custom_company' field.
    """
    if not company:
        return []

    suppliers = frappe.get_all(
        "Supplier",
        fields=["name", "supplier_name", "mobile_no"],
        filters={
            "custom_company": company
        },
        order_by="supplier_name ASC",
        limit_page_length=3000
    )
    return suppliers

@frappe.whitelist()
def get_pos_customers(company):
    """
    Fetch customers that have the selected company in their 'custom_companies' child table.
    """
    if not company:
        return []

    # We use a subquery or join to filter customers by the child table
    customers = frappe.get_all(
        "Customer",
        fields=["name", "customer_name", "mobile_no"],
        filters=[
            ["Customer Company", "company", "=", company]
        ],
        distinct=True,
        order_by="customer_name ASC",
        limit_page_length=3000
    )
    return customers

@frappe.whitelist()
def get_pos_data(company=None, pos_profile=None):
    # Get all companies
    companies = frappe.get_all("Company", fields=["name", "default_currency"])

    # Get all POS Profiles
    profiles = frappe.get_all("POS Profile", 
        fields=["name", "company", "warehouse", "selling_price_list"],
        filters={"disabled": 0}
    )

    # Enrich profiles with default payment method from the 'payments' child table
    for profile in profiles:
        # Fetch the default payment method
        default_payment = frappe.db.get_value("POS Payment Method",
            {"parent": profile.name, "default": 1},
            "mode_of_payment"
        )
        profile["default_payment_method"] = default_payment or "Cash"

        # Fetch all allowed payment methods for this profile
        payments = frappe.get_all("POS Payment Method",
            filters={"parent": profile.name},
            fields=["mode_of_payment", "default"]
        )
        profile["payment_methods"] = payments

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
        fields=["name", "pos_profile", "company", "period_start_date"],
        filters=filters,
        order_by="creation desc"
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
    
    doc = frappe.new_doc("POS Opening Entry")
    doc.company = company
    doc.pos_profile = pos_profile
    doc.user = frappe.session.user
    doc.period_start_date = frappe.utils.now_datetime()
    doc.posting_date      = frappe.utils.now_datetime()

    # Get default payment method from POS Profile
    default_payment = frappe.db.get_value("POS Payment Method",
        {"parent": pos_profile, "default": 1},
        "mode_of_payment"
    ) 

    print("=======> default_payment", default_payment)

    total = 0
    for d in denominations:
        if d.get("qty"):
            total += float(d.get("value")) * float(d.get("qty"))

    doc.append("balance_details", {
        "mode_of_payment": default_payment,
        "opening_amount": total
        })
    
    doc.insert()
    doc.submit()

    return {
        "status": "success",
        "name": doc.name,
        "pos_profile": doc.pos_profile,
        "company": doc.company,
        "opening_amount": opening_amount,
        "period_start_date": doc.period_start_date
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
def get_customer_invoices(customer, company=None):
    if not customer:
        return []

    filters = {
        "customer": customer,
        "docstatus": 1,
        "outstanding_amount": [">", 0]
    }

    if company:
        filters["company"] = company

    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=[
            "name", "posting_date", "grand_total",
            "outstanding_amount", "currency", "due_date"
        ],
        order_by="posting_date desc"
    )
    return invoices

@frappe.whitelist()
def get_supplier_invoices(supplier, company=None):
    if not supplier:
        return []

    filters = {
        "supplier": supplier,
        "docstatus": 1,
        "outstanding_amount": [">", 0]
    }

    if company:
        filters["company"] = company

    invoices = frappe.get_all(
        "Purchase Invoice",
        filters=filters,
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
    if isinstance(orders, str):
        orders = json.loads(orders)



    synced_count = 0
    frappe.log_error(title="POS Sync Debug", message=f"Attempting to sync {len(orders)} orders")

    for order in orders:
        try:

            frappe.log_error(title="POS Sync Debug", message=f"Processing order: {order}")



            # Create POS Invoice
            doc              = frappe.new_doc("POS Invoice")
            doc.customer     = order.get("selectedCustomer", {}).get("name")
            doc.pos_profile  = order.get("pos_profile")
            doc.company      = order.get("company")
            doc.is_pos       = 1
            doc.update_stock = 1

            # Map datetime correctly
            completed_at = order.get("completed_at")
            if completed_at:
                doc.posting_date = completed_at.split('T')[0]
                doc.posting_time = completed_at.split('T')[1].split('.')[0]
            else:
                frappe.throw("The posting date/time is required")

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
            mop = payment.get("method")
            amount = float(payment.get("amount") or 0)
            doc.append("payments", {
                "mode_of_payment": mop,
                "amount": amount
            })
            frappe.log_error(title="POS Sync Debug", message=f"Payments appended: {mop} - {amount}")

            doc.insert(ignore_permissions=True)
            #doc.submit()
            synced_count += 1
            frappe.db.commit()

        except Exception:
            frappe.db.rollback()
            frappe.log_error(title="POS Sync Error", message=frappe.get_traceback())
            continue

    return {"synced_count": synced_count}

@frappe.whitelist()
def process_payment(party_type, party, amount, invoices, payment_mode="Cash"):

    print("process_payment", party_type, party, amount, invoices, payment_mode)
    frappe.log_error(title="POS Payment Error", message=f"Party Type: {party_type}, Party: {party}, Amount: {amount}, Invoices: {invoices}, Payment Mode: {payment_mode}")



    """
    Creates a Payment Entry for selected invoices.
    """
    if isinstance(invoices, str):
        invoices = json.loads(invoices)

    amount = float(amount)

    try:
        # Create Payment Entry
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive" if party_type == "Customer" else "Pay"
        pe.party_type = party_type
        pe.party = party
        pe.paid_amount = amount
        pe.received_amount = amount
        pe.reference_no = f"POS-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"
        pe.reference_date = frappe.utils.today()

        # Get Mode of Payment details (Account)
        account_paid_to = frappe.get_value("Mode of Payment Account",
            {"parent": payment_mode, "company": frappe.defaults.get_user_default("company")},
            "default_account")

        if party_type == "Customer":
            pe.paid_to = account_paid_to or frappe.get_value("Company", pe.company, "default_cash_account")
        else:
            pe.paid_from = account_paid_to or frappe.get_value("Company", pe.company, "default_cash_account")

        # Add References (Invoices)
        for inv_name in invoices:
            inv_doc = frappe.get_doc("Sales Invoice" if party_type == "Customer" else "Purchase Invoice", inv_name)

            # Calculate how much to allocate to this invoice
            allocated = min(amount, inv_doc.outstanding_amount)
            if allocated <= 0:
                continue

            pe.append("references", {
                "reference_doctype": inv_doc.doctype,
                "reference_name": inv_doc.name,
                "total_amount": inv_doc.grand_total,
                "outstanding_amount": inv_doc.outstanding_amount,
                "allocated_amount": allocated
            })

            amount -= allocated
            if amount <= 0:
                break

        pe.insert()
        pe.submit()

        return {"status": "success", "name": pe.name}

    except Exception as e:
        frappe.log_error(title="POS Payment Error", message=frappe.get_traceback())
        frappe.throw(f"Error processing payment: {e!r}")

@frappe.whitelist()
def create_cash_transaction(type, amount, reason, company, pos_profile):
    """
    Creates a Cash Transaction record for In/Out movements from the POS.
    """
    try:
        doc = frappe.get_doc({
            "doctype": "Cash Transaction",
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
    except Exception:
        frappe.log_error(title="POS Cash Transaction Error", message=frappe.get_traceback())
        return {"status": "logged"}

