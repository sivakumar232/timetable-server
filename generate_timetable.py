import json
from nep_timetable_generator import NEPTimetableGenerator

def main():
    # Load the converted data
    with open('nep_timetable_data.json', 'r') as f:
        json_data = f.read()
    
    # Initialize the timetable generator
    generator = NEPTimetableGenerator()
    
    # Load the data
    generator.load_from_json(json_data)
    
    print("Data loaded successfully!")
    print(f"Loaded: {len(generator.courses)} courses, {len(generator.teachers)} faculty, "
          f"{len(generator.classrooms)} classrooms, {len(generator.student_batches)} student batches")
    
    # Generate the timetable
    print("\nStarting timetable generation...")
    timetable = generator.genetic_algorithm_evolution(
        population_size=30,  # Start with a smaller population for testing
        generations=50       # Start with fewer generations
    )
    
    # Export results
    if timetable:
        print("\nTimetable generated successfully!")
        result = generator.export_nep_timetable(timetable, "my_college_timetable.json")
        generator.print_nep_timetable_summary(timetable)
        print(f"\nDetailed timetable saved to my_college_timetable.json")
    else:
        print("Failed to generate timetable. Check for constraints issues.")

if __name__ == "__main__":
    main()