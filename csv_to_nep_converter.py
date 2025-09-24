import pandas as pd
import json
from collections import defaultdict
import numpy as np

def debug_csv_files(students_csv, classes_csv, faculty_csv, courses_csv):
    """
    Debug function to examine the structure of CSV files
    """
    print("=== DEBUGGING CSV FILES ===")
    
    # Load all CSV files with detailed info
    try:
        students_df = pd.read_csv(students_csv)
        print(f"\n1. STUDENTS.CSV")
        print(f"   Shape: {students_df.shape}")
        print(f"   Columns: {list(students_df.columns)}")
        print(f"   First few rows:")
        print(students_df.head(3))
        print(f"   Data types:\n{students_df.dtypes}")
        
        classes_df = pd.read_csv(classes_csv)
        print(f"\n2. CLASSES.CSV")
        print(f"   Shape: {classes_df.shape}")
        print(f"   Columns: {list(classes_df.columns)}")
        print(f"   First few rows:")
        print(classes_df.head(3))
        print(f"   Data types:\n{classes_df.dtypes}")
        
        faculty_df = pd.read_csv(faculty_csv)
        print(f"\n3. FACULTY_WORKLOAD.CSV")
        print(f"   Shape: {faculty_df.shape}")
        print(f"   Columns: {list(faculty_df.columns)}")
        print(f"   First few rows:")
        print(faculty_df.head(3))
        print(f"   Data types:\n{faculty_df.dtypes}")
        
        courses_df = pd.read_csv(courses_csv)
        print(f"\n4. COURSES.CSV")
        print(f"   Shape: {courses_df.shape}")
        print(f"   Columns: {list(courses_df.columns)}")
        print(f"   First few rows:")
        print(courses_df.head(3))
        print(f"   Data types:\n{courses_df.dtypes}")
        
    except Exception as e:
        print(f"Error reading CSV files: {e}")
        return False
    
    return True

def convert_csv_to_nep_json(students_csv, classes_csv, faculty_csv, courses_csv):
    """
    Convert your CSV files to the NEP timetable generator JSON format
    """
    # Load all CSV files with error handling
    try:
        students_df = pd.read_csv(students_csv)
        classes_df = pd.read_csv(classes_csv)
        faculty_df = pd.read_csv(faculty_csv)
        courses_df = pd.read_csv(courses_csv)
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return None
    
    result = {
        "courses": [],
        "faculty": [],
        "classrooms": [],
        "student_batches": []
    }
    
    # Process courses
    print("Processing courses...")
    for _, row in courses_df.iterrows():
        # Handle potential NaN values and data type issues
        try:
            course_name = str(row['name']) if pd.notna(row['name']) else ""
            course_code = str(row['code']) if pd.notna(row['code']) else ""
            course_type = str(row['course_type']) if pd.notna(row['course_type']) else "core"
            
            # Safely convert faculty serial number
            faculty_serial = row['faculty_serial_number']
            if pd.isna(faculty_serial):
                faculty_id = "F001"
            else:
                # Handle various data types that might be in the CSV
                if isinstance(faculty_serial, (int, float, np.integer)):
                    faculty_id = f"F{int(faculty_serial)}"
                else:
                    faculty_id = f"F{str(faculty_serial).split('.')[0]}"  # Handle floats as strings
                    
            course = {
                "id": course_code,
                "name": course_name,
                "code": course_code,
                "credits": float(row['credits']) if pd.notna(row['credits']) else 3.0,
                "course_type": course_type,
                "hours_per_week": int(float(row['hours_per_week'])) if pd.notna(row['hours_per_week']) else 3,
                "department": str(row['department']) if pd.notna(row['department']) else "CSE",
                "semester": int(float(row['semester'])) if pd.notna(row['semester']) else 5,
                "faculty_id": faculty_id,
                "requires_lab": "lab" in course_name.lower() or "practical" in course_name.lower(),
                "requires_smart_room": "smart" in course_name.lower() or "digital" in course_name.lower(),
                "max_students": 60
            }
            result["courses"].append(course)
        except Exception as e:
            print(f"Error processing course row {_}: {e}")
            continue
    
    # Process faculty
    print("Processing faculty...")
    faculty_subjects = defaultdict(list)
    for _, row in faculty_df.iterrows():
        try:
            if pd.notna(row['id']) and pd.notna(row['Subject Allocated']):
                # Convert ID to consistent format
                faculty_id = int(float(row['id'])) if isinstance(row['id'], (int, float, str)) and row['id'].replace('.', '').isdigit() else str(row['id'])
                faculty_subjects[faculty_id].append(str(row['Subject Allocated']))
        except Exception as e:
            print(f"Error processing faculty subject row {_}: {e}")
            continue
    
    faculty_processed = set()
    for _, row in faculty_df.iterrows():
        try:
            # Convert ID to consistent format
            faculty_id_val = int(float(row['id'])) if isinstance(row['id'], (int, float, str)) and str(row['id']).replace('.', '').isdigit() else str(row['id'])
            
            if faculty_id_val in faculty_processed:
                continue
                
            faculty_processed.add(faculty_id_val)
            
            # Calculate max hours based on designation
            designation = str(row['designation']) if pd.notna(row['designation']) else "Assistant Professor"
            
            if 'professor' in designation.lower():
                max_hours_week = 12
            elif 'associate' in designation.lower():
                max_hours_week = 16
            else:
                max_hours_week = 20
                
            faculty = {
                "id": f"F{faculty_id_val}",
                "name": str(row['name']) if pd.notna(row['name']) else f"Faculty {faculty_id_val}",
                "department": str(row['department']) if pd.notna(row['department']) else "CSE",
                "designation": designation,
                "specializations": ["Computer Science"],
                "courses_can_teach": faculty_subjects.get(faculty_id_val, []),
                "max_hours_per_day": 6,
                "max_hours_per_week": max_hours_week,
                "preferred_time": "any",
                "workload_preference": 1.0
            }
            result["faculty"].append(faculty)
        except Exception as e:
            print(f"Error processing faculty row {_}: {e}")
            continue
    
    # Process classrooms
    print("Processing classrooms...")
    for _, row in classes_df.iterrows():
        try:
            room_id = str(row['id']) if pd.notna(row['id']) else f"Room{_}"
            room_name = str(row['name']) if pd.notna(row['name']) else f"Room {room_id}"
            room_type = str(row['room_type']) if pd.notna(row['room_type']) else "lecture"
            
            # Safely convert capacity
            if pd.isna(row['capacity']):
                capacity = 50
            else:
                try:
                    capacity = int(float(row['capacity']))
                except:
                    capacity = 50
            
            classroom = {
                "id": room_id,
                "name": room_name,
                "capacity": capacity,
                "room_type": room_type,
                "department": str(row['department']) if pd.notna(row['department']) else "CSE",
                "equipment": [],
                "is_smart_room": "smart" in room_type.lower(),
                "is_ac": True,
                "has_projector": "smart" in room_type.lower() or "seminar" in room_type.lower()
            }
            
            # Add equipment based on room type
            if "lab" in room_type.lower():
                classroom["equipment"].append("computers")
            if "smart" in room_type.lower():
                classroom["equipment"].append("smart_board")
            if "seminar" in room_type.lower():
                classroom["equipment"].append("audio_system")
                
            result["classrooms"].append(classroom)
        except Exception as e:
            print(f"Error processing classroom row {_}: {e}")
            continue
    
    # Process student batches
    print("Processing student batches...")
    try:
        # Group students by their common properties - handle potential data issues
        if 'student_count' in students_df.columns:
            batch_groups = students_df.groupby(['student_count'])
        else:
            # If student_count column doesn't exist, create a single batch
            batch_groups = [(50, students_df)]
        
        for i, (student_count, group) in enumerate(batch_groups):
            try:
                first_row = group.iloc[0]
                
                # Parse course lists safely
                def parse_course_list(course_str):
                    if pd.isna(course_str):
                        return []
                    course_str = str(course_str)
                    return [course.strip() for course in course_str.split(',')]
                
                # Safely convert student_count
                try:
                    student_count_val = int(float(student_count))
                except:
                    student_count_val = 50
                
                batch = {
                    "id": f"B{i+1}",
                    "name": f"Batch {i+1} ({student_count_val} students)",
                    "department": "Artificial Intelligence and Machine Learning",
                    "semester": 5,
                    "student_count": student_count_val,
                    "core_courses": parse_course_list(first_row['core_courses']) if 'core_courses' in first_row else [],
                    "elective_courses": parse_course_list(first_row['elective_courses']) if 'elective_courses' in first_row else [],
                    "skill_courses": parse_course_list(first_row['skill_courses']) if 'skill_courses' in first_row else [],
                    "multidisciplinary_courses": parse_course_list(first_row['multidisciplinary_courses']) if 'multidisciplinary_courses' in first_row else [],
                    "preferred_morning_hours": bool(first_row['preferred_morning_hours']) if 'preferred_morning_hours' in first_row and pd.notna(first_row['preferred_morning_hours']) else True,
                    "max_hours_per_day": int(float(first_row['max_hours_per_day'])) if 'max_hours_per_day' in first_row and pd.notna(first_row['max_hours_per_day']) else 7
                }
                result["student_batches"].append(batch)
            except Exception as e:
                print(f"Error processing batch {i}: {e}")
                continue
    except Exception as e:
        print(f"Error processing student batches: {e}")
        # Create a default batch if batch processing fails
        result["student_batches"].append({
            "id": "B1",
            "name": "Default Batch (50 students)",
            "department": "Artificial Intelligence and Machine Learning",
            "semester": 5,
            "student_count": 50,
            "core_courses": [],
            "elective_courses": [],
            "skill_courses": [],
            "multidisciplinary_courses": [],
            "preferred_morning_hours": True,
            "max_hours_per_day": 7
        })
    
    return json.dumps(result, indent=2)

# Main execution
if __name__ == "__main__":
    print("Starting CSV to NEP JSON conversion...")
    
    # First, debug the CSV files
    debug_success = debug_csv_files(
        'students.csv', 
        'classes.csv', 
        'faculty_workload.csv', 
        'courses.csv'
    )
    
    if debug_success:
        # Then convert the files
        json_data = convert_csv_to_nep_json(
            'students.csv', 
            'classes.csv', 
            'faculty_workload.csv', 
            'courses.csv'
        )
        
        if json_data:
            # Save to file
            with open('nep_timetable_data.json', 'w') as f:
                f.write(json_data)
            
            print("JSON data has been saved to nep_timetable_data.json")
            
            # Validate the data
            print("\nValidating data...")
            try:
                data = json.loads(json_data)
                print(f"Converted: {len(data['courses'])} courses, {len(data['faculty'])} faculty, "
                      f"{len(data['classrooms'])} classrooms, {len(data['student_batches'])} student batches")
            except:
                print("Could not validate JSON structure")
                
            print("\nConversion completed!")
        else:
            print("Conversion failed!")
    else:
        print("CSV debugging failed. Please check your CSV files.")