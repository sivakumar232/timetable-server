# import pandas as pd
# import json
# import ast

# # --- 1. LOAD ORIGINAL DATA ---
# print("Loading original data files...")
# df_faculty_workload = pd.read_csv('faculty_workload.csv')
# df_rooms = pd.read_csv('classes.csv')
# df_students = pd.read_csv('students.csv')
# df_courses = pd.read_csv('courses.csv') # Your new crucial file

# # Add this at the beginning of your script to debug
# print("Faculty workload columns:", df_faculty_workload.columns.tolist())
# print("Courses columns:", df_courses.columns.tolist())
# print("Rooms columns:", df_rooms.columns.tolist())
# print("Students columns:", df_students.columns.tolist())

# # --- 2. CREATE FACULTY.CSV (NEPTimtableGenerator format) ---
# print("Transforming faculty data...")

# # First, create a mapping from faculty_serial_number to faculty_id and name
# # We assume the serial number in courses.csv corresponds to the faculty_id in faculty_workload.csv
# faculty_map = {}
# for _, row in df_faculty_workload.iterrows():
#     faculty_map[row['faculty_id']] = row['name']

# # Create a list to see which faculty from workload are assigned courses
# assigned_faculty_ids = set(df_courses['faculty_serial_number'].unique())
# # Create a reverse mapping: faculty_serial_number (from courses) -> faculty workload data
# faculty_data_dict = {}
# for fid in assigned_faculty_ids:
#     try:
#         workload_data = df_faculty_workload[df_faculty_workload['faculty_id'] == fid].iloc[0]
#         faculty_data_dict[fid] = workload_data
#     except IndexError:
#         print(f"Warning: Faculty serial number {fid} from courses.csv not found in faculty_workload.csv")
#         continue

# faculty_list = []
# for fid, workload_row in faculty_data_dict.items():
#     # Find all courses taught by this faculty
#     faculty_courses = df_courses[df_courses['faculty_serial_number'] == fid]
#     courses_can_teach = faculty_courses['code'].tolist()

#     faculty_dict = {
#         'id': str(workload_row['faculty_id']),
#         'name': workload_row['name'],
#         'department': workload_row['department'],
#         'designation': workload_row['designation'],
#         'specializations': [workload_row['Subject Allocated']], # Using assigned subject as specialization
#         'courses_can_teach': courses_can_teach,
#         'max_hours_per_week': int(workload_row['workload']),
#         'max_hours_per_day': 4 if 'Professor' in workload_row['designation'] else 5,
#         'preferred_time': 'any',
#         'unavailable_slots': [],
#         'research_slots': [],
#         'is_visiting': False,
#         'workload_preference': 1.0
#     }
#     faculty_list.append(faculty_dict)

# df_faculty_final = pd.DataFrame(faculty_list)
# df_faculty_final.to_csv('faculty_transformed.csv', index=False)
# print(f"Created faculty_transformed.csv with {len(faculty_list)} faculty members.")

# # --- 3. CREATE CLASSROOMS.CSV ---
# print("Transforming classroom data...")
# classrooms_list = []
# for _, room in df_rooms.iterrows():
#     room_dict = {
#         'id': room['id'],
#         'name': room['name'],
#         'capacity': room['capacity'],
#         'room_type': room['room_type'],
#         'department': room['department'],
#         'equipment': [],
#         'is_smart_room': room['room_type'] == 'smart_classroom',
#         'is_ac': True,
#         'has_projector': True,
#         'weekly_maintenance': []
#     }
#     classrooms_list.append(room_dict)

# df_classrooms_final = pd.DataFrame(classrooms_list)
# df_classrooms_final.to_csv('classrooms_transformed.csv', index=False)
# print(f"Created classrooms_transformed.csv with {len(classrooms_list)} rooms.")

# # --- 4. CREATE BATCHES.CSV ---
# print("Transforming student batch data...")
# # Create a mapping from course name to course code
# course_name_to_code = {}
# for _, course in df_courses.iterrows():
#     course_name_to_code[course['name']] = course['code']

# # Group all students into one batch for AIML Semester 5
# batch_id = "AIML_S5"
# batch_name = "AI & ML Semester 5"
# department = "Artificial Intelligence and Machine Learning"
# semester = 5
# student_count = len(df_students)

# # Initialize sets for collecting courses
# core_courses_set = set()
# elective_courses_set = set()
# skill_courses_set = set()
# multi_courses_set = set()

# # Process each student's courses
# for _, student in df_students.iterrows():
#     # Process core courses (JSON string)
#     try:
#         student_cores = ast.literal_eval(student['core_courses'])
#         for course_name in student_cores:
#             if course_name in course_name_to_code:
#                 core_courses_set.add(course_name_to_code[course_name])
#     except (ValueError, SyntaxError):
#         print(f"Could not parse core_courses for student {student['id']}")

#     # Process elective courses (JSON string)
#     try:
#         student_electives = ast.literal_eval(student['elective_courses'])
#         for course_name in student_electives:
#             if course_name in course_name_to_code:
#                 elective_courses_set.add(course_name_to_code[course_name])
#             else:
#                 # Use placeholder for general electives
#                 if "Professional Elective" in course_name:
#                     elective_courses_set.add("#PE-I")
#                 elif "Open Elective" in course_name:
#                     elective_courses_set.add("#OE-I")
#     except (ValueError, SyntaxError):
#         print(f"Could not parse elective_courses for student {student['id']}")

#     # Process skill courses (JSON string)
#     try:
#         student_skills = ast.literal_eval(student['skill_courses'])
#         for course_name in student_skills:
#             if course_name in course_name_to_code:
#                 skill_courses_set.add(course_name_to_code[course_name])
#     except (ValueError, SyntaxError):
#         print(f"Could not parse skill_courses for student {student['id']}")

# # Convert sets to lists
# core_courses_list = list(core_courses_set)
# elective_courses_list = list(elective_courses_set)
# skill_courses_list = list(skill_courses_set)
# multi_courses_list = list(multi_courses_set)

# # Create the batch dictionary
# batch_dict = {
#     'id': batch_id,
#     'name': batch_name,
#     'department': department,
#     'semester': semester,
#     'student_count': student_count,
#     'core_courses': core_courses_list,
#     'elective_courses': elective_courses_list,
#     'skill_courses': skill_courses_list,
#     'multidisciplinary_courses': multi_courses_list,
#     'preferred_morning_hours': True,
#     'max_hours_per_day': 7
# }

# df_batches_final = pd.DataFrame([batch_dict])
# df_batches_final.to_csv('batches_transformed.csv', index=False)
# print(f"Created batches_transformed.csv for {batch_name} with {student_count} students.")
# print(f"Core courses: {core_courses_list}")
# print(f"Elective courses: {elective_courses_list}")
# print(f"Skill courses: {skill_courses_list}")

# # --- 5. CREATE FINAL COURSES.CSV (NEPTimtableGenerator format) ---
# print("Creating final courses file...")
# courses_list = []
# for _, course in df_courses.iterrows():
#     # Determine if course requires lab based on name or type
#     requires_lab = 'lab' in course['name'].lower() or 'lab' in course['course_type'].lower()
#     requires_smart_room = 'smart' in course['name'].lower() or course['course_type'] == 'ability_enhancement'
    
#     course_dict = {
#         'id': course['code'],  # Using code as ID
#         'name': course['name'],
#         'code': course['code'],
#         'credits': int(course['credits']) if pd.notna(course['credits']) else 0,
#         'course_type': course['course_type'],
#         'hours_per_week': int(course['hours_per_week']) if pd.notna(course['hours_per_week']) else 3,
#         'department': course['department'],
#         'semester': int(course['semester']),
#         'faculty_id': str(course['faculty_serial_number']), # Map to faculty ID
#         'requires_lab': requires_lab,
#         'requires_smart_room': requires_smart_room,
#         'is_interdisciplinary': course['department'] == 'GENERAL',
#         'connected_departments': [],
#         'max_students': 60, # Default value
#         'min_duration_minutes': 50,
#         'max_consecutive_hours': 2,
#         'preferred_days': []
#     }
#     courses_list.append(course_dict)

# df_courses_final = pd.DataFrame(courses_list)
# df_courses_final.to_csv('courses_transformed.csv', index=False)
# print(f"Created courses_transformed.csv with {len(courses_list)} courses.")

# print("\n=== TRANSFORMATION COMPLETE ===")
# print("Generated files ready for NEPTimetableGenerator:")
# print("1. faculty_transformed.csv")
# print("2. classrooms_transformed.csv") 
# print("3. batches_transformed.csv")
# print("4. courses_transformed.csv")
# print("\nNext step: Use these files with your web API to generate the timetable!")


import pandas as pd
import json
import ast

# --- 1. LOAD ORIGINAL DATA ---
print("Loading original data files...")
df_faculty_workload = pd.read_csv('faculty_workload.csv')
df_rooms = pd.read_csv('classes.csv')
df_students = pd.read_csv('students.csv')
df_courses = pd.read_csv('courses.csv') # Your new crucial file

# Debug: print available columns
print("Faculty workload columns:", df_faculty_workload.columns.tolist())
print("Courses columns:", df_courses.columns.tolist())

# --- 2. CREATE FACULTY.CSV (NEPTimtableGenerator format) ---
print("Transforming faculty data...")

# First, create a mapping from faculty id to name (using 'id' column instead of 'faculty_id')
faculty_map = {}
for _, row in df_faculty_workload.iterrows():
    faculty_map[row['id']] = row['name']

# Create a list to see which faculty from workload are assigned courses
assigned_faculty_ids = set(df_courses['faculty_serial_number'].unique())
# Create a reverse mapping: faculty_serial_number (from courses) -> faculty workload data
faculty_data_dict = {}
for fid in assigned_faculty_ids:
    try:
        workload_data = df_faculty_workload[df_faculty_workload['id'] == fid].iloc[0]
        faculty_data_dict[fid] = workload_data
    except IndexError:
        print(f"Warning: Faculty serial number {fid} from courses.csv not found in faculty_workload.csv")
        continue

faculty_list = []
for fid, workload_row in faculty_data_dict.items():
    # Find all courses taught by this faculty
    faculty_courses = df_courses[df_courses['faculty_serial_number'] == fid]
    courses_can_teach = faculty_courses['code'].tolist()

    faculty_dict = {
        'id': str(workload_row['id']),  # Changed from 'faculty_id' to 'id'
        'name': workload_row['name'],
        'department': workload_row['department'],
        'designation': workload_row['designation'],
        'specializations': [workload_row['Subject Allocated']], # Using assigned subject as specialization
        'courses_can_teach': courses_can_teach,
        'max_hours_per_week': int(workload_row['workload']),
        'max_hours_per_day': 4 if 'Professor' in workload_row['designation'] else 5,
        'preferred_time': 'any',
        'unavailable_slots': [],
        'research_slots': [],
        'is_visiting': False,
        'workload_preference': 1.0
    }
    faculty_list.append(faculty_dict)

df_faculty_final = pd.DataFrame(faculty_list)
df_faculty_final.to_csv('faculty_transformed.csv', index=False)
print(f"Created faculty_transformed.csv with {len(faculty_list)} faculty members.")

# --- 3. CREATE CLASSROOMS.CSV ---
print("Transforming classroom data...")
classrooms_list = []
for _, room in df_rooms.iterrows():
    room_dict = {
        'id': room['id'],
        'name': room['name'],
        'capacity': room['capacity'],
        'room_type': room['room_type'],
        'department': room['department'],
        'equipment': [],
        'is_smart_room': room['room_type'] == 'smart_classroom',
        'is_ac': True,
        'has_projector': True,
        'weekly_maintenance': []
    }
    classrooms_list.append(room_dict)

df_classrooms_final = pd.DataFrame(classrooms_list)
df_classrooms_final.to_csv('classrooms_transformed.csv', index=False)
print(f"Created classrooms_transformed.csv with {len(classrooms_list)} rooms.")

# --- 4. CREATE BATCHES.CSV ---
print("Transforming student batch data...")
# Create a mapping from course name to course code
course_name_to_code = {}
for _, course in df_courses.iterrows():
    course_name_to_code[course['name']] = course['code']

# Group all students into one batch for AIML Semester 5
batch_id = "AIML_S5"
batch_name = "AI & ML Semester 5"
department = "Artificial Intelligence and Machine Learning"
semester = 5
student_count = len(df_students)

# Initialize sets for collecting courses
core_courses_set = set()
elective_courses_set = set()
skill_courses_set = set()
multi_courses_set = set()

# Process each student's courses
for _, student in df_students.iterrows():
    # Process core courses (JSON string)
    try:
        student_cores = ast.literal_eval(student['core_courses'])
        for course_name in student_cores:
            if course_name in course_name_to_code:
                core_courses_set.add(course_name_to_code[course_name])
    except (ValueError, SyntaxError):
        print(f"Could not parse core_courses for student {student['id']}")

    # Process elective courses (JSON string)
    try:
        student_electives = ast.literal_eval(student['elective_courses'])
        for course_name in student_electives:
            if course_name in course_name_to_code:
                elective_courses_set.add(course_name_to_code[course_name])
            else:
                # Use placeholder for general electives
                if "Professional Elective" in course_name:
                    elective_courses_set.add("#PE-I")
                elif "Open Elective" in course_name:
                    elective_courses_set.add("#OE-I")
    except (ValueError, SyntaxError):
        print(f"Could not parse elective_courses for student {student['id']}")

    # Process skill courses (JSON string)
    try:
        student_skills = ast.literal_eval(student['skill_courses'])
        for course_name in student_skills:
            if course_name in course_name_to_code:
                skill_courses_set.add(course_name_to_code[course_name])
    except (ValueError, SyntaxError):
        print(f"Could not parse skill_courses for student {student['id']}")

# Convert sets to lists
core_courses_list = list(core_courses_set)
elective_courses_list = list(elective_courses_set)
skill_courses_list = list(skill_courses_set)
multi_courses_list = list(multi_courses_set)

# Create the batch dictionary
batch_dict = {
    'id': batch_id,
    'name': batch_name,
    'department': department,
    'semester': semester,
    'student_count': student_count,
    'core_courses': core_courses_list,
    'elective_courses': elective_courses_list,
    'skill_courses': skill_courses_list,
    'multidisciplinary_courses': multi_courses_list,
    'preferred_morning_hours': True,
    'max_hours_per_day': 7
}

df_batches_final = pd.DataFrame([batch_dict])
df_batches_final.to_csv('batches_transformed.csv', index=False)
print(f"Created batches_transformed.csv for {batch_name} with {student_count} students.")
print(f"Core courses: {core_courses_list}")
print(f"Elective courses: {elective_courses_list}")
print(f"Skill courses: {skill_courses_list}")

# --- 5. CREATE FINAL COURSES.CSV (NEPTimtableGenerator format) ---
print("Creating final courses file...")
courses_list = []
for _, course in df_courses.iterrows():
    # Determine if course requires lab based on name or type
    requires_lab = 'lab' in course['name'].lower() or 'lab' in course['course_type'].lower()
    requires_smart_room = 'smart' in course['name'].lower() or course['course_type'] == 'ability_enhancement'
    
    course_dict = {
        'id': course['code'],  # Using code as ID
        'name': course['name'],
        'code': course['code'],
        'credits': int(course['credits']) if pd.notna(course['credits']) else 0,
        'course_type': course['course_type'],
        'hours_per_week': int(course['hours_per_week']) if pd.notna(course['hours_per_week']) else 3,
        'department': course['department'],
        'semester': int(course['semester']),
        'faculty_id': str(course['faculty_serial_number']), # Map to faculty ID
        'requires_lab': requires_lab,
        'requires_smart_room': requires_smart_room,
        'is_interdisciplinary': course['department'] == 'GENERAL',
        'connected_departments': [],
        'max_students': 60, # Default value
        'min_duration_minutes': 50,
        'max_consecutive_hours': 2,
        'preferred_days': []
    }
    courses_list.append(course_dict)

df_courses_final = pd.DataFrame(courses_list)
df_courses_final.to_csv('courses_transformed.csv', index=False)
print(f"Created courses_transformed.csv with {len(courses_list)} courses.")

print("\n=== TRANSFORMATION COMPLETE ===")
print("Generated files ready for NEPTimetableGenerator:")
print("1. faculty_transformed.csv")
print("2. classrooms_transformed.csv") 
print("3. batches_transformed.csv")
print("4. courses_transformed.csv")
print("\nNext step: Use these files with your web API to generate the timetable!")