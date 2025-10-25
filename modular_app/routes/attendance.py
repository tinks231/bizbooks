"""
Attendance management routes
PIN-based authentication + selfie capture
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, abort
from models import db, Employee, Attendance, Site
from datetime import datetime
import pytz
from utils.tenant_middleware import require_tenant, get_current_tenant_id
import base64
import os

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/')
@require_tenant
def index():
    """Main attendance page"""
    tenant_id = get_current_tenant_id()
    sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
    return render_template('attendance/index.html', sites=sites)

@attendance_bp.route('/submit', methods=['POST'])
@require_tenant
def submit():
    """Submit attendance (check-in or check-out)"""
    from werkzeug.utils import secure_filename
    from geopy.distance import geodesic
    from datetime import datetime as dt, timedelta
    
    tenant_id = get_current_tenant_id()
    pin = request.form.get('pin', '').strip()
    action = request.form.get('action', '').strip()
    lat_str = request.form.get('latitude', '')
    lon_str = request.form.get('longitude', '')
    site_id = request.form.get('site_id', 1)

    # Validate PIN (scoped to tenant)
    employee = Employee.query.filter_by(
        tenant_id=tenant_id,
        pin=pin,
        active=True
    ).first()
    if not employee:
        return f"""
        <div style="text-align: center; padding: 50px; font-family: Arial;">
            <h2 style="color: #dc3545;">❌ Invalid PIN</h2>
            <p>Please check your PIN and try again.</p>
            <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
        </div>
        """
    
    # Check for duplicate check-in or check-out today
    today_start = dt.now(pytz.timezone('Asia/Kolkata')).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Get today's attendance records for this employee
    today_records = Attendance.query.filter(
        Attendance.tenant_id == tenant_id,
        Attendance.employee_id == employee.id,
        Attendance.timestamp >= today_start,
        Attendance.timestamp < today_end
    ).order_by(Attendance.timestamp.desc()).all()
    
    # Check if already checked in (and not checked out yet)
    if action == 'check_in':
        # Look for the most recent record
        if today_records:
            last_record = today_records[0]
            if last_record.type == 'check_in':
                # Last action was check-in, so employee is already checked in
                last_time = last_record.timestamp.strftime('%I:%M %p')
                return f"""
                <div style="text-align: center; padding: 50px; font-family: Arial;">
                    <h2 style="color: #ff9800;">⚠️ Already Checked In!</h2>
                    <p style="font-size: 18px;"><strong>{employee.name}</strong></p>
                    <p>You already checked in at <strong>{last_time}</strong></p>
                    <p style="color: #666; margin-top: 15px;">Please check out first before checking in again.</p>
                    <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
                </div>
                """
    
    # Check if trying to check out without checking in first
    elif action == 'check_out':
        if not today_records or today_records[0].type == 'check_out':
            # No records today or last action was check-out
            return f"""
            <div style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #ff9800;">⚠️ Cannot Check Out</h2>
                <p style="font-size: 18px;"><strong>{employee.name}</strong></p>
                <p>You haven't checked in yet today!</p>
                <p style="color: #666; margin-top: 15px;">Please check in first.</p>
                <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
            </div>
            """

    # Validate GPS (MANDATORY - must be at site location)
    try:
        lat = float(lat_str) if lat_str else 0
        lon = float(lon_str) if lon_str else 0
    except ValueError:
        lat = 0
        lon = 0
    
    # GPS is MANDATORY
    if lat == 0 or lon == 0:
        return f"""
        <div style="text-align: center; padding: 50px; font-family: Arial;">
            <h2 style="color: #dc3545;">❌ Location Required</h2>
            <p>Please enable GPS/location services and try again.</p>
            <p style="color: #666; font-size: 14px;">We need to verify you are at the site location.</p>
            <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
        </div>
        """

    # Validate photo
    photo = request.files.get('photo')
    if not photo:
        return f"""
        <div style="text-align: center; padding: 50px; font-family: Arial;">
            <h2 style="color: #dc3545;">❌ Missing Photo</h2>
            <p>Please take a selfie.</p>
            <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
        </div>
        """

    # Calculate distance from site (MANDATORY check)
    distance = 0
    site = Site.query.get(site_id)
    if site and site.latitude and site.longitude:
        user_loc = (lat, lon)
        site_loc = (site.latitude, site.longitude)
        distance = geodesic(user_loc, site_loc).meters
        
        # Get allowed radius (handle both old 'radius' and new 'allowed_radius' column names)
        max_allowed_distance = getattr(site, 'allowed_radius', getattr(site, 'radius', 100))
        
        # Check if within allowed radius (MANDATORY)
        if distance > max_allowed_distance:
            return f"""
            <div style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #dc3545;">❌ Too Far from Site</h2>
                <p>You are <strong>{int(distance)} meters</strong> away from the site.</p>
                <p style="color: #666;">Maximum allowed distance: <strong>{int(max_allowed_distance)} meters</strong></p>
                <p style="color: #ff6b6b; margin-top: 20px;">Please move closer to the site location to mark attendance.</p>
                <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
            </div>
            """

    # Save photo (Vercel Blob Storage or local filesystem)
    photo_data = None
    if os.environ.get('VERCEL'):
        # On Vercel: Upload to Vercel Blob Storage
        from utils.vercel_blob import upload_to_vercel_blob, generate_blob_filename
        
        blob_filename = generate_blob_filename('attendance', employee.name, 'jpg')
        photo_url = upload_to_vercel_blob(photo, blob_filename, 'image/jpeg')
        
        if photo_url:
            photo_data = photo_url
        else:
            # Fallback: If Blob upload fails, skip photo
            print("⚠️  Photo upload failed, continuing without photo")
            photo_data = None
    else:
        # Local: Save to filesystem
        ist = pytz.timezone('Asia/Kolkata')
        timestamp = datetime.now(ist).strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{employee.name}_{timestamp}.jpg")
        photo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', 'selfies', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        photo.save(photo_path)
        photo_data = filename

    # Save attendance record (with IST timezone)
    ist = pytz.timezone('Asia/Kolkata')
    record = Attendance(
        tenant_id=tenant_id,
        employee_id=employee.id,
        site_id=site_id,
        employee_name=employee.name,
        type=action,
        timestamp=datetime.now(ist),
        latitude=lat,
        longitude=lon,
        distance=distance,
        photo=photo_data
    )
    db.session.add(record)
    db.session.commit()
    
    # Show distance and format time in IST
    distance_text = f"{int(distance)} meters from site"
    action_text = "Check In" if action == "check_in" else "Check Out"
    
    # Ensure timestamp is displayed in IST
    if record.timestamp.tzinfo is None:
        # If naive, assume UTC and convert to IST
        utc_time = pytz.UTC.localize(record.timestamp)
        ist_time_obj = utc_time.astimezone(ist)
    else:
        # If already timezone-aware, convert to IST
        ist_time_obj = record.timestamp.astimezone(ist)
    
    ist_time = ist_time_obj.strftime('%I:%M %p')
    
    return f"""
    <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h2 style="color: #4CAF50;">✅ Success!</h2>
        <h3>Hello {employee.name}!</h3>
        <p style="font-size: 1.2em;">{action_text} recorded at {ist_time}</p>
        <p style="color: #666;">Distance from site: {distance_text}</p>
        <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
    </div>
    """

@attendance_bp.route('/history')
def history():
    """View attendance history (last 50 records)"""
    records = Attendance.query.order_by(Attendance.timestamp.desc()).limit(50).all()
    return render_template('attendance/history.html', records=records)

