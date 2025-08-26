#!/usr/bin/env python3
"""
Tesla Order Status - Streamlit Web Interface

A user-friendly web interface for tracking Tesla orders without command line usage.
"""

import streamlit as st
import json
import os
import time
import base64
import hashlib
import requests
import urllib.parse
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any

# Import the original modules
from tesla_order_status import (
    TOKEN_FILE, ORDERS_FILE, HISTORY_FILE, OPTION_CODES,
    load_tokens_from_file, save_tokens_to_file, is_token_valid, refresh_tokens,
    retrieve_orders, get_order_details, save_orders_to_file, load_orders_from_file,
    load_history_from_file, save_history_to_file, compare_orders, decode_option_codes,
    truncate_timestamp, generate_code_verifier_and_challenge, exchange_code_for_tokens,
    CLIENT_ID, REDIRECT_URI, AUTH_URL, TOKEN_URL, SCOPE, CODE_CHALLENGE_METHOD, APP_VERSION
)
from tesla_stores import TeslaStore
from update_check import main as run_update_check

# Page configuration
st.set_page_config(
    page_title="Tesla Order Status Tracker",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .status-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-card {
        background-color: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    .warning-card {
        background-color: #fff3cd;
        border-color: #ffc107;
        color: #856404;
    }
    .error-card {
        background-color: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }
    .metric-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .option-code {
        background-color: #e9ecef;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        margin: 0.1rem;
        display: inline-block;
        font-family: monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'orders_data' not in st.session_state:
    st.session_state.orders_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'show_sensitive_data' not in st.session_state:
    st.session_state.show_sensitive_data = True

def check_existing_auth():
    """Check if there are existing valid tokens"""
    if os.path.exists(TOKEN_FILE):
        try:
            tokens = load_tokens_from_file()
            access_token = tokens['access_token']
            
            if is_token_valid(access_token):
                st.session_state.authenticated = True
                st.session_state.access_token = access_token
                return True
            else:
                # Try to refresh the token
                refresh_token = tokens['refresh_token']
                try:
                    new_tokens = refresh_tokens(refresh_token)
                    save_tokens_to_file(new_tokens)
                    st.session_state.authenticated = True
                    st.session_state.access_token = new_tokens['access_token']
                    return True
                except:
                    return False
        except:
            return False
    return False

def authenticate_user():
    """Handle Tesla authentication with improved UX"""
    st.markdown("### 🔐 Tesla Authentication")
    
    if check_existing_auth():
        st.success("✅ Already authenticated with valid tokens!")
        return True
    
    st.info("🚗 **Welcome to Tesla Order Status Tracker!**")
    st.markdown("""
    To track your Tesla order, you need to authenticate with your Tesla account.
    This process is secure and only happens between you and Tesla - no data is shared with third parties.
    """)
    
    # Generate code verifier and challenge if not already done
    if 'code_verifier' not in st.session_state:
        code_verifier, code_challenge = generate_code_verifier_and_challenge()
        st.session_state.code_verifier = code_verifier
        st.session_state.code_challenge = code_challenge
    
    # Create auth URL
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE,
        'state': os.urandom(16).hex(),
        'code_challenge': st.session_state.code_challenge,
        'code_challenge_method': CODE_CHALLENGE_METHOD,
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    
    st.markdown("---")
    st.markdown("### 📋 Authentication Steps")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        **Step 1:** Click the button below to open Tesla's login page in a new tab  
        **Step 2:** Log in with your Tesla account credentials  
        **Step 3:** You'll see a 'Page Not Found' error - **this is normal!**  
        **Step 4:** Copy the complete URL from your browser's address bar  
        **Step 5:** Paste it in the text field below and click authenticate  
        """)
    
    with col2:
        st.info("💡 **Tip:** The 'Page Not Found' error is expected. Just copy the URL from the address bar!")
    
    # Large, prominent button to open Tesla login
    st.markdown("### 🚀 Start Authentication")
    if st.button("🚗 Open Tesla Login Page", type="primary", use_container_width=True, help="This will open Tesla's login page in a new tab"):
        st.balloons()  # Fun animation
        st.success("🎉 Tesla login page should open in a new tab!")
        st.markdown("---")
        st.markdown("### 🔗 Tesla Login URL")
        st.markdown("If the page didn't open automatically, click the link below:")
        st.markdown(f"**[🌐 Tesla Login Page]({auth_url})**")
        
        # Show the URL in a copy-friendly format
        st.markdown("**Or copy this URL manually:**")
        st.code(auth_url, language="text")
        
        # Auto-scroll to the input field
        st.markdown("**👇 After logging in, paste the redirect URL below:**")
    
    st.markdown("---")
    st.markdown("### 📝 Complete Authentication")
    
    # Input for redirect URL with better styling
    redirect_url = st.text_input(
        "**Paste the redirect URL here:**",
        placeholder="https://auth.tesla.com/void/callback?code=NA_abc123...",
        help="After logging in to Tesla, copy the COMPLETE URL from your browser's address bar and paste it here",
        key="redirect_url_input"
    )
    
    # Show example of what URL should look like
    with st.expander("🤔 What should the URL look like?"):
        st.markdown("""
        The URL you need to paste should start with:  
        `https://auth.tesla.com/void/callback?code=`
        
        **Example:**
        ```
        https://auth.tesla.com/void/callback?code=NA_abc123def456ghi789...
        ```
        
        The code part (after `code=`) will be a long string of letters and numbers.
        """)
    
    # Authentication button
    if redirect_url and st.button("🔑 Complete Authentication", type="primary", use_container_width=True):
        try:
            with st.spinner("🔄 Validating and exchanging authentication code..."):
                # Parse the authorization code from URL
                parsed_url = urllib.parse.urlparse(redirect_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                if 'code' not in query_params:
                    st.error("❌ Invalid URL: No authentication code found. Please make sure you copied the complete URL.")
                    return False
                
                auth_code = query_params['code'][0]
                
                # Exchange code for tokens
                token_data = {
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'code': auth_code,
                    'redirect_uri': REDIRECT_URI,
                    'code_verifier': st.session_state.code_verifier,
                }
                
                response = requests.post(TOKEN_URL, data=token_data)
                response.raise_for_status()
                tokens = response.json()
            
            # Save tokens and update session state
            save_tokens_to_file(tokens)
            st.session_state.authenticated = True
            st.session_state.access_token = tokens['access_token']
            
            st.success("🎉 Authentication successful! You can now view your Tesla order status.")
            st.balloons()  # Celebration animation
            
            # Clear the redirect URL input
            if 'redirect_url_input' in st.session_state:
                del st.session_state.redirect_url_input
            
            time.sleep(2)  # Brief pause to show success message
            st.rerun()
            
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Authentication failed: Invalid or expired authorization code.")
            st.error("Please try the authentication process again.")
        except Exception as e:
            st.error(f"❌ Authentication failed: {str(e)}")
            st.error("Please make sure you copied the complete redirect URL and try again.")
    
    return st.session_state.authenticated

def fetch_order_data(force_refresh=False):
    """Fetch order data from Tesla API"""
    if not st.session_state.authenticated:
        return None
    
    # Check if we have recent cached data
    if (not force_refresh and 
        st.session_state.orders_data and 
        st.session_state.last_update and 
        datetime.now() - st.session_state.last_update < timedelta(minutes=5)):
        return st.session_state.orders_data
    
    try:
        with st.spinner("Fetching order information from Tesla..."):
            # Get orders
            orders = retrieve_orders(st.session_state.access_token)
            
            # Get detailed information for each order
            detailed_orders = []
            for order in orders:
                order_id = order['referenceNumber']
                order_details = get_order_details(order_id, st.session_state.access_token)
                
                if not order_details or not order_details.get('tasks'):
                    st.error("❌ Received empty response from Tesla API. Please try again later.")
                    return None
                
                detailed_order = {
                    'order': order,
                    'details': order_details
                }
                detailed_orders.append(detailed_order)
            
            # Save to file and session state (respects auto-save setting)
            if st.session_state.get('auto_save_orders', True):
                save_orders_to_file(detailed_orders)
            st.session_state.orders_data = detailed_orders
            st.session_state.last_update = datetime.now()
            
            # Check for changes and update history
            old_orders = load_orders_from_file()
            if old_orders:
                differences = compare_orders(old_orders, detailed_orders)
                if differences:
                    history = load_history_from_file()
                    history.append({
                        'timestamp': time.strftime('%Y-%m-%d'),
                        'changes': differences
                    })
                    save_history_to_file(history)
            
            return detailed_orders
            
    except Exception as e:
        st.error(f"❌ Error fetching order data: {str(e)}")
        return None

def display_order_summary(detailed_orders):
    """Display order summary cards"""
    if not detailed_orders:
        return
    
    st.markdown("### 📊 Order Summary")
    
    for i, detailed_order in enumerate(detailed_orders):
        order = detailed_order['order']
        order_details = detailed_order['details']
        scheduling = order_details.get('tasks', {}).get('scheduling', {})
        registration_data = order_details.get('tasks', {}).get('registration', {})
        order_info = registration_data.get('orderDetails', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Model",
                value=order.get('modelCode', 'N/A').upper(),
                help="Tesla model"
            )
        
        with col2:
            status = order.get('orderStatus', 'N/A')
            st.metric(
                label="Status",
                value=status,
                help="Current order status"
            )
        
        with col3:
            vin = order.get('vin', 'Not assigned')
            if not st.session_state.show_sensitive_data:
                vin = "***HIDDEN***" if vin != 'Not assigned' else vin
            st.metric(
                label="VIN",
                value=vin,
                help="Vehicle Identification Number"
            )
        
        with col4:
            delivery_window = scheduling.get('deliveryWindowDisplay', 'TBD')
            st.metric(
                label="Delivery Window",
                value=delivery_window,
                help="Estimated delivery timeframe"
            )

def display_detailed_order_info(detailed_orders):
    """Display detailed order information"""
    if not detailed_orders:
        return
    
    st.markdown("### 🚗 Detailed Order Information")
    
    for i, detailed_order in enumerate(detailed_orders):
        order = detailed_order['order']
        order_details = detailed_order['details']
        scheduling = order_details.get('tasks', {}).get('scheduling', {})
        registration_data = order_details.get('tasks', {}).get('registration', {})
        order_info = registration_data.get('orderDetails', {})
        final_payment_data = order_details.get('tasks', {}).get('finalPayment', {}).get('data', {})
        
        with st.expander(f"Order Details - {order.get('modelCode', 'Unknown').upper()}", expanded=True):
            # Basic order information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📋 Order Details")
                if st.session_state.show_sensitive_data:
                    st.write(f"**Order ID:** {order['referenceNumber']}")
                st.write(f"**Status:** {order['orderStatus']}")
                st.write(f"**Model:** {order['modelCode']}")
                
                vin = order.get('vin', 'N/A')
                if st.session_state.show_sensitive_data:
                    st.write(f"**VIN:** {vin}")
                else:
                    st.write(f"**VIN:** {'***HIDDEN***' if vin != 'N/A' else 'Not assigned'}")
            
            with col2:
                st.markdown("#### 📅 Timeline")
                reservation_date = truncate_timestamp(order_info.get('reservationDate', 'N/A'))
                order_booked_date = truncate_timestamp(order_info.get('orderBookedDate', 'N/A'))
                st.write(f"**Reservation Date:** {reservation_date}")
                st.write(f"**Order Booked Date:** {order_booked_date}")
                
                expected_reg_date = registration_data.get('expectedRegDate')
                if expected_reg_date:
                    st.write(f"**Expected Registration:** {truncate_timestamp(expected_reg_date)}")
            
            # Configuration options
            st.markdown("#### ⚙️ Configuration Options")
            decoded_options = decode_option_codes(order.get('mktOptions', ''))
            if decoded_options:
                option_cols = st.columns(2)
                for idx, (code, description) in enumerate(decoded_options):
                    col_idx = idx % 2
                    with option_cols[col_idx]:
                        st.markdown(f'<span class="option-code">{code}</span> {description}', 
                                  unsafe_allow_html=True)
            
            # Delivery information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🚚 Delivery Information")
                routing_location = order_info.get('vehicleRoutingLocation', 'N/A')
                tesla_store = TeslaStore(routing_location)
                st.write(f"**Routing Location:** {routing_location} ({tesla_store.label})")
                st.write(f"**Delivery Center:** {scheduling.get('deliveryAddressTitle', 'N/A')}")
                st.write(f"**Delivery Window:** {scheduling.get('deliveryWindowDisplay', 'N/A')}")
                
                eta = final_payment_data.get('etaToDeliveryCenter', 'N/A')
                if eta != 'N/A':
                    st.write(f"**ETA to Delivery Center:** {eta}")
                
                appointment = scheduling.get('apptDateTimeAddressStr', 'N/A')
                if appointment != 'N/A':
                    st.write(f"**Delivery Appointment:** {appointment}")
            
            with col2:
                st.markdown("#### 🔧 Vehicle Status")
                odometer = order_info.get('vehicleOdometer', 'N/A')
                odometer_type = order_info.get('vehicleOdometerType', '')
                st.write(f"**Vehicle Odometer:** {odometer} {odometer_type}")
                
                # Financing information
                financing_details = final_payment_data.get('financingDetails') or {}
                if financing_details:
                    st.markdown("#### 💰 Financing Information")
                    finance_partner = financing_details.get('teslaFinanceDetails', {}).get('financePartnerName', 'N/A')
                    if finance_partner != 'N/A':
                        st.write(f"**Finance Partner:** {finance_partner}")
                    
                    order_type = financing_details.get('orderType', 'N/A')
                    if order_type != 'N/A':
                        st.write(f"**Payment Type:** {order_type}")

def display_change_history():
    """Display order change history with visualizations"""
    st.markdown("### 📈 Change History")
    
    history = load_history_from_file()
    if not history:
        st.info("No change history available yet. Changes will appear here after your first update.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Recent Changes", "📊 Timeline", "🔍 Detailed History"])
    
    with tab1:
        st.markdown("#### Recent Changes (Last 30 days)")
        recent_changes = [entry for entry in history 
                         if datetime.strptime(entry['timestamp'], '%Y-%m-%d') > 
                         datetime.now() - timedelta(days=30)]
        
        if recent_changes:
            for entry in reversed(recent_changes[-10:]):  # Show last 10 changes
                with st.expander(f"Changes on {entry['timestamp']}", expanded=False):
                    for change in entry['changes']:
                        operation = change.get('operation', 'unknown')
                        key = change.get('key', 'unknown')
                        
                        if operation == 'added':
                            st.success(f"➕ Added {key}: {change.get('value', '')}")
                        elif operation == 'removed':
                            st.error(f"➖ Removed {key}: {change.get('old_value', '')}")
                        elif operation == 'changed':
                            st.warning(f"🔄 Changed {key}: {change.get('old_value', '')} → {change.get('value', '')}")
        else:
            st.info("No recent changes in the last 30 days.")
    
    with tab2:
        if history:
            # Create timeline chart
            df_changes = []
            for entry in history:
                date = entry['timestamp']
                change_count = len(entry['changes'])
                df_changes.append({'date': date, 'changes': change_count})
            
            if df_changes:
                df = pd.DataFrame(df_changes)
                df['date'] = pd.to_datetime(df['date'])
                
                fig = px.line(df, x='date', y='changes', 
                            title='Order Changes Over Time',
                            labels={'changes': 'Number of Changes', 'date': 'Date'})
                fig.update_traces(mode='markers+lines')
                st.plotly_chart(fig, use_container_width=True)
            
            # Change type distribution
            change_types = {'added': 0, 'removed': 0, 'changed': 0}
            for entry in history:
                for change in entry['changes']:
                    operation = change.get('operation', 'unknown')
                    if operation in change_types:
                        change_types[operation] += 1
            
            if any(change_types.values()):
                fig_pie = px.pie(values=list(change_types.values()), 
                               names=list(change_types.keys()),
                               title='Change Types Distribution')
                st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        st.markdown("#### Complete Change History")
        if history:
            for entry in reversed(history):
                st.markdown(f"**{entry['timestamp']}**")
                for change in entry['changes']:
                    operation = change.get('operation', 'unknown')
                    key = change.get('key', 'unknown')
                    
                    if operation == 'added':
                        st.markdown(f"  ➕ `{key}`: {change.get('value', '')}")
                    elif operation == 'removed':
                        st.markdown(f"  ➖ `{key}`: {change.get('old_value', '')}")
                    elif operation == 'changed':
                        st.markdown(f"  🔄 `{key}`: {change.get('old_value', '')} → {change.get('value', '')}")
                st.markdown("---")

def display_configuration_options():
    """Display configuration and options management"""
    st.markdown("### ⚙️ Configuration & Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔐 Privacy Settings")
        
        show_sensitive = st.checkbox(
            "Show sensitive data (Order ID, VIN)",
            value=st.session_state.show_sensitive_data,
            help="Uncheck to hide personal information for sharing"
        )
        st.session_state.show_sensitive_data = show_sensitive
        
        # Initialize auto-save setting if not exists
        if 'auto_save_orders' not in st.session_state:
            st.session_state.auto_save_orders = True
        
        auto_save = st.checkbox(
            "Automatically save order data",
            value=st.session_state.auto_save_orders,
            help="Automatically save order information for change tracking and comparison"
        )
        st.session_state.auto_save_orders = auto_save
        
        if st.button("🗑️ Clear Authentication"):
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.success("Authentication cleared. Please refresh the page.")
    
    with col2:
        st.markdown("#### 💾 Data Management")
        
        if st.button("🔄 Force Refresh Data"):
            st.session_state.orders_data = None
            st.session_state.last_update = None
            st.success("Data refresh forced. Navigate to 'Order Status' to reload.")
        
        # Manual save button when auto-save is disabled
        if not st.session_state.get('auto_save_orders', True) and st.session_state.orders_data:
            if st.button("💾 Save Order Data"):
                save_orders_to_file(st.session_state.orders_data)
                st.success("Order data saved manually!")
        
        # File information
        files_info = []
        for file_name, file_path in [
            ("Tokens", TOKEN_FILE),
            ("Orders", ORDERS_FILE),
            ("History", HISTORY_FILE)
        ]:
            exists = os.path.exists(file_path)
            size = os.path.getsize(file_path) if exists else 0
            files_info.append({"File": file_name, "Exists": "✅" if exists else "❌", "Size (KB)": f"{size/1024:.1f}"})
        
        st.dataframe(pd.DataFrame(files_info), use_container_width=True)

def display_option_codes_reference():
    """Display option codes reference"""
    st.markdown("### 📚 Tesla Option Codes Reference")
    
    if not OPTION_CODES:
        st.error("Option codes not loaded.")
        return
    
    # Search functionality
    search_term = st.text_input("🔍 Search option codes:", placeholder="Enter code or description...")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        show_all = st.checkbox("Show all codes", value=False)
    with col2:
        codes_per_page = st.selectbox("Codes per page", [50, 100, 200, 500], index=1)
    
    # Filter and display codes
    filtered_codes = OPTION_CODES
    
    if search_term:
        filtered_codes = {
            code: desc for code, desc in OPTION_CODES.items()
            if search_term.lower() in code.lower() or search_term.lower() in desc.lower()
        }
    
    if filtered_codes:
        # Convert to DataFrame for better display
        df_codes = pd.DataFrame([
            {"Code": code, "Description": desc} 
            for code, desc in list(filtered_codes.items())[:codes_per_page if not show_all else None]
        ])
        
        st.dataframe(
            df_codes,
            use_container_width=True,
            height=400 if not show_all else None
        )
        
        st.info(f"Showing {len(df_codes)} of {len(filtered_codes)} matching codes ({len(OPTION_CODES)} total)")
    else:
        st.warning("No option codes found matching your search.")

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🚗 Tesla Order Status Tracker</h1>', unsafe_allow_html=True)
    
    # Check for existing authentication on startup
    check_existing_auth()
    
    # Welcome message for new users
    if not st.session_state.authenticated:
        st.markdown("""
        ### 👋 Welcome to Tesla Order Status Tracker!
        
        Track your Tesla order status, delivery updates, and vehicle information - all from this easy-to-use web interface.
        
        **✨ Features:**
        - 📊 Real-time order status tracking
        - 📈 Change history with visualizations  
        - 🔍 Comprehensive option code reference
        - 💾 Local data caching for privacy
        - 🔒 Secure authentication with Tesla
        
        **🚀 To get started, please authenticate with your Tesla account below.**
        """)
        
        # Show authentication interface directly for new users
        if authenticate_user():
            st.success("🎉 Welcome! You're now authenticated and ready to track your Tesla order.")
            time.sleep(2)
            st.rerun()
        return
    
    # Sidebar navigation for authenticated users
    st.sidebar.markdown("## 🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📊 Order Status", "📈 Change History", "⚙️ Configuration", "📚 Option Codes", "ℹ️ About"],
        index=0  # Default to Order Status
    )
    
    # Quick status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🔍 Quick Status")
    
    if st.session_state.last_update:
        time_since = datetime.now() - st.session_state.last_update
        minutes_ago = time_since.seconds // 60
        if minutes_ago == 0:
            st.sidebar.success("✅ Just updated!")
        else:
            st.sidebar.success(f"✅ Updated {minutes_ago}m ago")
    else:
        st.sidebar.warning("⏳ No recent data")
    
    if st.sidebar.button("🔄 Quick Refresh", use_container_width=True):
        with st.spinner("Refreshing order data..."):
            fetch_order_data(force_refresh=True)
        st.success("✅ Data refreshed!")
        st.rerun()
    
    # Authentication status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🔐 Authentication")
    st.sidebar.success("✅ Authenticated")
    
    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        # Clear authentication
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        st.session_state.authenticated = False
        st.session_state.access_token = None
        st.session_state.orders_data = None
        st.session_state.last_update = None
        st.success("👋 Signed out successfully!")
        time.sleep(1)
        st.rerun()
    
    # Main content based on selected page
    if page == "📊 Order Status":
        # Fetch and display order data
        orders_data = fetch_order_data()
        
        if orders_data:
            display_order_summary(orders_data)
            st.markdown("---")
            display_detailed_order_info(orders_data)
        else:
            st.error("❌ Unable to fetch order data. Please check your authentication and try again.")
            if st.button("🔄 Try Again", type="primary"):
                st.rerun()
    
    elif page == "📈 Change History":
        display_change_history()
    
    elif page == "⚙️ Configuration":
        display_configuration_options()
    
    elif page == "📚 Option Codes":
        display_option_codes_reference()
    
    elif page == "ℹ️ About":
        st.markdown("### ℹ️ About Tesla Order Status Tracker")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            This web interface provides a user-friendly way to track your Tesla order status.
            
            **🌟 Key Features:**
            - 🔐 Secure Tesla authentication (OAuth2)
            - 📊 Real-time order status tracking
            - 📈 Interactive change history visualization
            - 🔍 Comprehensive Tesla option code reference
            - 💾 Local data caching for privacy
            - 🔒 Privacy controls for sharing screenshots
            - 🎨 Modern, responsive web interface
            
            **🙏 Credits:**
            - Original CLI script: [niklaswa](https://github.com/niklaswa/tesla-order-status)
            - Enhanced version: [MarcDGit](https://github.com/MarcDGit/tesla-order-status)
            - Streamlit web interface: This application
            """)
        
        with col2:
            st.info("""
            **🔒 Security & Privacy:**
            
            - All authentication happens directly with Tesla
            - Your credentials are never stored or shared
            - Data stays on your local machine
            - Open source and transparent
            """)
        
        # System status
        st.markdown("---")
        st.markdown("### 🖥️ System Status")
        
        status_data = {
            "Component": ["Python", "Streamlit", "Tesla API", "Local Storage"],
            "Status": ["✅ OK", "✅ OK", "✅ Connected", "✅ OK"],
            "Details": [
                f"Version {sys.version.split()[0]}",
                f"Version {st.__version__}",
                "Authenticated and ready",
                f"Files: {sum(1 for f in [TOKEN_FILE, ORDERS_FILE, HISTORY_FILE] if os.path.exists(f))}/3"
            ]
        }
        
        st.dataframe(pd.DataFrame(status_data), use_container_width=True)
        
        # Update check
        st.markdown("---")
        st.markdown("### 🔄 Updates")
        if st.button("Check for Updates", type="secondary"):
            with st.spinner("Checking for updates..."):
                try:
                    result = run_update_check()
                    if result == 0:
                        st.success("✅ You have the latest version!")
                    elif result == 1:
                        st.warning("⚠️ Update available! Check the GitHub repository.")
                    else:
                        st.error("❌ Error checking for updates.")
                except Exception as e:
                    st.error(f"❌ Update check failed: {str(e)}")
        
        # Quick stats
        if st.session_state.orders_data:
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            total_orders = len(st.session_state.orders_data)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Orders", total_orders)
            with col2:
                history = load_history_from_file()
                st.metric("History Entries", len(history))
            with col3:
                if st.session_state.last_update:
                    time_since = datetime.now() - st.session_state.last_update
                    st.metric("Minutes Since Update", time_since.seconds // 60)

if __name__ == "__main__":
    main()

