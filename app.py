import streamlit as st
import os
import json
from datetime import datetime
from user_management import register_user, authenticate_user, get_user_info, get_all_users, delete_user, update_last_active

# Set page title
st.set_page_config(page_title="Car Document Manager", layout="wide")

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = {}
if 'user' not in st.session_state:
    st.session_state.user = None
if 'show_registration' not in st.session_state:
    st.session_state.show_registration = False

# Create necessary directories
os.makedirs('car_documents', exist_ok=True)

def show_login_page():
    st.title("Car Document Manager")
    st.write("Please login to manage your car documents")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Login")
        username = st.text_input("Vehicle Number or Admin Username", 
                               help="Enter your vehicle number (e.g., JK03L2315) or 'admin' for admin access")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username.lower() == "admin" and password == "Cseeng123#":
                st.session_state.user = {"username": "admin", "is_admin": True}
                st.rerun()
            else:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with col2:
        st.subheader("New User?")
        if st.button("Register Here"):
            st.session_state.show_registration = True
            st.rerun()

def show_registration_page():
    st.title("Register New User")
    
    with st.form("registration_form"):
        vehicle_number = st.text_input("Vehicle Number", 
                                     help="Format: First 2 letters (state code) + 2 digits + 1-2 letters + 4 digits. No special characters allowed.")
        vehicle_model = st.text_input("Vehicle Model")
        owner_name = st.text_input("Owner Name")
        password = st.text_input("Password (default: last 4 digits of vehicle number)", type="password")
        
        if st.form_submit_button("Register"):
            if register_user(vehicle_number, vehicle_model, owner_name, password):
                st.success("Registration successful! Please login.")
                st.session_state.show_registration = False
                st.rerun()
            else:
                st.error("Registration failed. Please check your vehicle number format.")

def show_admin_panel():
    st.title("Admin Panel")
    
    # Show all users
    st.subheader("Registered Users")
    users = get_all_users()
    
    for user in users:
        with st.expander(f"Vehicle: {user['vehicle_number']}"):
            st.write(f"Model: {user['vehicle_model']}")
            st.write(f"Owner: {user['owner_name']}")
            st.write(f"🕒 Last Active: {user.get('last_active', 'Never')}")
            
            if st.button(f"Delete User {user['vehicle_number']}", key=f"delete_{user['vehicle_number']}"):
                if delete_user(user['vehicle_number']):
                    st.success(f"User {user['vehicle_number']} deleted successfully")
                    st.rerun()
                else:
                    st.error("Failed to delete user")

def show_main_app():
    st.title(f"Car Document Manager - {st.session_state.user['vehicle_number']}")
    
    # Update last active time
    update_last_active(st.session_state.user['vehicle_number'])
    
    # Logout button
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    # Document upload section
    st.subheader("Upload Document")
    doc_type = st.selectbox("Document Type", ["Vehicle Registration", "Insurance", "Service Records", "Other"])
    
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # Create user directory if it doesn't exist
        user_dir = os.path.join('car_documents', st.session_state.user['vehicle_number'])
        os.makedirs(user_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(user_dir, f"{doc_type}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Update metadata
        if st.session_state.user['vehicle_number'] not in st.session_state.documents:
            st.session_state.documents[st.session_state.user['vehicle_number']] = {}
        
        if doc_type not in st.session_state.documents[st.session_state.user['vehicle_number']]:
            st.session_state.documents[st.session_state.user['vehicle_number']][doc_type] = []
        
        st.session_state.documents[st.session_state.user['vehicle_number']][doc_type].append({
            'filename': uploaded_file.name,
            'path': file_path,
            'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        st.success("Document uploaded successfully!")
    
    # View documents section
    st.subheader("View Documents")
    view_doc_type = st.selectbox("Select Document Type", ["Vehicle Registration", "Insurance", "Service Records", "Other"], key="view_doc_type")
    
    if st.session_state.user['vehicle_number'] in st.session_state.documents and view_doc_type in st.session_state.documents[st.session_state.user['vehicle_number']]:
        for doc in st.session_state.documents[st.session_state.user['vehicle_number']][view_doc_type]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"File: {doc['filename']}")
                st.write(f"Upload Date: {doc['upload_date']}")
            with col2:
                if st.button("Delete", key=f"delete_{doc['filename']}"):
                    if os.path.exists(doc['path']):
                        os.remove(doc['path'])
                        st.session_state.documents[st.session_state.user['vehicle_number']][view_doc_type].remove(doc)
                        st.success("Document deleted successfully!")
                        st.rerun()
                    else:
                        st.error("File not found")

def show_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 10px; background: linear-gradient(to right, #f0f2f6, #ffffff, #f0f2f6); border-radius: 5px;'>
            <p style='margin: 0; font-size: 0.8em; color: #666;'>Developed by Your Name</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Main app logic
if st.session_state.user is None:
    if st.session_state.show_registration:
        show_registration_page()
    else:
        show_login_page()
else:
    if st.session_state.user.get('is_admin'):
        show_admin_panel()
    else:
        show_main_app()

show_footer() 