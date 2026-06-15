import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta
import base64
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="BSG Global Export Portal", 
    page_icon="🌍", 
    layout="centered"
)

# ============================================
# PASSWORD PROTECTION SYSTEM
# ============================================

def make_hashes(password):
    """Create password hash"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """Check password against hash"""
    if make_hashes(password) == hashed_text:
        return True
    return False

# User database (in production, use a real database)
# Default passwords - CHANGE THESE!
USER_CREDENTIALS = {
    "admin": {
        "password_hash": make_hashes("BSGadmin2026!"),  # Change this!
        "name": "Lizelle Kruger",
        "role": "Administrator"
    },
    "sales": {
        "password_hash": make_hashes("BSGsales2026!"),  # Change this!
        "name": "Sales Team",
        "role": "Sales"
    },
    "guest": {
        "password_hash": make_hashes("BSGguest2026!"),  # Change this!
        "name": "Guest User",
        "role": "Viewer"
    }
}

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0

def login_page():
    """Display login form"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.image("https://via.placeholder.com/150x50?text=BSG+Logo", width=150)
        st.markdown("### 🔐 BSG Export Portal")
        st.markdown("Please login to continue")
        
        # Check for too many attempts
        if st.session_state.login_attempts >= 3:
            st.error("🚫 Too many failed attempts. Please wait 30 seconds.")
            st.info("Contact: lizelle@bsg-global.co.za")
            return
        
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter password")
        
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Login", use_container_width=True):
                if username in USER_CREDENTIALS:
                    if check_hashes(password, USER_CREDENTIALS[username]['password_hash']):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.login_attempts = 0
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(f"❌ Wrong password! Attempts: {st.session_state.login_attempts}/3")
                else:
                    st.session_state.login_attempts += 1
                    st.error(f"❌ User not found! Attempts: {st.session_state.login_attempts}/3")
        
        with col_b:
            if st.button("Clear", use_container_width=True):
                st.session_state.login_attempts = 0
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Help section
        with st.expander("ℹ️ Need Help?"):
            st.markdown("""
            **Default Credentials:**
            - Admin: username `admin` / password `BSGadmin2026!`
            - Sales: username `sales` / password `BSGsales2026!`
            - Guest: username `guest` / password `BSGguest2026!`
            
            **Forgot password?** Contact IT Support
            """)

def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# ============================================
# MAIN APPLICATION
# ============================================

# Check if user is authenticated
if not st.session_state.authenticated:
    login_page()
    st.stop()  # Stop execution if not logged in

# If authenticated, show the main app
st.success(f"✅ Logged in as: **{USER_CREDENTIALS[st.session_state.username]['name']}** ({USER_CREDENTIALS[st.session_state.username]['role']})")

# Logout button in sidebar
with st.sidebar:
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# ============================================
# REST OF YOUR APPLICATION
# ============================================

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f7f9fa; }
    h1 { color: #1e3d2f; font-family: 'Helvetica', sans-serif; }
    .stButton>button { background-color: #1e3d2f; color: white; border-radius: 5px; }
    .security-badge {
        background: linear-gradient(135deg, #1e3d2f, #2e5d3f);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 BSG Global Wholesale (Pty) Ltd")
st.subheader("B2B Commercial Export Document Generator")

# Security badge
st.markdown(f'<span class="security-badge">🔒 Secured Access - {st.session_state.username}</span>', unsafe_allow_html=True)

# Sidebar Setup
st.sidebar.header("🏢 Exporter Directory")
st.sidebar.markdown("""
**Company:** BSG Global Wholesale (Pty) Ltd  
**Address:** 43 Barbet Crescent, Aston Bay, Jeffreys Bay, 6332, South Africa  
**Contact:** Lizelle Kruger  
**Email:** lizelle@bsg-global.co.za  
**Phone:** +27 (0) 78 368 0923  
""")

# Product Database
PRODUCT_DATABASE = {
    "Organic Rooibos Tea (Superior Short Cut)": {
        "unit": "kg",
        "default_price": 8.50,
        "botanical": "Aspalathus linearis",
        "packaging": "18kg multi-wall bags on standard pallet",
        "port": "Port of Cape Town",
        "hs_code": "1212.99",
        "origin": "Cederberg Region, Western Cape"
    },
    "Virgin Cold-Pressed Marula Oil": {
        "unit": "Litre",
        "default_price": 25.00,
        "botanical": "Sclerocarya birrea",
        "packaging": "200L UV-protected Steel Drums",
        "port": "Port of Port Elizabeth (Gqeberha)",
        "hs_code": "1515.90",
        "origin": "Limpopo Province, South Africa"
    }
}

# Interactive Data Input Form
st.header("📄 Create New Export Quotation")

# Role-based access
if USER_CREDENTIALS[st.session_state.username]['role'] == "Viewer":
    st.warning("⚠️ View-only mode. You cannot create quotations.")
else:
    with st.form("quote_form"):
        col1, col2 = st.columns(2)
        with col1:
            quote_no = st.text_input("Quotation Number", value=f"BSG-{datetime.now().year}-EU001")
            client_name = st.text_input("Buyer Company Name", value="Dutch Cosmetic Distributors BV")
            client_address = st.text_area("Buyer Address", value="Keizersgracht 421, 1016 EK Amsterdam, Netherlands")
        with col2:
            date_issue = st.date_input("Date of Issue", datetime.today())
            product_select = st.selectbox("Select Botanical Product", list(PRODUCT_DATABASE.keys()))
            qty = st.number_input("Quantity", min_value=1.0, value=900.0, step=1.0)
        
        # Get product info
        product_info = PRODUCT_DATABASE[product_select]
        
        unit_price = st.number_input(f"Unit Price (€/{product_info['unit']})", min_value=0.0, value=product_info['default_price'])
        
        submitted = st.form_submit_button("Compile Export Pack")

    # Processing
    if submitted:
        total_val = qty * unit_price
        st.success(f"Quotation {quote_no} successfully calculated! Total: €{total_val:,.2f}")
        
        # PDF Generator Class
        class ExportPDF(FPDF):
            def header(self):
                self.set_fill_color(30, 61, 47)
                self.rect(0, 0, 210, 35, 'F')
                self.set_text_color(255, 255, 255)
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'BSG GLOBAL WHOLESALE (PTY) LTD', ln=True, align='L')
                self.set_font('Arial', '', 10)
                self.cell(0, 5, 'Global Sourcing & Trade Logistics | Aston Bay, South Africa', ln=True, align='L')
                self.ln(12)

            def footer(self):
                self.set_y(-25)
                self.set_font('Arial', 'I', 8)
                self.set_text_color(128, 128, 128)
                self.cell(0, 10, 'Authorized Export Profile - Issued under EU-SADC Economic Partnership Agreement', align='C')

        # Build PDF
        pdf = ExportPDF()
        pdf.add_page()
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        
        # Metadata Block
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(100, 6, f"QUOTE NO: {quote_no}")
        pdf.cell(0, 6, f"DATE: {date_issue.strftime('%d %B %Y')}", ln=True, align='R')
        pdf.ln(5)
        
        # Addresses
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(100, 5, "EXPORTER:")
        pdf.cell(0, 5, "PREPARED FOR:", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.cell(100, 4, "BSG Global Wholesale (Pty) Ltd")
        pdf.cell(0, 4, client_name, ln=True)
        pdf.cell(100, 4, "43 Barbet Crescent, Aston Bay")
        pdf.cell(0, 4, client_address.split(',')[0], ln=True)
        pdf.cell(100, 4, "Jeffreys Bay, South Africa, 6332")
        pdf.ln(10)
        
        # Financial Matrix Table
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(85, 7, "Description / Botanical Name", 1, 0, 'L', True)
        pdf.cell(25, 7, "Qty", 1, 0, 'C', True)
        pdf.cell(25, 7, "Unit Price", 1, 0, 'C', True)
        pdf.cell(35, 7, "Total (EUR)", 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 9)
        pdf.cell(85, 6, f"{product_select} ({product_info['botanical']})", 1, 0, 'L')
        pdf.cell(25, 6, f"{qty:,.2f} {product_info['unit']}", 1, 0, 'C')
        pdf.cell(25, 6, f"EUR {unit_price:,.2f}", 1, 0, 'C')
        pdf.cell(35, 6, f"EUR {total_val:,.2f}", 1, 1, 'C')
        
        # Summary Totals
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(135, 7, "TOTAL FOB COMMERCIAL VALUE:", 1, 0, 'R')
        pdf.cell(35, 7, f"EUR {total_val:,.2f}", 1, 1, 'C', True)
        pdf.ln(8)
        
        # Trade Terms
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "TRADE TERMS & SHIPPING PARAMETERS", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4, f"- Terms: FOB (Free on Board Incoterms 2020) loaded via {product_info['port']}.\n- Packaging: {product_info['packaging']}.\n- Lead Time: 14-21 business days to port from advance TT payment clearance.")
        pdf.ln(4)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "EU COMPLIANCE & TARIFF GUARANTEES", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4, "- Tariff-Free Access: Sourced under the EU-SADC Economic Partnership Agreement. EUR.1 Movement Certificate provided for 0% customs entry.\n- Framework Compliance: Sourced in strict alignment with the Nagoya Protocol and EU Cosmetic Regulations (EC) 1223/2009 parameters.")
        
        # Generate PDF
        pdf_output = pdf.output(dest='S').encode('latin-1')
        
        # Download button
        st.download_button(
            label="📥 Download Export Document (PDF)",
            data=pdf_output,
            file_name=f"BSG_Quotation_{quote_no}_{date_issue.strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <small>BSG Global Wholesale (Pty) Ltd © 2026 | Secure Access Portal</small><br>
    <small>Logged in as: {}</small>
</div>
""".format(st.session_state.username), unsafe_allow_html=True)
