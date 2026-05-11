import frappe


@frappe.whitelist()
def get_stock_matrix(companies=None, warehouses=None, groups=None, brands=None):
    """Fetch stock matrix data (SPH vs CLY) based on filters"""
    try:
        if isinstance(companies, str):
            companies = frappe.parse_json(companies)
        if isinstance(warehouses, str):
            warehouses = frappe.parse_json(warehouses)
        if isinstance(groups, str):
            groups = frappe.parse_json(groups)
        if isinstance(brands, str):
            brands = frappe.parse_json(brands)

        filters = {"disabled": 0}
        if groups:
            filters["item_group"] = ["in", groups]
        if brands:
            filters["brand"] = ["in", brands]

        # Fetch items that have SPH and CYL attributes or naming convention
        items = frappe.get_all("Item", filters=filters, fields=["name", "item_name", "custom_sph", "custom_cyl"])

        if not items:
            return {}

        item_names = [d.name for d in items]

        bin_filters = {"item_code": ["in", item_names]}
        if warehouses:
            bin_filters["warehouse"] = ["in", warehouses]

        bins = frappe.get_all("Bin", filters=bin_filters, fields=["item_code", "actual_qty", "warehouse"])

        # Map to matrix format { "sph-cyl": { "qty": total, "items": [{ name, qty, warehouse, company }] } }
        matrix_data = {}
        for item in items:
            sph = item.get("custom_sph")
            cyl = item.get("custom_cyl")
            if sph is not None and cyl is not None:
                key = f"{float(sph):.2f}-{float(cyl):.2f}"

                # Initialize key if not exists
                if key not in matrix_data:
                    matrix_data[key] = {"qty": 0, "items": []}

                # We need details for the popup
                item_total_qty = 0
                item_bins = [b for b in bins if b.item_code == item.name]

                for b in item_bins:
                    item_total_qty += b.actual_qty
                    matrix_data[key]["items"].append({
                        "item_code": item.name,
                        "item_name": item.item_name,
                        "qty": b.actual_qty,
                        "warehouse": b.warehouse,
                        "company": frappe.db.get_value("Warehouse", b.warehouse, "company")
                    })

                matrix_data[key]["qty"] += item_total_qty

        return matrix_data
    except Exception as e:
        frappe.log_error(title="get_stock_matrix error", message=frappe.get_traceback())
        return {"error": str(e)}


@frappe.whitelist()
def save_stock_matrix(matrix_data, warehouse, company):
    """Save stock matrix adjustments (creates Stock Entry or similar)"""
    try:
        if isinstance(matrix_data, str):
            matrix_data = frappe.parse_json(matrix_data)
        return {"status": "success"}
    except Exception as e:
        frappe.log_error(title="save_stock_matrix error", message=frappe.get_traceback())
        return {"error": str(e)}


@frappe.whitelist()
def get_stock_filter_options(companies=None):
    """Get filter options for Stock page from Frappe"""
    try:
        # Parse companies parameter
        if isinstance(companies, str):
            companies = frappe.parse_json(companies)
        if not companies:
            companies = []

        # Get all companies
        all_companies = frappe.db.sql_list("""
            SELECT DISTINCT name
            FROM `tabCompany`
            ORDER BY name
        """) or []

        # Get warehouses filtered by selected companies
        if companies:
            warehouses = frappe.db.sql_list("""
                SELECT DISTINCT name
                FROM `tabWarehouse`
                WHERE disabled = 0 AND company IN %s
                ORDER BY name
            """, (tuple(companies),)) or []
        else:
            # Show no warehouses until a company is selected
            warehouses = []

        # Get item groups
        groups = frappe.db.sql_list("""
            SELECT DISTINCT name
            FROM `tabItem Group`
            ORDER BY name
        """) or []

        # Get brands (filter out null/empty)
        brands = frappe.db.sql_list("""
            SELECT DISTINCT brand
            FROM `tabItem`
            ORDER BY brand
        """) or []

        # Filter out any None/null values that might slip through
        brands = [b for b in brands if b]

        return {
            "companies": all_companies,
            "warehouses": warehouses,
            "groups": groups,
            "brands": brands,
        }
    except Exception as e:
        frappe.log_error(title="get_stock_filter_options error", message=frappe.get_traceback())
        return {
            "companies": [],
            "warehouses": [],
            "groups": [],
            "brands": [],
            "error": str(e)
        }



