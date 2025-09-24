import pandas as pd
import json

def create_simplified_csvs():
    """
    Generates a set of simplified CSV files with easy-to-satisfy constraints
    to test the timetable generator.
    """

    # --- 1. Simplified Course Data ---
    # Low hours, assigned to specific teachers.
    courses_data = {
        'id': ['CS101', 'MATH101', 'ENG101'],
        'name': ['Intro to Python', 'Basic Algebra', 'Communication Skills'],
        'code': ['CS101', 'MATH101', 'ENG101'],
        'credits': [3, 3, 2],
        'course_type': ['core', 'core', 'ability_enhancement'],
        'hours_per_week': [3, 3, 2],
        'department': ['Computer Science', 'Mathematics', 'English'],
        'semester': [1, 1, 1],
        'faculty_id': ['F01', 'F02', 'F03'],
        'requires_lab': [True, False, False],
        'requires_smart_room': [False, False, True],
        'is_interdisciplinary': [False, False, False],
        'max_students': [50, 50, 50]
    }
    courses_df = pd.DataFrame(courses_data)

    # --- 2. Simplified Faculty Data ---
    # No unavailable slots, plenty of hours.
    faculty_data = {
        'id': ['F01', 'F02', 'F03'],
        'name': ['Dr. Alan Turing', 'Dr. Ada Lovelace', 'Prof. Grace Hopper'],
        'department': ['Computer Science', 'Mathematics', 'English'],
        'designation': ['Professor', 'Associate Professor', 'Assistant Professor'],
        'specializations': [json.dumps(['Algorithms']), json.dumps(['Calculus']), json.dumps(['Languages'])],
        'courses_can_teach': [json.dumps(['CS101']), json.dumps(['MATH101']), json.dumps(['ENG101'])],
        'max_hours_per_week': [20, 20, 20],
        'unavailable_slots': [json.dumps([]), json.dumps([]), json.dumps([])] # Empty list = always available
    }
    faculty_df = pd.DataFrame(faculty_data)

    # --- 3. Simplified Classroom Data ---
    # Plenty of rooms for the few courses.
    classrooms_data = {
        'id': ['R101', 'R102', 'LAB1'],
        'name': ['Lecture Hall 1', 'Smart Room 1', 'CS Lab'],
        'capacity': [60, 60, 60],
        'room_type': ['lecture', 'smart_classroom', 'lab'],
        'department': ['General', 'General', 'Computer Science'],
        'is_smart_room': [False, True, False]
    }
    classrooms_df = pd.DataFrame(classrooms_data)

    # --- 4. Simplified Student Batch Data ---
    # One batch that takes all the defined courses.
    batches_data = {
        'id': ['CS1A'],
        'name': ['CS First Year Section A'],
        'department': ['Computer Science'],
        'semester': [1],
        'student_count': [50],
        'core_courses': [json.dumps(['CS101', 'MATH101'])],
        'elective_courses': [json.dumps([])],
        'skill_courses': [json.dumps([])],
        'multidisciplinary_courses': [json.dumps([])],
        'ability_enhancement_courses': [json.dumps(['ENG101'])]
    }
    batches_df = pd.DataFrame(batches_data)

    # --- Save to CSV Files ---
    try:
        courses_df.to_csv('courses.csv', index=False)
        faculty_df.to_csv('faculty.csv', index=False)
        classrooms_df.to_csv('classrooms.csv', index=False)
        batches_df.to_csv('student_batches.csv', index=False)
        print("✅ Successfully created simplified CSV files:")
        print("- courses.csv")
        print("- faculty.csv")
        print("- classrooms.csv")
        print("- student_batches.csv")
    except Exception as e:
        print(f"❌ Error saving files: {e}")


# --- Run the script ---
if __name__ == '__main__':
    create_simplified_csvs()