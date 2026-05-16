import frappe
from frappe.utils import flt




@frappe.whitelist()
def get_stock_matrix(
    companies=None,
    warehouses=None,
    groups=None,
    brands=None,
    matrix_type="+/+",
    sales_start=None,
    sales_end=None,
    include_sales_data=0
):

    try:

        # -------------------------
        # Parse inputs
        # -------------------------
        if isinstance(companies, str):
            companies = frappe.parse_json(companies)
        if isinstance(warehouses, str):
            warehouses = frappe.parse_json(warehouses)
        if isinstance(groups, str):
            groups = frappe.parse_json(groups)
        if isinstance(brands, str):
            brands = frappe.parse_json(brands)

        cyl_sign, sph_sign = matrix_type.split('/')

        # -------------------------
        # Fetch items
        # -------------------------
        item_filters = {
            "disabled": 0,
            "custom_sph_sign": sph_sign,
            "custom_cly_sign": cyl_sign
        }

        if groups:
            item_filters["item_group"] = ["in", groups]
        if brands:
            item_filters["brand"] = ["in", brands]

        items = frappe.get_all(
            "Item",
            filters=item_filters,
            fields=[
                "name",
                "item_name",
                "item_group",
                "brand",
                "custom_sph",
                "custom_cyl"
            ]
        )

        if not items:
            return {}

        item_names = [i.name for i in items]

        # -------------------------
        # STOCK (BIN)
        # -------------------------
        bin_filters = {"item_code": ["in", item_names]}
        if warehouses:
            bin_filters["warehouse"] = ["in", warehouses]

        bins = frappe.get_all(
            "Bin",
            filters=bin_filters,
            fields=["item_code", "warehouse", "actual_qty"]
        )

        bins_by_item = {}
        for b in bins:
            bins_by_item.setdefault(b.item_code, []).append(b)

        # -------------------------
        # SALES DATA
        # -------------------------
        sales_map = {}
        best_month_map = {}

        if int(include_sales_data) == 1:

            conditions = [
                "si.docstatus = 1",
                "sii.item_code IN %(items)s"
            ]

            params = {"items": item_names}

            if sales_start and sales_end:
                params["start"] = sales_start.split("T")[0]
                params["end"] = sales_end.split("T")[0]
                conditions.append("si.posting_date BETWEEN %(start)s AND %(end)s")

            if companies:
                conditions.append("si.company IN %(companies)s")
                params["companies"] = companies

            # -------------------------
            # TOTAL SALES
            # -------------------------
            total_sql = f"""
                SELECT
                    sii.item_code,
                    SUM(sii.qty) AS total_qty
                FROM `tabSales Invoice Item` sii
                JOIN `tabSales Invoice` si
                    ON si.name = sii.parent
                WHERE {" AND ".join(conditions)}
                GROUP BY sii.item_code
            """

            total_data = frappe.db.sql(total_sql, params, as_dict=1)

            sales_map = {
                d.item_code: flt(d.total_qty or 0)
                for d in total_data
            }

            # -------------------------
            # BEST SELL MONTH
            # -------------------------
            monthly_sql = f"""
                SELECT
                    sii.item_code,
                    YEAR(si.posting_date) AS y,
                    MONTH(si.posting_date) AS m,
                    SUM(sii.qty) AS qty_month
                FROM `tabSales Invoice Item` sii
                JOIN `tabSales Invoice` si
                    ON si.name = sii.parent
                WHERE {" AND ".join(conditions)}
                GROUP BY sii.item_code, y, m
            """

            monthly_data = frappe.db.sql(monthly_sql, params, as_dict=1)

            temp = {}

            for r in monthly_data:
                if r.item_code not in temp or r.qty_month > temp[r.item_code].qty_month:
                    temp[r.item_code] = r

            best_month_map = {
                k: {
                    "qty": flt(v.qty_month or 0),
                    "month": f"{v.y}-{str(v.m).zfill(2)}-01"
                }
                for k, v in temp.items()
            }

        # -------------------------
        # WAREHOUSE MAP
        # -------------------------
        warehouse_map = {}

        if bins:
            wh_names = list(set(b.warehouse for b in bins))

            wh_data = frappe.get_all(
                "Warehouse",
                filters={"name": ["in", wh_names]},
                fields=["name", "company"]
            )

            warehouse_map = {w.name: w.company for w in wh_data}

        # -------------------------
        # BUILD MATRIX
        # -------------------------
        matrix = {}

        for item in items:

            sph = item.custom_sph
            cyl = item.custom_cyl

            if sph is None or cyl is None:
                continue

            key = f"{float(sph):.2f}-{float(cyl):.2f}"

            if key not in matrix:
                matrix[key] = {
                    "qty": 0,
                    "sold_qty": 0,
                    "best_sell_qty": 0,
                    "best_sell_month": None,
                    "items": []
                }

            item_bins = bins_by_item.get(item.name, [])

            stock_total = 0
            sold_qty = sales_map.get(item.name, 0)
            best = best_month_map.get(item.name, {})

            for b in item_bins:

                qty = flt(b.actual_qty or 0)
                stock_total += qty

                matrix[key]["items"].append({
                    "item_code": item.name,
                    "item_name": item.item_name,
                    "item_group": item.item_group,
                    "brand": item.brand,

                    # STOCK
                    "qty": qty,

                    # SALES (same value repeated if needed)
                    "sold_qty": sold_qty,

                    "warehouse": b.warehouse,
                    "company": warehouse_map.get(b.warehouse)
                })

            matrix[key]["qty"] += stock_total
            matrix[key]["sold_qty"] += sold_qty

            matrix[key]["best_sell_qty"] += best.get("qty", 0)
            matrix[key]["best_sell_month"] = best.get("month")

        return matrix

    except Exception:
        frappe.log_error("get_stock_matrix error", frappe.get_traceback())
        return {"error": frappe.get_traceback()}





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



