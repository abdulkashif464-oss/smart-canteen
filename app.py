import streamlit as st
import pandas as pd
import time
import random

# --- CONFIGURATION & DATABASE ---
# 1. Verified Colleges (Simulating a secure database)
VERIFIED_ADMINS = {
    "krupanidhi_admin": "password123",
    "bengaluru_canteen": "admin2025"
}

# 2. Initialize Session State Variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None # "Student" or "Admin"
if 'canteen_open' not in st.session_state:
    st.session_state.canteen_open = True # Default Open
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None
if 'cart' not in st.session_state:
    st.session_state.cart = []

# 3. Menu Data
if 'menu_data' not in st.session_state:
    st.session_state.menu_data = [
        {"Item": "Samosa", "Price": 15, "Available": True},
        {"Item": "Tea", "Price": 10, "Available": True},
        {"Item": "Veg Biryani", "Price": 60, "Available": True},
    ]

st.set_page_config(page_title="Smart Canteen Pro", layout="wide")

# ==========================================
#  PART 1: LOGIN SYSTEM (Security Layer)
# ==========================================
def login_page():
    st.title("🔐 Smart Canteen Login")
    
    tab1, tab2 = st.tabs(["🎓 Student Login", "👨‍🍳 Admin Login"])

    # --- STUDENT LOGIN (OTP BASED) ---
    with tab1:
        st.subheader("Student Access")
        phone = st.text_input("Enter Mobile Number", max_chars=10)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Get OTP"):
                if len(phone) == 10:
                    # SIMULATE OTP GENERATION
                    otp = random.randint(1000, 9999)
                    st.session_state.generated_otp = otp
                    # In real life, this sends an SMS. Here, we show it on screen.
                    st.toast(f"SMS SENT: Your OTP is {otp}", icon="📱")
                    st.info(f"debug: Your OTP is {otp}") 
                else:
                    st.error("Enter valid 10-digit number")
        
        with col2:
            otp_input = st.text_input("Enter OTP", type="password")
            if st.button("Login"):
                if st.session_state.generated_otp and str(otp_input) == str(st.session_state.generated_otp):
                    st.session_state.logged_in = True
                    st.session_state.user_type = "Student"
                    st.rerun()
                else:
                    st.error("Invalid OTP")

    # --- ADMIN LOGIN (PASSWORD BASED) ---
    with tab2:
        st.subheader("Partner College Access")
        username = st.text_input("Admin Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Admin Login"):
            if username in VERIFIED_ADMINS and VERIFIED_ADMINS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user_type = "Admin"
                st.success("Verified College Account Found.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Access Denied. Contact Support to verify your college.")

# ==========================================
#  PART 2: MAIN APP
# ==========================================
def main_app():
    # Logout Button in Sidebar
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.user_type}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.rerun()

    # --- ADMIN DASHBOARD ---
    if st.session_state.user_type == "Admin":
        st.title("👨‍🍳 Canteen Control Center")
        
        # 1. GLOBAL STATUS SWITCH
        st.subheader("🏪 Shop Status")
        status_col, msg_col = st.columns([1, 3])
        with status_col:
            # The Toggle Switch
            is_open = st.toggle("Accepting Orders?", value=st.session_state.canteen_open)
            if is_open != st.session_state.canteen_open:
                st.session_state.canteen_open = is_open
                st.rerun()
        with msg_col:
            if st.session_state.canteen_open:
                st.success("🟢 STATUS: OPEN - Students can order.")
            else:
                st.error("🔴 STATUS: CLOSED - Orders paused.")

        st.markdown("---")

        # 2. MENU MANAGEMENT
        st.subheader("📋 Menu Manager")
        df = pd.DataFrame(st.session_state.menu_data)
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Menu Changes"):
            st.session_state.menu_data = edited_df.to_dict('records')
            st.toast("Menu Updated Successfully!")

    # --- STUDENT DASHBOARD ---
    elif st.session_state.user_type == "Student":
        st.title("🎓 Student Food Court")

        # 1. CHECK IF CLOSED
        if not st.session_state.canteen_open:
            st.error("🔴 The Canteen is currently CLOSED. Please check back later.")
            st.warning("Admin has paused online ordering.")
            return  # Stop loading the rest of the page

        # 2. MENU
        col_menu, col_cart = st.columns([2, 1])
        
        with col_menu:
            st.subheader("Available Items")
            df = pd.DataFrame(st.session_state.menu_data)
            # Only show available items
            available_df = df[df['Available'] == True]
            
            for index, row in available_df.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(f"**{row['Item']}**")
                    c2.write(f"₹{row['Price']}")
                    if c3.button("Add", key=index):
                        st.session_state.cart.append(row)
                        st.toast(f"Added {row['Item']}")

        # 3. CART & BILLING (The Complex Math)
        with col_cart:
            st.markdown("### 🛒 Your Bill")
            if st.session_state.cart:
                cart_df = pd.DataFrame(st.session_state.cart)
                st.dataframe(cart_df[['Item', 'Price']], hide_index=True)
                
                # --- FINANCIAL LOGIC ---
                subtotal = sum(item['Price'] for item in st.session_state.cart)
                student_fee = 1.00
                total_to_pay = subtotal + student_fee
                
                st.markdown("---")
                st.write(f"Food Total: ₹{subtotal}")
                st.write(f"App Convenience Fee: ₹{student_fee}")
                st.markdown(f"### Pay: ₹{total_to_pay}")
                
                st.info(f"ℹ️ Note: Total Platform Commission earned on this order: ₹2 (₹1 from you, ₹1 from Canteen)")

                # 4. PAYMENT & UPI
                st.markdown("#### Payment Method")
                pay_mode = st.radio("Select:", ["UPI (GPay/PhonePe)", "Cash"])
                
                if pay_mode == "UPI (GPay/PhonePe)":
                    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/220px-QR_code_for_mobile_English_Wikipedia.svg.png", width=150, caption="Scan to Pay")
                    utr = st.text_input("Enter UPI Transaction ID (UTR)")
                
                if st.button("Place Order"):
                    if pay_mode == "UPI (GPay/PhonePe)" and not utr:
                        st.error("Please enter UTR number for verification.")
                    else:
                        st.balloons()
                        st.success("✅ Order Placed! Show this screen at the counter.")
                        st.session_state.cart = [] # Clear cart

# --- APP FLOW CONTROL ---
if not st.session_state.logged_in:
    login_page()
else:
    main_app()