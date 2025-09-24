# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# import json
# import io
# import traceback
# from werkzeug.utils import secure_filename
# import os
# from datetime import datetime
# import ast
# import sys

# # Import your NEP timetable generator
# try:
#     from nep_timetable import NEPTimetableGenerator, generate_timetable_api, UserPreferences
# except ImportError as e:
#     print(f"Import error: {e}")
#     # Create dummy classes for testing
#     class NEPTimetableGenerator:
#         def __init__(self, **kwargs):
#             pass
#     def generate_timetable_api(*args, **kwargs):
#         return {"error": "NEP timetable module not available"}
#     class UserPreferences:
#         pass

# app = Flask(__name__)
# CORS(app)

# # Configuration
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# UPLOAD_FOLDER = 'temp_uploads'
# ALLOWED_EXTENSIONS = {'csv', 'json'}  # Added JSON support

# # Create upload folder if it doesn't exist
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def safe_read_csv(file_content, filename):
#     """Safely read CSV with error handling"""
#     try:
#         # Try different encodings
#         encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
#         for encoding in encodings:
#             try:
#                 df = pd.read_csv(io.StringIO(file_content.decode(encoding)))
#                 return df, None
#             except UnicodeDecodeError:
#                 continue
        
#         return None, f"Unable to decode {filename} with any common encoding"
#     except Exception as e:
#         return None, f"Error reading {filename}: {str(e)}"

# def safe_read_json(file_content, filename):
#     """Safely read JSON with error handling"""
#     try:
#         json_data = json.loads(file_content.decode('utf-8'))
#         return json_data, None
#     except json.JSONDecodeError as e:
#         return None, f"Invalid JSON in {filename}: {str(e)}"
#     except Exception as e:
#         return None, f"Error reading JSON file {filename}: {str(e)}"

# def parse_list_field(value, default=[]):
#     """Parse list fields from CSV that might be string representations"""
#     if pd.isna(value) or value == '' or value == '[]':
#         return default
    
#     if isinstance(value, list):
#         return value
    
#     if isinstance(value, str):
#         try:
#             # Try to parse as Python list
#             cleaned_value = value.strip()
#             if cleaned_value.startswith('[') and cleaned_value.endswith(']'):
#                 return ast.literal_eval(cleaned_value)
#             elif ',' in cleaned_value:
#                 return [item.strip() for item in cleaned_value.split(',') if item.strip()]
#             elif cleaned_value:
#                 return [cleaned_value]
#         except (ValueError, SyntaxError) as e:
#             print(f"Warning: Could not parse list field '{value}': {e}")
#             # If that fails, return as single item list
#             return [value] if value else default
    
#     return default

# def parse_boolean_field(value, default=False):
#     """Parse boolean fields from various formats"""
#     if pd.isna(value) or value == '':
#         return default
    
#     if isinstance(value, bool):
#         return value
    
#     if isinstance(value, (int, float)):
#         return bool(value)
    
#     if isinstance(value, str):
#         lower_val = value.lower().strip()
#         if lower_val in ['true', 'yes', '1', 't', 'y']:
#             return True
#         elif lower_val in ['false', 'no', '0', 'f', 'n']:
#             return False
    
#     return default

# def clean_dataframe(df, required_columns, optional_columns=None):
#     """Clean and validate DataFrame"""
#     if optional_columns is None:
#         optional_columns = {}
    
#     # Strip whitespace from column names
#     df.columns = df.columns.str.strip()
    
#     # Check required columns
#     missing_cols = set(required_columns) - set(df.columns)
#     if missing_cols:
#         raise ValueError(f"Missing required columns: {missing_cols}")
    
#     # Fill optional columns with defaults
#     for col, default_val in optional_columns.items():
#         if col not in df.columns:
#             df[col] = default_val
    
#     # Strip whitespace from string columns
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             df[col] = df[col].astype(str).str.strip()
    
#     # Remove empty rows
#     df = df.dropna(how='all')
    
#     return df

# # Helper functions for processing each file type
# def process_courses_file(df):
#     """Process courses CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Courses CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'course_id': 'id', 'course_name': 'name', 'course_code': 'code',
#             'course_credits': 'credits', 'course_type': 'course_type',
#             'hours_per_week': 'hours_per_week', 'department': 'department',
#             'semester': 'semester', 'faculty_id': 'faculty_id',
#             'requires_lab': 'requires_lab', 'requires_smart_room': 'requires_smart_room',
#             'is_interdisciplinary': 'is_interdisciplinary', 'connected_departments': 'connected_departments',
#             'max_students': 'max_students', 'min_duration_minutes': 'min_duration_minutes',
#             'max_consecutive_hours': 'max_consecutive_hours', 'preferred_days': 'preferred_days'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'code', 'credits', 'course_type', 'hours_per_week', 
#                        'department', 'semester', 'faculty_id']
#         optional_cols = {
#             'requires_lab': False, 'requires_smart_room': False, 'is_interdisciplinary': False,
#             'connected_departments': '[]', 'max_students': 60, 'min_duration_minutes': 50,
#             'max_consecutive_hours': 2, 'preferred_days': '[]'
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         courses_data = []
#         for _, row in df.iterrows():
#             course_data = {
#                 "id": str(row['id']), "name": str(row['name']), "code": str(row['code']),
#                 "credits": int(float(row['credits'])), "course_type": str(row['course_type']).lower(),
#                 "hours_per_week": int(float(row['hours_per_week'])), "department": str(row['department']),
#                 "semester": int(float(row['semester'])), "faculty_id": str(row['faculty_id']),
#                 "requires_lab": parse_boolean_field(row.get('requires_lab', False)),
#                 "requires_smart_room": parse_boolean_field(row.get('requires_smart_room', False)),
#                 "is_interdisciplinary": parse_boolean_field(row.get('is_interdisciplinary', False)),
#                 "connected_departments": parse_list_field(row.get('connected_departments', [])),
#                 "max_students": int(float(row.get('max_students', 60))),
#                 "min_duration_minutes": int(float(row.get('min_duration_minutes', 50))),
#                 "max_consecutive_hours": int(float(row.get('max_consecutive_hours', 2))),
#                 "preferred_days": parse_list_field(row.get('preferred_days', []))
#             }
#             courses_data.append(course_data)
            
#         return {"data": courses_data}
        
#     except Exception as e:
#         return {"error": f"Error processing courses: {str(e)}"}

# def process_faculty_file(df):
#     """Process faculty CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Faculty CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'faculty_id': 'id', 'faculty_name': 'name', 'department': 'department',
#             'designation': 'designation', 'specializations': 'specializations',
#             'courses_can_teach': 'courses_can_teach', 'max_hours_per_day': 'max_hours_per_day',
#             'max_hours_per_week': 'max_hours_per_week', 'preferred_time': 'preferred_time',
#             'unavailable_slots': 'unavailable_slots', 'research_slots': 'research_slots',
#             'is_visiting': 'is_visiting', 'workload_preference': 'workload_preference'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'department', 'designation', 'specializations', 'courses_can_teach']
#         optional_cols = {
#             'max_hours_per_day': 6, 'max_hours_per_week': 24, 'preferred_time': 'any',
#             'unavailable_slots': '[]', 'research_slots': '[]', 'is_visiting': False,
#             'workload_preference': 1.0
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         faculty_data = []
#         for _, row in df.iterrows():
#             faculty_data.append({
#                 "id": str(row['id']), "name": str(row['name']), "department": str(row['department']),
#                 "designation": str(row['designation']), "specializations": parse_list_field(row['specializations']),
#                 "courses_can_teach": parse_list_field(row['courses_can_teach']),
#                 "max_hours_per_day": int(float(row.get('max_hours_per_day', 6))),
#                 "max_hours_per_week": int(float(row.get('max_hours_per_week', 24))),
#                 "preferred_time": str(row.get('preferred_time', 'any')).lower(),
#                 "unavailable_slots": parse_list_field(row.get('unavailable_slots', [])),
#                 "research_slots": parse_list_field(row.get('research_slots', [])),
#                 "is_visiting": parse_boolean_field(row.get('is_visiting', False)),
#                 "workload_preference": float(row.get('workload_preference', 1.0))
#             })
            
#         return {"data": faculty_data}
        
#     except Exception as e:
#         return {"error": f"Error processing faculty: {str(e)}"}

# def process_classrooms_file(df):
#     """Process classrooms CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Classrooms CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'room_id': 'id', 'room_name': 'name', 'capacity': 'capacity',
#             'room_type': 'room_type', 'department': 'department',
#             'equipment': 'equipment', 'is_smart_room': 'is_smart_room',
#             'is_ac': 'is_ac', 'has_projector': 'has_projector',
#             'weekly_maintenance': 'weekly_maintenance'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'capacity', 'room_type', 'department']
#         optional_cols = {
#             'equipment': '[]', 'is_smart_room': False, 'is_ac': False,
#             'has_projector': True, 'weekly_maintenance': '[]'
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         classrooms_data = []
#         for _, row in df.iterrows():
#             classroom_data = {
#                 "id": str(row['id']), "name": str(row['name']),
#                 "capacity": int(float(row['capacity'])),
#                 "room_type": str(row['room_type']).lower(),
#                 "department": str(row['department']),
#                 "equipment": parse_list_field(row.get('equipment', [])),
#                 "is_smart_room": parse_boolean_field(row.get('is_smart_room', False)),
#                 "is_ac": parse_boolean_field(row.get('is_ac', False)),
#                 "has_projector": parse_boolean_field(row.get('has_projector', True)),
#                 "weekly_maintenance": parse_list_field(row.get('weekly_maintenance', []))
#             }
#             classrooms_data.append(classroom_data)
            
#         return {"data": classrooms_data}
        
#     except Exception as e:
#         return {"error": f"Error processing classrooms: {str(e)}"}

# def process_batches_file(df):
#     """Process batches CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Batches CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'batch_id': 'id', 'batch_name': 'name', 'department': 'department',
#             'semester': 'semester', 'student_count': 'student_count',
#             'core_courses': 'core_courses', 'elective_courses': 'elective_courses',
#             'skill_courses': 'skill_courses', 'multidisciplinary_courses': 'multidisciplinary_courses',
#             'preferred_morning_hours': 'preferred_morning_hours', 'max_hours_per_day': 'max_hours_per_day'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'department', 'semester', 'student_count']
#         optional_cols = {
#             'core_courses': '[]', 'elective_courses': '[]', 'skill_courses': '[]',
#             'multidisciplinary_courses': '[]', 'preferred_morning_hours': True,
#             'max_hours_per_day': 7
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         batches_data = []
#         for _, row in df.iterrows():
#             batch_data = {
#                 "id": str(row['id']), "name": str(row['name']),
#                 "department": str(row['department']),
#                 "semester": int(float(row['semester'])),
#                 "student_count": int(float(row['student_count'])),
#                 "core_courses": parse_list_field(row.get('core_courses', [])),
#                 "elective_courses": parse_list_field(row.get('elective_courses', [])),
#                 "skill_courses": parse_list_field(row.get('skill_courses', [])),
#                 "multidisciplinary_courses": parse_list_field(row.get('multidisciplinary_courses', [])),
#                 "preferred_morning_hours": parse_boolean_field(row.get('preferred_morning_hours', True)),
#                 "max_hours_per_day": int(float(row.get('max_hours_per_day', 7)))
#             }
#             batches_data.append(batch_data)
            
#         return {"data": batches_data}
        
#     except Exception as e:
#         return {"error": f"Error processing batches: {str(e)}"}

# @app.route('/api/user-preferences-template', methods=['GET'])
# def get_user_preferences_template():
#     """Get user preferences template for the frontend"""
#     try:
#         template = {
#             "working_days": {
#                 "type": "integer",
#                 "value": 5,
#                 "range": [5, 6],
#                 "description": "Number of working days per week"
#             },
#             "periods_per_day": {
#                 "type": "integer", 
#                 "value": 8,
#                 "range": [6, 10],
#                 "description": "Number of periods per day"
#             },
#             "lunch_break_period": {
#                 "type": "integer",
#                 "value": 4,
#                 "range": [3, 6],
#                 "description": "Period number for lunch break"
#             },
#             "max_consecutive_same_subject": {
#                 "type": "integer",
#                 "value": 2,
#                 "range": [1, 4],
#                 "description": "Maximum consecutive hours for same subject"
#             },
#             "gap_penalty_weight": {
#                 "type": "float",
#                 "value": 10.0,
#                 "range": [0.0, 50.0],
#                 "description": "Penalty weight for schedule gaps"
#             },
#             "faculty_preference_weight": {
#                 "type": "float",
#                 "value": 15.0,
#                 "range": [0.0, 50.0],
#                 "description": "Weight for faculty time preferences"
#             },
#             "workload_balance_weight": {
#                 "type": "float",
#                 "value": 20.0,
#                 "range": [0.0, 50.0],
#                 "description": "Weight for workload balance optimization"
#             },
#             "room_preference_weight": {
#                 "type": "float",
#                 "value": 5.0,
#                 "range": [0.0, 20.0],
#                 "description": "Weight for room preference matching"
#             },
#             "interdisciplinary_bonus": {
#                 "type": "float",
#                 "value": 10.0,
#                 "range": [0.0, 30.0],
#                 "description": "Bonus for interdisciplinary courses"
#             },
#             "research_slot_protection": {
#                 "type": "boolean",
#                 "value": True,
#                 "description": "Protect faculty research time slots"
#             },
#             "allow_saturday_classes": {
#                 "type": "boolean",
#                 "value": False,
#                 "description": "Allow classes on Saturday"
#             },
#             "morning_start_time": {
#                 "type": "string",
#                 "value": "9:00",
#                 "options": ["8:00", "8:30", '9:00', '9:30'],
#                 "description": "Morning classes start time"
#             },
#             "evening_end_time": {
#                 "type": "string",
#                 "value": "5:00",
#                 "options": ["4:00", "4:30", '5:00', '5:30', '6:00'],
#                 "description": "Evening classes end time"
#             }
#         }
        
#         return jsonify({
#             "success": True,
#             "template": template
#         })
    
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": f"Failed to load preferences template: {str(e)}"
#         }), 500

# @app.route('/api/convert-csv-to-json', methods=['POST'])
# def convert_csv_to_json():
#     """Convert uploaded CSV or JSON files to standardized JSON format"""
#     try:
#         # Check if all required files are present
#         required_files = ['courses_csv', 'faculty_csv', 'classrooms_csv', 'batches_csv']
        
#         for file_key in required_files:
#             if file_key not in request.files:
#                 return jsonify({
#                     "success": False,
#                     "error": f"Missing required file: {file_key}"
#                 }), 400
        
#         # Process each file
#         processed_data = {
#             "courses": [],
#             "faculty": [],
#             "classrooms": [],
#             "student_batches": []
#         }
        
#         file_processors = {
#             'courses_csv': process_courses_file,
#             'faculty_csv': process_faculty_file,
#             'classrooms_csv': process_classrooms_file,
#             'batches_csv': process_batches_file
#         }
        
#         file_type_mapping = {
#             'courses_csv': 'courses',
#             'faculty_csv': 'faculty',
#             'classrooms_csv': 'classrooms',
#             'batches_csv': 'student_batches'
#         }
        
#         for file_key, processor in file_processors.items():
#             file_obj = request.files[file_key]
#             filename = file_obj.filename.lower()
            
#             if filename.endswith('.json'):
#                 # Process JSON file directly
#                 try:
#                     file_content = file_obj.read()
#                     json_data, error = safe_read_json(file_content, filename)
#                     if error:
#                         return jsonify({"success": False, "error": error}), 400
                    
#                     # Handle different JSON structures
#                     if isinstance(json_data, dict):
#                         # Check if the JSON has the expected key (e.g., "faculty": [...])
#                         expected_key = file_type_mapping[file_key]
#                         if expected_key in json_data:
#                             processed_data[expected_key] = json_data[expected_key]
#                         else:
#                             # Assume the JSON contains the array directly at the top level
#                             processed_data[expected_key] = list(json_data.values())[0] if json_data else []
#                     elif isinstance(json_data, list):
#                         # JSON is already an array
#                         processed_data[file_type_mapping[file_key]] = json_data
#                     else:
#                         return jsonify({
#                             "success": False,
#                             "error": f"Invalid JSON structure in {filename}. Expected object with key '{file_type_mapping[file_key]}' or array."
#                         }), 400
                        
#                 except Exception as e:
#                     return jsonify({
#                         "success": False,
#                         "error": f"Error processing JSON file {filename}: {str(e)}"
#                     }), 400
                    
#             elif filename.endswith('.csv'):
#                 # Process CSV file
#                 file_content = file_obj.read()
#                 df, error = safe_read_csv(file_content, filename)
#                 if error:
#                     return jsonify({"success": False, "error": error}), 400
                
#                 # Call the appropriate processor
#                 result = processor(df)
#                 if 'error' in result:
#                     return jsonify({"success": False, "error": result['error']}), 400
                
#                 processed_data[file_type_mapping[file_key]] = result['data']
                
#             else:
#                 return jsonify({
#                     "success": False,
#                     "error": f"Unsupported file format for {filename}. Please use .csv or .json"
#                 }), 400
        
#         print(f"Processed data summary:")
#         print(f"- Courses: {len(processed_data['courses'])}")
#         print(f"- Faculty: {len(processed_data['faculty'])}")
#         print(f"- Classrooms: {len(processed_data['classrooms'])}")
#         print(f"- Batches: {len(processed_data['student_batches'])}")
        
#         return jsonify({
#             "success": True,
#             "data": processed_data,
#             "message": f"Successfully processed {len(processed_data['courses'])} courses, {len(processed_data['faculty'])} faculty, {len(processed_data['classrooms'])} classrooms, and {len(processed_data['student_batches'])} batches"
#         })
    
#     except Exception as e:
#         error_msg = f"Error processing files: {str(e)}"
#         print(error_msg)
#         print(traceback.format_exc())
#         return jsonify({
#             "success": False,
#             "error": error_msg,
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/api/validate-data', methods=['POST'])
# def validate_data():
#     """Validate the processed institutional data"""
#     try:
#         request_data = request.get_json()
        
#         if not request_data:
#             return jsonify({"success": False, "error": "No data provided"}), 400
        
#         data = request_data.get('institution_data', {})
#         user_preferences = request_data.get('user_preferences', {})
        
#         errors = []
#         warnings = []
        
#         # --- START OF VALIDATION LOGIC ---
        
#         # Determine working days and periods from preferences, with defaults
#         allow_saturday = user_preferences.get('allow_saturday_classes', False)
#         working_days = 6 if allow_saturday else 5
#         periods_per_day = user_preferences.get('periods_per_day', 8)
        
#         # Validate faculty slots
#         faculty = data.get('faculty', [])
#         faculty_ids = {fac['id'] for fac in faculty}
        
#         for fac in faculty:
#             # Check research_slots
#             for slot in fac.get('research_slots', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot on day {day}, which is outside the configured {working_days} working days (0-{working_days-1}).")
#                     if period >= periods_per_day:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot in period {period}, which is outside the configured {periods_per_day} periods per day (0-{periods_per_day-1}).")
            
#             # Check unavailable_slots
#             for slot in fac.get('unavailable_slots', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot on day {day}, which is outside the configured {working_days} working days.")
#                     if period >= periods_per_day:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot in period {period}, which is outside the configured {periods_per_day} periods per day.")

#         # Validate classroom maintenance slots
#         classrooms = data.get('classrooms', [])
#         classroom_ids = {room['id'] for room in classrooms}

#         for room in classrooms:
#             for slot in room.get('weekly_maintenance', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot on day {day}, which is outside the configured {working_days} working days.")
#                     if period >= periods_per_day:
#                         errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot in period {period}, which is outside the configured {periods_per_day} periods per day.")
        
#         # Check for duplicate IDs
#         courses = data.get('courses', [])
#         course_ids = set()
#         for course in courses:
#             if course['id'] in course_ids:
#                 errors.append(f"Duplicate course ID: {course['id']}")
#             course_ids.add(course['id'])
            
#             if course.get('faculty_id') not in faculty_ids:
#                 warnings.append(f"Course '{course['name']}' (ID: {course['id']}) references a non-existent faculty ID: {course.get('faculty_id')}")

#         batches = data.get('student_batches', [])
#         batch_ids = set()
#         for batch in batches:
#             if batch['id'] in batch_ids:
#                 errors.append(f"Duplicate batch ID: {batch['id']}")
#             batch_ids.add(batch['id'])
            
#             all_batch_courses = (batch.get('core_courses', []) + batch.get('elective_courses', []) + 
#                                batch.get('skill_courses', []) + batch.get('multidisciplinary_courses', []))
#             for course_id in all_batch_courses:
#                 if course_id not in course_ids:
#                     warnings.append(f"Batch '{batch['name']}' references an unknown course ID: {course_id}")

#         total_course_hours = sum(c.get('hours_per_week', 0) for c in courses)
        
#         return jsonify({
#             "success": True,
#             "valid": len(errors) == 0,
#             "errors": errors,
#             "warnings": warnings,
#             "statistics": { 
#                 "courses": len(courses), 
#                 "faculty": len(faculty), 
#                 "classrooms": len(classrooms), 
#                 "batches": len(batches),
#                 "total_course_hours": total_course_hours
#             }
#         })
    
#     except Exception as e:
#         error_msg = f"Error validating data: {str(e)}"
#         print(error_msg)
#         print(traceback.format_exc())
#         return jsonify({ 
#             "success": False, 
#             "error": error_msg, 
#             "traceback": traceback.format_exc() 
#         }), 500

# @app.route('/api/generate-timetable', methods=['POST'])
# def generate_timetable():
#     """Generate NEP compliant timetable using genetic algorithm"""
#     try:
#         request_data = request.get_json()
        
#         if not request_data:
#             return jsonify({
#                 "success": False,
#                 "error": "No data provided"
#             }), 400
        
#         institution_data = request_data.get('institution_data')
#         user_preferences = request_data.get('user_preferences', {})
#         generation_params = request_data.get('generation_params', {})
        
#         if not institution_data:
#             return jsonify({
#                 "success": False,
#                 "error": "Institution data is required"
#             }), 400
        
#         # Set default generation parameters
#         population_size = generation_params.get('population_size', 30)
#         generations = generation_params.get('generations', 50)
        
#         # Ensure reasonable limits
#         population_size = max(10, min(100, population_size))
#         generations = max(20, min(200, generations))
        
#         print(f"Starting timetable generation with population_size={population_size}, generations={generations}")
#         print(f"User preferences: {user_preferences}")
        
#         # Generate timetable using your existing function
#         result = generate_timetable_api(
#             json.dumps(institution_data),
#             user_preferences,
#             population_size=population_size,
#             generations=generations
#         )
        
#         return jsonify({
#             "success": True,
#             "data": result,
#             "generation_params": {
#                 "population_size": population_size,
#                 "generations": generations
#             },
#             "timestamp": datetime.now().isoformat()
#         })
    
#     except Exception as e:
#         error_msg = f"Timetable generation failed: {str(e)}"
#         print(error_msg)
#         print(f"Traceback: {traceback.format_exc()}")
        
#         return jsonify({
#             "success": False,
#             "error": error_msg,
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/api/debug', methods=['POST'])
# def debug_endpoint():
#     """Debug endpoint to test data processing"""
#     try:
#         request_data = request.get_json()
#         print("Debug request received:")
#         print(json.dumps(request_data, indent=2))
        
#         return jsonify({
#             "success": True,
#             "message": "Debug data received",
#             "data": request_data
#         })
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": f"Debug error: {str(e)}"
#         }), 500

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         "success": True,
#         "message": "NEP Timetable Generator API is running",
#         "timestamp": datetime.now().isoformat(),
#         "python_version": sys.version
#     })

# @app.errorhandler(413)
# def request_entity_too_large(error):
#     return jsonify({
#         "success": False,
#         "error": "File too large. Maximum size is 16MB."
#     }), 413

# @app.errorhandler(500)
# def internal_server_error(error):
#     error_msg = "Internal server error occurred."
#     print(error_msg)
#     print(traceback.format_exc())
#     return jsonify({
#         "success": False,
#         "error": error_msg,
#         "traceback": traceback.format_exc()
#     }), 500

# if __name__ == '__main__':
#     print("Starting NEP 2020 Timetable Generator API...")
#     print("API endpoints:")
#     print("- GET  /api/health - Health check")
#     print("- GET  /api/user-preferences-template - Get user preferences template")
#     print("- POST /api/convert-csv-to-json - Convert CSV files to JSON")
#     print("- POST /api/validate-data - Validate institutional data")
#     print("- POST /api/generate-timetable - Generate timetable")
#     print("- POST /api/debug - Debug endpoint")
    
#     app.run(debug=True, host='0.0.0.0', port=5000)


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# import json
# import io
# import traceback
# from werkzeug.utils import secure_filename
# import os
# from datetime import datetime
# import ast
# import sys

# # Import your NEP timetable generator
# try:
#     from nep_timetable import NEPTimetableGenerator, generate_timetable_api, UserPreferences
# except ImportError as e:
#     print(f"Import error: {e}")
#     # Create dummy classes for testing
#     class NEPTimetableGenerator:
#         def __init__(self, **kwargs):
#             pass
#     def generate_timetable_api(*args, **kwargs):
#         return {"error": "NEP timetable module not available"}
#     class UserPreferences:
#         pass

# app = Flask(__name__)
# CORS(app)

# # Configuration
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# UPLOAD_FOLDER = 'temp_uploads'
# ALLOWED_EXTENSIONS = {'csv', 'json'}  # Added JSON support

# # Create upload folder if it doesn't exist
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def safe_read_csv(file_content, filename):
#     """Safely read CSV with error handling"""
#     try:
#         # Try different encodings
#         encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
#         for encoding in encodings:
#             try:
#                 df = pd.read_csv(io.StringIO(file_content.decode(encoding)))
#                 return df, None
#             except UnicodeDecodeError:
#                 continue
        
#         return None, f"Unable to decode {filename} with any common encoding"
#     except Exception as e:
#         return None, f"Error reading {filename}: {str(e)}"

# def safe_read_json(file_content, filename):
#     """Safely read JSON with error handling"""
#     try:
#         json_data = json.loads(file_content.decode('utf-8'))
#         return json_data, None
#     except json.JSONDecodeError as e:
#         return None, f"Invalid JSON in {filename}: {str(e)}"
#     except Exception as e:
#         return None, f"Error reading JSON file {filename}: {str(e)}"

# def parse_list_field(value, default=[]):
#     """Parse list fields from CSV that might be string representations"""
#     if pd.isna(value) or value == '' or value == '[]':
#         return default
    
#     if isinstance(value, list):
#         return value
    
#     if isinstance(value, str):
#         try:
#             # Try to parse as Python list
#             cleaned_value = value.strip()
#             if cleaned_value.startswith('[') and cleaned_value.endswith(']'):
#                 return ast.literal_eval(cleaned_value)
#             elif ',' in cleaned_value:
#                 return [item.strip() for item in cleaned_value.split(',') if item.strip()]
#             elif cleaned_value:
#                 return [cleaned_value]
#         except (ValueError, SyntaxError) as e:
#             print(f"Warning: Could not parse list field '{value}': {e}")
#             # If that fails, return as single item list
#             return [value] if value else default
    
#     return default

# def parse_boolean_field(value, default=False):
#     """Parse boolean fields from various formats"""
#     if pd.isna(value) or value == '':
#         return default
    
#     if isinstance(value, bool):
#         return value
    
#     if isinstance(value, (int, float)):
#         return bool(value)
    
#     if isinstance(value, str):
#         lower_val = value.lower().strip()
#         if lower_val in ['true', 'yes', '1', 't', 'y']:
#             return True
#         elif lower_val in ['false', 'no', '0', 'f', 'n']:
#             return False
    
#     return default

# def clean_dataframe(df, required_columns, optional_columns=None):
#     """Clean and validate DataFrame"""
#     if optional_columns is None:
#         optional_columns = {}
    
#     # Strip whitespace from column names
#     df.columns = df.columns.str.strip()
    
#     # Check required columns
#     missing_cols = set(required_columns) - set(df.columns)
#     if missing_cols:
#         raise ValueError(f"Missing required columns: {missing_cols}")
    
#     # Fill optional columns with defaults
#     for col, default_val in optional_columns.items():
#         if col not in df.columns:
#             df[col] = default_val
    
#     # Strip whitespace from string columns
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             df[col] = df[col].astype(str).str.strip()
    
#     # Remove empty rows
#     df = df.dropna(how='all')
    
#     return df

# # Helper functions for processing each file type
# def process_courses_file(df):
#     """Process courses CSV with lab duration support"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Courses CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'course_id': 'id', 'course_name': 'name', 'course_code': 'code',
#             'course_credits': 'credits', 'course_type': 'course_type',
#             'hours_per_week': 'hours_per_week', 'department': 'department',
#             'semester': 'semester', 'faculty_id': 'faculty_id',
#             'requires_lab': 'requires_lab', 'requires_smart_room': 'requires_smart_room',
#             'is_interdisciplinary': 'is_interdisciplinary', 'connected_departments': 'connected_departments',
#             'max_students': 'max_students', 'min_duration_minutes': 'min_duration_minutes',
#             'max_consecutive_hours': 'max_consecutive_hours', 'preferred_days': 'preferred_days'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'code', 'credits', 'course_type', 'hours_per_week', 
#                          'department', 'semester', 'faculty_id']
#         optional_cols = {
#             'requires_lab': False, 'requires_smart_room': False, 'is_interdisciplinary': False,
#             'connected_departments': '[]', 'max_students': 60, 'min_duration_minutes': 50,
#             'max_consecutive_hours': 2, 'preferred_days': '[]'
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         courses_data = []
#         for _, row in df.iterrows():
#             # Parse lab duration properly
#             requires_lab = parse_boolean_field(row.get('requires_lab', False))
#             min_duration = int(float(row.get('min_duration_minutes', 50)))
#             max_consecutive = int(float(row.get('max_consecutive_hours', 2)))
            
#             # Auto-detect lab courses and set proper duration
#             if requires_lab and min_duration == 50:
#                 min_duration = 240  # Set to 4 hours for labs
#                 max_consecutive = 4
            
#             course_data = {
#                 "id": str(row['id']), "name": str(row['name']), "code": str(row['code']),
#                 "credits": int(float(row['credits'])), "course_type": str(row['course_type']).lower(),
#                 "hours_per_week": int(float(row['hours_per_week'])), "department": str(row['department']),
#                 "semester": int(float(row['semester'])), "faculty_id": str(row['faculty_id']),
#                 "requires_lab": requires_lab,
#                 "requires_smart_room": parse_boolean_field(row.get('requires_smart_room', False)),
#                 "is_interdisciplinary": parse_boolean_field(row.get('is_interdisciplinary', False)),
#                 "connected_departments": parse_list_field(row.get('connected_departments', [])),
#                 "max_students": int(float(row.get('max_students', 60))),
#                 "min_duration_minutes": min_duration,
#                 "max_consecutive_hours": max_consecutive,
#                 "preferred_days": parse_list_field(row.get('preferred_days', []))
#             }
#             courses_data.append(course_data)
            
#         return {"data": courses_data}
        
#     except Exception as e:
#         return {"error": f"Error processing courses: {str(e)}"}

# def process_faculty_file(df):
#     """Process faculty CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Faculty CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'faculty_id': 'id', 'faculty_name': 'name', 'department': 'department',
#             'designation': 'designation', 'specializations': 'specializations',
#             'courses_can_teach': 'courses_can_teach', 'max_hours_per_day': 'max_hours_per_day',
#             'max_hours_per_week': 'max_hours_per_week', 'preferred_time': 'preferred_time',
#             'unavailable_slots': 'unavailable_slots', 'research_slots': 'research_slots',
#             'is_visiting': 'is_visiting', 'workload_preference': 'workload_preference'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'department', 'designation', 'specializations', 'courses_can_teach']
#         optional_cols = {
#             'max_hours_per_day': 6, 'max_hours_per_week': 24, 'preferred_time': 'any',
#             'unavailable_slots': '[]', 'research_slots': '[]', 'is_visiting': False,
#             'workload_preference': 1.0
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         faculty_data = []
#         for _, row in df.iterrows():
#             faculty_data.append({
#                 "id": str(row['id']), "name": str(row['name']), "department": str(row['department']),
#                 "designation": str(row['designation']), "specializations": parse_list_field(row['specializations']),
#                 "courses_can_teach": parse_list_field(row['courses_can_teach']),
#                 "max_hours_per_day": int(float(row.get('max_hours_per_day', 6))),
#                 "max_hours_per_week": int(float(row.get('max_hours_per_week', 24))),
#                 "preferred_time": str(row.get('preferred_time', 'any')).lower(),
#                 "unavailable_slots": parse_list_field(row.get('unavailable_slots', [])),
#                 "research_slots": parse_list_field(row.get('research_slots', [])),
#                 "is_visiting": parse_boolean_field(row.get('is_visiting', False)),
#                 "workload_preference": float(row.get('workload_preference', 1.0))
#             })
            
#         return {"data": faculty_data}
        
#     except Exception as e:
#         return {"error": f"Error processing faculty: {str(e)}"}

# def process_classrooms_file(df):
#     """Process classrooms CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Classrooms CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'room_id': 'id', 'room_name': 'name', 'capacity': 'capacity',
#             'room_type': 'room_type', 'department': 'department',
#             'equipment': 'equipment', 'is_smart_room': 'is_smart_room',
#             'is_ac': 'is_ac', 'has_projector': 'has_projector',
#             'weekly_maintenance': 'weekly_maintenance'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'capacity', 'room_type', 'department']
#         optional_cols = {
#             'equipment': '[]', 'is_smart_room': False, 'is_ac': False,
#             'has_projector': True, 'weekly_maintenance': '[]'
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         classrooms_data = []
#         for _, row in df.iterrows():
#             classroom_data = {
#                 "id": str(row['id']), "name": str(row['name']),
#                 "capacity": int(float(row['capacity'])),
#                 "room_type": str(row['room_type']).lower(),
#                 "department": str(row['department']),
#                 "equipment": parse_list_field(row.get('equipment', [])),
#                 "is_smart_room": parse_boolean_field(row.get('is_smart_room', False)),
#                 "is_ac": parse_boolean_field(row.get('is_ac', False)),
#                 "has_projector": parse_boolean_field(row.get('has_projector', True)),
#                 "weekly_maintenance": parse_list_field(row.get('weekly_maintenance', []))
#             }
#             classrooms_data.append(classroom_data)
            
#         return {"data": classrooms_data}
        
#     except Exception as e:
#         return {"error": f"Error processing classrooms: {str(e)}"}

# def process_batches_file(df):
#     """Process batches CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Batches CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'batch_id': 'id', 'batch_name': 'name', 'department': 'department',
#             'semester': 'semester', 'student_count': 'student_count',
#             'core_courses': 'core_courses', 'elective_courses': 'elective_courses',
#             'skill_courses': 'skill_courses', 'multidisciplinary_courses': 'multidisciplinary_courses',
#             'preferred_morning_hours': 'preferred_morning_hours', 'max_hours_per_day': 'max_hours_per_day'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'department', 'semester', 'student_count']
#         optional_cols = {
#             'core_courses': '[]', 'elective_courses': '[]', 'skill_courses': '[]',
#             'multidisciplinary_courses': '[]', 'preferred_morning_hours': True,
#             'max_hours_per_day': 7
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         batches_data = []
#         for _, row in df.iterrows():
#             batch_data = {
#                 "id": str(row['id']), "name": str(row['name']),
#                 "department": str(row['department']),
#                 "semester": int(float(row['semester'])),
#                 "student_count": int(float(row['student_count'])),
#                 "core_courses": parse_list_field(row.get('core_courses', [])),
#                 "elective_courses": parse_list_field(row.get('elective_courses', [])),
#                 "skill_courses": parse_list_field(row.get('skill_courses', [])),
#                 "multidisciplinary_courses": parse_list_field(row.get('multidisciplinary_courses', [])),
#                 "preferred_morning_hours": parse_boolean_field(row.get('preferred_morning_hours', True)),
#                 "max_hours_per_day": int(float(row.get('max_hours_per_day', 7)))
#             }
#             batches_data.append(batch_data)
            
#         return {"data": batches_data}
        
#     except Exception as e:
#         return {"error": f"Error processing batches: {str(e)}"}

# @app.route('/api/user-preferences-template', methods=['GET'])
# def get_user_preferences_template():
#     """Get user preferences template for the frontend"""
#     try:
#         template = {
#             "working_days": {
#                 "type": "integer",
#                 "value": 5,
#                 "range": [5, 6],
#                 "description": "Number of working days per week"
#             },
#             "periods_per_day": {
#                 "type": "integer", 
#                 "value": 8,
#                 "range": [6, 10],
#                 "description": "Number of periods per day"
#             },
#             "lunch_break_period": {
#                 "type": "integer",
#                 "value": 4,
#                 "range": [3, 6],
#                 "description": "Period number for lunch break"
#             },
#             "max_consecutive_same_subject": {
#                 "type": "integer",
#                 "value": 2,
#                 "range": [1, 4],
#                 "description": "Maximum consecutive hours for same subject"
#             },
#             "gap_penalty_weight": {
#                 "type": "float",
#                 "value": 10.0,
#                 "range": [0.0, 50.0],
#                 "description": "Penalty weight for schedule gaps"
#             },
#             "faculty_preference_weight": {
#                 "type": "float",
#                 "value": 15.0,
#                 "range": [0.0, 50.0],
#                 "description": "Weight for faculty time preferences"
#             },
#             "workload_balance_weight": {
#                 "type": "float",
#                 "value": 20.0,
#                 "range": [0.0, 50.0],
#                 "description": "Weight for workload balance optimization"
#             },
#             "room_preference_weight": {
#                 "type": "float",
#                 "value": 5.0,
#                 "range": [0.0, 20.0],
#                 "description": "Weight for room preference matching"
#             },
#             "interdisciplinary_bonus": {
#                 "type": "float",
#                 "value": 10.0,
#                 "range": [0.0, 30.0],
#                 "description": "Bonus for interdisciplinary courses"
#             },
#             "research_slot_protection": {
#                 "type": "boolean",
#                 "value": True,
#                 "description": "Protect faculty research time slots"
#             },
#             "allow_saturday_classes": {
#                 "type": "boolean",
#                 "value": False,
#                 "description": "Allow classes on Saturday"
#             },
#             "morning_start_time": {
#                 "type": "string",
#                 "value": "9:00",
#                 "options": ["8:00", "8:30", '9:00', '9:30'],
#                 "description": "Morning classes start time"
#             },
#             "evening_end_time": {
#                 "type": "string",
#                 "value": "5:00",
#                 "options": ["4:00", "4:30", '5:00', '5:30', '6:00'],
#                 "description": "Evening classes end time"
#             }
#         }
        
#         return jsonify({
#             "success": True,
#             "template": template
#         })
    
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": f"Failed to load preferences template: {str(e)}"
#         }), 500

# @app.route('/api/convert-csv-to-json', methods=['POST'])
# def convert_csv_to_json():
#     """Convert uploaded CSV or JSON files to standardized JSON format"""
#     try:
#         # Check if all required files are present
#         required_files = ['courses_csv', 'faculty_csv', 'classrooms_csv', 'batches_csv']
        
#         for file_key in required_files:
#             if file_key not in request.files:
#                 return jsonify({
#                     "success": False,
#                     "error": f"Missing required file: {file_key}"
#                 }), 400
        
#         # Process each file
#         processed_data = {
#             "courses": [],
#             "faculty": [],
#             "classrooms": [],
#             "student_batches": []
#         }
        
#         file_processors = {
#             'courses_csv': process_courses_file,
#             'faculty_csv': process_faculty_file,
#             'classrooms_csv': process_classrooms_file,
#             'batches_csv': process_batches_file
#         }
        
#         file_type_mapping = {
#             'courses_csv': 'courses',
#             'faculty_csv': 'faculty',
#             'classrooms_csv': 'classrooms',
#             'batches_csv': 'student_batches'
#         }
        
#         for file_key, processor in file_processors.items():
#             file_obj = request.files[file_key]
#             filename = file_obj.filename.lower()
            
#             if filename.endswith('.json'):
#                 # Process JSON file directly
#                 try:
#                     file_content = file_obj.read()
#                     json_data, error = safe_read_json(file_content, filename)
#                     if error:
#                         return jsonify({"success": False, "error": error}), 400
                    
#                     # Handle different JSON structures
#                     if isinstance(json_data, dict):
#                         # Check if the JSON has the expected key (e.g., "faculty": [...])
#                         expected_key = file_type_mapping[file_key]
#                         if expected_key in json_data:
#                             processed_data[expected_key] = json_data[expected_key]
#                         else:
#                             # Assume the JSON contains the array directly at the top level
#                             processed_data[expected_key] = list(json_data.values())[0] if json_data else []
#                     elif isinstance(json_data, list):
#                         # JSON is already an array
#                         processed_data[file_type_mapping[file_key]] = json_data
#                     else:
#                         return jsonify({
#                             "success": False,
#                             "error": f"Invalid JSON structure in {filename}. Expected object with key '{file_type_mapping[file_key]}' or array."
#                         }), 400
                        
#                 except Exception as e:
#                     return jsonify({
#                         "success": False,
#                         "error": f"Error processing JSON file {filename}: {str(e)}"
#                     }), 400
                    
#             elif filename.endswith('.csv'):
#                 # Process CSV file
#                 file_content = file_obj.read()
#                 df, error = safe_read_csv(file_content, filename)
#                 if error:
#                     return jsonify({"success": False, "error": error}), 400
                
#                 # Call the appropriate processor
#                 result = processor(df)
#                 if 'error' in result:
#                     return jsonify({"success": False, "error": result['error']}), 400
                
#                 processed_data[file_type_mapping[file_key]] = result['data']
                
#             else:
#                 return jsonify({
#                     "success": False,
#                     "error": f"Unsupported file format for {filename}. Please use .csv or .json"
#                 }), 400
        
#         print(f"Processed data summary:")
#         print(f"- Courses: {len(processed_data['courses'])}")
#         print(f"- Faculty: {len(processed_data['faculty'])}")
#         print(f"- Classrooms: {len(processed_data['classrooms'])}")
#         print(f"- Batches: {len(processed_data['student_batches'])}")
        
#         return jsonify({
#             "success": True,
#             "data": processed_data,
#             "message": f"Successfully processed {len(processed_data['courses'])} courses, {len(processed_data['faculty'])} faculty, {len(processed_data['classrooms'])} classrooms, and {len(processed_data['student_batches'])} batches"
#         })
    
#     except Exception as e:
#         error_msg = f"Error processing files: {str(e)}"
#         print(error_msg)
#         print(traceback.format_exc())
#         return jsonify({
#             "success": False,
#             "error": error_msg,
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/api/validate-data', methods=['POST'])
# def validate_data():
#     """Validate the processed institutional data"""
#     try:
#         request_data = request.get_json()
        
#         if not request_data:
#             return jsonify({"success": False, "error": "No data provided"}), 400
        
#         data = request_data.get('institution_data', {})
#         user_preferences = request_data.get('user_preferences', {})
        
#         errors = []
#         warnings = []
        
#         # --- START OF VALIDATION LOGIC ---
        
#         # Determine working days and periods from preferences, with defaults
#         allow_saturday = user_preferences.get('allow_saturday_classes', False)
#         working_days = 6 if allow_saturday else 5
#         periods_per_day = user_preferences.get('periods_per_day', 8)
        
#         # Validate faculty slots
#         faculty = data.get('faculty', [])
#         faculty_ids = {fac['id'] for fac in faculty}
        
#         for fac in faculty:
#             # Check research_slots
#             for slot in fac.get('research_slots', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot on day {day}, which is outside the configured {working_days} working days (0-{working_days-1}).")
#                     if period >= periods_per_day:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot in period {period}, which is outside the configured {periods_per_day} periods per day (0-{periods_per_day-1}).")
            
#             # Check unavailable_slots
#             for slot in fac.get('unavailable_slots', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot on day {day}, which is outside the configured {working_days} working days.")
#                     if period >= periods_per_day:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot in period {period}, which is outside the configured {periods_per_day} periods per day.")

#         # Validate classroom maintenance slots
#         classrooms = data.get('classrooms', [])
#         classroom_ids = {room['id'] for room in classrooms}

#         for room in classrooms:
#             for slot in room.get('weekly_maintenance', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot on day {day}, which is outside the configured {working_days} working days.")
#                     if period >= periods_per_day:
#                         errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot in period {period}, which is outside the configured {periods_per_day} periods per day.")
        
#         # Check for duplicate IDs
#         courses = data.get('courses', [])
#         course_ids = set()
#         for course in courses:
#             if course['id'] in course_ids:
#                 errors.append(f"Duplicate course ID: {course['id']}")
#             course_ids.add(course['id'])
            
#             if course.get('faculty_id') not in faculty_ids:
#                 warnings.append(f"Course '{course['name']}' (ID: {course['id']}) references a non-existent faculty ID: {course.get('faculty_id')}")

#         batches = data.get('student_batches', [])
#         batch_ids = set()
#         for batch in batches:
#             if batch['id'] in batch_ids:
#                 errors.append(f"Duplicate batch ID: {batch['id']}")
#             batch_ids.add(batch['id'])
            
#             all_batch_courses = (batch.get('core_courses', []) + batch.get('elective_courses', []) + 
#                                  batch.get('skill_courses', []) + batch.get('multidisciplinary_courses', []))
#             for course_id in all_batch_courses:
#                 if course_id not in course_ids:
#                     warnings.append(f"Batch '{batch['name']}' references an unknown course ID: {course_id}")

#         total_course_hours = sum(c.get('hours_per_week', 0) for c in courses)
        
#         return jsonify({
#             "success": True,
#             "valid": len(errors) == 0,
#             "errors": errors,
#             "warnings": warnings,
#             "statistics": { 
#                 "courses": len(courses), 
#                 "faculty": len(faculty), 
#                 "classrooms": len(classrooms), 
#                 "batches": len(batches),
#                 "total_course_hours": total_course_hours
#             }
#         })
    
#     except Exception as e:
#         error_msg = f"Error validating data: {str(e)}"
#         print(error_msg)
#         print(traceback.format_exc())
#         return jsonify({ 
#             "success": False, 
#             "error": error_msg, 
#             "traceback": traceback.format_exc() 
#         }), 500

# @app.route('/api/generate-timetable', methods=['POST'])
# def generate_timetable():
#     """Generate NEP compliant timetable using genetic algorithm"""
#     try:
#         request_data = request.get_json()
        
#         if not request_data:
#             return jsonify({
#                 "success": False,
#                 "error": "No data provided"
#             }), 400
        
#         institution_data = request_data.get('institution_data')
#         user_preferences = request_data.get('user_preferences', {})
#         generation_params = request_data.get('generation_params', {})
        
#         if not institution_data:
#             return jsonify({
#                 "success": False,
#                 "error": "Institution data is required"
#             }), 400
        
#         # Set default generation parameters
#         population_size = generation_params.get('population_size', 30)
#         generations = generation_params.get('generations', 50)
        
#         # Ensure reasonable limits
#         population_size = max(10, min(100, population_size))
#         generations = max(20, min(200, generations))
        
#         print(f"Starting timetable generation with population_size={population_size}, generations={generations}")
#         print(f"User preferences: {user_preferences}")
        
#         # Generate timetable using your existing function
#         result = generate_timetable_api(
#             json.dumps(institution_data),
#             user_preferences,
#             population_size=population_size,
#             generations=generations
#         )
        
#         return jsonify({
#             "success": True,
#             "data": result,
#             "generation_params": {
#                 "population_size": population_size,
#                 "generations": generations
#             },
#             "timestamp": datetime.now().isoformat()
#         })
    
#     except Exception as e:
#         error_msg = f"Timetable generation failed: {str(e)}"
#         print(error_msg)
#         print(f"Traceback: {traceback.format_exc()}")
        
#         return jsonify({
#             "success": False,
#             "error": error_msg,
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/api/debug', methods=['POST'])
# def debug_endpoint():
#     """Debug endpoint to test data processing"""
#     try:
#         request_data = request.get_json()
#         print("Debug request received:")
#         print(json.dumps(request_data, indent=2))
        
#         return jsonify({
#             "success": True,
#             "message": "Debug data received",
#             "data": request_data
#         })
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": f"Debug error: {str(e)}"
#         }), 500

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         "success": True,
#         "message": "NEP Timetable Generator API is running",
#         "timestamp": datetime.now().isoformat(),
#         "python_version": sys.version
#     })

# @app.errorhandler(413)
# def request_entity_too_large(error):
#     return jsonify({
#         "success": False,
#         "error": "File too large. Maximum size is 16MB."
#     }), 413

# @app.errorhandler(500)
# def internal_server_error(error):
#     error_msg = "Internal server error occurred."
#     print(error_msg)
#     print(traceback.format_exc())
#     return jsonify({
#         "success": False,
#         "error": error_msg,
#         "traceback": traceback.format_exc()
#     }), 500

# if __name__ == '__main__':
#     print("Starting NEP 2020 Timetable Generator API...")
#     print("API endpoints:")
#     print("- GET   /api/health - Health check")
#     print("- GET   /api/user-preferences-template - Get user preferences template")
#     print("- POST  /api/convert-csv-to-json - Convert CSV files to JSON")
#     print("- POST  /api/validate-data - Validate institutional data")
#     print("- POST  /api/generate-timetable - Generate timetable")
#     print("- POST  /api/debug - Debug endpoint")
    
#     app.run(debug=True, host='0.0.0.0', port=5000)




# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# import json
# import io
# import traceback
# from werkzeug.utils import secure_filename
# import os
# from datetime import datetime
# import ast
# import sys

# # Import the multi-section timetable generator
# try:
#     from nep_timetable import MultiSectionTimetableGenerator, generate_multi_section_timetable_api, UserPreferences
# except ImportError as e:
#     print(f"Import error: {e}")
#     # Create dummy classes for testing
#     class MultiSectionTimetableGenerator:
#         def __init__(self, **kwargs):
#             pass
#     def generate_multi_section_timetable_api(*args, **kwargs):
#         return {"error": "Multi-section timetable module not available"}
#     class UserPreferences:
#         pass

# app = Flask(__name__)

# # Enhanced CORS configuration
# CORS(app, 
#      resources={
#          r"/api/*": {
#              "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
#              "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#              "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
#              "supports_credentials": True
#          }
#      })

# # Configuration
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# UPLOAD_FOLDER = 'temp_uploads'
# ALLOWED_EXTENSIONS = {'csv', 'json'}

# # Create upload folder if it doesn't exist
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def safe_read_csv(file_content, filename):
#     """Safely read CSV with error handling"""
#     try:
#         # Try different encodings
#         encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
#         for encoding in encodings:
#             try:
#                 df = pd.read_csv(io.StringIO(file_content.decode(encoding)))
#                 return df, None
#             except UnicodeDecodeError:
#                 continue
        
#         return None, f"Unable to decode {filename} with any common encoding"
#     except Exception as e:
#         return None, f"Error reading {filename}: {str(e)}"

# def safe_read_json(file_content, filename):
#     """Safely read JSON with error handling"""
#     try:
#         json_data = json.loads(file_content.decode('utf-8'))
#         return json_data, None
#     except json.JSONDecodeError as e:
#         return None, f"Invalid JSON in {filename}: {str(e)}"
#     except Exception as e:
#         return None, f"Error reading JSON file {filename}: {str(e)}"

# def parse_list_field(value, default=[]):
#     """Parse list fields from CSV that might be string representations"""
#     if pd.isna(value) or value == '' or value == '[]':
#         return default
    
#     if isinstance(value, list):
#         return value
    
#     if isinstance(value, str):
#         try:
#             # Try to parse as Python list
#             cleaned_value = value.strip()
#             if cleaned_value.startswith('[') and cleaned_value.endswith(']'):
#                 return ast.literal_eval(cleaned_value)
#             elif ',' in cleaned_value:
#                 return [item.strip() for item in cleaned_value.split(',') if item.strip()]
#             elif cleaned_value:
#                 return [cleaned_value]
#         except (ValueError, SyntaxError) as e:
#             print(f"Warning: Could not parse list field '{value}': {e}")
#             # If that fails, return as single item list
#             return [value] if value else default
    
#     return default

# def parse_boolean_field(value, default=False):
#     """Parse boolean fields from various formats"""
#     if pd.isna(value) or value == '':
#         return default
    
#     if isinstance(value, bool):
#         return value
    
#     if isinstance(value, (int, float)):
#         return bool(value)
    
#     if isinstance(value, str):
#         lower_val = value.lower().strip()
#         if lower_val in ['true', 'yes', '1', 't', 'y']:
#             return True
#         elif lower_val in ['false', 'no', '0', 'f', 'n']:
#             return False
    
#     return default

# def clean_dataframe(df, required_columns, optional_columns=None):
#     """Clean and validate DataFrame"""
#     if optional_columns is None:
#         optional_columns = {}
    
#     # Strip whitespace from column names
#     df.columns = df.columns.str.strip()
    
#     # Check required columns
#     missing_cols = set(required_columns) - set(df.columns)
#     if missing_cols:
#         raise ValueError(f"Missing required columns: {missing_cols}")
    
#     # Fill optional columns with defaults
#     for col, default_val in optional_columns.items():
#         if col not in df.columns:
#             df[col] = default_val
    
#     # Strip whitespace from string columns
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             df[col] = df[col].astype(str).str.strip()
    
#     # Remove empty rows
#     df = df.dropna(how='all')
    
#     return df

# # Helper functions for processing each file type
# def process_courses_file(df):
#     """Process courses CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Courses CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'course_id': 'id', 'course_name': 'name', 'course_code': 'code',
#             'course_credits': 'credits', 'course_type': 'course_type',
#             'hours_per_week': 'hours_per_week', 'department': 'department',
#             'semester': 'semester', 'faculty_id': 'faculty_id',
#             'requires_lab': 'requires_lab', 'requires_smart_room': 'requires_smart_room',
#             'is_interdisciplinary': 'is_interdisciplinary', 'connected_departments': 'connected_departments',
#             'max_students': 'max_students', 'min_duration_minutes': 'min_duration_minutes',
#             'max_consecutive_hours': 'max_consecutive_hours', 'preferred_days': 'preferred_days'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'code', 'credits', 'course_type', 'hours_per_week', 
#                        'department', 'semester', 'faculty_id']
#         optional_cols = {
#             'requires_lab': False, 'requires_smart_room': False, 'is_interdisciplinary': False,
#             'connected_departments': '[]', 'max_students': 60, 'min_duration_minutes': 50,
#             'max_consecutive_hours': 2, 'preferred_days': '[]'
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         courses_data = []
#         for _, row in df.iterrows():
#             course_data = {
#                 "id": str(row['id']), "name": str(row['name']), "code": str(row['code']),
#                 "credits": int(float(row['credits'])), "course_type": str(row['course_type']).lower(),
#                 "hours_per_week": int(float(row['hours_per_week'])), "department": str(row['department']),
#                 "semester": int(float(row['semester'])), "faculty_id": str(row['faculty_id']),
#                 "requires_lab": parse_boolean_field(row.get('requires_lab', False)),
#                 "requires_smart_room": parse_boolean_field(row.get('requires_smart_room', False)),
#                 "is_interdisciplinary": parse_boolean_field(row.get('is_interdisciplinary', False)),
#                 "connected_departments": parse_list_field(row.get('connected_departments', [])),
#                 "max_students": int(float(row.get('max_students', 60))),
#                 "min_duration_minutes": int(float(row.get('min_duration_minutes', 50))),
#                 "max_consecutive_hours": int(float(row.get('max_consecutive_hours', 2))),
#                 "preferred_days": parse_list_field(row.get('preferred_days', []))
#             }
#             courses_data.append(course_data)
            
#         return {"data": courses_data}
        
#     except Exception as e:
#         return {"error": f"Error processing courses: {str(e)}"}

# def process_faculty_file(df):
#     """Process faculty CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Faculty CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'faculty_id': 'id', 'faculty_name': 'name', 'department': 'department',
#             'designation': 'designation', 'specializations': 'specializations',
#             'courses_can_teach': 'courses_can_teach', 'max_hours_per_day': 'max_hours_per_day',
#             'max_hours_per_week': 'max_hours_per_week', 'preferred_time': 'preferred_time',
#             'unavailable_slots': 'unavailable_slots', 'research_slots': 'research_slots',
#             'is_visiting': 'is_visiting', 'workload_preference': 'workload_preference'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'department', 'designation', 'specializations', 'courses_can_teach']
#         optional_cols = {
#             'max_hours_per_day': 6, 'max_hours_per_week': 24, 'preferred_time': 'any',
#             'unavailable_slots': '[]', 'research_slots': '[]', 'is_visiting': False,
#             'workload_preference': 1.0
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         faculty_data = []
#         for _, row in df.iterrows():
#             faculty_data.append({
#                 "id": str(row['id']), "name": str(row['name']), "department": str(row['department']),
#                 "designation": str(row['designation']), "specializations": parse_list_field(row['specializations']),
#                 "courses_can_teach": parse_list_field(row['courses_can_teach']),
#                 "max_hours_per_day": int(float(row.get('max_hours_per_day', 6))),
#                 "max_hours_per_week": int(float(row.get('max_hours_per_week', 24))),
#                 "preferred_time": str(row.get('preferred_time', 'any')).lower(),
#                 "unavailable_slots": parse_list_field(row.get('unavailable_slots', [])),
#                 "research_slots": parse_list_field(row.get('research_slots', [])),
#                 "is_visiting": parse_boolean_field(row.get('is_visiting', False)),
#                 "workload_preference": float(row.get('workload_preference', 1.0))
#             })
            
#         return {"data": faculty_data}
        
#     except Exception as e:
#         return {"error": f"Error processing faculty: {str(e)}"}

# def process_classrooms_file(df):
#     """Process classrooms CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Classrooms CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'room_id': 'id', 'room_name': 'name', 'capacity': 'capacity',
#             'room_type': 'room_type', 'department': 'department',
#             'equipment': 'equipment', 'is_smart_room': 'is_smart_room',
#             'is_ac': 'is_ac', 'has_projector': 'has_projector',
#             'weekly_maintenance': 'weekly_maintenance'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'capacity', 'room_type', 'department']
#         optional_cols = {
#             'equipment': '[]', 'is_smart_room': False, 'is_ac': False,
#             'has_projector': True, 'weekly_maintenance': '[]'
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         classrooms_data = []
#         for _, row in df.iterrows():
#             classroom_data = {
#                 "id": str(row['id']), "name": str(row['name']),
#                 "capacity": int(float(row['capacity'])),
#                 "room_type": str(row['room_type']).lower(),
#                 "department": str(row['department']),
#                 "equipment": parse_list_field(row.get('equipment', [])),
#                 "is_smart_room": parse_boolean_field(row.get('is_smart_room', False)),
#                 "is_ac": parse_boolean_field(row.get('is_ac', False)),
#                 "has_projector": parse_boolean_field(row.get('has_projector', True)),
#                 "weekly_maintenance": parse_list_field(row.get('weekly_maintenance', []))
#             }
#             classrooms_data.append(classroom_data)
            
#         return {"data": classrooms_data}
        
#     except Exception as e:
#         return {"error": f"Error processing classrooms: {str(e)}"}

# def process_batches_file(df):
#     """Process batches CSV DataFrame"""
#     try:
#         df.columns = df.columns.str.strip().str.lower()
#         print(f"Batches CSV columns: {list(df.columns)}")
        
#         column_mapping = {
#             'batch_id': 'id', 'batch_name': 'name', 'department': 'department',
#             'semester': 'semester', 'student_count': 'student_count',
#             'core_courses': 'core_courses', 'elective_courses': 'elective_courses',
#             'skill_courses': 'skill_courses', 'multidisciplinary_courses': 'multidisciplinary_courses',
#             'preferred_morning_hours': 'preferred_morning_hours', 'max_hours_per_day': 'max_hours_per_day'
#         }
        
#         df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
#         required_cols = ['id', 'name', 'department', 'semester', 'student_count']
#         optional_cols = {
#             'core_courses': '[]', 'elective_courses': '[]', 'skill_courses': '[]',
#             'multidisciplinary_courses': '[]', 'preferred_morning_hours': True,
#             'max_hours_per_day': 7
#         }
        
#         df = clean_dataframe(df, required_cols, optional_cols)
        
#         batches_data = []
#         for _, row in df.iterrows():
#             batch_data = {
#                 "id": str(row['id']), "name": str(row['name']),
#                 "department": str(row['department']),
#                 "semester": int(float(row['semester'])),
#                 "student_count": int(float(row['student_count'])),
#                 "core_courses": parse_list_field(row.get('core_courses', [])),
#                 "elective_courses": parse_list_field(row.get('elective_courses', [])),
#                 "skill_courses": parse_list_field(row.get('skill_courses', [])),
#                 "multidisciplinary_courses": parse_list_field(row.get('multidisciplinary_courses', [])),
#                 "preferred_morning_hours": parse_boolean_field(row.get('preferred_morning_hours', True)),
#                 "max_hours_per_day": int(float(row.get('max_hours_per_day', 7)))
#             }
#             batches_data.append(batch_data)
            
#         return {"data": batches_data}
        
#     except Exception as e:
#         return {"error": f"Error processing batches: {str(e)}"}

# # Add OPTIONS handler for preflight requests
# @app.before_request
# def handle_preflight():
#     if request.method == "OPTIONS":
#         response = jsonify()
#         response.headers.add("Access-Control-Allow-Origin", "*")
#         response.headers.add('Access-Control-Allow-Headers', "*")
#         response.headers.add('Access-Control-Allow-Methods', "*")
#         return response

# @app.route('/api/user-preferences-template', methods=['GET'])
# def get_user_preferences_template():
#     """Get user preferences template for the frontend"""
#     try:
#         template = {
#             "working_days": {
#                 "type": "integer",
#                 "value": 5,
#                 "range": [5, 6],
#                 "description": "Number of working days per week"
#             },
#             "periods_per_day": {
#                 "type": "integer", 
#                 "value": 5,
#                 "range": [5, 8],
#                 "description": "Number of periods per day"
#             },
#             "lunch_break_period": {
#                 "type": "integer",
#                 "value": 2,
#                 "range": [2, 4],
#                 "description": "Period number for lunch break (0-indexed)"
#             },
#             "max_consecutive_same_subject": {
#                 "type": "integer",
#                 "value": 2,
#                 "range": [1, 4],
#                 "description": "Maximum consecutive hours for same subject"
#             },
#             "gap_penalty_weight": {
#                 "type": "float",
#                 "value": 10.0,
#                 "range": [0.0, 50.0],
#                 "description": "Penalty weight for schedule gaps"
#             },
#             "faculty_preference_weight": {
#                 "type": "float",
#                 "value": 15.0,
#                 "range": [0.0, 50.0],
#                 "description": "Weight for faculty time preferences"
#             },
#             "workload_balance_weight": {
#                 "type": "float",
#                 "value": 20.0,
#                 "range": [0.0, 50.0],
#                 "description": "Weight for workload balance optimization"
#             },
#             "room_preference_weight": {
#                 "type": "float",
#                 "value": 5.0,
#                 "range": [0.0, 20.0],
#                 "description": "Weight for room preference matching"
#             },
#             "interdisciplinary_bonus": {
#                 "type": "float",
#                 "value": 10.0,
#                 "range": [0.0, 30.0],
#                 "description": "Bonus for interdisciplinary courses"
#             },
#             "research_slot_protection": {
#                 "type": "boolean",
#                 "value": True,
#                 "description": "Protect faculty research time slots"
#             },
#             "allow_saturday_classes": {
#                 "type": "boolean",
#                 "value": False,
#                 "description": "Allow classes on Saturday"
#             },
#             "morning_start_time": {
#                 "type": "string",
#                 "value": "9:00",
#                 "options": ["8:00", "8:30", '9:00', '9:30'],
#                 "description": "Morning classes start time"
#             },
#             "evening_end_time": {
#                 "type": "string",
#                 "value": "4:30",
#                 "options": ["4:00", "4:30", '5:00', '5:30', '6:00'],
#                 "description": "Evening classes end time"
#             }
#         }
        
#         return jsonify({
#             "success": True,
#             "template": template
#         })
    
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": f"Failed to load preferences template: {str(e)}"
#         }), 500

# @app.route('/api/convert-csv-to-json', methods=['POST'])
# def convert_csv_to_json():
#     """Convert uploaded CSV or JSON files to standardized JSON format"""
#     try:
#         # Check if all required files are present
#         required_files = ['courses_csv', 'faculty_csv', 'classrooms_csv', 'batches_csv']
        
#         for file_key in required_files:
#             if file_key not in request.files:
#                 return jsonify({
#                     "success": False,
#                     "error": f"Missing required file: {file_key}"
#                 }), 400
        
#         # Process each file
#         processed_data = {
#             "courses": [],
#             "faculty": [],
#             "classrooms": [],
#             "student_batches": []
#         }
        
#         file_processors = {
#             'courses_csv': process_courses_file,
#             'faculty_csv': process_faculty_file,
#             'classrooms_csv': process_classrooms_file,
#             'batches_csv': process_batches_file
#         }
        
#         file_type_mapping = {
#             'courses_csv': 'courses',
#             'faculty_csv': 'faculty',
#             'classrooms_csv': 'classrooms',
#             'batches_csv': 'student_batches'
#         }
        
#         for file_key, processor in file_processors.items():
#             file_obj = request.files[file_key]
#             filename = file_obj.filename.lower()
            
#             if filename.endswith('.json'):
#                 # Process JSON file directly
#                 try:
#                     file_content = file_obj.read()
#                     json_data, error = safe_read_json(file_content, filename)
#                     if error:
#                         return jsonify({"success": False, "error": error}), 400
                    
#                     # Handle different JSON structures
#                     if isinstance(json_data, dict):
#                         # Check if the JSON has the expected key (e.g., "faculty": [...])
#                         expected_key = file_type_mapping[file_key]
#                         if expected_key in json_data:
#                             processed_data[expected_key] = json_data[expected_key]
#                         else:
#                             # Assume the JSON contains the array directly at the top level
#                             processed_data[expected_key] = list(json_data.values())[0] if json_data else []
#                     elif isinstance(json_data, list):
#                         # JSON is already an array
#                         processed_data[file_type_mapping[file_key]] = json_data
#                     else:
#                         return jsonify({
#                             "success": False,
#                             "error": f"Invalid JSON structure in {filename}. Expected object with key '{file_type_mapping[file_key]}' or array."
#                         }), 400
                        
#                 except Exception as e:
#                     return jsonify({
#                         "success": False,
#                         "error": f"Error processing JSON file {filename}: {str(e)}"
#                     }), 400
                    
#             elif filename.endswith('.csv'):
#                 # Process CSV file
#                 file_content = file_obj.read()
#                 df, error = safe_read_csv(file_content, filename)
#                 if error:
#                     return jsonify({"success": False, "error": error}), 400
                
#                 # Call the appropriate processor
#                 result = processor(df)
#                 if 'error' in result:
#                     return jsonify({"success": False, "error": result['error']}), 400
                
#                 processed_data[file_type_mapping[file_key]] = result['data']
                
#             else:
#                 return jsonify({
#                     "success": False,
#                     "error": f"Unsupported file format for {filename}. Please use .csv or .json"
#                 }), 400
        
#         print(f"Processed data summary:")
#         print(f"- Courses: {len(processed_data['courses'])}")
#         print(f"- Faculty: {len(processed_data['faculty'])}")
#         print(f"- Classrooms: {len(processed_data['classrooms'])}")
#         print(f"- Batches: {len(processed_data['student_batches'])}")
        
#         return jsonify({
#             "success": True,
#             "data": processed_data,
#             "message": f"Successfully processed {len(processed_data['courses'])} courses, {len(processed_data['faculty'])} faculty, {len(processed_data['classrooms'])} classrooms, and {len(processed_data['student_batches'])} batches"
#         })
    
#     except Exception as e:
#         error_msg = f"Error processing files: {str(e)}"
#         print(error_msg)
#         print(traceback.format_exc())
#         return jsonify({
#             "success": False,
#             "error": error_msg,
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/api/validate-data', methods=['POST'])
# def validate_data():
#     """Validate the processed institutional data"""
#     try:
#         request_data = request.get_json()
        
#         if not request_data:
#             return jsonify({"success": False, "error": "No data provided"}), 400
        
#         data = request_data.get('institution_data', {})
#         user_preferences = request_data.get('user_preferences', {})
        
#         errors = []
#         warnings = []
        
#         # Determine working days and periods from preferences, with defaults
#         allow_saturday = user_preferences.get('allow_saturday_classes', False)
#         working_days = 6 if allow_saturday else 5
#         periods_per_day = user_preferences.get('periods_per_day', 5)
        
#         # Validate faculty slots
#         faculty = data.get('faculty', [])
#         faculty_ids = {fac['id'] for fac in faculty}
        
#         for fac in faculty:
#             # Check research_slots
#             for slot in fac.get('research_slots', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot on day {day}, which is outside the configured {working_days} working days (0-{working_days-1}).")
#                     if period >= periods_per_day:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot in period {period}, which is outside the configured {periods_per_day} periods per day (0-{periods_per_day-1}).")
            
#             # Check unavailable_slots
#             for slot in fac.get('unavailable_slots', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot on day {day}, which is outside the configured {working_days} working days.")
#                     if period >= periods_per_day:
#                         errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot in period {period}, which is outside the configured {periods_per_day} periods per day.")

#         # Validate classroom maintenance slots
#         classrooms = data.get('classrooms', [])
#         classroom_ids = {room['id'] for room in classrooms}

#         for room in classrooms:
#             for slot in room.get('weekly_maintenance', []):
#                 if isinstance(slot, list) and len(slot) == 2:
#                     day, period = slot
#                     if day >= working_days:
#                         errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot on day {day}, which is outside the configured {working_days} working days.")
#                     if period >= periods_per_day:
#                         errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot in period {period}, which is outside the configured {periods_per_day} periods per day.")
        
#         # Check for duplicate IDs
#         courses = data.get('courses', [])
#         course_ids = set()
#         for course in courses:
#             if course['id'] in course_ids:
#                 errors.append(f"Duplicate course ID: {course['id']}")
#             course_ids.add(course['id'])
            
#             if course.get('faculty_id') not in faculty_ids:
#                 warnings.append(f"Course '{course['name']}' (ID: {course['id']}) references a non-existent faculty ID: {course.get('faculty_id')}")

#         batches = data.get('student_batches', [])
#         batch_ids = set()
#         for batch in batches:
#             if batch['id'] in batch_ids:
#                 errors.append(f"Duplicate batch ID: {batch['id']}")
#             batch_ids.add(batch['id'])
            
#             all_batch_courses = (batch.get('core_courses', []) + batch.get('elective_courses', []) + 
#                                batch.get('skill_courses', []) + batch.get('multidisciplinary_courses', []))
#             for course_id in all_batch_courses:
#                 if course_id not in course_ids:
#                     warnings.append(f"Batch '{batch['name']}' references an unknown course ID: {course_id}")

#         total_course_hours = sum(c.get('hours_per_week', 0) for c in courses)
        
#         return jsonify({
#             "success": True,
#             "valid": len(errors) == 0,
#             "errors": errors,
#             "warnings": warnings,
#             "statistics": { 
#                 "courses": len(courses), 
#                 "faculty": len(faculty), 
#                 "classrooms": len(classrooms), 
#                 "batches": len(batches),
#                 "total_course_hours": total_course_hours
#             }
#         })
    
#     except Exception as e:
#         error_msg = f"Error validating data: {str(e)}"
#         print(error_msg)
#         print(traceback.format_exc())
#         return jsonify({ 
#             "success": False, 
#             "error": error_msg, 
#             "traceback": traceback.format_exc() 
#         }), 500

# # Add backward compatibility endpoint for existing frontend
# @app.route('/api/generate-timetable', methods=['POST'])
# def generate_timetable():
#     """Backward compatibility endpoint - redirects to multi-section timetable generator"""
#     return generate_multi_section_timetable()

# @app.route('/api/generate-multi-section-timetable', methods=['POST'])
# def generate_multi_section_timetable():
#     """Generate multi-section NEP compliant timetable"""
#     try:
#         request_data = request.get_json()
        
#         if not request_data:
#             return jsonify({
#                 "success": False,
#                 "error": "No data provided"
#             }), 400
        
#         institution_data = request_data.get('institution_data')
#         user_preferences = request_data.get('user_preferences', {})
#         generation_params = request_data.get('generation_params', {})
        
#         if not institution_data:
#             return jsonify({
#                 "success": False,
#                 "error": "Institution data is required"
#             }), 400
        
#         # Set default generation parameters
#         population_size = generation_params.get('population_size', 20)
#         generations = generation_params.get('generations', 30)
        
#         # Ensure reasonable limits
#         population_size = max(10, min(100, population_size))
#         generations = max(20, min(200, generations))
        
#         print(f"Starting multi-section timetable generation with population_size={population_size}, generations={generations}")
#         print(f"User preferences: {user_preferences}")
        
#         # Generate multi-section timetable using the updated function
#         result = generate_multi_section_timetable_api(
#             json.dumps(institution_data),
#             user_preferences,
#             population_size=population_size,
#             generations=generations
#         )
        
#         return jsonify({
#             "success": True,
#             "data": result,
#             "generation_params": {
#                 "population_size": population_size,
#                 "generations": generations
#             },
#             "timestamp": datetime.now().isoformat()
#         })
    
#     except Exception as e:
#         error_msg = f"Multi-section timetable generation failed: {str(e)}"
#         print(error_msg)
#         print(f"Traceback: {traceback.format_exc()}")
        
#         return jsonify({
#             "success": False,
#             "error": error_msg,
#             "traceback": traceback.format_exc()
#         }), 500

# @app.route('/api/debug', methods=['POST'])
# def debug_endpoint():
#     """Debug endpoint to test data processing"""
#     try:
#         request_data = request.get_json()
#         print("Debug request received:")
#         print(json.dumps(request_data, indent=2))
        
#         return jsonify({
#             "success": True,
#             "message": "Debug data received",
#             "data": request_data
#         })
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "error": f"Debug error: {str(e)}"
#         }), 500

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         "success": True,
#         "message": "Multi-Section NEP Timetable Generator API is running",
#         "timestamp": datetime.now().isoformat(),
#         "python_version": sys.version,
#         "features": [
#             "Multi-section conflict resolution",
#             "Theory courses: 2 sessions per week",
#             "Lab courses: 1 session per week (4 hours continuous)",
#             "NEP 2020 compliant structure"
#         ]
#     })

# @app.errorhandler(413)
# def request_entity_too_large(error):
#     return jsonify({
#         "success": False,
#         "error": "File too large. Maximum size is 16MB."
#     }), 413

# @app.errorhandler(500)
# def internal_server_error(error):
#     error_msg = "Internal server error occurred."
#     print(error_msg)
#     print(traceback.format_exc())
#     return jsonify({
#         "success": False,
#         "error": error_msg,
#         "traceback": traceback.format_exc()
#     }), 500

# if __name__ == '__main__':
#     print("Starting Multi-Section NEP 2020 Timetable Generator API...")
#     print("API endpoints:")
#     print("- GET  /api/health - Health check")
#     print("- GET  /api/user-preferences-template - Get user preferences template")
#     print("- POST /api/convert-csv-to-json - Convert CSV files to JSON")
#     print("- POST /api/validate-data - Validate institutional data")
#     print("- POST /api/generate-timetable - Generate timetable (backward compatibility)")
#     print("- POST /api/generate-multi-section-timetable - Generate multi-section timetable")
#     print("- POST /api/debug - Debug endpoint")
#     print("\nKey features:")
#     print("- Theory courses scheduled 2 times per week")
#     print("- Lab courses scheduled 1 time per week (4-hour continuous sessions)")
#     print("- Multi-section conflict resolution")
#     print("- Faculty and room availability tracking across sections")
    
#     app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import io
import traceback
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import ast
import sys

# Import the multi-section timetable generator
try:
    from nep_timetable_fixed import MultiSectionTimetableGenerator, generate_multi_section_timetable_api, UserPreferences
except ImportError as e:
    print(f"Import error: {e}")
    # Create dummy classes for testing
    class MultiSectionTimetableGenerator:
        def __init__(self, **kwargs):
            pass
    def generate_multi_section_timetable_api(*args, **kwargs):
        return {"error": "Multi-section timetable module not available"}
    class UserPreferences:
        pass

app = Flask(__name__)

# Enhanced CORS configuration
CORS(app, 
     resources={
         r"/api/*": {
             "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
             "supports_credentials": True
         }
     })

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}

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

def safe_read_json(file_content, filename):
    """Safely read JSON with error handling"""
    try:
        json_data = json.loads(file_content.decode('utf-8'))
        return json_data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in {filename}: {str(e)}"
    except Exception as e:
        return None, f"Error reading JSON file {filename}: {str(e)}"

def parse_list_field(value, default=[]):
    """Parse list fields from CSV that might be string representations"""
    if pd.isna(value) or value == '' or value == '[]':
        return default
    
    if isinstance(value, list):
        return value
    
    if isinstance(value, str):
        try:
            # Try to parse as Python list
            cleaned_value = value.strip()
            if cleaned_value.startswith('[') and cleaned_value.endswith(']'):
                return ast.literal_eval(cleaned_value)
            elif ',' in cleaned_value:
                return [item.strip() for item in cleaned_value.split(',') if item.strip()]
            elif cleaned_value:
                return [cleaned_value]
        except (ValueError, SyntaxError) as e:
            print(f"Warning: Could not parse list field '{value}': {e}")
            # If that fails, return as single item list
            return [value] if value else default
    
    return default

def parse_boolean_field(value, default=False):
    """Parse boolean fields from various formats"""
    if pd.isna(value) or value == '':
        return default
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    if isinstance(value, str):
        lower_val = value.lower().strip()
        if lower_val in ['true', 'yes', '1', 't', 'y']:
            return True
        elif lower_val in ['false', 'no', '0', 'f', 'n']:
            return False
    
    return default

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

# Helper functions for processing each file type
def process_courses_file(df):
    """Process courses CSV DataFrame with enhanced lab detection"""
    try:
        df.columns = df.columns.str.strip().str.lower()
        print(f"Courses CSV columns: {list(df.columns)}")
        
        column_mapping = {
            'course_id': 'id', 'course_name': 'name', 'course_code': 'code',
            'course_credits': 'credits', 'course_type': 'course_type',
            'hours_per_week': 'hours_per_week', 'department': 'department',
            'semester': 'semester', 'faculty_id': 'faculty_id',
            'requires_lab': 'requires_lab', 'requires_smart_room': 'requires_smart_room',
            'is_interdisciplinary': 'is_interdisciplinary', 'connected_departments': 'connected_departments',
            'max_students': 'max_students', 'min_duration_minutes': 'min_duration_minutes',
            'max_consecutive_hours': 'max_consecutive_hours', 'preferred_days': 'preferred_days'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        required_cols = ['id', 'name', 'code', 'credits', 'course_type', 'hours_per_week', 
                       'department', 'semester', 'faculty_id']
        optional_cols = {
            'requires_lab': False, 'requires_smart_room': False, 'is_interdisciplinary': False,
            'connected_departments': '[]', 'max_students': 60, 'min_duration_minutes': 50,
            'max_consecutive_hours': 2, 'preferred_days': '[]'
        }
        
        df = clean_dataframe(df, required_cols, optional_cols)
        
        courses_data = []
        for _, row in df.iterrows():
            # Enhanced lab detection
            course_name = str(row['name']).lower()
            course_id = str(row['id'])
            is_lab_course = (parse_boolean_field(row.get('requires_lab', False)) or 
                           'lab' in course_name or
                           course_id in ["B23AM3110", "B23AM3111", "B23AM3112", "B23AM3113"])
            
            # Set min_duration_minutes for lab courses
            min_duration = int(float(row.get('min_duration_minutes', 50)))
            if is_lab_course and min_duration < 180:
                min_duration = 180  # 3 hours for labs
            
            course_data = {
                "id": course_id, "name": str(row['name']), "code": str(row['code']),
                "credits": int(float(row['credits'])), "course_type": str(row['course_type']).lower(),
                "hours_per_week": int(float(row['hours_per_week'])), "department": str(row['department']),
                "semester": int(float(row['semester'])), "faculty_id": str(row['faculty_id']),
                "requires_lab": is_lab_course,
                "requires_smart_room": parse_boolean_field(row.get('requires_smart_room', False)),
                "is_interdisciplinary": parse_boolean_field(row.get('is_interdisciplinary', False)),
                "connected_departments": parse_list_field(row.get('connected_departments', [])),
                "max_students": int(float(row.get('max_students', 60))),
                "min_duration_minutes": min_duration,
                "max_consecutive_hours": int(float(row.get('max_consecutive_hours', 2))),
                "preferred_days": parse_list_field(row.get('preferred_days', []))
            }
            courses_data.append(course_data)
            
        return {"data": courses_data}
        
    except Exception as e:
        return {"error": f"Error processing courses: {str(e)}"}

def process_faculty_file(df):
    """Process faculty CSV DataFrame"""
    try:
        df.columns = df.columns.str.strip().str.lower()
        print(f"Faculty CSV columns: {list(df.columns)}")
        
        column_mapping = {
            'faculty_id': 'id', 'faculty_name': 'name', 'department': 'department',
            'designation': 'designation', 'specializations': 'specializations',
            'courses_can_teach': 'courses_can_teach', 'max_hours_per_day': 'max_hours_per_day',
            'max_hours_per_week': 'max_hours_per_week', 'preferred_time': 'preferred_time',
            'unavailable_slots': 'unavailable_slots', 'research_slots': 'research_slots',
            'is_visiting': 'is_visiting', 'workload_preference': 'workload_preference'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        required_cols = ['id', 'name', 'department', 'designation', 'specializations', 'courses_can_teach']
        optional_cols = {
            'max_hours_per_day': 6, 'max_hours_per_week': 24, 'preferred_time': 'any',
            'unavailable_slots': '[]', 'research_slots': '[]', 'is_visiting': False,
            'workload_preference': 1.0
        }
        
        df = clean_dataframe(df, required_cols, optional_cols)
        
        faculty_data = []
        for _, row in df.iterrows():
            faculty_data.append({
                "id": str(row['id']), "name": str(row['name']), "department": str(row['department']),
                "designation": str(row['designation']), "specializations": parse_list_field(row['specializations']),
                "courses_can_teach": parse_list_field(row['courses_can_teach']),
                "max_hours_per_day": int(float(row.get('max_hours_per_day', 6))),
                "max_hours_per_week": int(float(row.get('max_hours_per_week', 24))),
                "preferred_time": str(row.get('preferred_time', 'any')).lower(),
                "unavailable_slots": parse_list_field(row.get('unavailable_slots', [])),
                "research_slots": parse_list_field(row.get('research_slots', [])),
                "is_visiting": parse_boolean_field(row.get('is_visiting', False)),
                "workload_preference": float(row.get('workload_preference', 1.0))
            })
            
        return {"data": faculty_data}
        
    except Exception as e:
        return {"error": f"Error processing faculty: {str(e)}"}

def process_classrooms_file(df):
    """Process classrooms CSV DataFrame"""
    try:
        df.columns = df.columns.str.strip().str.lower()
        print(f"Classrooms CSV columns: {list(df.columns)}")
        
        column_mapping = {
            'room_id': 'id', 'room_name': 'name', 'capacity': 'capacity',
            'room_type': 'room_type', 'department': 'department',
            'equipment': 'equipment', 'is_smart_room': 'is_smart_room',
            'is_ac': 'is_ac', 'has_projector': 'has_projector',
            'weekly_maintenance': 'weekly_maintenance'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        required_cols = ['id', 'name', 'capacity', 'room_type', 'department']
        optional_cols = {
            'equipment': '[]', 'is_smart_room': False, 'is_ac': False,
            'has_projector': True, 'weekly_maintenance': '[]'
        }
        
        df = clean_dataframe(df, required_cols, optional_cols)
        
        classrooms_data = []
        for _, row in df.iterrows():
            classroom_data = {
                "id": str(row['id']), "name": str(row['name']),
                "capacity": int(float(row['capacity'])),
                "room_type": str(row['room_type']).lower(),
                "department": str(row['department']),
                "equipment": parse_list_field(row.get('equipment', [])),
                "is_smart_room": parse_boolean_field(row.get('is_smart_room', False)),
                "is_ac": parse_boolean_field(row.get('is_ac', False)),
                "has_projector": parse_boolean_field(row.get('has_projector', True)),
                "weekly_maintenance": parse_list_field(row.get('weekly_maintenance', []))
            }
            classrooms_data.append(classroom_data)
            
        return {"data": classrooms_data}
        
    except Exception as e:
        return {"error": f"Error processing classrooms: {str(e)}"}

def process_batches_file(df):
    """Process batches CSV DataFrame"""
    try:
        df.columns = df.columns.str.strip().str.lower()
        print(f"Batches CSV columns: {list(df.columns)}")
        
        column_mapping = {
            'batch_id': 'id', 'batch_name': 'name', 'department': 'department',
            'semester': 'semester', 'student_count': 'student_count',
            'core_courses': 'core_courses', 'elective_courses': 'elective_courses',
            'skill_courses': 'skill_courses', 'multidisciplinary_courses': 'multidisciplinary_courses',
            'preferred_morning_hours': 'preferred_morning_hours', 'max_hours_per_day': 'max_hours_per_day'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        required_cols = ['id', 'name', 'department', 'semester', 'student_count']
        optional_cols = {
            'core_courses': '[]', 'elective_courses': '[]', 'skill_courses': '[]',
            'multidisciplinary_courses': '[]', 'preferred_morning_hours': True,
            'max_hours_per_day': 7
        }
        
        df = clean_dataframe(df, required_cols, optional_cols)
        
        batches_data = []
        for _, row in df.iterrows():
            batch_data = {
                "id": str(row['id']), "name": str(row['name']),
                "department": str(row['department']),
                "semester": int(float(row['semester'])),
                "student_count": int(float(row['student_count'])),
                "core_courses": parse_list_field(row.get('core_courses', [])),
                "elective_courses": parse_list_field(row.get('elective_courses', [])),
                "skill_courses": parse_list_field(row.get('skill_courses', [])),
                "multidisciplinary_courses": parse_list_field(row.get('multidisciplinary_courses', [])),
                "preferred_morning_hours": parse_boolean_field(row.get('preferred_morning_hours', True)),
                "max_hours_per_day": int(float(row.get('max_hours_per_day', 7)))
            }
            batches_data.append(batch_data)
            
        return {"data": batches_data}
        
    except Exception as e:
        return {"error": f"Error processing batches: {str(e)}"}

# Add OPTIONS handler for preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

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
                "value": 5,
                "range": [5, 8],
                "description": "Number of periods per day"
            },
            "lunch_break_period": {
                "type": "integer",
                "value": 2,
                "range": [2, 4],
                "description": "Period number for lunch break (0-indexed)"
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
                "options": ["8:00", "8:30", '9:00', '9:30'],
                "description": "Morning classes start time"
            },
            "evening_end_time": {
                "type": "string",
                "value": "4:30",
                "options": ["4:00", "4:30", '5:00', '5:30', '6:00'],
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
    """Convert uploaded CSV or JSON files to standardized JSON format"""
    try:
        # Check if all required files are present
        required_files = ['courses_csv', 'faculty_csv', 'classrooms_csv', 'batches_csv']
        
        for file_key in required_files:
            if file_key not in request.files:
                return jsonify({
                    "success": False,
                    "error": f"Missing required file: {file_key}"
                }), 400
        
        # Process each file
        processed_data = {
            "courses": [],
            "faculty": [],
            "classrooms": [],
            "student_batches": []
        }
        
        file_processors = {
            'courses_csv': process_courses_file,
            'faculty_csv': process_faculty_file,
            'classrooms_csv': process_classrooms_file,
            'batches_csv': process_batches_file
        }
        
        file_type_mapping = {
            'courses_csv': 'courses',
            'faculty_csv': 'faculty',
            'classrooms_csv': 'classrooms',
            'batches_csv': 'student_batches'
        }
        
        for file_key, processor in file_processors.items():
            file_obj = request.files[file_key]
            filename = file_obj.filename.lower()
            
            if filename.endswith('.json'):
                # Process JSON file directly
                try:
                    file_content = file_obj.read()
                    json_data, error = safe_read_json(file_content, filename)
                    if error:
                        return jsonify({"success": False, "error": error}), 400
                    
                    # Handle different JSON structures
                    if isinstance(json_data, dict):
                        # Check if the JSON has the expected key (e.g., "faculty": [...])
                        expected_key = file_type_mapping[file_key]
                        if expected_key in json_data:
                            processed_data[expected_key] = json_data[expected_key]
                        else:
                            # Assume the JSON contains the array directly at the top level
                            processed_data[expected_key] = list(json_data.values())[0] if json_data else []
                    elif isinstance(json_data, list):
                        # JSON is already an array
                        processed_data[file_type_mapping[file_key]] = json_data
                    else:
                        return jsonify({
                            "success": False,
                            "error": f"Invalid JSON structure in {filename}. Expected object with key '{file_type_mapping[file_key]}' or array."
                        }), 400
                        
                except Exception as e:
                    return jsonify({
                        "success": False,
                        "error": f"Error processing JSON file {filename}: {str(e)}"
                    }), 400
                    
            elif filename.endswith('.csv'):
                # Process CSV file
                file_content = file_obj.read()
                df, error = safe_read_csv(file_content, filename)
                if error:
                    return jsonify({"success": False, "error": error}), 400
                
                # Call the appropriate processor
                result = processor(df)
                if 'error' in result:
                    return jsonify({"success": False, "error": result['error']}), 400
                
                processed_data[file_type_mapping[file_key]] = result['data']
                
            else:
                return jsonify({
                    "success": False,
                    "error": f"Unsupported file format for {filename}. Please use .csv or .json"
                }), 400
        
        print(f"Processed data summary:")
        print(f"- Courses: {len(processed_data['courses'])}")
        print(f"- Faculty: {len(processed_data['faculty'])}")
        print(f"- Classrooms: {len(processed_data['classrooms'])}")
        print(f"- Batches: {len(processed_data['student_batches'])}")
        
        # Enhanced validation for lab courses
        lab_courses = [c for c in processed_data['courses'] if c.get('requires_lab', False)]
        lab_rooms = [r for r in processed_data['classrooms'] if r.get('room_type') in ['lab', 'computer_lab']]
        
        print(f"- Lab courses detected: {len(lab_courses)}")
        print(f"- Lab rooms available: {len(lab_rooms)}")
        
        for course in lab_courses:
            print(f"  Lab course: {course['id']} - {course['name']} (Duration: {course.get('min_duration_minutes', 50)} min)")
        
        return jsonify({
            "success": True,
            "data": processed_data,
            "message": f"Successfully processed {len(processed_data['courses'])} courses, {len(processed_data['faculty'])} faculty, {len(processed_data['classrooms'])} classrooms, and {len(processed_data['student_batches'])} batches",
            "lab_info": {
                "lab_courses": len(lab_courses),
                "lab_rooms": len(lab_rooms),
                "lab_courses_list": [{"id": c['id'], "name": c['name']} for c in lab_courses]
            }
        })
    
    except Exception as e:
        error_msg = f"Error processing files: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": error_msg,
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/validate-data', methods=['POST'])
def validate_data():
    """Validate the processed institutional data with enhanced lab validation"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        data = request_data.get('institution_data', {})
        user_preferences = request_data.get('user_preferences', {})
        
        errors = []
        warnings = []
        
        # Determine working days and periods from preferences, with defaults
        allow_saturday = user_preferences.get('allow_saturday_classes', False)
        working_days = 6 if allow_saturday else 5
        periods_per_day = user_preferences.get('periods_per_day', 5)
        
        # Validate courses
        courses = data.get('courses', [])
        course_ids = {course['id'] for course in courses}
        lab_courses = [c for c in courses if c.get('requires_lab', False) or 'lab' in c.get('name', '').lower()]
        
        # Validate faculty
        faculty = data.get('faculty', [])
        faculty_ids = {fac['id'] for fac in faculty}
        
        # Enhanced faculty validation
        for fac in faculty:
            # Check research_slots
            for slot in fac.get('research_slots', []):
                if isinstance(slot, list) and len(slot) == 2:
                    day, period = slot
                    if day >= working_days:
                        errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot on day {day}, which is outside the configured {working_days} working days (0-{working_days-1}).")
                    if period >= periods_per_day:
                        errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has a research slot in period {period}, which is outside the configured {periods_per_day} periods per day (0-{periods_per_day-1}).")
            
            # Check unavailable_slots
            for slot in fac.get('unavailable_slots', []):
                if isinstance(slot, list) and len(slot) == 2:
                    day, period = slot
                    if day >= working_days:
                        errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot on day {day}, which is outside the configured {working_days} working days.")
                    if period >= periods_per_day:
                        errors.append(f"Faculty '{fac['name']}' (ID: {fac['id']}) has an unavailable slot in period {period}, which is outside the configured {periods_per_day} periods per day.")

        # Validate classrooms with enhanced lab room checking
        classrooms = data.get('classrooms', [])
        classroom_ids = {room['id'] for room in classrooms}
        lab_rooms = [r for r in classrooms if r.get('room_type') in ['lab', 'computer_lab']]

        for room in classrooms:
            for slot in room.get('weekly_maintenance', []):
                if isinstance(slot, list) and len(slot) == 2:
                    day, period = slot
                    if day >= working_days:
                        errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot on day {day}, which is outside the configured {working_days} working days.")
                    if period >= periods_per_day:
                        errors.append(f"Classroom '{room['name']}' (ID: {room['id']}) has a maintenance slot in period {period}, which is outside the configured {periods_per_day} periods per day.")
        
        # Check for duplicate IDs
        course_ids_list = [course['id'] for course in courses]
        if len(course_ids_list) != len(set(course_ids_list)):
            duplicates = [x for x in course_ids_list if course_ids_list.count(x) > 1]
            errors.append(f"Duplicate course IDs found: {list(set(duplicates))}")
            
        for course in courses:
            if course.get('faculty_id') not in faculty_ids:
                warnings.append(f"Course '{course['name']}' (ID: {course['id']}) references a non-existent faculty ID: {course.get('faculty_id')}")

        # Enhanced lab course validation
        if lab_courses:
            if not lab_rooms:
                errors.append("Lab courses detected but no lab rooms available. Please ensure rooms with type 'lab' or 'computer_lab' are available.")
            elif len(lab_courses) > len(lab_rooms):
                warnings.append(f"More lab courses ({len(lab_courses)}) than available lab rooms ({len(lab_rooms)}). This may cause scheduling conflicts.")
            
            # Check lab course duration
            for course in lab_courses:
                if course.get('min_duration_minutes', 50) < 180:
                    warnings.append(f"Lab course '{course['name']}' has duration less than 3 hours ({course.get('min_duration_minutes', 50)} minutes). Consider increasing to 180+ minutes for proper lab sessions.")

        batches = data.get('student_batches', [])
        batch_ids = set()
        pe_oe_sections = []
        
        for batch in batches:
            if batch['id'] in batch_ids:
                errors.append(f"Duplicate batch ID: {batch['id']}")
            batch_ids.add(batch['id'])
            
            # Check for PE/OE courses
            elective_courses = batch.get('elective_courses', [])
            has_pe = any('PE_I' in course for course in elective_courses)
            has_oe = any('OE_I' in course for course in elective_courses)
            
            if has_pe or has_oe:
                pe_oe_sections.append({
                    'batch': batch['name'],
                    'has_pe': has_pe,
                    'has_oe': has_oe
                })
            
            all_batch_courses = (batch.get('core_courses', []) + batch.get('elective_courses', []) + 
                               batch.get('skill_courses', []) + batch.get('multidisciplinary_courses', []))
            for course_id in all_batch_courses:
                if course_id not in course_ids:
                    warnings.append(f"Batch '{batch['name']}' references an unknown course ID: {course_id}")

        # Validate PE/OE synchronization requirements
        if len(pe_oe_sections) > 1:
            pe_courses = [s for s in pe_oe_sections if s['has_pe']]
            oe_courses = [s for s in pe_oe_sections if s['has_oe']]
            
            if len(pe_courses) > 1 and len(pe_courses) != len(pe_oe_sections):
                warnings.append("PE courses are not present in all sections. For proper synchronization, all sections should have PE courses.")
            
            if len(oe_courses) > 1 and len(oe_courses) != len(pe_oe_sections):
                warnings.append("OE courses are not present in all sections. For proper synchronization, all sections should have OE courses.")

        total_course_hours = sum(c.get('hours_per_week', 0) for c in courses)
        
        return jsonify({
            "success": True,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "statistics": { 
                "courses": len(courses), 
                "faculty": len(faculty), 
                "classrooms": len(classrooms), 
                "batches": len(batches),
                "total_course_hours": total_course_hours,
                "lab_courses": len(lab_courses),
                "lab_rooms": len(lab_rooms),
                "pe_oe_sections": len(pe_oe_sections)
            },
            "lab_validation": {
                "lab_courses_count": len(lab_courses),
                "lab_rooms_count": len(lab_rooms),
                "lab_courses_details": [{"id": c['id'], "name": c['name'], "duration": c.get('min_duration_minutes', 50)} for c in lab_courses],
                "lab_rooms_details": [{"id": r['id'], "name": r['name'], "type": r['room_type']} for r in lab_rooms]
            },
            "synchronization_info": {
                "pe_oe_sections": pe_oe_sections,
                "requires_synchronization": len(pe_oe_sections) > 1
            }
        })
    
    except Exception as e:
        error_msg = f"Error validating data: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({ 
            "success": False, 
            "error": error_msg, 
            "traceback": traceback.format_exc() 
        }), 500

# Add backward compatibility endpoint for existing frontend
@app.route('/api/generate-timetable', methods=['POST'])
def generate_timetable():
    """Backward compatibility endpoint - redirects to multi-section timetable generator"""
    return generate_multi_section_timetable()

@app.route('/api/generate-multi-section-timetable', methods=['POST'])
def generate_multi_section_timetable():
    """Generate multi-section NEP compliant timetable with enhanced lab and PE/OE support"""
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
        population_size = generation_params.get('population_size', 20)
        generations = generation_params.get('generations', 30)
        
        # Ensure reasonable limits
        population_size = max(10, min(100, population_size))
        generations = max(20, min(200, generations))
        
        print(f"Starting multi-section timetable generation with lab support...")
        print(f"Population size: {population_size}, Generations: {generations}")
        print(f"User preferences: {user_preferences}")
        
        # Pre-validation checks
        courses = institution_data.get('courses', [])
        classrooms = institution_data.get('classrooms', [])
        lab_courses = [c for c in courses if c.get('requires_lab', False) or 'lab' in c.get('name', '').lower()]
        lab_rooms = [r for r in classrooms if r.get('room_type') in ['lab', 'computer_lab']]
        
        print(f"Detected {len(lab_courses)} lab courses and {len(lab_rooms)} lab rooms")
        
        if lab_courses and not lab_rooms:
            return jsonify({
                "success": False,
                "error": f"Found {len(lab_courses)} lab courses but no lab rooms available. Please ensure classrooms with room_type 'lab' or 'computer_lab' are configured."
            }), 400
        
        # Generate multi-section timetable using the updated function
        result = generate_multi_section_timetable_api(
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
            "timestamp": datetime.now().isoformat(),
            "features_used": [
                f"Lab courses: {len(lab_courses)}",
                f"Lab rooms: {len(lab_rooms)}",
                "PE/OE synchronization",
                "Multi-section conflict resolution"
            ]
        })
    
    except Exception as e:
        error_msg = f"Multi-section timetable generation failed: {str(e)}"
        print(error_msg)
        print(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "success": False,
            "error": error_msg,
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/debug', methods=['POST'])
def debug_endpoint():
    """Debug endpoint to test data processing"""
    try:
        request_data = request.get_json()
        print("Debug request received:")
        print(json.dumps(request_data, indent=2))
        
        return jsonify({
            "success": True,
            "message": "Debug data received",
            "data": request_data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Debug error: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "message": "Enhanced Multi-Section NEP Timetable Generator API is running",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "features": [
            "Multi-section conflict resolution",
            "Lab courses: 3-hour continuous sessions",
            "PE/OE synchronized across all sections",
            "Theory courses: 2 sessions per week", 
            "Enhanced lab room detection and assignment",
            "NEP 2020 compliant structure"
        ]
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 16MB."
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    error_msg = "Internal server error occurred."
    print(error_msg)
    print(traceback.format_exc())
    return jsonify({
        "success": False,
        "error": error_msg,
        "traceback": traceback.format_exc()
    }), 500

if __name__ == '__main__':
    print("Starting Enhanced Multi-Section NEP 2020 Timetable Generator API...")
    print("API endpoints:")
    print("- GET  /api/health - Health check")
    print("- GET  /api/user-preferences-template - Get user preferences template")
    print("- POST /api/convert-csv-to-json - Convert CSV files to JSON")
    print("- POST /api/validate-data - Validate institutional data")
    print("- POST /api/generate-timetable - Generate timetable (backward compatibility)")
    print("- POST /api/generate-multi-section-timetable - Generate multi-section timetable")
    print("- POST /api/debug - Debug endpoint")
    print("\nKey enhanced features:")
    print("- Lab courses scheduled as 3-hour continuous sessions")
    print("- PE/OE courses synchronized across all sections")
    print("- Theory courses scheduled 2 times per week")
    print("- Multi-section conflict resolution")
    print("- Enhanced lab room detection (room_type: lab or computer_lab)")
    print("- Faculty and room availability tracking across sections")
    
    app.run(debug=True, host='0.0.0.0', port=5000)