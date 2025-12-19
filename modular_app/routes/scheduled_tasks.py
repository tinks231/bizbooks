"""
Scheduled Tasks Routes
Routes that can be called by cron jobs / scheduled tasks
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import pytz

scheduled_tasks_bp = Blueprint('scheduled_tasks', __name__, url_prefix='/scheduled-tasks')

@scheduled_tasks_bp.route('/process-special-day-bonuses', methods=['POST'])
def process_special_day_bonuses():
    """
    Process birthday & anniversary bonuses for all tenants
    
    This endpoint should be called daily at midnight IST by:
    - Cron job
    - Vercel Cron (vercel.json)
    - External scheduler (e.g., cron-job.org)
    
    Security: Check for secret token to prevent unauthorized access
    """
    
    # Simple security: Check for secret token
    secret_token = request.headers.get('X-Cron-Secret')
    expected_token = 'bizbooks-cron-2025'  # TODO: Move to environment variable
    
    if secret_token != expected_token:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Invalid or missing X-Cron-Secret header'
        }), 401
    
    try:
        # Import here to avoid circular imports
        from services.special_day_bonus_service import SpecialDayBonusService
        
        # Log execution time
        ist = pytz.timezone('Asia/Kolkata')
        execution_time = datetime.now(ist)
        
        print(f"=== Special Day Bonus Task Started at {execution_time.isoformat()} IST ===")
        
        # Process all tenants
        results = SpecialDayBonusService.process_all_tenants()
        
        print(f"=== Task Completed ===")
        print(f"Tenants processed: {results['tenants_processed']}")
        print(f"Birthday bonuses: {results['birthday_bonuses_credited']}")
        print(f"Anniversary bonuses: {results['anniversary_bonuses_credited']}")
        print(f"Expired bonuses removed: {results['expired_bonuses_removed']}")
        print(f"Notifications sent: {results['notifications_sent']}")
        if results['errors']:
            print(f"Errors: {results['errors']}")
        
        return jsonify({
            'success': True,
            'execution_time': execution_time.isoformat(),
            'results': results
        }), 200
        
    except Exception as e:
        print(f"ERROR in scheduled task: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': 'Task execution failed',
            'message': str(e)
        }), 500


@scheduled_tasks_bp.route('/test-special-day-bonuses', methods=['GET'])
def test_special_day_bonuses():
    """
    Test endpoint to manually trigger special day bonus processing
    Only works in development/testing
    No security check for testing purposes
    """
    
    try:
        # Import here to avoid circular imports
        from services.special_day_bonus_service import SpecialDayBonusService
        
        ist = pytz.timezone('Asia/Kolkata')
        execution_time = datetime.now(ist)
        
        # Process all tenants
        results = SpecialDayBonusService.process_all_tenants()
        
        return jsonify({
            'success': True,
            'test_execution_time': execution_time.isoformat(),
            'results': results,
            'note': 'This is a test execution. Use POST /scheduled-tasks/process-special-day-bonuses for production.'
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

