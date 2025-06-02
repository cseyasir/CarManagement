import streamlit as st
import os
from PIL import Image
import datetime
import json
from user_management import (
    register_user, authenticate_user, get_user_info,
    get_all_users, delete_user, ADMIN_USERNAME,
    update_last_active
)

# Set page configuration with reduced margins
st.set_page_config(
    page_title="Car Document Manager",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to reduce margins and padding
st.markdown("""
    <style>
        .main > div {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .stButton > button {
            width: 100%;
        }
        div[data-testid="stVerticalBlock"] > div:nth-child(1) {
            padding-top: 0;
        }
        .stAlert {
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        @keyframes welcomeAnimation {
            0% { transform: translateY(100px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }
        .welcome-message {
            animation: welcomeAnimation 1s ease-out;
            text-align: center;
            font-size: 24px;
            color: #1a73e8;
            margin: 20px 0;
            padding: 15px;
            background: linear-gradient(45deg, #f0f2f6, #e6e9ef);
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .welcome-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Create a directory to store documents if it doesn't exist
UPLOAD_DIR = "car_documents"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# JSON file to store document metadata
METADATA_FILE = "document_metadata.json"

def load_documents():
    """Load document metadata from JSON file"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_documents(documents):
    """Save document metadata to JSON file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(documents, f)

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = load_documents()
if 'user' not in st.session_state:
    st.session_state.user = None
if 'show_registration' not in st.session_state:
    st.session_state.show_registration = False
if 'show_balloons' not in st.session_state:
    st.session_state.show_balloons = False
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = False

def delete_document(document_type, document_index):
    """Delete a document and its metadata"""
    try:
        # Get the document to delete
        doc_to_delete = st.session_state.documents[document_type][document_index]
        
        # Delete the physical file
        if os.path.exists(doc_to_delete['filepath']):
            os.remove(doc_to_delete['filepath'])
        
        # Remove from metadata
        st.session_state.documents[document_type].pop(document_index)
        
        # If no more documents of this type, remove the type
        if not st.session_state.documents[document_type]:
            del st.session_state.documents[document_type]
        
        # Save changes
        save_documents(st.session_state.documents)
        return True
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return False

def save_document(file, document_type):
    """Save uploaded document and store its metadata"""
    if file is not None:
        # Create a unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{document_type}_{timestamp}{os.path.splitext(file.name)[1]}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Save the file
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        
        # Initialize document type list if it doesn't exist
        if document_type not in st.session_state.documents:
            st.session_state.documents[document_type] = []
        
        # Add new document to the list
        st.session_state.documents[document_type].append({
            'filename': filename,
            'upload_date': timestamp,
            'filepath': filepath
        })
        
        # Save to JSON file
        save_documents(st.session_state.documents)
        return True
    return False

def show_footer():
    """Display a beautiful footer with developer information"""
    st.markdown("---")
    footer_html = """
    <div style='text-align: center; padding: 10px; background: linear-gradient(to right, #f0f2f6, #e6e9ef); border-radius: 5px; margin-top: 20px;'>
        <p style='color: #2c3e50; font-size: 14px; margin: 0; font-family: Arial, sans-serif;'>
            Developed by <span style='font-weight: 600; color: #1a73e8;'>Yasir Arfat</span> | © 2025
        </p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def show_welcome_message(owner_name, vehicle_number):
    """Display welcome message with animation"""
    welcome_html = f"""
    <div class="welcome-message">
        <div class="welcome-icon">🎉</div>
        <h2>Welcome, {owner_name}!</h2>
        <p>Your vehicle {vehicle_number} has been successfully registered.</p>
        <p>You can now start managing your documents.</p>
    </div>
    """
    st.markdown(welcome_html, unsafe_allow_html=True)
    st.balloons()

def show_back_button():
    """Display a back button in the top right corner"""
    back_container = st.container()
    with back_container:
        _, col2 = st.columns([6, 1])
        with col2:
            if st.button("← Back", key="back_button"):
                if st.session_state.show_registration:
                    st.session_state.show_registration = False
                elif st.session_state.user:
                    st.session_state.user = None
                st.rerun()

def show_login_page():
    """Display login page"""
    st.title("🚗 Car Document Manager")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Login")
        username = st.text_input(
            "Vehicle Number or Admin Username",
            key="login_username",
            help="Enter your vehicle number (e.g., JK03L2315, JK03LA2315) or 'admin' for admin access"
        )
        # Convert to uppercase if it's a vehicle number
        if username and not username == "Admin":
            username = username.upper()
        password = st.text_input("Password", type="password", key="login_password")
        
        with st.form("login_form"):
            submitted = st.form_submit_button("Login")
            if submitted or (username and password):
                if username and password:
                    success, result = authenticate_user(username, password)
                    if success:
                        st.session_state.user = result
                        if not result.get('is_admin'):
                            st.session_state.user['vehicle_number'] = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.error("Please fill in all fields")
    
    with col2:
        st.header("New User? Register Here")
        if st.button("Register New Vehicle"):
            st.session_state.show_registration = True
            st.rerun()
    
    # Add footer to login page
    show_footer()

def show_registration_page():
    """Display registration page"""
    show_back_button()
    
    st.title("🚗 New Vehicle Registration")
    
    with st.form("registration_form"):
        vehicle_number = st.text_input(
            "Vehicle Number (e.g., JK03L2315, JK03LA2315)",
            help="Format: First 2 letters (state code) + 2 digits + 1-2 letters + 4 digits. No special characters allowed."
        )
        # Convert to uppercase
        if vehicle_number:
            vehicle_number = vehicle_number.upper()
        vehicle_model = st.text_input("Vehicle Model")
        owner_name = st.text_input("Owner Name")
        password = st.text_input("Password (leave empty to use last 4 digits of vehicle number)", type="password")
        
        submitted = st.form_submit_button("Register")
        if submitted:
            if vehicle_number and vehicle_model and owner_name:
                if not password:
                    password = vehicle_number[-4:]
                success, message = register_user(vehicle_number, vehicle_model, owner_name, password)
                if success:
                    st.session_state.show_welcome = True
                    show_welcome_message(owner_name, vehicle_number)
                    st.session_state.show_registration = False
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please fill in all required fields")
    
    # Add footer to registration page
    show_footer()

def show_admin_panel():
    """Display admin panel"""
    show_back_button()
    
    st.title("👨‍💼 Admin Panel")
    
    st.header("Registered Users")
    users = get_all_users()
    
    if users:
        for vehicle_number, user_data in users.items():
            with st.expander(f"Vehicle: {vehicle_number}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"Owner: {user_data['owner_name']}")
                    st.write(f"Model: {user_data['vehicle_model']}")
                    st.write(f"Registered: {user_data['registration_date']}")
                    # Show last active time with a clock emoji
                    st.write(f"🕒 Last Active: {user_data.get('last_active', 'Never')}")
                with col2:
                    if st.button("Delete User", key=f"delete_user_{vehicle_number}"):
                        success, message = delete_user(vehicle_number)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
    else:
        st.info("No users registered yet.")
    
    # Add footer to admin panel
    show_footer()

def show_main_app():
    """Display main application"""
    show_back_button()
    
    # Update last active time when user accesses the main app
    if st.session_state.user and not st.session_state.user.get('is_admin'):
        update_last_active(st.session_state.user['vehicle_number'])
    
    st.title(f"🚗 Car Document {st.session_state.user['vehicle_number']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Upload Documents")
        
        document_type = st.selectbox(
            "Select Document Type",
            ["Vehicle Registration", "Insurance", "Pollution Certificate", "License", "Other"]
        )
        
        if document_type == "Other":
            custom_type = st.text_input("Enter Document Type (e.g., Challan, Receipt, etc.)")
            if custom_type:
                document_type = custom_type
        
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=['pdf', 'jpg', 'jpeg', 'png'],
            key=f"upload_{document_type}"
        )
        
        if uploaded_file is not None:
            if save_document(uploaded_file, document_type):
                st.success(f"{document_type} uploaded successfully!")
                st.balloons()
            else:
                st.error("Error uploading document.")
    
    with col2:
        st.header("View Documents")
        
        all_document_types = list(st.session_state.documents.keys())
        if not all_document_types:
            all_document_types = ["Vehicle Registration", "Insurance", "Pollution Certificate", "License", "Other"]
        
        view_document_type = st.selectbox(
            "Select Document to View",
            all_document_types,
            key="view_document"
        )
        
        if view_document_type in st.session_state.documents and st.session_state.documents[view_document_type]:
            documents = st.session_state.documents[view_document_type]
            
            if len(documents) > 1:
                version_dates = [doc['upload_date'] for doc in documents]
                selected_version = st.selectbox(
                    "Select Version",
                    version_dates,
                    index=len(version_dates)-1,
                    format_func=lambda x: f"Version from {x}"
                )
                selected_doc = next(doc for doc in documents if doc['upload_date'] == selected_version)
                selected_index = next(i for i, doc in enumerate(documents) if doc['upload_date'] == selected_version)
            else:
                selected_doc = documents[0]
                selected_index = 0
            
            st.write(f"Uploaded on: {selected_doc['upload_date']}")
            
            file_extension = os.path.splitext(selected_doc['filename'])[1].lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png']:
                try:
                    image = Image.open(selected_doc['filepath'])
                    st.image(image, caption=selected_doc['filename'])
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")
            elif file_extension == '.pdf':
                try:
                    with open(selected_doc['filepath'], "rb") as f:
                        st.download_button(
                            label="Download PDF",
                            data=f,
                            file_name=selected_doc['filename'],
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Error loading PDF: {str(e)}")
            
            delete_col1, delete_col2 = st.columns([1, 2])
            with delete_col1:
                if st.button("🗑️ Delete", key=f"delete_{selected_index}"):
                    st.session_state[f"show_password_{selected_index}"] = True
            
            if st.session_state.get(f"show_password_{selected_index}", False):
                with delete_col2:
                    password = st.text_input("Enter last 4 digits of vehicle number", type="password", key=f"password_{selected_index}")
                    if password:
                        if password == st.session_state.user['vehicle_number'][-4:]:
                            if delete_document(view_document_type, selected_index):
                                st.success("Document deleted successfully!")
                                st.session_state[f"show_password_{selected_index}"] = False
                                st.rerun()
                        else:
                            st.error("Incorrect vehicle number!")
                            st.session_state[f"show_password_{selected_index}"] = False
        else:
            st.info(f"No {view_document_type} document uploaded yet.")
    
    show_footer()

def main():
    if st.session_state.show_registration:
        show_registration_page()
    elif st.session_state.user is None:
        show_login_page()
    elif st.session_state.user.get('is_admin'):
        show_admin_panel()
    else:
        show_main_app()

if __name__ == "__main__":
    main() 