"""
Configuration management for modular app
Loads settings from settings.ini
"""
import configparser
import os

class Config:
    """Application configuration"""
    
    def __init__(self, config_file='config/settings.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # Check if running on Vercel (read-only filesystem)
        self.is_vercel = os.environ.get('VERCEL') == '1'
        
        # Load config if exists (only for local dev)
        if not self.is_vercel and os.path.exists(config_file):
            self.config.read(config_file)
        else:
            # Create default config in memory only
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config['APP'] = {
            'SECRET_KEY': os.urandom(24).hex(),
            'PORT': '5001',
            'DEBUG': 'True',
            'HOST': '0.0.0.0'
        }
        
        self.config['DATABASE'] = {
            'URI': 'sqlite:///instance/app.db'
        }
        
        self.config['ADMIN'] = {
            'USERNAME': 'admin',
            'PASSWORD': 'admin123'  # Change this!
        }
        
        self.config['LOCATION'] = {
            'OFFICE_LAT': '0.0',
            'OFFICE_LON': '0.0',
            'ALLOWED_RADIUS_METERS': '100'
        }
        
        self.config['UPLOAD'] = {
            'SELFIE_FOLDER': 'uploads/selfies',
            'DOCUMENT_FOLDER': 'uploads/documents',
            'INVENTORY_IMAGES_FOLDER': 'uploads/inventory_images',
            'MAX_FILE_SIZE': '5242880',  # 5MB
            'ALLOWED_EXTENSIONS': 'png,jpg,jpeg,pdf'
        }
        
        # Save default config (only for local dev, not on Vercel)
        if not self.is_vercel:
            try:
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w') as f:
                    self.config.write(f)
            except (OSError, PermissionError):
                # Filesystem is read-only (cloud deployment)
                pass
    
    def get(self, section, key, fallback=None):
        """Get configuration value"""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section, key, fallback=None):
        """Get integer configuration value"""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getfloat(self, section, key, fallback=None):
        """Get float configuration value"""
        try:
            return self.config.getfloat(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getboolean(self, section, key, fallback=None):
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
    
    def save(self):
        """Save configuration to file (only for local dev)"""
        if not self.is_vercel:
            try:
                with open(self.config_file, 'w') as f:
                    self.config.write(f)
            except (OSError, PermissionError):
                # Filesystem is read-only (cloud deployment)
                pass
    
    # Convenience properties
    @property
    def SECRET_KEY(self):
        # Use environment variable first, then config file, then generate one
        secret = os.environ.get('SECRET_KEY') or self.get('APP', 'SECRET_KEY')
        if not secret:
            secret = os.urandom(24).hex()
        return secret
    
    @property
    def BASE_DOMAIN(self):
        """Base domain for multi-tenant (e.g., 'bizbooks.co.in')"""
        return os.environ.get('BASE_DOMAIN') or self.get('APP', 'BASE_DOMAIN', 'bizbooks.co.in')
    
    @property
    def PORT(self):
        return self.getint('APP', 'PORT', 5001)
    
    @property
    def DEBUG(self):
        return self.getboolean('APP', 'DEBUG', True)
    
    @property
    def HOST(self):
        return self.get('APP', 'HOST', '0.0.0.0')
    
    @property
    def DATABASE_URI(self):
        return self.get('DATABASE', 'URI', 'sqlite:///instance/app.db')
    
    @property
    def ADMIN_USERNAME(self):
        return self.get('ADMIN', 'USERNAME', 'admin')
    
    @property
    def ADMIN_PASSWORD(self):
        return self.get('ADMIN', 'PASSWORD', 'admin123')
    
    @property
    def OFFICE_LAT(self):
        return self.getfloat('LOCATION', 'OFFICE_LAT', 0.0)
    
    @property
    def OFFICE_LON(self):
        return self.getfloat('LOCATION', 'OFFICE_LON', 0.0)
    
    @property
    def ALLOWED_RADIUS_METERS(self):
        return self.getint('LOCATION', 'ALLOWED_RADIUS_METERS', 100)
    
    @property
    def SELFIE_FOLDER(self):
        return self.get('UPLOAD', 'SELFIE_FOLDER', 'uploads/selfies')
    
    @property
    def DOCUMENT_FOLDER(self):
        return self.get('UPLOAD', 'DOCUMENT_FOLDER', 'uploads/documents')
    
    @property
    def INVENTORY_IMAGES_FOLDER(self):
        return self.get('UPLOAD', 'INVENTORY_IMAGES_FOLDER', 'uploads/inventory_images')

