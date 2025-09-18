from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import io
import traceback
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Import your NEP timetable generator
# Assuming the complete implementation from document 2 is in a file called nep_timetable.py
from nep_timetable import NEPTimetableGenerator, generate_timetable_api, UserPreferences

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_read_csv(file_content, filename):
    """Safely read CSV with error handling"""
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(io.StringIO(file_content.decode(encoding)))
                return df, None
            except UnicodeDecodeError:
                continue
        
        return None, f"Unable to decode {filename} with any common encoding"
    except Exception as e:
        return None, f"Error reading {filename}: {str(e)}"

def clean_dataframe(df, required_columns, optional_columns=None):
    """Clean and validate DataFrame"""
    if optional_columns is None:
        optional_columns = {}
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Check required columns
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Fill optional columns with defaults
    for col, default_val in optional_columns.items():
        if col not in df.columns:
            df[col] = default_val
    
    # Strip whitespace from string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    # Remove empty rows
    df = df.dropna(how='all')
    
    return df

@app.route('/api/user-preferences-template', methods=['GET'])
def get_user_preferences_template():
    """Get user preferences template for the frontend"""
    try:
        template = {
            "working_days": {
                "type": "integer",
                "value": 5,
                "range": [5, 6],
                "description": "Number of working days per week"
            },
            "periods_per_day": {
                "type": "integer", 
                "value": 8,
                "range": [6, 10],
                "description": "Number of periods per day"
            },
            "lunch_break_period": {
                "type": "integer",
                "value": 4,
                "range": [3, 6],
                "description": "Period number for lunch break"
            },
            "max_consecutive_same_subject": {
                "type": "integer",
                "value": 2,
                "range": [1, 4],
                "description": "Maximum consecutive hours for same subject"
            },
            "gap_penalty_weight": {
                "type": "float",
                "value": 10.0,
                "range": [0.0, 50.0],
                "description": "Penalty weight for schedule gaps"
            },
            "faculty_preference_weight": {
                "type": "float",
                "value": 15.0,
                "range": [0.0, 50.0],
                "description": "Weight for faculty time preferences"
            },
            "workload_balance_weight": {
                "type": "float",
                "value": 20.0,
                "range": [0.0, 50.0],
                "description": "Weight for workload balance optimization"
            },
            "room_preference_weight": {
                "type": "float",
                "value": 5.0,
                "range": [0.0, 20.0],
                "description": "Weight for room preference matching"
            },
            "interdisciplinary_bonus": {
                "type": "float",
                "value": 10.0,
                "range": [0.0, 30.0],
                "description": "Bonus for interdisciplinary courses"
            },
            "research_slot_protection": {
                "type": "boolean",
                "value": True,
                "description": "Protect faculty research time slots"
            },
            "allow_saturday_classes": {
                "type": "boolean",
                "value": False,
                "description": "Allow classes on Saturday"
            },
            "morning_start_time": {
                "type": "string",
                "value": "9:00",
                "options": ["8:00", "8:30", "9:00", "9:30"],
                "description": "Morning classes start time"
            },
            "evening_end_time": {
                "type": "string",
                "value": "5:00",
                "options": ["4:00", "4:30", "5:00", "5:30", "6:00"],
                "description": "Evening classes end time"
            }
        }
        
        return jsonify({
            "success": True,
            "template": template
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load preferences template: {str(e)}"
        }), 500

@app.route('/api/convert-csv-to-json', methods=['POST'])
def convert_csv_to_json():
    """Convert uploaded CSV files to JSON format"""
    try:
        # Check if all required files are present
        required_files = ['courses_csv', 'faculty_csv', 'classrooms_csv', 'batches_csv']
        
        for file_key in required_files:
            if file_key not in request.files:
                return jsonify({
                    "success": False,
                    "error": f"Missing required file: {file_key}"
                }), 400
        
        # Process each CSV file
        processed_data = {
            "courses": [],
            "faculty": [],
            "classrooms": [],
            "student_batches": []
        }
        
        # Process courses CSV
        courses_file = request.files['courses_csv']
        if courses_file and allowed_file(courses_file.filename):
            file_content = courses_file.read()
            df, error = safe_read_csv(file_content, courses_file.filename)
            if error:
                return jsonify({"success": False, "error": error}), 400
            
            required_cols = ['id', 'name', 'code', 'credits', 'course_type', 'hours_per_week', 
                           'department', 'semester', 'faculty_id']
            optional_cols = {
                'requires_lab': False,
                'requires_smart_room': False,
                'is_interdisciplinary': False,
                'connected_departments': '[]',
                'max_students': 60,
                'min_duration_minutes': 50,
                'max_consecutive_hours': 2,
                'preferred_days': '[]'
            }
            
            df = clean_dataframe(df, required_cols, optional_cols)
            
            for _, row in df.iterrows():
                course_data = {
                    "id": str(row['id']),
                    "name": str(row['name']),
                    "code": str(row['code']),
                    "credits": int(row['credits']),
                    "course_type": str(row['course_type']).lower(),
                    "hours_per_week": int(row['hours_per_week']),
                    "department": str(row['department']),
                    "semester": int(row['semester']),
                    "faculty_id": str(row['faculty_id']),
                    "requires_lab": bool(row.get('requires_lab', False)),
                    "requires_smart_room": bool(row.get('requires_smart_room', False)),
                    "is_interdisciplinary": bool(row.get('is_interdisciplinary', False)),
                    "connected_departments": json.loads(str(row.get('connected_departments', '[]'))),
                    "max_students": int(row.get('max_students', 60)),
                    "min_duration_minutes": int(row.get('min_duration_minutes', 50)),
                    "max_consecutive_hours": int(row.get('max_consecutive_hours', 2)),
                    "preferred_days": json.loads(str(row.get('preferred_days', '[]')))
                }
                processed_data['courses'].append(course_data)
        
        # Process faculty CSV
        faculty_file = request.files['faculty_csv']
        if faculty_file and allowed_file(faculty_file.filename):
            file_content = faculty_file.read()
            df, error = safe_read_csv(file_content, faculty_file.filename)
            if error:
                return jsonify({"success": False, "error": error}), 400
            
            required_cols = ['id', 'name', 'department', 'designation', 'specializations', 'courses_can_teach']
            optional_cols = {
                'max_hours_per_day': 6,
                'max_hours_per_week': 24,
                'preferred_time': 'any',
                'unavailable_slots': '[]',
                'research_slots': '[]',
                'is_visiting': False,
                'workload_preference': 1.0
            }
            
            df = clean_dataframe(df, required_cols, optional_cols)
            
            for _, row in df.iterrows():
                faculty_data = {
                    "id": str(row['id']),
                    "name": str(row['name']),
                    "department": str(row['department']),
                    "designation": str(row['designation']),
                    "specializations": json.loads(str(row['specializations'])) if isinstance(row['specializations'], str) else [str(row['specializations'])],
                    "courses_can_teach": json.loads(str(row['courses_can_teach'])) if isinstance(row['courses_can_teach'], str) else [str(row['courses_can_teach'])],
                    "max_hours_per_day": int(row.get('max_hours_per_day', 6)),
                    "max_hours_per_week": int(row.get('max_hours_per_week', 24)),
                    "preferred_time": str(row.get('preferred_time', 'any')).lower(),
                    "unavailable_slots": json.loads(str(row.get('unavailable_slots', '[]'))),
                    "research_slots": json.loads(str(row.get('research_slots', '[]'))),
                    "is_visiting": bool(row.get('is_visiting', False)),
                    "workload_preference": float(row.get('workload_preference', 1.0))
                }
                processed_data['faculty'].append(faculty_data)
        
        # Process classrooms CSV
        classrooms_file = request.files['classrooms_csv']
        if classrooms_file and allowed_file(classrooms_file.filename):
            file_content = classrooms_file.read()
            df, error = safe_read_csv(file_content, classrooms_file.filename)
            if error:
                return jsonify({"success": False, "error": error}), 400
            
            required_cols = ['id', 'name', 'capacity', 'room_type', 'department']
            optional_cols = {
                'equipment': '[]',
                'is_smart_room': False,
                'is_ac': False,
                'has_projector': True,
                'weekly_maintenance': '[]'
            }
            
            df = clean_dataframe(df, required_cols, optional_cols)
            
            for _, row in df.iterrows():
                classroom_data = {
                    "id": str(row['id']),
                    "name": str(row['name']),
                    "capacity": int(row['capacity']),
                    "room_type": str(row['room_type']).lower(),
                    "department": str(row['department']),
                    "equipment": json.loads(str(row.get('equipment', '[]'))),
                    "is_smart_room": bool(row.get('is_smart_room', False)),
                    "is_ac": bool(row.get('is_ac', False)),
                    "has_projector": bool(row.get('has_projector', True)),
                    "weekly_maintenance": json.loads(str(row.get('weekly_maintenance', '[]')))
                }
                processed_data['classrooms'].append(classroom_data)
        
        # Process student batches CSV
        batches_file = request.files['batches_csv']
        if batches_file and allowed_file(batches_file.filename):
            file_content = batches_file.read()
            df, error = safe_read_csv(file_content, batches_file.filename)
            if error:
                return jsonify({"success": False, "error": error}), 400
            
            required_cols = ['id', 'name', 'department', 'semester', 'student_count']
            optional_cols = {
                'core_courses': '[]',
                'elective_courses': '[]', 
                'skill_courses': '[]',
                'multidisciplinary_courses': '[]',
                'preferred_morning_hours': True,
                'max_hours_per_day': 7
            }
            
            df = clean_dataframe(df, required_cols, optional_cols)
            
            for _, row in df.iterrows():
                batch_data = {
                    "id": str(row['id']),
                    "name": str(row['name']),
                    "department": str(row['department']),
                    "semester": int(row['semester']),
                    "student_count": int(row['student_count']),
                    "core_courses": json.loads(str(row.get('core_courses', '[]'))),
                    "elective_courses": json.loads(str(row.get('elective_courses', '[]'))),
                    "skill_courses": json.loads(str(row.get('skill_courses', '[]'))),
                    "multidisciplinary_courses": json.loads(str(row.get('multidisciplinary_courses', '[]'))),
                    "preferred_morning_hours": bool(row.get('preferred_morning_hours', True)),
                    "max_hours_per_day": int(row.get('max_hours_per_day', 7))
                }
                processed_data['student_batches'].append(batch_data)
        
        return jsonify({
            "success": True,
            "data": processed_data,
            "message": f"Successfully processed {len(processed_data['courses'])} courses, {len(processed_data['faculty'])} faculty, {len(processed_data['classrooms'])} classrooms, and {len(processed_data['student_batches'])} batches"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error processing CSV files: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/validate-data', methods=['POST'])
def validate_data():
    """Validate the processed institutional data"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        data = request_data.get('institution_data', {})
        user_preferences = request_data.get('user_preferences', {})
        
        errors = []
        warnings = []
        
        # --- START OF NEW VALIDATION LOGIC ---
        
        # Determine working days and periods from preferences, with defaults
        allow_saturday = user_preferences.get('allow_saturday_classes', False)
        working_days = 6 if allow_saturday else 5
        periods_per_day = user_preferences.get('periods_per_day', 8)
        
        # Validate faculty slots
        faculty = data.get('faculty', [])
        faculty_ids = {fac['id'] for fac in faculty}
        
        for fac in faculty:
            # Check research_slots
            for day, period in fac.get('research_slots', []):
                if day >= working_days:
                    errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot on day {day}, which is outside the configured {working_days} working days (0-{working_days-1}).")
                if period >= periods_per_day:
                    errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot in period {period}, which is outside the configured {periods_per_day} periods per day (0-{periods_per_day-1}).")
            
            # Check unavailable_slots
            for day, period in fac.get('unavailable_slots', []):
                if day >= working_days:
                    errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot on day {day}, which is outside the configured {working_days} working days.")
                if period >= periods_per_day:
                    errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot in period {period}, which is outside the configured {periods_per_day} periods per day.")

        # Validate classroom maintenance slots
        classrooms = data.get('classrooms', [])
        classroom_ids = {room['id'] for room in classrooms}

        for room in classrooms:
            for day, period in room.get('weekly_maintenance', []):
                if day >= working_days:
                    errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot on day {day}, which is outside the configured {working_days} working days.")
                if period >= periods_per_day:
                    errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot in period {period}, which is outside the configured {periods_per_day} periods per day.")
        
        # --- END OF NEW VALIDATION LOGIC ---

        # Existing validations (duplicates, etc.)
        courses = data.get('courses', [])
        course_ids = set()
        for course in courses:
            if course['id'] in course_ids:
                errors.append(f"Duplicate course ID: {course['id']}")
            course_ids.add(course['id'])
            
            if course.get('faculty_id') not in faculty_ids:
                errors.append(f"Course '{course['name']}' (ID: {course['id']}) references a non-existent faculty ID: {course.get('faculty_id')}")

        batches = data.get('student_batches', [])
        for batch in batches:
            all_batch_courses = (batch.get('core_courses', []) + batch.get('elective_courses', []) + 
                               batch.get('skill_courses', []) + batch.get('multidisciplinary_courses', []))
            for course_id in all_batch_courses:
                if course_id not in course_ids:
                    warnings.append(f"Batch '{batch['name']}' references an unknown course ID: {course_id}")

        total_course_hours = sum(c.get('hours_per_week', 0) for c in courses)
        
        return jsonify({
            "success": True,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "statistics": { "courses": len(courses), "faculty": len(faculty), "classrooms": len(classrooms), "batches": len(batches) }
        })
    
    except Exception as e:
        return jsonify({ "success": False, "error": f"Error validating data: {str(e)}", "traceback": traceback.format_exc() }), 500

@app.route('/api/generate-timetable', methods=['POST'])
def generate_timetable():
    """Generate NEP compliant timetable using genetic algorithm"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        institution_data = request_data.get('institution_data')
        user_preferences = request_data.get('user_preferences', {})
        generation_params = request_data.get('generation_params', {})
        
        if not institution_data:
            return jsonify({
                "success": False,
                "error": "Institution data is required"
            }), 400
        
        # Set default generation parameters
        population_size = generation_params.get('population_size', 30)
        generations = generation_params.get('generations', 50)
        
        # Ensure reasonable limits
        population_size = max(10, min(100, population_size))
        generations = max(20, min(200, generations))
        
        print(f"Starting timetable generation with population_size={population_size}, generations={generations}")
        
        # Generate timetable using your existing function
        result = generate_timetable_api(
            json.dumps(institution_data),
            user_preferences,
            population_size=population_size,
            generations=generations
        )
        
        return jsonify({
            "success": True,
            "data": result,
            "generation_params": {
                "population_size": population_size,
                "generations": generations
            },
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"Timetable generation error: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "success": False,
            "error": f"Timetable generation failed: {error_msg}",
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "message": "NEP Timetable Generator API is running",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 16MB."
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error occurred."
    }), 500

if __name__ == '__main__':
    print("Starting NEP 2020 Timetable Generator API...")
    print("API endpoints:")
    print("- GET  /api/health - Health check")
    print("- GET  /api/user-preferences-template - Get user preferences template")
    print("- POST /api/convert-csv-to-json - Convert CSV files to JSON")
    print("- POST /api/validate-data - Validate institutional data")
    print("- POST /api/generate-timetable - Generate timetable")
    
    app.run(debug=True, host='0.0.0.0', port=5000)