from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from geopy.distance import geodesic
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import configparser

# ---------------- Load Configuration ----------------
config = configparser.ConfigParser()
config_file = 'config.ini'

# Load config or use defaults
if os.path.exists(config_file):
    config.read(config_file)
    OFFICE_LAT = config.getfloat('OFFICE_LOCATION', 'LATITUDE', fallback=22.610113)
    OFFICE_LON = config.getfloat('OFFICE_LOCATION', 'LONGITUDE', fallback=77.768982)
    ALLOWED_RADIUS_METERS = config.getint('OFFICE_LOCATION', 'ALLOWED_RADIUS', fallback=150)
    ADMIN_USERNAME = config.get('ADMIN', 'USERNAME', fallback='admin')
    ADMIN_PASSWORD = config.get('ADMIN', 'PASSWORD', fallback='admin123')
    APP_PORT = config.getint('APP', 'PORT', fallback=5001)
    APP_DEBUG = config.getboolean('APP', 'DEBUG', fallback=True)
    print(f"✅ Configuration loaded from {config_file}")
    print(f"📍 Office Location: {OFFICE_LAT}, {OFFICE_LON}")
    print(f"📏 Allowed Radius: {ALLOWED_RADIUS_METERS}m")
else:
    # Default values if config doesn't exist
    OFFICE_LAT = 22.610113
    OFFICE_LON = 77.768982
    ALLOWED_RADIUS_METERS = 150
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    APP_PORT = 5001
    APP_DEBUG = True
    print("⚠️  Warning: config.ini not found! Using default values.")
    print("   Run 'python3 setup_wizard.py' to configure your shop location.")

# ---------------- Flask App Configuration ----------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['UPLOAD_FOLDER'] = 'selfies'
app.config['DOCUMENT_FOLDER'] = 'employee_documents'
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production-12345'
app.config['ALLOWED_DOCUMENT_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png'}
db = SQLAlchemy(app)

# Create folders if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOCUMENT_FOLDER'], exist_ok=True)

# ---------------- Database ----------------
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pin = db.Column(db.String(4), unique=True, nullable=False)  # 4-digit PIN
    phone = db.Column(db.String(15))
    document_path = db.Column(db.String(200))  # Path to Aadhar/ID document (optional)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.String(50))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    employee_name = db.Column(db.String(50))
    action = db.Column(db.String(10))
    timestamp = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    distance = db.Column(db.Float)
    photo = db.Column(db.String(100))
    comment = db.Column(db.String(500))  # Admin comment for manual entries
    manual_entry = db.Column(db.Boolean, default=False)  # Flag for manual entries
    # Relationship
    employee = db.relationship('Employee', backref='attendances')

# Create DB tables safely
with app.app_context():
    db.create_all()

# ---------------- Helper Functions ----------------
def allowed_document(filename):
    """Check if file extension is allowed for documents"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_DOCUMENT_EXTENSIONS']

# ---------------- HTML Template ----------------
template = """
<!DOCTYPE html>
<html>
<head>
  <title>Attendance App</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial; text-align: center; margin: 20px; }
    input, button { font-size: 1.1em; margin: 10px; padding: 10px; }
    button:disabled { 
      background: #ccc !important; 
      color: #666 !important;
      cursor: not-allowed;
      opacity: 0.6;
    }
    img { width: 100px; border-radius: 10px; }
    #locationStatus { 
      padding: 10px; 
      margin: 10px; 
      border-radius: 5px; 
      font-weight: bold;
    }
    .loading { background: #fff3cd; color: #856404; }
    .success { background: #d4edda; color: #155724; }
    .error { background: #f8d7da; color: #721c24; }
  </style>
</head>
<body>
  <h2>🏪 Employee Attendance</h2>
  <div id="locationStatus" class="loading">📍 Getting your location...</div>
  <form id="attendanceForm" method="POST" enctype="multipart/form-data" action="/submit">
    <input type="password" name="pin" placeholder="Enter Your 4-Digit PIN" maxlength="4" pattern="[0-9]{4}" required autofocus><br>
    <input type="hidden" name="latitude" id="latitude">
    <input type="hidden" name="longitude" id="longitude">
    <label>Take a Selfie:</label><br>
    <input type="file" id="photoInput" name="photo" accept="image/*" capture="user" required><br>
    <button type="submit" name="action" value="Check In">✅ Check In</button>
    <button type="submit" name="action" value="Check Out">🏁 Check Out</button>
  </form>
  <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
    <a href="/admin/login" style="color: #666; text-decoration: none; font-size: 0.9em;">Admin Login</a>
  </div>

  <script>
    const statusDiv = document.getElementById('locationStatus');
    let locationObtained = false;

    // Location optional - WiFi connection itself proves they're at workplace
    // If location works, great! If not, no problem.
    // No validation needed - just submit

    // Get GPS coordinates with better error handling
    if (navigator.geolocation) {
        const options = {
            enableHighAccuracy: true,
            timeout: 10000,  // 10 seconds timeout
            maximumAge: 0
        };
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // Success!
                document.getElementById('latitude').value = position.coords.latitude;
                document.getElementById('longitude').value = position.coords.longitude;
                locationObtained = true;
                statusDiv.className = 'success';
                statusDiv.innerHTML = '✅ Location obtained! Ready to submit.';
            }, 
            function(error) {
                // Error handling with specific messages
                statusDiv.className = 'error';
                let errorMsg = '';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = '❌ Location permission denied. Please check settings.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = '⚠️ Location unavailable. Try going near a window or outside.';
                        break;
                    case error.TIMEOUT:
                        errorMsg = '⏱️ Location timeout. Retrying...';
                        // Retry once
                        setTimeout(() => {
                            navigator.geolocation.getCurrentPosition(
                                function(pos) {
                                    document.getElementById('latitude').value = pos.coords.latitude;
                                    document.getElementById('longitude').value = pos.coords.longitude;
                                    locationObtained = true;
                                    statusDiv.className = 'success';
                                    statusDiv.innerHTML = '✅ Location obtained! Ready to submit.';
                                },
                                function() {
                                    statusDiv.innerHTML = '❌ Still cannot get location. You can try submitting anyway.';
                                },
                                options
                            );
                        }, 1000);
                        break;
                    default:
                        errorMsg = '❌ Unknown error getting location.';
                        break;
                }
                statusDiv.innerHTML = errorMsg;
            },
            options
        );
    } else {
        statusDiv.className = 'error';
        statusDiv.innerHTML = '❌ Geolocation not supported by your browser!';
    }
  </script>
</body>
</html>
"""

# Admin Login Template
admin_login_template = """
<!DOCTYPE html>
<html>
<head>
  <title>Admin Login</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial; text-align: center; margin: 0; padding: 20px; background: #f5f5f5; }
    .login-container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    h2 { color: #333; margin-bottom: 30px; }
    input { width: 90%; font-size: 1.1em; margin: 10px 0; padding: 12px; border: 1px solid #ddd; border-radius: 5px; }
    button { width: 95%; font-size: 1.1em; margin: 20px 0 10px 0; padding: 12px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
    button:hover { background: #45a049; }
    .error { color: red; margin: 10px 0; }
    a { color: #666; text-decoration: none; }
  </style>
</head>
<body>
  <div class="login-container">
    <h2>🔐 Admin Login</h2>
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    <form method="POST">
      <input type="text" name="username" placeholder="Username" required autofocus><br>
      <input type="password" name="password" placeholder="Password" required><br>
      <button type="submit">Login</button>
    </form>
    <p style="margin-top: 30px;"><a href="/">← Back to Employee Page</a></p>
  </div>
</body>
</html>
"""

# Admin Dashboard Template
admin_dashboard_template = """
<!DOCTYPE html>
<html>
<head>
  <title>Admin Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 20px; background: white; border-radius: 10px; }
    .header h2 { margin: 0; }
    .nav { display: flex; gap: 20px; }
    .nav a { padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
    .nav a:hover { background: #45a049; }
    .logout { background: #f44336 !important; }
    .logout:hover { background: #da190b !important; }
    .stats { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
    .stat-box { flex: 1; min-width: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .stat-box h3 { margin: 0; font-size: 3em; }
    .stat-box p { margin: 10px 0 0 0; font-size: 1.1em; }
    .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { background: #4CAF50; color: white; padding: 15px; text-align: left; font-size: 0.9em; }
    td { padding: 12px; border-bottom: 1px solid #ddd; vertical-align: middle; }
    tr:hover { background-color: #f5f5f5; }
    .photo { width: 50px; height: 50px; object-fit: cover; border-radius: 5px; cursor: pointer; transition: transform 0.2s; }
    .photo:hover { transform: scale(3); z-index: 1000; }
    .time-in { color: #4CAF50; }
    .time-out { color: #f44336; }
    .duration { background: #e3f2fd; padding: 5px 10px; border-radius: 5px; font-weight: bold; color: #1976d2; }
    .working { background: #fff3cd; padding: 5px 10px; border-radius: 5px; color: #856404; }
    .distance { color: #666; font-size: 0.85em; }
  </style>
</head>
<body>
  <div class="header">
    <h2>📊 Admin Dashboard</h2>
    <div class="nav">
      <a href="/admin/employees">👥 Manage Employees</a>
      <a href="/admin/manual_entry" style="background: #ff9800;">✍️ Manual Entry</a>
      <a href="/admin/logout" class="logout">Logout</a>
    </div>
  </div>
  
  <div class="stats">
    <div class="stat-box">
      <h3>{{ employees|length }}</h3>
      <p>Total Employees</p>
    </div>
    <div class="stat-box">
      <h3>{{ employees|selectattr('active')|list|length }}</h3>
      <p>Active Employees</p>
    </div>
    <div class="stat-box">
      <h3>{{ attendance_pairs|length }}</h3>
      <p>Today's Records</p>
    </div>
  </div>
  
  <div class="container">
    <h3>📅 Attendance Records (Grouped by Employee & Date)</h3>
    <div style="margin-bottom: 20px; display: flex; gap: 10px;">
      <a href="/admin/export" style="padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px;">📥 Export to CSV</a>
      <a href="/admin/clear_attendance" onclick="return confirm('⚠️ Delete ALL attendance records? This cannot be undone!');" style="padding: 10px 20px; background: #f44336; color: white; text-decoration: none; border-radius: 5px;">🗑️ Clear All Attendance Data</a>
    </div>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Employee</th>
          <th>Check In</th>
          <th>Check Out</th>
          <th>Duration</th>
          <th>In Photo</th>
          <th>Out Photo</th>
          <th>Comment</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for pair in attendance_pairs %}
        <tr>
          <td>{{ pair.date }}</td>
          <td><strong>{{ pair.employee_name }}</strong></td>
          <td>
            <span class="time-in">{{ pair.check_in_time }}</span>
            <div class="distance">{{ pair.check_in_distance }}</div>
          </td>
          <td>
            {% if pair.check_out_time %}
              <span class="time-out">{{ pair.check_out_time }}</span>
              <div class="distance">{{ pair.check_out_distance }}</div>
            {% else %}
              <span class="working">Still Working</span>
            {% endif %}
          </td>
          <td>
            {% if pair.duration %}
              <span class="duration">{{ pair.duration }}</span>
            {% else %}
              <span class="working">—</span>
            {% endif %}
          </td>
          <td>
            {% if pair.check_in_photo %}
              <img src='/selfie/{{ pair.check_in_photo }}' class='photo' title='Check In'>
            {% else %}
              —
            {% endif %}
          </td>
          <td>
            {% if pair.check_out_photo %}
              <img src='/selfie/{{ pair.check_out_photo }}' class='photo' title='Check Out'>
            {% else %}
              —
            {% endif %}
          </td>
          <td style="max-width: 200px; font-size: 0.85em; color: #666;">
            {% if pair.check_in_comment or pair.check_out_comment %}
              <div style="background: #fff3cd; padding: 5px; border-radius: 3px;">
                {% if pair.check_in_comment %}
                  <div style="margin-bottom: 3px;">
                    <strong>In:</strong> {{ pair.check_in_comment }}
                    {% if pair.check_in_manual %}<span style="color: #ff9800; font-weight: bold;" title="Manual Entry">✍️</span>{% endif %}
                  </div>
                {% endif %}
                {% if pair.check_out_comment %}
                  <div>
                    <strong>Out:</strong> {{ pair.check_out_comment }}
                    {% if pair.check_out_manual %}<span style="color: #ff9800; font-weight: bold;" title="Manual Entry">✍️</span>{% endif %}
                  </div>
                {% endif %}
              </div>
            {% else %}
              —
            {% endif %}
          </td>
          <td>
            <div style="display: flex; gap: 5px;">
              {% if pair.check_in_id %}
              <a href="/admin/record/delete/{{ pair.check_in_id }}" onclick="return confirm('Delete check-in record?');" style="padding: 5px 10px; background: #f44336; color: white; text-decoration: none; border-radius: 3px; font-size: 0.85em;">🗑️ In</a>
              {% endif %}
              {% if pair.check_out_id %}
              <a href="/admin/record/delete/{{ pair.check_out_id }}" onclick="return confirm('Delete check-out record?');" style="padding: 5px 10px; background: #f44336; color: white; text-decoration: none; border-radius: 3px; font-size: 0.85em;">🗑️ Out</a>
              {% endif %}
            </div>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</body>
</html>
"""

# Admin Employees Template
admin_manual_entry_template = """
<!DOCTYPE html>
<html>
<head>
  <title>Manual Attendance Entry</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 20px; background: white; border-radius: 10px; }
    .header h2 { margin: 0; }
    .nav { display: flex; gap: 20px; }
    .nav a { padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
    .nav a:hover { background: #45a049; }
    .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
    .form-group { margin-bottom: 20px; }
    .form-group label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
    .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 12px; font-size: 1em; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
    .form-group textarea { resize: vertical; min-height: 80px; }
    .form-group button { width: 100%; padding: 15px; font-size: 1.1em; background: #ff9800; color: white; border: none; border-radius: 5px; cursor: pointer; }
    .form-group button:hover { background: #f57c00; }
    .info-box { background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #2196F3; }
    .info-box ul { margin: 10px 0; padding-left: 20px; }
    .success-msg { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #28a745; }
    .error-msg { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #f44336; }
  </style>
</head>
<body>
  <div class="header">
    <h2>✍️ Manual Attendance Entry</h2>
    <div class="nav">
      <a href="/admin/dashboard">📊 Dashboard</a>
      <a href="/admin/employees">👥 Employees</a>
      <a href="/admin/logout" style="background: #f44336;">Logout</a>
    </div>
  </div>
  
  {% if message %}
    <div class="{{ 'success-msg' if success else 'error-msg' }}">
      {{ message }}
    </div>
  {% endif %}
  
  <div class="container">
    <div class="info-box">
      <strong>ℹ️ Use this to:</strong>
      <ul>
        <li>Mark attendance for employees who forgot</li>
        <li>Adjust check-in/check-out timing</li>
        <li>Add explanations with comments</li>
      </ul>
      <strong>Note:</strong> Photo and location are optional for manual entries.
    </div>
    
    <form method="POST" action="/admin/manual_entry">
      <div class="form-group">
        <label for="employee">Select Employee *</label>
        <select name="employee_id" id="employee" required>
          <option value="">-- Choose Employee --</option>
          {% for emp in employees %}
            <option value="{{ emp.id }}">{{ emp.name }} (PIN: {{ emp.pin }})</option>
          {% endfor %}
        </select>
      </div>
      
      <div class="form-group">
        <label for="action">Action *</label>
        <select name="action" id="action" required>
          <option value="">-- Choose Action --</option>
          <option value="Check In">Check In</option>
          <option value="Check Out">Check Out</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="date">Date *</label>
        <input type="date" name="date" id="date" required>
      </div>
      
      <div class="form-group">
        <label for="time">Time *</label>
        <input type="time" name="time" id="time" required>
      </div>
      
      <div class="form-group">
        <label for="comment">Comment (Optional)</label>
        <textarea name="comment" id="comment" placeholder="e.g., Forgot to check out, left at 6 PM"></textarea>
      </div>
      
      <div class="form-group">
        <button type="submit">✍️ Add Manual Entry</button>
      </div>
    </form>
  </div>
  
  <script>
    // Set today's date and current time as default
    document.addEventListener('DOMContentLoaded', function() {
      const today = new Date();
      const dateInput = document.getElementById('date');
      const timeInput = document.getElementById('time');
      
      // Set date to today
      const yyyy = today.getFullYear();
      const mm = String(today.getMonth() + 1).padStart(2, '0');
      const dd = String(today.getDate()).padStart(2, '0');
      dateInput.value = `${yyyy}-${mm}-${dd}`;
      
      // Set time to now
      const hh = String(today.getHours()).padStart(2, '0');
      const min = String(today.getMinutes()).padStart(2, '0');
      timeInput.value = `${hh}:${min}`;
    });
  </script>
</body>
</html>
"""

admin_employees_template = """
<!DOCTYPE html>
<html>
<head>
  <title>Manage Employees</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 20px; background: white; border-radius: 10px; }
    .header h2 { margin: 0; }
    .nav { display: flex; gap: 20px; }
    .nav a { padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
    .nav a:hover { background: #45a049; }
    .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
    .add-form { display: grid; gap: 15px; max-width: 600px; }
    .add-form input { padding: 12px; font-size: 1em; border: 1px solid #ddd; border-radius: 5px; }
    .add-form button { padding: 15px; font-size: 1.1em; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
    .add-form button:hover { background: #45a049; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #4CAF50; color: white; padding: 15px; text-align: left; }
    td { padding: 15px; border-bottom: 1px solid #ddd; }
    tr:hover { background-color: #f5f5f5; }
    .active { color: #4CAF50; font-weight: bold; }
    .inactive { color: #999; }
    .actions { display: flex; gap: 10px; }
    .actions a { padding: 8px 15px; text-decoration: none; border-radius: 5px; font-size: 0.9em; }
    .toggle { background: #ff9800; color: white; }
    .delete { background: #f44336; color: white; }
    .pin-display { font-family: monospace; font-size: 1.2em; font-weight: bold; background: #f5f5f5; padding: 5px 10px; border-radius: 5px; }
  </style>
</head>
<body>
  <div class="header">
    <h2>👥 Manage Employees</h2>
    <div class="nav">
      <a href="/admin/dashboard">📊 Dashboard</a>
      <a href="/admin/logout" style="background: #f44336;">Logout</a>
    </div>
  </div>
  
  <div class="container">
    <h3>➕ Add New Employee</h3>
    <form method="POST" action="/admin/employee/add" class="add-form" enctype="multipart/form-data">
      <input type="text" name="name" placeholder="Employee Name" required>
      <input type="text" name="pin" placeholder="4-Digit PIN" maxlength="4" pattern="[0-9]{4}" required>
      <input type="tel" name="phone" placeholder="Phone Number (optional)">
      <div style="text-align: left;">
        <label style="font-size: 0.9em; color: #666; display: block; margin-bottom: 5px;">
          📄 ID Document (Aadhar/Driving License - Optional)
        </label>
        <input type="file" name="document" accept=".pdf,.jpg,.jpeg,.png" style="padding: 8px;">
        <div style="font-size: 0.8em; color: #999; margin-top: 5px;">
          Accepted: PDF, JPG, PNG (Max 5MB)
        </div>
      </div>
      <button type="submit">Add Employee</button>
    </form>
  </div>
  
  <div class="container">
    <h3>📋 Employee List ({{ employees|length }})</h3>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>PIN</th>
          <th>Phone</th>
          <th>ID Document</th>
          <th>Status</th>
          <th>Created</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for emp in employees %}
        <tr>
          <td>{{ emp.name }}</td>
          <td><span class="pin-display">{{ emp.pin }}</span></td>
          <td>{{ emp.phone or '-' }}</td>
          <td>
            {% if emp.document_path %}
              <a href="/admin/employee/document/{{ emp.id }}" target="_blank" style="color: #4CAF50; text-decoration: none;">
                📄 View
              </a>
            {% else %}
              <span style="color: #999;">-</span>
            {% endif %}
          </td>
          <td class="{{ 'active' if emp.active else 'inactive' }}">{{ 'Active' if emp.active else 'Inactive' }}</td>
          <td>{{ emp.created_at }}</td>
          <td class="actions">
            <a href="/admin/employee/toggle/{{ emp.id }}" class="toggle">{{ 'Deactivate' if emp.active else 'Activate' }}</a>
            <a href="/admin/employee/delete/{{ emp.id }}" class="delete" onclick="return confirm('Delete {{ emp.name }}?')">Delete</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</body>
</html>
"""

# ---------------- Routes ----------------
@app.route('/')
def index():
    return render_template_string(template)

@app.route('/submit', methods=['POST'])
def submit():
    pin = request.form.get('pin', '').strip()
    action = request.form.get('action', '').strip()
    lat_str = request.form.get('latitude', '')
    lon_str = request.form.get('longitude', '')

    # Validate PIN and get employee
    employee = Employee.query.filter_by(pin=pin, active=True).first()
    if not employee:
        return "<h3>❌ Invalid PIN or employee not active!</h3><p>Please check your PIN and try again.</p><a href='/'>Go back</a>"

    # Validate GPS (optional - WiFi connection is the primary security)
    try:
        lat = float(lat_str) if lat_str else 0
        lon = float(lon_str) if lon_str else 0
    except ValueError:
        lat = 0
        lon = 0

    # Validate photo
    photo = request.files.get('photo')
    if not photo:
        return "<h3>❌ Please upload a selfie.</h3><a href='/'>Go back</a>"

    # Calculate distance from office (if location available)
    if lat != 0 and lon != 0:
        user_loc = (lat, lon)
        office_loc = (OFFICE_LAT, OFFICE_LON)
        distance = geodesic(user_loc, office_loc).meters
        
        # Check if within allowed radius
        if distance > ALLOWED_RADIUS_METERS:
            return f"<h3>❌ You are too far from the workplace!</h3><p>Distance: {int(distance)} meters<br>Required: Within {ALLOWED_RADIUS_METERS} meters</p><a href='/'>Go back</a>"
    else:
        # Location not available, set distance to -1
        distance = -1

    # Save attendance record
    filename = secure_filename(f"{employee.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    record = Attendance(
        employee_id=employee.id,
        employee_name=employee.name,
        action=action,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        latitude=lat,
        longitude=lon,
        distance=distance,
        photo=filename
    )
    db.session.add(record)
    db.session.commit()
    
    # Show distance if available
    distance_text = f"{int(distance)} meters" if distance != -1 else "N/A (WiFi verified)"
    
    return f"""
    <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h2 style="color: #4CAF50;">✅ Success!</h2>
        <h3>Hello {employee.name}!</h3>
        <p style="font-size: 1.2em;">Attendance recorded at {datetime.now().strftime('%I:%M %p')}</p>
        <p style="color: #666;">Distance from office: {distance_text}</p>
        <a href='/' style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">← Go Back</a>
    </div>
    """

# ---------------- Admin Routes ----------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template_string(admin_login_template, error="Invalid credentials!")
    
    return render_template_string(admin_login_template, error=None)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    from flask import make_response
    
    employees = Employee.query.all()
    
    # Get all records, ordered by oldest first for proper pairing
    all_records = Attendance.query.order_by(Attendance.timestamp.asc()).all()
    
    # Group records by employee and date
    from collections import defaultdict
    records_by_employee_date = defaultdict(list)
    
    for record in all_records:
        try:
            record_dt = datetime.strptime(record.timestamp, "%Y-%m-%d %H:%M:%S")
            record_date = record_dt.strftime("%Y-%m-%d")
            key = (record.employee_id, record_date)
            records_by_employee_date[key].append(record)
        except:
            continue
    
    # Format distance helper
    def format_distance(dist):
        return f"{int(dist)}m" if dist != -1 else "N/A"
    
    # Create pairs from grouped records
    attendance_pairs = []
    
    for (emp_id, date), day_records in records_by_employee_date.items():
        # Sort by timestamp to ensure chronological order
        day_records.sort(key=lambda r: r.timestamp)
        
        i = 0
        while i < len(day_records):
            record = day_records[i]
            
            if record.action == "Check In":
                # Look for next Check Out for this employee
                check_out = None
                for j in range(i + 1, len(day_records)):
                    if day_records[j].action == "Check Out":
                        check_out = day_records[j]
                        break
                
                # Calculate duration if check-out exists
                duration = None
                if check_out:
                    try:
                        in_dt = datetime.strptime(record.timestamp, "%Y-%m-%d %H:%M:%S")
                        out_dt = datetime.strptime(check_out.timestamp, "%Y-%m-%d %H:%M:%S")
                        diff = out_dt - in_dt
                        hours = diff.seconds // 3600
                        minutes = (diff.seconds % 3600) // 60
                        duration = f"{hours}h {minutes}m"
                    except:
                        duration = "N/A"
                
                # Add pair
                record_dt = datetime.strptime(record.timestamp, "%Y-%m-%d %H:%M:%S")
                attendance_pairs.append({
                    'date': date,
                    'employee_name': record.employee_name,
                    'check_in_time': record_dt.strftime("%I:%M %p"),
                    'check_in_distance': format_distance(record.distance),
                    'check_in_photo': record.photo,
                    'check_in_id': record.id,
                    'check_in_comment': record.comment,
                    'check_in_manual': record.manual_entry,
                    'check_out_time': datetime.strptime(check_out.timestamp, "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p") if check_out else None,
                    'check_out_distance': format_distance(check_out.distance) if check_out else None,
                    'check_out_photo': check_out.photo if check_out else None,
                    'check_out_id': check_out.id if check_out else None,
                    'check_out_comment': check_out.comment if check_out else None,
                    'check_out_manual': check_out.manual_entry if check_out else False,
                    'duration': duration
                })
                
                # Skip the check-out we just processed
                if check_out:
                    i += 2  # Skip both check-in and check-out
                else:
                    i += 1  # Only skip check-in
            
            elif record.action == "Check Out":
                # Orphaned check-out (no prior check-in)
                record_dt = datetime.strptime(record.timestamp, "%Y-%m-%d %H:%M:%S")
                attendance_pairs.append({
                    'date': date,
                    'employee_name': record.employee_name,
                    'check_in_time': "—",
                    'check_in_distance': "—",
                    'check_in_photo': None,
                    'check_in_id': None,
                    'check_in_comment': None,
                    'check_in_manual': False,
                    'check_out_time': record_dt.strftime("%I:%M %p"),
                    'check_out_distance': format_distance(record.distance),
                    'check_out_photo': record.photo,
                    'check_out_id': record.id,
                    'check_out_comment': record.comment,
                    'check_out_manual': record.manual_entry,
                    'duration': None
                })
                i += 1
            else:
                i += 1
    
    # Sort pairs by date (newest first) for display
    attendance_pairs.sort(key=lambda x: x['date'], reverse=True)
    
    # Create response with cache-busting headers
    response = make_response(render_template_string(admin_dashboard_template, employees=employees, attendance_pairs=attendance_pairs))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/admin/manual_entry', methods=['GET', 'POST'])
def admin_manual_entry():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    employees = Employee.query.filter_by(active=True).all()
    message = None
    success = False
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        action = request.form.get('action')
        date = request.form.get('date')
        time = request.form.get('time')
        comment = request.form.get('comment', '').strip()
        
        # Validate inputs
        if not employee_id or not action or not date or not time:
            message = "❌ Please fill all required fields!"
            success = False
        else:
            employee = Employee.query.get(employee_id)
            if not employee:
                message = "❌ Employee not found!"
                success = False
            else:
                # Create timestamp from date and time
                timestamp = f"{date} {time}:00"
                
                # Create manual attendance record
                attendance = Attendance(
                    employee_id=employee.id,
                    employee_name=employee.name,
                    action=action,
                    timestamp=timestamp,
                    latitude=0.0,  # No location for manual entries
                    longitude=0.0,
                    distance=0.0,
                    photo='manual_entry.jpg',  # Placeholder
                    comment=comment if comment else None,
                    manual_entry=True
                )
                db.session.add(attendance)
                db.session.commit()
                
                message = f"✅ Manual {action} recorded for {employee.name} at {timestamp}"
                if comment:
                    message += f" with comment: {comment}"
                success = True
    
    return render_template_string(admin_manual_entry_template, 
                                   employees=employees, 
                                   message=message, 
                                   success=success)

@app.route('/admin/employees')
def admin_employees():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    employees = Employee.query.all()
    return render_template_string(admin_employees_template, employees=employees)

@app.route('/admin/employee/add', methods=['POST'])
def admin_add_employee():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    name = request.form.get('name', '').strip()
    pin = request.form.get('pin', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if not name or not pin or len(pin) != 4:
        return "<h3>❌ Invalid data! Name and 4-digit PIN required.</h3><a href='/admin/employees'>Go back</a>"
    
    # Check if PIN already exists
    existing = Employee.query.filter_by(pin=pin).first()
    if existing:
        return "<h3>❌ PIN already exists! Choose a different PIN.</h3><a href='/admin/employees'>Go back</a>"
    
    # Handle document upload (optional)
    document_path = None
    if 'document' in request.files:
        file = request.files['document']
        if file and file.filename and allowed_document(file.filename):
            # Create unique filename: PIN_timestamp_originalname
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = secure_filename(file.filename)
            filename = f"{pin}_{timestamp}_{original_filename}"
            
            # Save file
            filepath = os.path.join(app.config['DOCUMENT_FOLDER'], filename)
            file.save(filepath)
            document_path = filename
    
    employee = Employee(
        name=name,
        pin=pin,
        phone=phone,
        document_path=document_path,
        active=True,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(employee)
    db.session.commit()
    
    return redirect(url_for('admin_employees'))

@app.route('/admin/employee/toggle/<int:emp_id>')
def admin_toggle_employee(emp_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    employee = Employee.query.get_or_404(emp_id)
    employee.active = not employee.active
    db.session.commit()
    return redirect(url_for('admin_employees'))

@app.route('/admin/employee/delete/<int:emp_id>')
def admin_delete_employee(emp_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    employee = Employee.query.get_or_404(emp_id)
    
    # Delete document file if exists
    if employee.document_path:
        doc_path = os.path.join(app.config['DOCUMENT_FOLDER'], employee.document_path)
        if os.path.exists(doc_path):
            os.remove(doc_path)
    
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for('admin_employees'))

@app.route('/admin/employee/document/<int:emp_id>')
def admin_view_document(emp_id):
    """View/download employee document"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    employee = Employee.query.get_or_404(emp_id)
    
    if not employee.document_path:
        return "<h3>❌ No document found for this employee!</h3><a href='/admin/employees'>Go back</a>"
    
    # Send file from document folder
    return send_from_directory(app.config['DOCUMENT_FOLDER'], employee.document_path)

@app.route('/admin/record/delete/<int:record_id>')
def admin_delete_record(record_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    record = Attendance.query.get_or_404(record_id)
    
    # Delete associated photo file
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], record.photo)
    if os.path.exists(photo_path):
        os.remove(photo_path)
    
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/clear_attendance')
def admin_clear_attendance():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Delete all attendance records
    records = Attendance.query.all()
    for record in records:
        # Delete photo file
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], record.photo)
        if os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except:
                pass
        db.session.delete(record)
    
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export')
def admin_export():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    import csv
    from io import StringIO
    from flask import Response
    
    # Get all attendance records
    records = Attendance.query.order_by(Attendance.timestamp.desc()).all()
    
    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['Employee Name', 'Action', 'Date', 'Time', 'Latitude', 'Longitude', 'Distance (m)', 'Photo', 'Comment', 'Manual Entry'])
    
    # Write data
    for r in records:
        try:
            dt = datetime.strptime(r.timestamp, "%Y-%m-%d %H:%M:%S")
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%I:%M %p")
        except:
            date_str = r.timestamp
            time_str = ""
        
        distance_str = "N/A" if r.distance == -1 else f"{int(r.distance)}"
        
        writer.writerow([
            r.employee_name,
            r.action,
            date_str,
            time_str,
            r.latitude,
            r.longitude,
            distance_str,
            r.photo,
            r.comment if r.comment else "",
            "Yes" if r.manual_entry else "No"
        ])
    
    # Create response
    output = si.getvalue()
    response = Response(output, mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return response

# Old admin route - redirect to dashboard
@app.route('/admin/old')
def admin_old():
    records = Attendance.query.order_by(Attendance.id.desc()).all()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attendance Admin</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            h2 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .container {
                max-width: 95%;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th {
                background: #4CAF50;
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: bold;
                font-size: 1.1em;
            }
            td {
                padding: 15px;
                border-bottom: 1px solid #ddd;
                font-size: 1em;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .photo {
                width: 80px;
                height: 80px;
                object-fit: cover;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 0.2s;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            .photo:hover {
                transform: scale(2.5);
                z-index: 1000;
                position: relative;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
            .check-in {
                color: #4CAF50;
                font-weight: bold;
            }
            .check-out {
                color: #f44336;
                font-weight: bold;
            }
            .distance {
                font-weight: bold;
            }
            .distance.good {
                color: #4CAF50;
            }
            .distance.na {
                color: #ff9800;
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            .stat-box {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                min-width: 200px;
                margin: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .stat-box h3 {
                margin: 0;
                font-size: 3em;
                font-weight: bold;
            }
            .stat-box p {
                margin: 10px 0 0 0;
                opacity: 0.95;
                font-size: 1.1em;
            }
            @media (max-width: 768px) {
                .photo {
                    width: 40px;
                    height: 40px;
                }
                td, th {
                    padding: 8px 4px;
                    font-size: 0.9em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 Attendance Logs</h2>
            <div class="stats">
                <div class="stat-box">
                    <h3>""" + str(len(records)) + """</h3>
                    <p>Total Records</p>
                </div>
                <div class="stat-box">
                    <h3>""" + str(len([r for r in records if r.action == 'Check In'])) + """</h3>
                    <p>Check Ins</p>
                </div>
                <div class="stat-box">
                    <h3>""" + str(len([r for r in records if r.action == 'Check Out'])) + """</h3>
                    <p>Check Outs</p>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Action</th>
                        <th>Time</th>
                        <th>Distance</th>
                        <th>Photo</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for r in records:
        distance_str = "N/A" if r.distance == -1 else f"{int(r.distance)}m"
        distance_class = "na" if r.distance == -1 else "good"
        action_class = "check-in" if r.action == "Check In" else "check-out"
        
        html += f"""
                    <tr>
                        <td>{r.name}</td>
                        <td class="{action_class}">{r.action}</td>
                        <td>{r.timestamp}</td>
                        <td class="distance {distance_class}">{distance_str}</td>
                        <td><img src='/selfie/{r.photo}' class='photo' title='Click to enlarge'></td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/selfie/<filename>')
def selfie(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------- Run App ----------------
if __name__ == '__main__':
    # Use HTTPS for location verification (MANDATORY for iOS)
    # Android users: Accept certificate warning once
    app.run(host='0.0.0.0', port=APP_PORT, debug=APP_DEBUG, ssl_context=('cert.pem', 'key.pem'))

