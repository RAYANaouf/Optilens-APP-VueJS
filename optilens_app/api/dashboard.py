import frappe
from frappe.utils import today, add_days

@frappe.whitelist()
def get_dashboard_stats():
    """Get comprehensive dashboard stats for POS, Stock, and Pricing"""
    
    # Today's sales from POS Invoices
    today_sales = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabPOS Invoice`
        WHERE posting_date = %s AND docstatus = 1
    """, today(), as_dict=1)[0].total
    
    # Yesterday's sales for trend
    yesterday_sales = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabPOS Invoice`
        WHERE posting_date = %s AND docstatus = 1
    """, add_days(today(), -1), as_dict=1)[0].total
    
    sales_trend = 0
    if yesterday_sales > 0:
        sales_trend = round(((today_sales - yesterday_sales) / yesterday_sales) * 100, 1)
    
    # Total active items
    total_items = frappe.db.count("Item", {"disabled": 0})
    
    # Low stock items
    low_stock_items = frappe.db.sql("""
        SELECT 
            b.item_code,
            i.item_name,
            b.warehouse,
            b.actual_qty,
            COALESCE(i.reorder_level, 10) as reorder_level
        FROM `tabBin` b
        JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty < COALESCE(i.reorder_level, 10)
        OR b.projected_qty < 0
        ORDER BY b.actual_qty ASC
        LIMIT 10
    """, as_dict=1)
    
    # Active price lists
    active_price_lists = frappe.db.count("Price List", {"enabled": 1, "selling": 1})
    
    # Active POS profiles
    active_pos_profiles = frappe.db.count("POS Profile", {"disabled": 0})
    
    # Total warehouses
    total_warehouses = frappe.db.count("Warehouse", {"is_group": 0, "disabled": 0})
    
    # Pending stock entries
    pending_stock_entries = frappe.db.count("Stock Entry", {"docstatus": 0})
    
    return {
        "today_sales": today_sales,
        "sales_trend": sales_trend,
        "total_items": total_items,
        "low_stock_count": len(low_stock_items),
        "low_stock_items": low_stock_items,
        "active_price_lists": active_price_lists,
        "active_pos_profiles": active_pos_profiles,
        "total_warehouses": total_warehouses,
        "pending_stock_entries": pending_stock_entries,
    }

@frappe.whitelist()
def get_recent_pos_invoices(limit=10):
    """Get recent POS invoices for dashboard"""
    return frappe.get_all(
        "POS Invoice",
        fields=["name", "customer", "grand_total", "posting_date", "status"],
        filters={"docstatus": 1},
        order_by="posting_date desc, creation desc",
        limit=limit
    )

@frappe.whitelist()
def get_low_stock_items(limit=10):
    """Get items with low stock for dashboard alerts"""
    return frappe.db.sql("""
        SELECT 
            b.item_code,
            i.item_name,
            b.warehouse,
            w.warehouse_name,
            b.actual_qty,
            COALESCE(i.reorder_level, 10) as reorder_level,
            (COALESCE(i.reorder_level, 10) - b.actual_qty) as shortage
        FROM `tabBin` b
        JOIN `tabItem` i ON b.item_code = i.name
        JOIN `tabWarehouse` w ON b.warehouse = w.name
        WHERE b.actual_qty < COALESCE(i.reorder_level, 10)
        OR b.projected_qty < 0
        ORDER BY b.actual_qty ASC
        LIMIT %s
    """, limit, as_dict=1)
