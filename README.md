# Car Document Manager

A Streamlit application for managing car documents with user authentication and admin features.

## Features

- User registration and authentication
- Document upload and management
- Admin panel for user management
- Last active tracking
- Secure document deletion
- Beautiful UI with animations

## Deployment Instructions

1. Fork this repository to your GitHub account
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your forked repository
6. Set the main file path as `app.py`
7. Click "Deploy"

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Admin Access

- Username: `admin`
- Password: `admin123`

## File Structure

- `app.py`: Main application file
- `user_management.py`: User authentication and management
- `requirements.txt`: Python dependencies
- `car_documents/`: Directory for storing uploaded documents
- `users.json`: User data storage
- `document_metadata.json`: Document metadata storage

## Security Notes

- Change the admin password in production
- Keep your deployment URL private
- Regularly backup user data and documents

## Usage

1. Select the document type you want to upload
2. Click on "Browse files" to select your document
3. The document will be automatically saved
4. To view documents, select the document type from the "View Documents" section
5. Images will be displayed directly in the app
6. PDFs can be downloaded for viewing

## Document Types

- Vehicle Registration
- Insurance
- Service Records
- Other 