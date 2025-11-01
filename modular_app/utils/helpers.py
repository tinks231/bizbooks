"""
Helper functions for the application
"""
import os
from werkzeug.utils import secure_filename
from geopy.distance import geodesic
from datetime import datetime

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf', 'gif', 'svg', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder):
    """
    Save uploaded file with secure filename
    On Vercel (serverless): Uploads to Vercel Blob Storage
    On local: Saves to filesystem
    Returns: filename/URL if successful, None otherwise
    """
    # Determine allowed extensions based on folder
    if 'logos' in upload_folder:
        allowed_ext = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
    elif 'task_media' in upload_folder:
        allowed_ext = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webp'}
    else:
        allowed_ext = {'png', 'jpg', 'jpeg', 'pdf'}
    
    if file and allowed_file(file.filename, allowed_ext):
        # Check if running on Vercel (read-only filesystem)
        if os.environ.get('VERCEL'):
            # Upload to Vercel Blob Storage
            from utils.vercel_blob import upload_to_vercel_blob, generate_blob_filename
            
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            # Determine MIME type
            mime_types = {
                'pdf': 'application/pdf',
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'svg': 'image/svg+xml',
                'webp': 'image/webp',
                'mp4': 'video/mp4',
                'mov': 'video/quicktime',
                'avi': 'video/x-msvideo'
            }
            mime_type = mime_types.get(file_ext, 'application/octet-stream')
            
            # Determine blob prefix based on upload folder
            if 'logos' in upload_folder:
                prefix = 'logos'
            elif 'task_media' in upload_folder:
                prefix = 'task_media'
            else:
                prefix = 'documents'
            
            # Generate blob filename
            blob_filename = generate_blob_filename(prefix, None, file_ext)
            
            # Upload to Vercel Blob
            blob_url = upload_to_vercel_blob(file, blob_filename, mime_type)
            
            if blob_url:
                print(f"✅ Uploaded to Vercel Blob: {blob_url}")
                return blob_url
            else:
                print(f"⚠️  {prefix.capitalize()} upload to Vercel Blob failed")
                return None
        else:
            # Local: Save to filesystem
            filename = secure_filename(file.filename)
            # Add timestamp to avoid overwriting
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            # Ensure upload folder exists
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            return filename
    else:
        print(f"⚠️ File not allowed: {file.filename if file else 'No file'}")
    return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates in meters
    """
    try:
        coords_1 = (lat1, lon1)
        coords_2 = (lat2, lon2)
        distance = geodesic(coords_1, coords_2).meters
        return round(distance, 2)
    except:
        return 0.0

def format_duration(seconds):
    """
    Format duration in seconds to human-readable format
    Example: 3665 seconds -> "1h 1m"
    """
    if not seconds:
        return "0m"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

def format_datetime(dt, format='%Y-%m-%d %H:%M'):
    """Format datetime object to string"""
    if not dt:
        return ""
    return dt.strftime(format)

def is_within_radius(user_lat, user_lon, office_lat, office_lon, allowed_radius):
    """
    Check if user is within allowed radius of office
    Returns: (is_within, distance)
    """
    distance = calculate_distance(user_lat, user_lon, office_lat, office_lon)
    return (distance <= allowed_radius, distance)

