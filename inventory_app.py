import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# ==========================================================================
# 1. DATABASE & INITIALIZATION LAYER
# ==========================================================================
DB_FILE = "inventory_data.json"

DEFAULT_CATEGORIES = [
    {"CategoryID": "1", "CategoryName": "Electronics"},
    {"CategoryID": "2", "CategoryName": "Office Supplies"},
    {"CategoryID": "3", "CategoryName": "Furniture"},
    {"CategoryID": "4", "CategoryName": "Apparel"}
]

DEFAULT_SUPPLIERS = [
    {
        "SupplierID": "1",
        "SupplierName": "TechWorld Wholesalers",
        "ContactPerson": "Alice Vance",
        "Phone": "+1-555-0199",
        "Email": "alice@techworld.com",
        "Address": "100 Silicon Blvd, San Jose, CA"
    },
    {
        "SupplierID": "2",
        "SupplierName": "Global Office Corp",
        "ContactPerson": "Robert Miller",
        "Phone": "+1-555-0142",
        "Email": "orders@globaloffice.com",
        "Address": "450 Commerce Pkwy, Chicago, IL"
    },
    {
        "SupplierID": "3",
        "SupplierName": "Comfort Seats Ltd",
        "ContactPerson": "Elena Rostova",
        "Phone": "+1-555-0177",
        "Email": "sales@comfortseats.com",
        "Address": "78 Ergonomic Way, Grand Rapids, MI"
    },
    {
        "SupplierID": "4",
        "SupplierName": "Apex Apparel Group",
        "ContactPerson": "Marcus Brody",
        "Phone": "+1-555-0121",
        "Email": "m.brody@apexapparel.com",
        "Address": "12 Garment St, New York, NY"
    }
]

DEFAULT_PRODUCTS = [
    {
        "ProductID": "PRD-1001",
        "ProductName": "Logitech MX Master 3S",
        "CategoryID": "1",
        "SupplierID": "1",
        "PurchasePrice": 75.00,
        "SellingPrice": 99.99,
        "Quantity": 25,
        "ReorderLevel": 10,
        "Barcode": "097855171734",
        "Image": "electronics",
        "CreatedDate": "2026-07-20T10:00:00Z"
    },
    {
        "ProductID": "PRD-1002",
        "ProductName": "Dell UltraSharp 27 Monitor",
        "CategoryID": "1",
        "SupplierID": "1",
        "PurchasePrice": 220.00,
        "SellingPrice": 299.99,
        "Quantity": 8,
        "ReorderLevel": 12,
        "Barcode": "884116382905",
        "Image": "electronics",
        "CreatedDate": "2026-07-21T11:30:00Z"
    },
    {
        "ProductID": "PRD-1003",
        "ProductName": "Ergonomic Office Chair",
        "CategoryID": "3",
        "SupplierID": "3",
        "PurchasePrice": 150.00,
        "SellingPrice": 249.99,
        "Quantity": 15,
        "ReorderLevel": 5,
        "Barcode": "712493018241",
        "Image": "furniture",
        "CreatedDate": "2026-07-15T09:00:00Z"
    },
    {
        "ProductID": "PRD-1004",
        "ProductName": "Pilot G2 Gel Pens (12 Pack)",
        "CategoryID": "2",
        "SupplierID": "2",
        "PurchasePrice": 6.50,
        "SellingPrice": 12.99,
        "Quantity": 45,
        "ReorderLevel": 15,
        "Barcode": "072838310202",
        "Image": "office",
        "CreatedDate": "2026-07-18T14:15:00Z"
    },
    {
        "ProductID": "PRD-1005",
        "ProductName": "Premium Cotton Hoodie",
        "CategoryID": "4",
        "SupplierID": "4",
        "PurchasePrice": 18.00,
        "SellingPrice": 39.99,
        "Quantity": 3,
        "ReorderLevel": 8,
        "Barcode": "609214731804",
        "Image": "apparel",
        "CreatedDate": "2026-07-22T16:45:00Z"
    },
    {
        "ProductID": "PRD-1006",
        "ProductName": "Standing Desk Converter",
        "CategoryID": "3",
        "SupplierID": "3",
        "PurchasePrice": 85.00,
        "SellingPrice": 149.99,
        "Quantity": 0,
        "ReorderLevel": 5,
        "Barcode": "810056782312",
        "Image": "furniture",
        "CreatedDate": "2026-07-23T10:00:00Z"
    }
]

DEFAULT_TRANSACTIONS = [
    {"TransactionID": "TXN-1001", "ProductID": "PRD-1001", "TransactionType": "Stock In", "Quantity": 25, "Date": "2026-07-20T10:05:00Z", "Remarks": "Initial setup"},
    {"TransactionID": "TXN-1002", "ProductID": "PRD-1002", "TransactionType": "Stock In", "Quantity": 10, "Date": "2026-07-21T11:35:00Z", "Remarks": "Initial setup"},
    {"TransactionID": "TXN-1003", "ProductID": "PRD-1002", "TransactionType": "Stock Out", "Quantity": 2, "Date": "2026-07-24T15:10:00Z", "Remarks": "Corporate sale"},
    {"TransactionID": "TXN-1004", "ProductID": "PRD-1003", "TransactionType": "Stock In", "Quantity": 15, "Date": "2026-07-15T09:10:00Z", "Remarks": "Initial setup"},
    {"TransactionID": "TXN-1005", "ProductID": "PRD-1004", "TransactionType": "Stock In", "Quantity": 50, "Date": "2026-07-18T14:20:00Z", "Remarks": "Opening stock"},
    {"TransactionID": "TXN-1006", "ProductID": "PRD-1004", "TransactionType": "Stock Out", "Quantity": 5, "Date": "2026-07-25T11:00:00Z", "Remarks": "Office use stockout"},
    {"TransactionID": "TXN-1007", "ProductID": "PRD-1005", "TransactionType": "Stock In", "Quantity": 3, "Date": "2026-07-22T16:50:00Z", "Remarks": "Sample package"}
]

def load_db():
    if not os.path.exists(DB_FILE):
        data = {
            "categories": DEFAULT_CATEGORIES,
            "suppliers": DEFAULT_SUPPLIERS,
            "products": DEFAULT_PRODUCTS,
            "transactions": DEFAULT_TRANSACTIONS
        }
        save_db(data)
        return data
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        # fallback
        return {
            "categories": DEFAULT_CATEGORIES,
            "suppliers": DEFAULT_SUPPLIERS,
            "products": DEFAULT_PRODUCTS,
            "transactions": DEFAULT_TRANSACTIONS
        }

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Load database into Session State
if 'db' not in st.session_state:
    st.session_state['db'] = load_db()

# Helper getters
def get_categories():
    return st.session_state['db']['categories']

def get_suppliers():
    return st.session_state['db']['suppliers']

def get_products():
    return st.session_state['db']['products']

def get_transactions():
    return st.session_state['db']['transactions']

def commit_changes():
    save_db(st.session_state['db'])

# ==========================================================================
# 2. STREAMLIT APP CONFIG & STYLES
# ==========================================================================
st.set_page_config(
    page_title="Smart Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme CSS
st.markdown("""
<style>
    /* Professional business color variables */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* KPI Card styling */
    .kpi-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
        flex-wrap: wrap;
    }
    
    .kpi-card {
        flex: 1;
        min-width: 200px;
        padding: 20px;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .dark .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
    }
    
    .kpi-icon {
        width: 50px;
        height: 50px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: #ffffff;
    }
    
    .bg-blue { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .bg-indigo { background: linear-gradient(135deg, #6366f1, #4f46e5); }
    .bg-orange { background: linear-gradient(135deg, #f97316, #ea580c); }
    .bg-red { background: linear-gradient(135deg, #ef4444, #b91c1c); }
    
    .kpi-content h3 {
        margin: 0;
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        margin-top: 2px;
        color: #1e293b;
    }
    
    /* Role Switcher indicators */
    .role-badge {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 12px;
        color: #ffffff;
        display: inline-block;
    }
    
    .role-admin { background-color: #2563eb; }
    .role-staff { background-color: #0d9488; }
</style>
""", unsafe_allow_dict=True, unsafe_allow_html=True)

# ==========================================================================
# 3. SIDEBAR NAVIGATION & ROLE SELECTOR
# ==========================================================================
st.sidebar.markdown("<h2 style='text-align: center; color: #1e3a8a; font-weight: 800;'>📦 SmartStock</h2>", unsafe_allow_html=True)

# Role switcher
user_role = st.sidebar.selectbox("Active Account Role", ["Admin", "Staff"])
role_badge = f'<span class="role-badge role-admin">Admin Profile</span>' if user_role == "Admin" else f'<span class="role-badge role-staff">Staff Profile</span>'
st.sidebar.markdown(f"<div style='text-align: center; margin-bottom: 20px;'>{role_badge}</div>", unsafe_allow_html=True)

# Navigation Menu
menu = st.sidebar.radio("Navigation Directory", [
    "📊 Dashboard",
    "📦 Product Catalog",
    "📁 Category Manager",
    "🚚 Supplier Directory",
    "🔄 Stock Flow Flow",
    "⚠️ Replenishment Alerts",
    "📈 Reports Center",
    "⚙️ System Settings"
])

# Lock validation helper
def check_write_permission():
    if user_role != "Admin":
        st.error("🔒 Restricted: This action requires Admin privileges.")
        return False
    return True

# Load lists
products = get_products()
categories = get_categories()
suppliers = get_suppliers()
transactions = get_transactions()

# Dynamic low stock threshold counts
low_stock_count = len([p for p in products if p["Quantity"] <= p["ReorderLevel"]])

# ==========================================================================
# MODULE 1: DASHBOARD
# ==========================================================================
if menu == "📊 Dashboard":
    st.markdown("<h1 style='font-weight: 800; letter-spacing: -0.5px;'>Dashboard Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Real-time metrics and charts of your inventory state</p>", unsafe_allow_html=True)
    
    # Pre-calculations
    total_val = sum(p["Quantity"] * p["PurchasePrice"] for p in products)
    total_items = len(products)
    total_units = sum(p["Quantity"] for p in products)
    out_stock = len([p for p in products if p["Quantity"] == 0])

    # Render CSS KPI Cards
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-icon bg-indigo">📊</div>
            <div class="kpi-content">
                <h3>Total Products</h3>
                <div class="kpi-value">{total_items} SKUs</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon bg-blue">📦</div>
            <div class="kpi-content">
                <h3>Available Stock</h3>
                <div class="kpi-value">{total_units} Units</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon bg-orange">⚠️</div>
            <div class="kpi-content">
                <h3>Low Stock Alerts</h3>
                <div class="kpi-value">{low_stock_count} Items</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon bg-red">🚨</div>
            <div class="kpi-content">
                <h3>Out of Stock</h3>
                <div class="kpi-value">{out_stock} Items</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Stock Levels vs Safety Thresholds")
        # Build pandas DataFrame for visualization
        df_stock = pd.DataFrame([{
            "Product": p["ProductName"],
            "Quantity": p["Quantity"],
            "Reorder Level": p["ReorderLevel"]
        } for p in products]).sort_values(by="Quantity").head(7)
        
        if not df_stock.empty:
            st.bar_chart(df_stock.set_index("Product"))
        else:
            st.info("No product stock levels logged.")

    with col2:
        st.subheader("Inventory Valuation Share by Category")
        cat_map = {c["CategoryID"]: c["CategoryName"] for c in categories}
        cat_shares = []
        for p in products:
            c_name = cat_map.get(p["CategoryID"], "Unknown")
            cat_shares.append({
                "Category": c_name,
                "Valuation": p["Quantity"] * p["PurchasePrice"]
            })
        df_cat = pd.DataFrame(cat_shares)
        if not df_cat.empty:
            df_cat_grouped = df_cat.groupby("Category").sum().reset_index()
            st.dataframe(df_cat_grouped.style.format({"Valuation": "${:,.2f}"}), use_container_width=True)
        else:
            st.info("No valuations cataloged.")

    # Recent Transactions Timeline
    st.markdown("### 🔄 Recent Stock Movements")
    df_txns = pd.DataFrame(transactions)
    if not df_txns.empty:
        prod_map = {p["ProductID"]: p["ProductName"] for p in products}
        df_txns["Product Name"] = df_txns["ProductID"].map(prod_map)
        df_txns_sorted = df_txns.sort_values(by="Date", ascending=False).head(5)
        st.table(df_txns_sorted[["TransactionID", "ProductID", "Product Name", "TransactionType", "Quantity", "Remarks"]])
    else:
        st.info("No transaction activities logged yet.")

# ==========================================================================
# MODULE 2: PRODUCT CATALOG
# ==========================================================================
elif menu == "📦 Product Catalog":
    st.markdown("<h1 style='font-weight: 800;'>Product Catalog</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Update items list, search barcodes, and manage quantities</p>", unsafe_allow_html=True)

    # Advanced Filters
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        search_query = st.text_input("🔍 Search by Name, ID, or Barcode").strip().lower()
    with col_f2:
        cat_options = ["All Categories"] + [c["CategoryName"] for c in categories]
        sel_cat = st.selectbox("Category Filter", cat_options)
    with col_f3:
        sup_options = ["All Suppliers"] + [s["SupplierName"] for s in suppliers]
        sel_sup = st.selectbox("Supplier Filter", sup_options)
    with col_f4:
        sel_status = st.selectbox("Stock Status", ["All Levels", "In Stock Only", "Low Stock (Safety Warnings)", "Out of Stock"])

    # Filter Logic
    cat_map_id = {c["CategoryName"]: c["CategoryID"] for c in categories}
    sup_map_id = {s["SupplierName"]: s["SupplierID"] for s in suppliers}
    
    filtered_prods = []
    for p in products:
        # Search match
        match_q = not search_query or (
            search_query in p["ProductName"].lower() or 
            search_query in p["ProductID"].lower() or 
            search_query in p["Barcode"].lower()
        )
        
        # Category match
        match_c = sel_cat == "All Categories" or p["CategoryID"] == cat_map_id.get(sel_cat)
        
        # Supplier match
        match_s = sel_sup == "All Suppliers" or p["SupplierID"] == sup_map_id.get(sel_sup)
        
        # Status match
        match_stat = True
        if sel_status == "In Stock Only":
            match_stat = p["Quantity"] > p["ReorderLevel"]
        elif sel_status == "Low Stock (Safety Warnings)":
            match_stat = 0 < p["Quantity"] <= p["ReorderLevel"]
        elif sel_status == "Out of Stock":
            match_stat = p["Quantity"] == 0

        if match_q and match_c and match_s and match_stat:
            filtered_prods.append(p)

    # Catalog Grid / Table display
    st.markdown(f"**Found {len(filtered_prods)} registered products.**")
    
    cat_map = {c["CategoryID"]: c["CategoryName"] for c in categories}
    sup_map = {s["SupplierID"]: s["SupplierName"] for s in suppliers}
    
    table_data = []
    for p in filtered_prods:
        c_name = cat_map.get(p["CategoryID"], "N/A")
        s_name = sup_map.get(p["SupplierID"], "N/A")
        
        status = "🟢 In Stock"
        if p["Quantity"] == 0:
            status = "🔴 Out of Stock"
        elif p["Quantity"] <= p["ReorderLevel"]:
            status = "🟡 Low Stock"
            
        table_data.append({
            "ProductID": p["ProductID"],
            "Product Name": p["ProductName"],
            "Category": c_name,
            "Supplier": s_name,
            "Buy Price": f"${p['PurchasePrice']:.2f}",
            "Sell Price": f"${p['SellingPrice']:.2f}",
            "Qty": p["Quantity"],
            "Safety Level": p["ReorderLevel"],
            "Status": status,
            "Barcode": p["Barcode"]
        })
        
    if table_data:
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)
    else:
        st.warning("No products found matching active filters.")

    # CRUD Controls in Expander
    st.markdown("---")
    st.subheader("Manage Inventory Items")
    
    tabs = st.tabs(["🆕 Add Product", "✏️ Edit Product", "❌ Delete Product"])
    
    with tabs[0]:
        st.markdown("##### Register a New Product SKU")
        if user_role != "Admin":
            st.info("🔒 Creation restricted to Admin mode only.")
        else:
            with st.form("add_product_form"):
                ap_name = st.text_input("Product Name *")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    ap_cat = st.selectbox("Category", [c["CategoryName"] for c in categories])
                with col_p2:
                    ap_sup = st.selectbox("Supplier", [s["SupplierName"] for s in suppliers])
                
                col_p3, col_p4, col_p5 = st.columns(3)
                with col_p3:
                    ap_buy = st.number_input("Purchase Price ($) *", min_value=0.0, step=0.01)
                with col_p4:
                    ap_sell = st.number_input("Selling Price ($) *", min_value=0.0, step=0.01)
                with col_p5:
                    ap_qty = st.number_input("Opening Quantity *", min_value=0, step=1)
                    
                col_p6, col_p7 = st.columns(2)
                with col_p6:
                    ap_reorder = st.number_input("Safety Reorder Level *", min_value=0, step=1)
                with col_p7:
                    ap_barcode = st.text_input("Barcode (Optional)")
                    
                ap_theme = st.selectbox("Image Theme Color Mode", ["electronics", "office", "furniture", "apparel"])
                
                ap_submit = st.form_submit_button("Save Product details")
                
                if ap_submit:
                    if not ap_name:
                        st.error("Product name field is required.")
                    elif ap_sell < ap_buy:
                        st.warning("Warning: Selling price is set below Purchase Cost.")
                    else:
                        # Generate Product ID
                        max_id = 1000
                        for p in products:
                            try:
                                parts = p["ProductID"].split("-")
                                if len(parts) > 1:
                                    max_id = max(max_id, int(parts[1]))
                            except ValueError:
                                pass
                        new_id = f"PRD-{max_id + 1}"
                        
                        new_prod = {
                            "ProductID": new_id,
                            "ProductName": ap_name,
                            "CategoryID": cat_map_id.get(ap_cat),
                            "SupplierID": sup_map_id.get(ap_sup),
                            "PurchasePrice": ap_buy,
                            "SellingPrice": ap_sell,
                            "Quantity": ap_qty,
                            "ReorderLevel": ap_reorder,
                            "Barcode": ap_barcode,
                            "Image": ap_theme,
                            "CreatedDate": datetime.utcnow().isoformat() + "Z"
                        }
                        
                        products.append(new_prod)
                        
                        # Log Stock In transaction
                        if ap_qty > 0:
                            max_txn = 1000
                            for t in transactions:
                                try:
                                    parts = t["TransactionID"].split("-")
                                    if len(parts) > 1:
                                        max_txn = max(max_txn, int(parts[1]))
                                except ValueError:
                                    pass
                            new_txn_id = f"TXN-{max_txn + 1}"
                            
                            transactions.append({
                                "TransactionID": new_txn_id,
                                "ProductID": new_id,
                                "TransactionType": "Stock In",
                                "Quantity": ap_qty,
                                "Date": datetime.utcnow().isoformat() + "Z",
                                "Remarks": "Initial quantity set upon product creation"
                            })
                            
                        commit_changes()
                        st.success(f"Success: Registered {new_id} ({ap_name}) successfully.")
                        st.rerun()

    with tabs[1]:
        st.markdown("##### Modify Existing Product details")
        if user_role != "Admin":
            st.info("🔒 Edits restricted to Admin mode only.")
        else:
            ep_id = st.selectbox("Select Product SKU to Edit", [p["ProductID"] for p in products])
            selected_prod = next((p for p in products if p["ProductID"] == ep_id), None)
            
            if selected_prod:
                with st.form("edit_product_form"):
                    ep_name = st.text_input("Product Name", value=selected_prod["ProductName"])
                    
                    cat_index = 0
                    cat_ids = [c["CategoryID"] for c in categories]
                    if selected_prod["CategoryID"] in cat_ids:
                        cat_index = cat_ids.index(selected_prod["CategoryID"])
                        
                    sup_index = 0
                    sup_ids = [s["SupplierID"] for s in suppliers]
                    if selected_prod["SupplierID"] in sup_ids:
                        sup_index = sup_ids.index(selected_prod["SupplierID"])
                        
                    col_ep1, col_ep2 = st.columns(2)
                    with col_ep1:
                        ep_cat = st.selectbox("Category", [c["CategoryName"] for c in categories], index=cat_index)
                    with col_ep2:
                        ep_sup = st.selectbox("Supplier", [s["SupplierName"] for s in suppliers], index=sup_index)
                        
                    col_ep3, col_ep4, col_ep5 = st.columns(3)
                    with col_ep3:
                        ep_buy = st.number_input("Purchase Price ($)", min_value=0.0, step=0.01, value=float(selected_prod["PurchasePrice"]))
                    with col_ep4:
                        ep_sell = st.number_input("Selling Price ($)", min_value=0.0, step=0.01, value=float(selected_prod["SellingPrice"]))
                    with col_ep5:
                        st.info(f"Quantity: {selected_prod['Quantity']} (Adjust in Stock Flow)")
                        
                    col_ep6, col_ep7 = st.columns(2)
                    with col_ep6:
                        ep_reorder = st.number_input("Safety Reorder Level", min_value=0, step=1, value=int(selected_prod["ReorderLevel"]))
                    with col_ep7:
                        ep_barcode = st.text_input("Barcode", value=selected_prod["Barcode"])
                        
                    ep_submit = st.form_submit_button("Update Product Profile")
                    
                    if ep_submit:
                        selected_prod["ProductName"] = ep_name
                        selected_prod["CategoryID"] = cat_map_id.get(ep_cat)
                        selected_prod["SupplierID"] = sup_map_id.get(ep_sup)
                        selected_prod["PurchasePrice"] = ep_buy
                        selected_prod["SellingPrice"] = ep_sell
                        selected_prod["ReorderLevel"] = ep_reorder
                        selected_prod["Barcode"] = ep_barcode
                        
                        commit_changes()
                        st.success(f"Product {ep_id} details updated.")
                        st.rerun()

    with tabs[2]:
        st.markdown("##### Remove Product SKU from DB")
        if user_role != "Admin":
            st.info("🔒 Deletion restricted to Admin mode only.")
        else:
            dp_id = st.selectbox("Select Product SKU to Delete", [p["ProductID"] for p in products], key="del_prod")
            dp_submit = st.button("Permanently Delete Product", type="secondary")
            
            if dp_submit:
                # Remove product
                st.session_state['db']['products'] = [p for p in products if p["ProductID"] != dp_id]
                # Remove transactions
                st.session_state['db']['transactions'] = [t for t in transactions if t["ProductID"] != dp_id]
                commit_changes()
                st.success(f"Success: Product {dp_id} and all related logs wiped.")
                st.rerun()

# ==========================================================================
# MODULE 3: CATEGORY MANAGER
# ==========================================================================
elif menu == "📁 Category Manager":
    st.markdown("<h1 style='font-weight: 800;'>Category Management</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Configure structural classes and group products</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Registered Categories List")
        cat_data = []
        for c in categories:
            count = len([p for p in products if p["CategoryID"] == c["CategoryID"]])
            val = sum(p["Quantity"] * p["PurchasePrice"] for p in products if p["CategoryID"] == c["CategoryID"])
            cat_data.append({
                "CategoryID": c["CategoryID"],
                "Category Name": c["CategoryName"],
                "Active Products": count,
                "Category Asset Valuation": f"${val:,.2f}"
            })
        st.dataframe(pd.DataFrame(cat_data), use_container_width=True)

    with col2:
        st.subheader("Manage Categories")
        cat_ops = st.tabs(["🆕 Add", "✏️ Edit", "❌ Delete"])
        
        with cat_ops[0]:
            if user_role != "Admin":
                st.info("🔒 Create locked.")
            else:
                new_cat_name = st.text_input("New Category Name", key="ac_name")
                ac_btn = st.button("Save Category", key="ac_btn")
                if ac_btn and new_cat_name.strip():
                    max_id = max(int(c["CategoryID"]) for c in categories) if categories else 0
                    categories.append({
                        "CategoryID": str(max_id + 1),
                        "CategoryName": new_cat_name.strip()
                    })
                    commit_changes()
                    st.success(f"Added Category: {new_cat_name}")
                    st.rerun()

        with cat_ops[1]:
            if user_role != "Admin":
                st.info("🔒 Edit locked.")
            else:
                ec_id = st.selectbox("Category to Edit", [c["CategoryID"] for c in categories], format_func=lambda x: next(c["CategoryName"] for c in categories if c["CategoryID"] == x))
                ec_name = st.text_input("Updated Name", key="ec_name")
                ec_btn = st.button("Update Category Name", key="ec_btn")
                if ec_btn and ec_name.strip():
                    cat = next(c for c in categories if c["CategoryID"] == ec_id)
                    cat["CategoryName"] = ec_name.strip()
                    commit_changes()
                    st.success("Category details updated.")
                    st.rerun()

        with cat_ops[2]:
            if user_role != "Admin":
                st.info("🔒 Delete locked.")
            else:
                dc_id = st.selectbox("Category to Delete", [c["CategoryID"] for c in categories], format_func=lambda x: next(c["CategoryName"] for c in categories if c["CategoryID"] == x), key="del_cat_box")
                dc_btn = st.button("Remove Category", key="dc_btn")
                if dc_btn:
                    # Check usage
                    if any(p["CategoryID"] == dc_id for p in products):
                        st.error("Error: Cannot delete category. Active items are currently assigned to it.")
                    else:
                        st.session_state['db']['categories'] = [c for c in categories if c["CategoryID"] != dc_id]
                        commit_changes()
                        st.success("Category removed.")
                        st.rerun()

# ==========================================================================
# MODULE 4: SUPPLIER DIRECTORY
# ==========================================================================
elif menu == "🚚 Supplier Directory":
    st.markdown("<h1 style='font-weight: 800;'>Supplier Wholesalers Directory</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>View vendor details and direct shipping logistics</p>", unsafe_allow_html=True)

    # Grid Display
    for i in range(0, len(suppliers), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(suppliers):
                s = suppliers[i + j]
                with cols[j]:
                    sup_items = len([p for p in products if p["SupplierID"] == s["SupplierID"]])
                    st.markdown(f"""
                    <div style="background-color:#f8fafc; border:1px solid #e2e8f0; padding:20px; border-radius:12px; margin-bottom:15px;">
                        <h4 style="color:#1e3a8a; margin:0 0 5px 0;">{s['SupplierName']}</h4>
                        <p style="font-size:12px; color:#2563eb; font-weight:600; margin:0 0 10px 0;">👤 Contact: {s['ContactPerson']}</p>
                        <div style="font-size:12px; color:#475569;">
                            <div>📞 Phone: {s['Phone']}</div>
                            <div>✉️ Email: {s['Email']}</div>
                            <div>📍 Address: {s.get('Address', 'No Address')}</div>
                        </div>
                        <hr style="margin:10px 0;">
                        <div style="font-weight:700; color:#0f172a; font-size:12px;">Active SKUs Supplied: {sup_items}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Manage Supplier Expanders
    st.markdown("---")
    st.subheader("Manage Wholesaler directory profiles")
    sup_tabs = st.tabs(["🆕 Add Supplier", "✏️ Edit Supplier", "❌ Delete Supplier"])

    with sup_tabs[0]:
        if user_role != "Admin":
            st.info("🔒 Register locked.")
        else:
            with st.form("add_supplier_form"):
                as_name = st.text_input("Business Name *")
                as_person = st.text_input("Contact Name *")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    as_phone = st.text_input("Phone Number *")
                with col_s2:
                    as_email = st.text_input("Email *")
                as_addr = st.text_area("Address")
                as_submit = st.form_submit_button("Register Supplier")
                
                if as_submit:
                    if not as_name or not as_person or not as_phone or not as_email:
                        st.error("All asterisk (*) fields are required.")
                    else:
                        max_id = max(int(s["SupplierID"]) for s in suppliers) if suppliers else 0
                        suppliers.append({
                            "SupplierID": str(max_id + 1),
                            "SupplierName": as_name,
                            "ContactPerson": as_person,
                            "Phone": as_phone,
                            "Email": as_email,
                            "Address": as_addr
                        })
                        commit_changes()
                        st.success(f"Supplier {as_name} registered.")
                        st.rerun()

    with sup_tabs[1]:
        if user_role != "Admin":
            st.info("🔒 Edit locked.")
        else:
            es_id = st.selectbox("Wholesaler Profile to Edit", [s["SupplierID"] for s in suppliers], format_func=lambda x: next(s["SupplierName"] for s in suppliers if s["SupplierID"] == x))
            selected_sup = next(s for s in suppliers if s["SupplierID"] == es_id)
            if selected_sup:
                with st.form("edit_supplier_form"):
                    es_name = st.text_input("Business Name", value=selected_sup["SupplierName"])
                    es_person = st.text_input("Contact Name", value=selected_sup["ContactPerson"])
                    col_es1, col_es2 = st.columns(2)
                    with col_es1:
                        es_phone = st.text_input("Phone", value=selected_sup["Phone"])
                    with col_es2:
                        es_email = st.text_input("Email", value=selected_sup["Email"])
                    es_addr = st.text_area("Address", value=selected_sup.get("Address", ""))
                    es_submit = st.form_submit_button("Update Wholesaler details")
                    
                    if es_submit:
                        selected_sup["SupplierName"] = es_name
                        selected_sup["ContactPerson"] = es_person
                        selected_sup["Phone"] = es_phone
                        selected_sup["Email"] = es_email
                        selected_sup["Address"] = es_addr
                        commit_changes()
                        st.success("Supplier profile updated.")
                        st.rerun()

    with sup_tabs[2]:
        if user_role != "Admin":
            st.info("🔒 Delete locked.")
        else:
            ds_id = st.selectbox("Wholesaler Profile to Delete", [s["SupplierID"] for s in suppliers], format_func=lambda x: next(s["SupplierName"] for s in suppliers if s["SupplierID"] == x), key="del_sup_box")
            ds_btn = st.button("Delete Wholesaler Profile")
            if ds_btn:
                if any(p["SupplierID"] == ds_id for p in products):
                    st.error("Error: Cannot delete supplier. Active items are currently assigned to them.")
                else:
                    st.session_state['db']['suppliers'] = [s for s in suppliers if s["SupplierID"] != ds_id]
                    commit_changes()
                    st.success("Supplier profile removed.")
                    st.rerun()

# ==========================================================================
# MODULE 5: STOCK FLOW FLOW
# ==========================================================================
elif menu == "🔄 Stock Flow Flow":
    st.markdown("<h1 style='font-weight: 800;'>Stock Flow Transactions Logger</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Post warehouse intake/shipping actions or check historical logs</p>", unsafe_allow_html=True)

    # Split: Form and Audit Logs
    col_st1, col_st2 = st.columns([1, 2])

    with col_st1:
        st.subheader("Post Stock Shift")
        with st.form("txn_form"):
            t_prod = st.selectbox("Select Product SKU", [p["ProductID"] for p in products], format_func=lambda x: f"{x} - {next(p['ProductName'] for p in products if p['ProductID'] == x)} ({next(p['Quantity'] for p in products if p['ProductID'] == x)} available)")
            t_type = st.selectbox("Transaction Flow Type", ["Stock In", "Stock Out"])
            t_qty = st.number_input("Quantity *", min_value=1, step=1)
            t_notes = st.text_input("Remarks / Reference Notes")
            t_submit = st.form_submit_button("Post Transaction")

            if t_submit:
                prod = next(p for p in products if p["ProductID"] == t_prod)
                
                # Check Out of stock validation
                if t_type == "Stock Out" and t_qty > prod["Quantity"]:
                    st.error(f"Error: Deducted quantity ({t_qty}) exceeds available warehouse stock ({prod['Quantity']}).")
                else:
                    # Update product quantity
                    if t_type == "Stock In":
                        prod["Quantity"] += t_qty
                    else:
                        prod["Quantity"] -= t_qty
                        
                    # Save transaction
                    max_txn = 1000
                    for t in transactions:
                        try:
                            parts = t["TransactionID"].split("-")
                            if len(parts) > 1:
                                max_txn = max(max_txn, int(parts[1]))
                        except ValueError:
                            pass
                    new_txn_id = f"TXN-{max_txn + 1}"
                    
                    transactions.append({
                        "TransactionID": new_txn_id,
                        "ProductID": t_prod,
                        "TransactionType": t_type,
                        "Quantity": t_qty,
                        "Date": datetime.utcnow().isoformat() + "Z",
                        "Remarks": t_notes
                    })
                    
                    commit_changes()
                    st.success(f"Posted transaction {new_txn_id} successfully.")
                    st.rerun()

    with col_st2:
        st.subheader("Transaction Audit Log")
        
        # Filter transactions
        st_filter = st.selectbox("Filter History by Type", ["All Movements", "Stock In Only", "Stock Out Only"])
        
        df_hist = pd.DataFrame(transactions)
        if not df_hist.empty:
            df_hist_sorted = df_hist.sort_values(by="Date", ascending=False)
            
            if st_filter == "Stock In Only":
                df_hist_sorted = df_hist_sorted[df_hist_sorted["TransactionType"] == "Stock In"]
            elif st_filter == "Stock Out Only":
                df_hist_sorted = df_hist_sorted[df_hist_sorted["TransactionType"] == "Stock Out"]
                
            st.dataframe(df_hist_sorted[["TransactionID", "ProductID", "TransactionType", "Quantity", "Date", "Remarks"]], use_container_width=True)
        else:
            st.info("No transaction logs recorded.")

# ==========================================================================
# MODULE 6: REPLENISHMENT ALERTS
# ==========================================================================
elif menu == "⚠️ Replenishment Alerts":
    st.markdown("<h1 style='font-weight: 800;'>Replenishment Warnings Panel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Critical catalog products matching or falling below designated safety levels</p>", unsafe_allow_html=True)

    low_items = [p for p in products if p["Quantity"] <= p["ReorderLevel"]]

    if not low_items:
        st.success("✅ Marvelous! All warehouse items hold healthy margins.")
    else:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #ffe4e6 0%, #ffedd5 100%); border:1px solid #ffe4e6; padding:20px; border-radius:12px; margin-bottom:20px; color:#0f172a;">
            <h4 style="margin:0 0 5px 0; font-weight:800;">🚨 {len(low_items)} Critical Stock Safety Violations</h4>
            <p style="font-size:12px; margin:0;">Warehouse quantities are immediately low. Trigger restock PO requests to avoid supply gaps.</p>
        </div>
        """, unsafe_allow_html=True)

        sup_map = {s["SupplierID"]: s["SupplierName"] for s in suppliers}
        
        alert_data = []
        for p in low_items:
            alert_data.append({
                "SKU": p["ProductID"],
                "Name": p["ProductName"],
                "Supplier": sup_map.get(p["SupplierID"], "N/A"),
                "Current Qty": p["Quantity"],
                "Reorder Safety Margin": p["ReorderLevel"],
                "Severity": "🔴 Depleted" if p["Quantity"] == 0 else "🟠 Low Level"
            })
            
        st.dataframe(pd.DataFrame(alert_data), use_container_width=True)

        # Bulk Quick reorder action
        st.markdown("---")
        st.subheader("Emergency Stock Procurement Action")
        reorder_btn = st.button("Bulk Procurement Trigger (+25 Units to All Low Stock)", type="primary")
        if reorder_btn:
            for p in low_items:
                p["Quantity"] += 25
                
                # Write log
                max_txn = 1000
                for t in transactions:
                    try:
                        parts = t["TransactionID"].split("-")
                        if len(parts) > 1:
                            max_txn = max(max_txn, int(parts[1]))
                    except ValueError:
                        pass
                new_txn_id = f"TXN-{max_txn + 1}"
                
                transactions.append({
                    "TransactionID": new_txn_id,
                    "ProductID": p["ProductID"],
                    "TransactionType": "Stock In",
                    "Quantity": 25,
                    "Date": datetime.utcnow().isoformat() + "Z",
                    "Remarks": "Bulk automated safety replenishment trigger"
                })
                
            commit_changes()
            st.success("Procurement command executed. Stored balances replenished.")
            st.rerun()

# ==========================================================================
# MODULE 7: REPORTS CENTER
# ==========================================================================
elif menu == "📈 Reports Center":
    st.markdown("<h1 style='font-weight: 800;'>Executive Reporting Desk</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Download analytical summaries and stock margins metrics</p>", unsafe_allow_html=True)

    # Summarize stats
    total_asset_val = sum(p["Quantity"] * p["PurchasePrice"] for p in products)
    total_selling_val = sum(p["Quantity"] * p["SellingPrice"] for p in products)
    profit_margin = total_selling_val - total_asset_val
    
    avg_markup = 0
    markup_items = [p for p in products if p["PurchasePrice"] > 0]
    if markup_items:
        avg_markup = sum(((p["SellingPrice"] - p["PurchasePrice"]) / p["PurchasePrice"]) * 100 for p in markup_items) / len(markup_items)

    rep_col1, rep_col2, rep_col3, rep_col4 = st.columns(4)
    with rep_col1:
        st.metric("Total Asset Value (Cost)", f"${total_asset_val:,.2f}")
    with rep_col2:
        st.metric("Retail Potential Value", f"${total_selling_val:,.2f}")
    with rep_col3:
        st.metric("Projected Margin Surplus", f"${profit_margin:,.2f}")
    with rep_col4:
        st.metric("Average Portfolio Markup", f"{avg_markup:.1f}%")

    # Categories Summary Table
    st.markdown("### Category Value Summary")
    cat_summary = []
    cat_map = {c["CategoryID"]: c["CategoryName"] for c in categories}
    
    for c_id, c_name in cat_map.items():
        c_prods = [p for p in products if p["CategoryID"] == c_id]
        c_skus = len(c_prods)
        c_qty = sum(p["Quantity"] for p in c_prods)
        c_cost = sum(p["Quantity"] * p["PurchasePrice"] for p in c_prods)
        c_retail = sum(p["Quantity"] * p["SellingPrice"] for p in c_prods)
        
        cat_summary.append({
            "Category Name": c_name,
            "Unique SKUs": c_skus,
            "Total Units": c_qty,
            "Total Cost Value": f"${c_cost:,.2f}",
            "Total Selling Value": f"${c_retail:,.2f}"
        })
        
    df_rep = pd.DataFrame(cat_summary)
    st.dataframe(df_rep, use_container_width=True)

    # Downloads section
    st.markdown("### Export Spreadsheet Reports")
    
    csv_raw = "Product ID,Product Name,Category ID,Supplier ID,Purchase Price,Selling Price,Quantity,Reorder Level,Barcode,Created Date\n"
    for p in products:
        csv_raw += f"{p['ProductID']},{p['ProductName']},{p['CategoryID']},{p['SupplierID']},{p['PurchasePrice']},{p['SellingPrice']},{p['Quantity']},{p['ReorderLevel']},{p['Barcode']},{p['CreatedDate']}\n"
        
    st.download_button(
        label="Download Full Inventory CSV",
        data=csv_raw,
        file_name=f"smartstock_report_{datetime.utcnow().strftime('%Y-%m-%d')}.csv",
        mime="text/csv"
    )

# ==========================================================================
# MODULE 8: SYSTEM SETTINGS
# ==========================================================================
elif menu == "⚙️ System Settings":
    st.markdown("<h1 style='font-weight: 800;'>System Configuration Panel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Manage JSON database disaster backup files and data defaults</p>", unsafe_allow_html=True)

    st.subheader("Disaster Recovery Controls")
    
    col_set1, col_set2 = st.columns(2)
    
    with col_set1:
        st.markdown("##### Download Database Backup")
        st.write("Extract the full schema contents into a single-file JSON layout to share terminals or save archives.")
        
        # Load db text
        db_string = json.dumps(st.session_state['db'], indent=4)
        st.download_button(
            label="Download database JSON",
            data=db_string,
            file_name="smartstock_database_backup.json",
            mime="application/json"
        )
        
    with col_set2:
        st.markdown("##### Restore Database Backup")
        st.write("Overwrite current browser records with a previously exported JSON dataset backup.")
        if user_role != "Admin":
            st.info("🔒 Restricted: Requires Admin role switching.")
        else:
            uploaded_file = st.file_uploader("Upload database JSON", type="json")
            if uploaded_file is not None:
                try:
                    uploaded_data = json.load(uploaded_file)
                    if all(k in uploaded_data for k in ["categories", "suppliers", "products", "transactions"]):
                        st.session_state['db'] = uploaded_data
                        commit_changes()
                        st.success("Disaster Recovery: Database state restored successfully.")
                        st.rerun()
                    else:
                        st.error("Error: JSON does not match database schema requirements.")
                except Exception as e:
                    st.error(f"Error parsing file: {e}")

    st.markdown("---")
    st.subheader("Factory Wipe Settings")
    if user_role != "Admin":
        st.info("🔒 Factory Wipe restricted to Admin mode only.")
    else:
        st.write("Clear all custom profiles, logs, and categories to restore the system default seed data.")
        wipe_btn = st.button("Reset DB to default settings", type="secondary")
        if wipe_btn:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            del st.session_state['db']
            st.success("Wipe command logged. Reloading application defaults...")
            st.rerun()
