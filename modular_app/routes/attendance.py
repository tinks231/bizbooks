"""
Attendance management routes
PIN-based authentication + selfie capture
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, abort
from models import db, Employee, Attendance, Site
from datetime import datetime
import pytz
from utils.tenant_middleware import require_tenant, get_current_tenant_id
from utils.license_check import check_license
import base64
import os

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/')
@require_tenant
@check_license  # ← Check license/trial before allowing employee attendance
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
        # Look for the most recent check-in (regardless of date)
        last_checkin = Attendance.query.filter(
            Attendance.tenant_id == tenant_id,
            Attendance.employee_id == employee.id,
            Attendance.type == 'check_in'
        ).order_by(Attendance.timestamp.desc()).first()
        
        if last_checkin:
            # Check if there's a checkout after this check-in
            checkout_after_last_checkin = Attendance.query.filter(
                Attendance.tenant_id == tenant_id,
                Attendance.employee_id == employee.id,
                Attendance.type == 'check_out',
                Attendance.timestamp > last_checkin.timestamp
            ).first()
            
            if not checkout_after_last_checkin:
                # Last check-in has no corresponding checkout yet
                ist = pytz.timezone('Asia/Kolkata')
                if last_checkin.timestamp.tzinfo is None:
                    utc_time = pytz.UTC.localize(last_checkin.timestamp)
                    ist_time = utc_time.astimezone(ist)
                else:
                    ist_time = last_checkin.timestamp.astimezone(ist)
                
                last_time = ist_time.strftime('%I:%M %p on %b %d')
                
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
        # Look for the most recent check-in (even from previous days) that doesn't have a checkout
        last_checkin = Attendance.query.filter(
            Attendance.tenant_id == tenant_id,
            Attendance.employee_id == employee.id,
            Attendance.type == 'check_in'
        ).order_by(Attendance.timestamp.desc()).first()
        
        if not last_checkin:
            # No check-in found at all
            return f"""
            <div style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #ff9800;">⚠️ Cannot Check Out</h2>
                <p style="font-size: 18px;"><strong>{employee.name}</strong></p>
                <p>You haven't checked in yet!</p>
                <p style="color: #666; margin-top: 15px;">Please check in first.</p>
                <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
            </div>
            """
        
        # Check if there's a checkout after this check-in
        checkout_after_last_checkin = Attendance.query.filter(
            Attendance.tenant_id == tenant_id,
            Attendance.employee_id == employee.id,
            Attendance.type == 'check_out',
            Attendance.timestamp > last_checkin.timestamp
        ).first()
        
        if checkout_after_last_checkin:
            # Already checked out after the last check-in
            return f"""
            <div style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #ff9800;">⚠️ Already Checked Out!</h2>
                <p style="font-size: 18px;"><strong>{employee.name}</strong></p>
                <p>You already checked out after your last check-in.</p>
                <p style="color: #666; margin-top: 15px;">Please check in again if you want to mark a new entry.</p>
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

    # AUTO-DETECT SITE: Find closest site within allowed radius
    user_loc = (lat, lon)
    all_sites = Site.query.filter_by(tenant_id=tenant_id, active=True).all()
    
    if not all_sites:
        return f"""
        <div style="text-align: center; padding: 50px; font-family: Arial;">
            <h2 style="color: #dc3545;">❌ No Sites Configured</h2>
            <p>Please contact admin to set up site locations.</p>
            <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
        </div>
        """
    
    # Calculate distance to each site
    sites_with_distance = []
    for site in all_sites:
        if site.latitude and site.longitude:
            site_loc = (site.latitude, site.longitude)
            distance = geodesic(user_loc, site_loc).meters
            max_allowed = getattr(site, 'allowed_radius', getattr(site, 'radius', 100))
            
            sites_with_distance.append({
                'site': site,
                'distance': distance,
                'max_allowed': max_allowed,
                'within_radius': distance <= max_allowed
            })
    
    # Sort by distance (closest first)
    sites_with_distance.sort(key=lambda x: x['distance'])
    
    # Find the closest site within allowed radius
    matched_site = None
    for site_info in sites_with_distance:
        if site_info['within_radius']:
            matched_site = site_info
            break
    
    # If no site is within allowed radius, reject
    if not matched_site:
        # Show details of closest site
        closest = sites_with_distance[0] if sites_with_distance else None
        if closest:
            return f"""
            <div style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #dc3545;">❌ Too Far from Any Site</h2>
                <p>Closest site: <strong>{closest['site'].name}</strong></p>
                <p>You are <strong>{int(closest['distance'])} meters</strong> away.</p>
                <p style="color: #666;">Maximum allowed: <strong>{int(closest['max_allowed'])} meters</strong></p>
                <p style="color: #ff6b6b; margin-top: 20px;">Please move closer to one of your registered sites.</p>
                <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
            </div>
            """
        else:
            return f"""
            <div style="text-align: center; padding: 50px; font-family: Arial;">
                <h2 style="color: #dc3545;">❌ No Valid Sites Found</h2>
                <p>Please contact admin to configure site locations with GPS coordinates.</p>
                <a href='/attendance' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
            </div>
            """
    
    # Use the matched site
    site = matched_site['site']
    distance = matched_site['distance']

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

