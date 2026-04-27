import frappe

@frappe.whitelist(allow_guest=True)
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
        frappe.log_error(f"get_stock_filter_options error: {str(e)}")
        return {
            "companies": [],
            "warehouses": [],
            "groups": [],
            "brands": [],
            "error": str(e)
        }



