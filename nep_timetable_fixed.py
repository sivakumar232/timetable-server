# import json
# import numpy as np
# import pandas as pd
# from datetime import datetime, timedelta
# import random
# from dataclasses import dataclass, asdict
# from typing import List, Dict, Tuple, Optional, Union
# from collections import defaultdict
# from enum import Enum
# import copy

# class CourseType(Enum):
#     CORE = "core"
#     ELECTIVE = "elective" 
#     MULTIDISCIPLINARY = "multidisciplinary"
#     SKILL_ENHANCEMENT = "skill_enhancement"
#     VALUE_ADDED = "value_added"
#     ABILITY_ENHANCEMENT = "ability_enhancement"
#     SEMINAR = "seminar"
#     PROJECT = "project"
#     HONORS = "honors"
#     MINOR = "minor"

# class RoomType(Enum):
#     LECTURE = "lecture"
#     LAB = "lab"
#     SEMINAR = "seminar"
#     COMPUTER_LAB = "computer_lab"
#     SMART_CLASSROOM = "smart_classroom"
#     AUDITORIUM = "auditorium"

# class TimePreference(Enum):
#     MORNING = "morning"
#     AFTERNOON = "afternoon"
#     EVENING = "evening"
#     ANY = "any"

# @dataclass
# class NEPCourse:
#     """Enhanced course structure following NEP 2020 guidelines"""
#     id: str
#     name: str
#     code: str
#     credits: int
#     course_type: CourseType
#     hours_per_week: int
#     department: str
#     semester: int
#     faculty_id: str
#     requires_lab: bool = False
#     requires_smart_room: bool = False
#     is_interdisciplinary: bool = False
#     connected_departments: List[str] = None
#     max_students: int = 60
#     min_duration_minutes: int = 50
#     max_consecutive_hours: int = 2
#     preferred_days: List[int] = None
    
#     def __post_init__(self):
#         if self.connected_departments is None:
#             self.connected_departments = []
#         if self.preferred_days is None:
#             self.preferred_days = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPCourse from dictionary"""
#         # Convert string course_type to enum
#         if isinstance(data['course_type'], str):
#             # Handle case-insensitive matching and different naming conventions
#             course_type_str = data['course_type'].lower().strip()
#             if course_type_str == 'honors':
#                 data['course_type'] = CourseType.HONORS
#             elif course_type_str == 'minor':
#                 data['course_type'] = CourseType.MINOR
#             else:
#                 try:
#                     data['course_type'] = CourseType(course_type_str)
#                 except ValueError:
#                     # Fallback to core for unknown types
#                     print(f"Warning: Unknown course type '{data['course_type']}', defaulting to 'core'")
#                     data['course_type'] = CourseType.CORE
#         return cls(**data)

# @dataclass 
# class NEPFaculty:
#     """Faculty with NEP 2020 compliant parameters"""
#     id: str
#     name: str
#     department: str
#     designations: str
#     specializations: List[str]
#     courses_can_teach: List[str]
#     max_hours_per_day: int = 6
#     max_hours_per_week: int = 24
#     preferred_time: TimePreference = TimePreference.ANY
#     unavailable_slots: List[Tuple[int, int]] = None
#     research_slots: List[Tuple[int, int]] = None
#     is_visiting: bool = False
#     workload_preference: float = 1.0
    
#     def __post_init__(self):
#         if self.unavailable_slots is None:
#             self.unavailable_slots = []
#         if self.research_slots is None:
#             self.research_slots = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPFaculty from dictionary"""
#         # Rename 'designation' key from JSON to 'designations' for the dataclass
#         if 'designation' in data:
#             data['designations'] = data.pop('designation')
#         # Convert string preferred_time to enum
#         if isinstance(data.get('preferred_time'), str):
#             data['preferred_time'] = TimePreference(data['preferred_time'])
#         return cls(**data)

# @dataclass
# class NEPClassroom:
#     """Classroom with modern facilities"""
#     id: str
#     name: str
#     capacity: int
#     room_type: RoomType
#     department: str
#     equipment: List[str]
#     is_smart_room: bool = False
#     is_ac: bool = False
#     has_projector: bool = True
#     weekly_maintenance: List[Tuple[int, int]] = None
    
#     def __post_init__(self):
#         if self.weekly_maintenance is None:
#             self.weekly_maintenance = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPClassroom from dictionary"""
#         # Convert string room_type to enum
#         if isinstance(data['room_type'], str):
#             data['room_type'] = RoomType(data['room_type'])
#         return cls(**data)

# @dataclass
# class NEPStudentBatch:
#     """Student batch/class with NEP parameters"""
#     id: str
#     name: str
#     department: str
#     semester: int
#     student_count: int
#     core_courses: List[str]
#     elective_courses: List[str]
#     skill_courses: List[str]
#     multidisciplinary_courses: List[str]
#     preferred_morning_hours: bool = True
#     max_hours_per_day: int = 7
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPStudentBatch from dictionary"""
#         return cls(**data)

# @dataclass
# class UserPreferences:
#     """User-configurable preferences"""
#     working_days: int = 5
#     periods_per_day: int = 8
#     lunch_break_period: int = 4
#     max_consecutive_same_subject: int = 2
#     gap_penalty_weight: float = 10.0
#     faculty_preference_weight: float = 15.0
#     workload_balance_weight: float = 20.0
#     room_preference_weight: float = 5.0
#     interdisciplinary_bonus: float = 10.0
#     research_slot_protection: bool = True
#     allow_saturday_classes: bool = False
#     morning_start_time: str = "9:00"
#     evening_end_time: str = "5:00"

# class NEPTimetableGenerator:
#     """Enhanced timetable generator compliant with NEP 2020"""
    
#     def __init__(self, config_json: str = None, user_preferences: UserPreferences = None):
#         self.preferences = user_preferences or UserPreferences()
#         self.days = 6 if self.preferences.allow_saturday_classes else 5
#         self.periods_per_day = self.preferences.periods_per_day
        
#         # Data containers
#         self.courses = {}
#         self.teachers = {}
#         self.classrooms = {}
#         self.student_batches = {}
#         self.departments = set()
        
#         # Generate time slots and timeslots list
#         self.generate_time_slots()
#         self.timeslots = [f"Day{d}_Period{p}" for d in range(self.days) for p in range(self.periods_per_day)]
        
#         self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:self.days]
        
#         # Load configuration if provided
#         if config_json:
#             self.load_from_json(config_json)
    
#     def generate_time_slots(self):
#         """Generate flexible time slots following NEP guidelines"""
#         start_hour = int(self.preferences.morning_start_time.split(':')[0])
        
#         self.time_slots = []
#         for i in range(self.periods_per_day):
#             if i < 4:
#                 hour = start_hour + i
#                 self.time_slots.append(f"{hour}:00-{hour}:50")
#             elif i == 4:
#                 self.time_slots.append("12:50-1:40 (LUNCH)")
#             else:
#                 hour = 13 + (i - 4)
#                 self.time_slots.append(f"{hour}:40-{hour+1}:30")
    
#     def load_from_json(self, config_json: str):
#         """Load configuration from JSON string"""
#         try:
#             data = json.loads(config_json)
#         except json.JSONDecodeError as e:
#             print(f"Error: Invalid JSON format provided. Details: {e}")
#             return

#         # Load Courses
#         for course_data in data.get("courses", []):
#             try:
#                 course_obj = NEPCourse.from_dict(course_data)
#                 self.add_course(course_obj)
#             except Exception as e:
#                 print(f"Error loading course {course_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Faculty
#         for faculty_data in data.get("faculty", []):
#             try:
#                 teacher_obj = NEPFaculty.from_dict(faculty_data)
#                 self.add_teacher(teacher_obj)
#             except Exception as e:
#                 print(f"Error loading faculty {faculty_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Classrooms
#         for classroom_data in data.get("classrooms", []):
#             try:
#                 classroom_obj = NEPClassroom.from_dict(classroom_data)
#                 self.add_classroom(classroom_obj)
#             except Exception as e:
#                 print(f"Error loading classroom {classroom_data.get('id', 'unknown')}: {e}")
#                 continue
            
#         # Load Student Batches
#         for batch_data in data.get("student_batches", []):
#             try:
#                 batch_obj = NEPStudentBatch.from_dict(batch_data)
#                 self.add_student_batch(batch_obj)
#             except Exception as e:
#                 print(f"Error loading batch {batch_data.get('id', 'unknown')}: {e}")
#                 continue

#         print("Configuration loaded successfully from JSON.")

#     def add_course(self, course: NEPCourse):
#         """Add course to system"""
#         self.courses[course.id] = course
#         self.departments.add(course.department)
    
#     def add_teacher(self, teacher: NEPFaculty):
#         """Add teacher to system"""
#         # Filter out slots that are outside the configured days/periods
#         if teacher.research_slots:
#             teacher.research_slots = [
#                 (day, period) for day, period in teacher.research_slots 
#                 if day < self.days and period < self.periods_per_day
#             ]
#         if teacher.unavailable_slots:
#             teacher.unavailable_slots = [
#                 (day, period) for day, period in teacher.unavailable_slots
#                 if day < self.days and period < self.periods_per_day
#             ]
        
#         self.teachers[teacher.id] = teacher
#         self.departments.add(teacher.department)
    
#     def add_classroom(self, classroom: NEPClassroom):
#         """Add classroom to system"""
#         if classroom.weekly_maintenance:
#             classroom.weekly_maintenance = [
#                 (day, period) for day, period in classroom.weekly_maintenance
#                 if day < self.days and period < self.periods_per_day
#             ]

#         self.classrooms[classroom.id] = classroom
#         self.departments.add(classroom.department)
    
#     def add_student_batch(self, batch: NEPStudentBatch):
#         """Add student batch to system"""
#         self.student_batches[batch.id] = batch
#         self.departments.add(batch.department)
    
#     def is_break_period(self, period: int) -> bool:
#         """Check if the given period is a designated break period"""
#         return period == self.preferences.lunch_break_period
    
#     def create_initial_timetable(self):
#         """
#         Creates an initial, complete, but random timetable.
#         This method ensures all course hours are scheduled, letting the GA fix clashes.
#         """
#         timetable = {}
        
#         # Initialize an empty schedule for each batch
#         for batch_id in self.student_batches:
#             timetable[batch_id] = np.full((self.days, self.periods_per_day), None, dtype=object)

#         # Place each course the required number of times randomly
#         for batch_id, batch in self.student_batches.items():
#             all_courses = (batch.core_courses + batch.elective_courses + 
#                          batch.skill_courses + batch.multidisciplinary_courses)
            
#             for course_id in all_courses:
#                 if course_id not in self.courses:
#                     continue

#                 course = self.courses[course_id]
#                 hours_to_schedule = course.hours_per_week
                
#                 for _ in range(hours_to_schedule):
#                     # Keep trying to find an empty slot for this batch
#                     attempts = 0
#                     while attempts < 100:
#                         day = random.randrange(self.days)
#                         period = random.randrange(self.periods_per_day)

#                         # Ensure it's not a lunch break and the slot is empty for the batch
#                         if period != self.preferences.lunch_break_period and timetable[batch_id][day][period] is None:
#                             # Find any suitable classroom
#                             classroom_id = self.find_suitable_classroom(course, day, period, {})
                            
#                             if classroom_id:
#                                 timetable[batch_id][day][period] = {
#                                     'course_id': course_id,
#                                     'faculty_id': course.faculty_id,
#                                     'classroom_id': classroom_id
#                                 }
#                                 break # Move to the next hour for this course
#                         attempts += 1
#         return timetable
    
#     def get_course_priority_order(self, courses: List[str]) -> List[str]:
#         """Get NEP 2020 compliant course priority order"""
#         priority_order = []
        
#         # Group courses by type
#         by_type = defaultdict(list)
#         for course_id in courses:
#             if course_id in self.courses:
#                 course_type = self.courses[course_id].course_type
#                 by_type[course_type].append(course_id)
        
#         # NEP priority: Core -> Ability Enhancement -> Skill -> Multi -> Electives
#         type_priority = [
#             CourseType.CORE,
#             CourseType.ABILITY_ENHANCEMENT, 
#             CourseType.SKILL_ENHANCEMENT,
#             CourseType.MULTIDISCIPLINARY,
#             CourseType.ELECTIVE,
#             CourseType.VALUE_ADDED,
#             CourseType.SEMINAR,
#             CourseType.PROJECT,
#             CourseType.HONORS,
#             CourseType.MINOR
#         ]
        
#         for course_type in type_priority:
#             priority_order.extend(by_type[course_type])
        
#         return priority_order
    
#     def find_best_slot(self, course: NEPCourse, batch: NEPStudentBatch, schedule) -> Tuple[Optional[int], Optional[int]]:
#         """Find best time slot considering NEP guidelines"""
#         best_slots = []
        
#         for day in range(self.days):
#             for period in range(self.periods_per_day):
#                 if schedule[day][period] is None and period != self.preferences.lunch_break_period:
#                     score = self.calculate_slot_preference_score(course, batch, day, period, schedule)
#                     best_slots.append((score, day, period))
        
#         if not best_slots:
#             return None, None
        
#         best_slots.sort(reverse=True, key=lambda x: x[0])
#         top_candidates = [slot for slot in best_slots[:5] if slot[0] >= best_slots[0][0] * 0.8]
        
#         if top_candidates:
#             _, day, period = random.choice(top_candidates)
#             return day, period
        
#         return None, None
    
#     def calculate_slot_preference_score(self, course: NEPCourse, batch: NEPStudentBatch, 
#                                      day: int, period: int, schedule) -> float:
#         """Calculate preference score for a time slot"""
#         score = 100.0
        
#         # NEP guideline: Morning classes preferred for core subjects
#         if course.course_type == CourseType.CORE and period < 4:
#             score += 20.0
        
#         # Faculty time preferences
#         teacher = self.teachers[course.faculty_id]
#         if teacher.preferred_time == TimePreference.MORNING and period < 4:
#             score += 15.0
#         elif teacher.preferred_time == TimePreference.AFTERNOON and 4 < period < 7:
#             score += 15.0
        
#         # Avoid research slots
#         if (day, period) in teacher.research_slots:
#             score -= 50.0
        
#         # Course preferred days
#         if course.preferred_days and day in course.preferred_days:
#             score += 10.0
        
#         # Avoid too many consecutive hours
#         consecutive_penalty = self.calculate_consecutive_penalty(schedule, day, period)
#         score -= consecutive_penalty * 5.0
        
#         # Minimize gaps in schedule
#         gap_penalty = self.calculate_gap_penalty(schedule, day, period)
#         score -= gap_penalty * 3.0
        
#         return score
    
#     def calculate_consecutive_penalty(self, schedule, day: int, period: int) -> float:
#         """Calculate penalty for consecutive same subject hours"""
#         if period == 0:
#             return 0.0
        
#         consecutive_count = 1
#         prev_period = period - 1
        
#         while prev_period >= 0 and schedule[day][prev_period] is not None:
#             consecutive_count += 1
#             prev_period -= 1
        
#         return max(0, consecutive_count - self.preferences.max_consecutive_same_subject)
    
#     def calculate_gap_penalty(self, schedule, day: int, period: int) -> float:
#         """Calculate penalty for creating gaps in daily schedule"""
#         penalty = 0.0
        
#         # Check for gaps before this period
#         gaps_before = 0
#         for p in range(period):
#             if schedule[day][p] is None and not self.is_break_period(p):
#                 gaps_before += 1
        
#         # Penalize gaps in middle of schedule
#         if gaps_before > 0:
#             penalty += gaps_before * 2.0
        
#         return penalty
    
#     def find_suitable_classroom(self, course: NEPCourse, day: int, period: int, timetable: dict) -> Optional[str]:
#         """Find suitable classroom based on course requirements"""
#         suitable_rooms = []
        
#         for room_id, room in self.classrooms.items():
#             # Check capacity
#             if room.capacity < course.max_students:
#                 continue
            
#             # Check room type requirements
#             if course.requires_lab and room.room_type not in [RoomType.LAB, RoomType.COMPUTER_LAB]:
#                 continue
            
#             if course.requires_smart_room and not room.is_smart_room:
#                 continue
            
#             # Check availability
#             if self.is_room_available(room_id, day, period, timetable):
#                 pref_score = 0
#                 if room.department == course.department:
#                     pref_score += 10
#                 if course.course_type == CourseType.SEMINAR and room.room_type == RoomType.SEMINAR:
#                     pref_score += 15
                
#                 suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         return None
    
#     def is_room_available(self, room_id: str, day: int, period: int, timetable: dict) -> bool:
#         """Check if room is available at given time"""
#         room = self.classrooms[room_id]
        
#         # Check maintenance slots
#         if (day, period) in room.weekly_maintenance:
#             return False
        
#         # Check if room is already occupied
#         for batch_id, schedule in timetable.items():
#             if schedule[day][period] is not None:
#                 if schedule[day][period]['classroom_id'] == room_id:
#                     return False
        
#         return True
    
#     def is_faculty_available(self, faculty_id: str, day: int, period: int, timetable: dict) -> bool:
#         """Check if faculty is available"""
#         teacher = self.teachers[faculty_id]
        
#         # Check unavailable slots
#         if (day, period) in teacher.unavailable_slots:
#             return False
        
#         # Check research slots
#         if self.preferences.research_slot_protection and (day, period) in teacher.research_slots:
#             return False
        
#         # Check if already assigned
#         for batch_id, schedule in timetable.items():
#             if schedule[day][period] is not None:
#                 if schedule[day][period]['faculty_id'] == faculty_id:
#                     return False
        
#         # Check daily hour limit
#         daily_hours = self.get_faculty_daily_hours(faculty_id, day, timetable)
#         if daily_hours >= teacher.max_hours_per_day:
#             return False
        
#         return True
    
#     def get_faculty_daily_hours(self, faculty_id: str, day: int, timetable: dict) -> int:
#         """Get current daily hours for faculty"""
#         hours = 0
#         for batch_id, schedule in timetable.items():
#             for period in range(self.periods_per_day):
#                 if schedule[day][period] is not None:
#                     if schedule[day][period]['faculty_id'] == faculty_id:
#                         hours += 1
#         return hours
    
#     def genetic_algorithm_evolution(self, population_size: int = 50, generations: int = 100) -> dict:
#         """Main genetic algorithm with NEP-specific optimizations"""
#         print(f"Initializing NEP-compliant timetable generation...")
#         print(f"Population: {population_size}, Generations: {generations}")
        
#         # Initialize population
#         population = []
#         for _ in range(population_size):
#             individual = self.create_initial_timetable()
#             population.append(individual)
        
#         best_fitness = 0
#         best_timetable = None
        
#         for gen in range(generations):
#             # Calculate fitness
#             fitness_scores = []
#             for individual in population:
#                 fitness = self.calculate_nep_fitness(individual)
#                 fitness_scores.append(fitness)
            
#             # Track best solution
#             max_fitness = max(fitness_scores)
#             if max_fitness > best_fitness:
#                 best_fitness = max_fitness
#                 best_timetable = copy.deepcopy(population[fitness_scores.index(max_fitness)])
#                 print(f"Generation {gen}: New best fitness = {best_fitness:.2f}")
            
#             # Early termination if perfect solution found
#             if best_fitness >= 950:  # Near perfect solution
#                 break
            
#             # Selection - Tournament selection with elitism
#             new_population = []
            
#             # Keep best 10% (elitism)
#             elite_count = max(1, population_size // 10)
#             elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elite_count]
#             for i in elite_indices:
#                 new_population.append(copy.deepcopy(population[i]))
            
#             # Tournament selection for remaining
#             while len(new_population) < population_size:
#                 tournament_size = 5
#                 tournament_indices = random.sample(range(population_size), min(tournament_size, population_size))
#                 tournament_fitness = [fitness_scores[i] for i in tournament_indices]
#                 winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
#                 new_population.append(copy.deepcopy(population[winner_idx]))
            
#             # Crossover and Mutation
#             next_population = new_population[:elite_count]
            
#             for i in range(elite_count, population_size, 2):
#                 if i + 1 < population_size:
#                     parent1 = new_population[i]
#                     parent2 = new_population[i + 1]
                    
#                     if random.random() < 0.8:  # Crossover probability
#                         child1, child2 = self.nep_crossover(parent1, parent2)
#                     else:
#                         child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                    
#                     # Mutation
#                     child1 = self.nep_mutation(child1, mutation_rate=0.1)
#                     child2 = self.nep_mutation(child2, mutation_rate=0.1)
                    
#                     next_population.extend([child1, child2])
#                 else:
#                     next_population.append(copy.deepcopy(new_population[i]))
            
#             population = next_population[:population_size]
        
#         print(f"Evolution complete. Final best fitness: {best_fitness:.2f}")
#         return best_timetable

#     def calculate_nep_fitness(self, timetable: dict) -> float:
#         """Calculate fitness score based on NEP 2020 guidelines"""
#         base_score = 1000.0
#         penalty = 0.0
        
#         # Hard constraint violations
#         penalty += self.check_faculty_conflicts(timetable) * 100
#         penalty += self.check_classroom_conflicts(timetable) * 100
#         penalty += self.check_workload_violations(timetable) * 80
#         penalty += self.check_course_hour_requirements(timetable) * 60
        
#         # Soft constraints
#         penalty += self.check_faculty_preferences(timetable) * self.preferences.faculty_preference_weight
#         penalty += self.check_schedule_gaps(timetable) * self.preferences.gap_penalty_weight
#         penalty += self.check_workload_balance(timetable) * self.preferences.workload_balance_weight
#         penalty += self.check_consecutive_violations(timetable) * 15
#         penalty += self.check_lunch_violations(timetable) * 25
        
#         # Bonuses
#         bonus = 0.0
#         bonus += self.calculate_interdisciplinary_bonus(timetable)
#         bonus += self.calculate_skill_course_bonus(timetable)
#         bonus += self.calculate_research_protection_bonus(timetable)
        
#         return max(0, base_score - penalty + bonus)
    
#     def check_faculty_conflicts(self, timetable: dict) -> int:
#         """Check for faculty double-booking"""
#         conflicts = 0
#         faculty_schedule = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         faculty_id = slot['faculty_id']
#                         faculty_schedule[faculty_id][day].append(period)
        
#         for faculty_id, days in faculty_schedule.items():
#             for day, periods in days.items():
#                 duplicates = len(periods) - len(set(periods))
#                 conflicts += duplicates
        
#         return conflicts
    
#     def check_classroom_conflicts(self, timetable: dict) -> int:
#         """Check for classroom double-booking"""
#         conflicts = 0
#         room_schedule = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         room_id = slot['classroom_id']
#                         room_schedule[room_id][day].append(period)
        
#         for room_id, days in room_schedule.items():
#             for day, periods in days.items():
#                 duplicates = len(periods) - len(set(periods))
#                 conflicts += duplicates
        
#         return conflicts
    
#     def check_workload_violations(self, timetable: dict) -> int:
#         """Check NEP workload guideline violations"""
#         violations = 0
        
#         for faculty_id, faculty in self.teachers.items():
#             weekly_hours = 0
            
#             for batch_id, schedule in timetable.items():
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = schedule[day][period]
#                         if slot and slot['faculty_id'] == faculty_id:
#                             weekly_hours += 1
            
#             if weekly_hours > faculty.max_hours_per_week:
#                 violations += weekly_hours - faculty.max_hours_per_week
            
#             for day in range(self.days):
#                 daily_hours = self.get_faculty_daily_hours(faculty_id, day, timetable)
#                 if daily_hours > faculty.max_hours_per_day:
#                     violations += daily_hours - faculty.max_hours_per_day
        
#         return violations
    
#     def check_course_hour_requirements(self, timetable: dict) -> int:
#         """Check if courses have required weekly hours"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             batch = self.student_batches[batch_id]
#             course_hours = defaultdict(int)
            
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course_hours[slot['course_id']] += 1
            
#             all_courses = (batch.core_courses + batch.elective_courses + 
#                           batch.skill_courses + batch.multidisciplinary_courses)
            
#             for course_id in all_courses:
#                 if course_id in self.courses:
#                     required = self.courses[course_id].hours_per_week
#                     actual = course_hours[course_id]
#                     violations += abs(required - actual)
        
#         return violations
    
#     def check_faculty_preferences(self, timetable: dict) -> int:
#         """Check faculty time preference violations"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         teacher = self.teachers[slot['faculty_id']]
                        
#                         if teacher.preferred_time == TimePreference.MORNING and period >= 4:
#                             violations += 1
#                         elif teacher.preferred_time == TimePreference.AFTERNOON and period < 4:
#                             violations += 1
        
#         return violations
    
#     def check_schedule_gaps(self, timetable: dict) -> int:
#         """Check for gaps in daily schedules"""
#         gaps = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 day_periods = []
#                 for period in range(self.periods_per_day):
#                     if schedule[day][period] is not None:
#                         day_periods.append(period)
                
#                 if len(day_periods) > 1:
#                     first_class = min(day_periods)
#                     last_class = max(day_periods)
                    
#                     for period in range(first_class + 1, last_class):
#                         if period != self.preferences.lunch_break_period and schedule[day][period] is None:
#                             gaps += 1
        
#         return gaps
    
#     def check_workload_balance(self, timetable: dict) -> float:
#         """Check workload balance across faculty"""
#         faculty_loads = defaultdict(int)
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         faculty_loads[slot['faculty_id']] += 1
        
#         if not faculty_loads:
#             return 0.0
        
#         loads = list(faculty_loads.values())
#         avg_load = sum(loads) / len(loads)
#         variance = sum((load - avg_load) ** 2 for load in loads) / len(loads)
        
#         return variance
    
#     def check_consecutive_violations(self, timetable: dict) -> int:
#         """Check for too many consecutive hours violations"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 consecutive_count = 0
#                 prev_subject = None
                
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     current_subject = slot['course_id'] if slot else None
                    
#                     if current_subject == prev_subject and current_subject is not None:
#                         consecutive_count += 1
#                         if consecutive_count > self.preferences.max_consecutive_same_subject:
#                             violations += 1
#                     else:
#                         consecutive_count = 1 if current_subject else 0
                    
#                     prev_subject = current_subject
        
#         return violations
    
#     def check_lunch_violations(self, timetable: dict) -> int:
#         """Check lunch break violations"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 if schedule[day][self.preferences.lunch_break_period] is not None:
#                     violations += 1
        
#         return violations
    
#     def calculate_interdisciplinary_bonus(self, timetable: dict) -> float:
#         """Calculate bonus for interdisciplinary courses"""
#         bonus = 0.0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         if course.is_interdisciplinary or course.course_type == CourseType.MULTIDISCIPLINARY:
#                             bonus += self.preferences.interdisciplinary_bonus
        
#         return bonus
    
#     def calculate_skill_course_bonus(self, timetable: dict) -> float:
#         """Calculate bonus for skill enhancement courses"""
#         bonus = 0.0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         if course.course_type in [CourseType.SKILL_ENHANCEMENT, CourseType.ABILITY_ENHANCEMENT]:
#                             bonus += 5.0
        
#         return bonus
    
#     def calculate_research_protection_bonus(self, timetable: dict) -> float:
#         """Calculate bonus for protecting faculty research time"""
#         bonus = 0.0
        
#         if not self.preferences.research_slot_protection:
#             return bonus
        
#         for faculty_id, teacher in self.teachers.items():
#             research_slots_protected = 0
            
#             for day, period in teacher.research_slots:
#                 if day < self.days:
#                     slot_free = True
#                     for batch_id, schedule in timetable.items():
#                         if schedule[day][period] is not None:
#                             if schedule[day][period]['faculty_id'] == faculty_id:
#                                 slot_free = False
#                                 break
                    
#                     if slot_free:
#                         research_slots_protected += 1
            
#             bonus += research_slots_protected * 5.0
        
#         return bonus
    
#     def nep_crossover(self, parent1: dict, parent2: dict) -> Tuple[dict, dict]:
#         """Perform crossover between two parent timetables"""
#         child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
        
#         if not self.student_batches:
#             return child1, child2
            
#         batch_id_to_cross = random.choice(list(self.student_batches.keys()))
#         day_to_swap = random.randrange(self.days)
        
#         if batch_id_to_cross in child1 and batch_id_to_cross in child2:
#             child1[batch_id_to_cross][day_to_swap] = parent2[batch_id_to_cross][day_to_swap].copy()
#             child2[batch_id_to_cross][day_to_swap] = parent1[batch_id_to_cross][day_to_swap].copy()

#         return child1, child2
    
#     def nep_mutation(self, timetable: dict, mutation_rate: float = 0.1) -> dict:
#         """Perform mutation on a timetable"""
#         mutated = copy.deepcopy(timetable)
        
#         if random.random() < mutation_rate:
#             if not self.student_batches:
#                 return mutated
                
#             batch_id_to_mutate = random.choice(list(self.student_batches.keys()))
            
#             if batch_id_to_mutate in mutated and self.days >= 2:
#                 schedule = mutated[batch_id_to_mutate]
#                 day1, day2 = random.sample(range(self.days), 2)
                
#                 # Swap entire days
#                 temp = schedule[day1].copy()
#                 schedule[day1] = schedule[day2].copy()
#                 schedule[day2] = temp

#         return mutated
    
#     def export_nep_timetable(self, timetable: dict, filename: str = "nep_timetable.json") -> dict:
#         """Export NEP-compliant timetable with detailed metadata"""
#         export_data = {
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "nep_2020_compliant": True,
#                 "total_batches": len(self.student_batches),
#                 "total_faculty": len(self.teachers),
#                 "total_courses": len(self.courses),
#                 "working_days": self.days,
#                 "periods_per_day": self.periods_per_day,
#                 "user_preferences": asdict(self.preferences)
#             },
#             "departments": list(self.departments),
#             "timetables": {},
#             "faculty_schedules": {},
#             "classroom_utilization": {},
#             "course_distribution": {},
#             "analytics": {}
#         }
        
#         # Export batch timetables
#         for batch_id, schedule in timetable.items():
#             batch = self.student_batches[batch_id]
#             batch_data = {
#                 "batch_info": {
#                     "name": batch.name,
#                     "department": batch.department,
#                     "semester": batch.semester,
#                     "student_count": batch.student_count
#                 },
#                 "weekly_schedule": []
#             }
            
#             for day in range(self.days):
#                 day_schedule = {
#                     "day": self.day_names[day],
#                     "periods": []
#                 }
                
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         teacher = self.teachers[slot['faculty_id']]
#                         classroom = self.classrooms[slot['classroom_id']]
                        
#                         period_data = {
#                             "time": self.time_slots[period],
#                             "course": {
#                                 "id": course.id,
#                                 "name": course.name,
#                                 "code": course.code,
#                                 "type": course.course_type.value,
#                                 "credits": course.credits,
#                                 "department": course.department
#                             },
#                             "faculty": {
#                                 "id": teacher.id,
#                                 "name": teacher.name,
#                                 "designation": teacher.designations # Corrected from `teacher.designation`
#                             },
#                             "classroom": {
#                                 "id": classroom.id,
#                                 "name": classroom.name,
#                                 "type": classroom.room_type.value,
#                                 "capacity": classroom.capacity
#                             }
#                         }
#                     else:
#                         if period == self.preferences.lunch_break_period:
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "lunch_break"
#                             }
#                         else:
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "free"
#                             }
                    
#                     day_schedule["periods"].append(period_data)
                
#                 batch_data["weekly_schedule"].append(day_schedule)
            
#             export_data["timetables"][batch.name] = batch_data
        
#         # Generate faculty schedules
#         for faculty_id, teacher in self.teachers.items():
#             faculty_schedule = {
#                 "faculty_info": {
#                     "name": teacher.name,
#                     "department": teacher.department,
#                     "designation": teacher.designations # Corrected from `teacher.designation`
#                 },
#                 "weekly_load": 0,
#                 "schedule": []
#             }
            
#             weekly_hours = 0
            
#             for day in range(self.days):
#                 day_schedule = {
#                     "day": self.day_names[day],
#                     "periods": []
#                 }
                
#                 for period in range(self.periods_per_day):
#                     period_info = {"time": self.time_slots[period], "status": "free"}
                    
#                     # Check if faculty is teaching
#                     for batch_id, schedule in timetable.items():
#                         slot = schedule[day][period]
#                         if slot and slot['faculty_id'] == faculty_id:
#                             course = self.courses[slot['course_id']]
#                             batch = self.student_batches[batch_id]
                            
#                             period_info = {
#                                 "time": self.time_slots[period],
#                                 "status": "teaching",
#                                 "course": course.name,
#                                 "batch": batch.name,
#                                 "classroom": self.classrooms[slot['classroom_id']].name
#                             }
#                             weekly_hours += 1
#                             break
                    
#                     # Check research slots
#                     if (day, period) in teacher.research_slots:
#                         period_info["status"] = "research"
                    
#                     day_schedule["periods"].append(period_info)
                
#                 faculty_schedule["schedule"].append(day_schedule)
            
#             faculty_schedule["weekly_load"] = weekly_hours
#             export_data["faculty_schedules"][teacher.name] = faculty_schedule
        
#         # Calculate analytics
#         export_data["analytics"] = self.calculate_timetable_analytics(timetable)
        
#         # Save to file
#         with open(filename, 'w') as f:
#             json.dump(export_data, f, indent=2, default=str)
        
#         print(f"NEP-compliant timetable exported to {filename}")
#         return export_data
    
#     def calculate_timetable_analytics(self, timetable: dict) -> dict:
#         """Calculate comprehensive timetable analytics"""
#         analytics = {
#             "fitness_score": self.calculate_nep_fitness(timetable),
#             "constraint_violations": {
#                 "faculty_conflicts": self.check_faculty_conflicts(timetable),
#                 "classroom_conflicts": self.check_classroom_conflicts(timetable),
#                 "workload_violations": self.check_workload_violations(timetable),
#                 "lunch_violations": self.check_lunch_violations(timetable)
#             },
#             "faculty_utilization": {},
#             "classroom_utilization": {},
#             "course_type_distribution": defaultdict(int),
#             "department_load_balance": defaultdict(int)
#         }
        
#         # Faculty utilization
#         for faculty_id, teacher in self.teachers.items():
#             weekly_hours = 0
#             for batch_id, schedule in timetable.items():
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = schedule[day][period]
#                         if slot and slot['faculty_id'] == faculty_id:
#                             weekly_hours += 1
            
#             utilization_percentage = (weekly_hours / teacher.max_hours_per_week) * 100
#             analytics["faculty_utilization"][teacher.name] = {
#                 "weekly_hours": weekly_hours,
#                 "max_hours": teacher.max_hours_per_week,
#                 "utilization_percentage": round(utilization_percentage, 2)
#             }
        
#         # Classroom utilization
#         total_slots = self.days * self.periods_per_day
#         for room_id, room in self.classrooms.items():
#             used_slots = 0
#             for batch_id, schedule in timetable.items():
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = schedule[day][period]
#                         if slot and slot['classroom_id'] == room_id:
#                             used_slots += 1
            
#             utilization_percentage = (used_slots / total_slots) * 100
#             analytics["classroom_utilization"][room.name] = {
#                 "used_slots": used_slots,
#                 "total_slots": total_slots,
#                 "utilization_percentage": round(utilization_percentage, 2)
#             }
        
#         # Course type distribution
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         analytics["course_type_distribution"][course.course_type.value] += 1
        
#         return analytics
    
#     def print_nep_timetable_summary(self, timetable: dict):
#         """Print NEP-compliant timetable summary"""
#         print("\n" + "="*80)
#         print("NEP 2020 COMPLIANT TIMETABLE GENERATION SUMMARY")
#         print("="*80)
        
#         analytics = self.calculate_timetable_analytics(timetable)
        
#         print(f"\nOVERALL METRICS:")
#         print(f"    Fitness Score: {analytics['fitness_score']:.2f}/1000")
#         print(f"    Departments: {len(self.departments)}")
#         print(f"    Student Batches: {len(self.student_batches)}")
#         print(f"    Total Courses: {len(self.courses)}")
#         print(f"    Faculty Members: {len(self.teachers)}")
#         print(f"    Classrooms: {len(self.classrooms)}")
        
#         print(f"\nCONSTRAINT VIOLATIONS:")
#         violations = analytics['constraint_violations']
#         print(f"    Faculty Conflicts: {violations['faculty_conflicts']}")
#         print(f"    Classroom Conflicts: {violations['classroom_conflicts']}")
#         print(f"    Workload Violations: {violations['workload_violations']}")
#         print(f"    Lunch Break Violations: {violations['lunch_violations']}")
        
#         print(f"\nCOURSE TYPE DISTRIBUTION (NEP 2020):")
#         for course_type, count in analytics['course_type_distribution'].items():
#             print(f"    {course_type.replace('_', ' ').title()}: {count} slots")
        
#         print(f"\nTOP FACULTY UTILIZATION:")
#         faculty_util = analytics['faculty_utilization']
#         sorted_faculty = sorted(faculty_util.items(), key=lambda x: x[1]['utilization_percentage'], reverse=True)
#         for name, util in sorted_faculty[:5]:
#             print(f"    {name}: {util['weekly_hours']}/{util['max_hours']} hrs ({util['utilization_percentage']}%)")
        
#         print(f"\nTOP CLASSROOM UTILIZATION:")
#         room_util = analytics['classroom_utilization']
#         sorted_rooms = sorted(room_util.items(), key=lambda x: x[1]['utilization_percentage'], reverse=True)
#         for name, util in sorted_rooms[:5]:
#             print(f"    {name}: {util['used_slots']}/{util['total_slots']} slots ({util['utilization_percentage']}%)")


# # Web API Integration Functions
# def create_nep_system_from_json(json_input: str, user_preferences: dict = None) -> NEPTimetableGenerator:
#     """Create NEP system from JSON input"""
#     prefs = UserPreferences()
#     if user_preferences:
#         for key, value in user_preferences.items():
#             if hasattr(prefs, key):
#                 setattr(prefs, key, value)
    
#     generator = NEPTimetableGenerator(user_preferences=prefs)
#     generator.load_from_json(json_input)
    
#     return generator

# def generate_timetable_api(json_input: str, user_preferences: dict = None, 
#                            population_size: int = 50, generations: int = 100) -> dict:
#     """Main API function for web integration"""
#     print("Starting NEP 2020 Compliant Timetable Generation...")
    
#     # Create system
#     generator = create_nep_system_from_json(json_input, user_preferences)
    
#     # Generate timetable
#     best_timetable = generator.genetic_algorithm_evolution(population_size, generations)
    
#     if best_timetable:
#         # Export and return result
#         result = generator.export_nep_timetable(best_timetable)
#         generator.print_nep_timetable_summary(best_timetable)
#         return result
#     else:
#         raise Exception("Failed to generate valid timetable. Please check constraints.")

# # Sample data for testing
# def create_sample_nep_data() -> dict:
#     """Create sample NEP 2020 compliant data for testing"""
#     return {
#         "courses": [
#             {
#                 "id": "CS101", "name": "Programming Fundamentals", "code": "CS101",
#                 "credits": 4, "course_type": "core", "hours_per_week": 4,
#                 "department": "Computer Science", "semester": 1, "faculty_id": "F001",
#                 "requires_lab": True, "requires_smart_room": False,
#                 "is_interdisciplinary": False, "max_students": 60,
#                 "preferred_days": [0, 2, 4]
#             },
#             {
#                 "id": "MATH101", "name": "Calculus I", "code": "MATH101",
#                 "credits": 4, "course_type": "core", "hours_per_week": 4,
#                 "department": "Mathematics", "semester": 1, "faculty_id": "F002",
#                 "requires_lab": False, "max_students": 80
#             },
#             {
#                 "id": "ENG101", "name": "Communication Skills", "code": "ENG101",
#                 "credits": 3, "course_type": "ability_enhancement", "hours_per_week": 3,
#                 "department": "English", "semester": 1, "faculty_id": "F003",
#                 "requires_smart_room": True, "max_students": 50
#             },
#             {
#                 "id": "ENV101", "name": "Environmental Science", "code": "ENV101",
#                 "credits": 2, "course_type": "multidisciplinary", "hours_per_week": 2,
#                 "department": "Environmental Science", "semester": 1, "faculty_id": "F004",
#                 "is_interdisciplinary": True, "connected_departments": ["Biology", "Chemistry"]
#             }
#         ],
#         "faculty": [
#             {
#                 "id": "F001", "name": "Dr. Rajesh Kumar", "department": "Computer Science",
#                 "designation": "Professor", "specializations": ["Programming", "Software Engineering"],
#                 "courses_can_teach": ["CS101"], "max_hours_per_day": 6, "max_hours_per_week": 20,
#                 "preferred_time": "morning", "research_slots": [[1, 6], [3, 7]]
#             },
#             {
#                 "id": "F002", "name": "Dr. Priya Sharma", "department": "Mathematics",
#                 "designation": "Associate Professor", "specializations": ["Calculus", "Linear Algebra"],
#                 "courses_can_teach": ["MATH101"], "preferred_time": "morning"
#             },
#             {
#                 "id": "F003", "name": "Prof. Anita Singh", "department": "English",
#                 "designation": "Assistant Professor", "specializations": ["Communication", "Literature"],
#                 "courses_can_teach": ["ENG101"], "preferred_time": "afternoon"
#             },
#             {
#                 "id": "F004", "name": "Dr. Kiran Patel", "department": "Environmental Science",
#                 "designation": "Professor", "specializations": ["Ecology", "Climate Change"],
#                 "courses_can_teach": ["ENV101"], "is_visiting": False
#             }
#         ],
#         "classrooms": [
#             {
#                 "id": "R101", "name": "Lecture Hall 1", "capacity": 80,
#                 "room_type": "lecture", "department": "General", "equipment": ["projector", "whiteboard"],
#                 "is_smart_room": True, "is_ac": True
#             },
#             {
#                 "id": "R201", "name": "Computer Lab 1", "capacity": 40,
#                 "room_type": "computer_lab", "department": "Computer Science",
#                 "equipment": ["computers", 'projector'], "is_ac": True
#             },
#             {
#                 "id": "R301", "name": "Seminar Hall", "capacity": 50,
#                 "room_type": "seminar", "department": "General",
#                 "equipment": ["smart_board", "audio_system"], "is_smart_room": True
#             }
#         ],
#         "student_batches": [
#             {
#                 "id": "CS1A", "name": "CS First Year Section A", "department": "Computer Science",
#                 "semester": 1, "student_count": 55,
#                 "core_courses": ["CS101", "MATH101"],
#                 "elective_courses": [],
#                 "skill_courses": [],
#                 "multidisciplinary_courses": ["ENV101"],
#                 "preferred_morning_hours": True
#             },
#             {
#                 "id": "CS1B", "name": "CS First Year Section B", "department": "Computer Science",
#                 "semester": 1, "student_count": 50,
#                 "core_courses": ["CS101", "MATH101"],
#                 "elective_courses": [],
#                 "skill_courses": [],
#                 "multidisciplinary_courses": ["ENV101"]
#             }
#         ]
#     }

# # Main execution for testing
# if __name__ == "__main__":
#     sample_data = create_sample_nep_data()
    
#     user_prefs = {
#         "working_days": 5,
#         "periods_per_day": 8,
#         "lunch_break_period": 4,
#         "faculty_preference_weight": 20.0,
#         "interdisciplinary_bonus": 15.0,
#         "research_slot_protection": True
#     }
    
#     try:
#         result = generate_timetable_api(
#             json.dumps(sample_data), 
#             user_prefs, 
#             population_size=30, 
#             generations=100
#         )
        
#         print(f"\nTimetable generated successfully!")
#         print(f"Exported to: nep_timetable.json")
        
#     except Exception as e:
#         print(f"Error: {e}")



# import json
# import numpy as np
# import pandas as pd
# from datetime import datetime, timedelta
# import random
# from dataclasses import dataclass, asdict
# from typing import List, Dict, Tuple, Optional, Union
# from collections import defaultdict
# from enum import Enum
# import copy
# import math

# class CourseType(Enum):
#     CORE = "core"
#     ELECTIVE = "elective" 
#     MULTIDISCIPLINARY = "multidisciplinary"
#     SKILL_ENHANCEMENT = "skill_enhancement"
#     VALUE_ADDED = "value_added"
#     ABILITY_ENHANCEMENT = "ability_enhancement"
#     SEMINAR = "seminar"
#     PROJECT = "project"
#     HONORS = "honors"
#     MINOR = "minor"

# class RoomType(Enum):
#     LECTURE = "lecture"
#     LAB = "lab"
#     SEMINAR = "seminar"
#     COMPUTER_LAB = "computer_lab"
#     SMART_CLASSROOM = "smart_classroom"
#     AUDITORIUM = "auditorium"

# class TimePreference(Enum):
#     MORNING = "morning"
#     AFTERNOON = "afternoon"
#     EVENING = "evening"
#     ANY = "any"

# @dataclass
# class NEPCourse:
#     """Enhanced course structure following NEP 2020 guidelines"""
#     id: str
#     name: str
#     code: str
#     credits: int
#     course_type: CourseType
#     hours_per_week: int
#     department: str
#     semester: int
#     faculty_id: str
#     requires_lab: bool = False
#     requires_smart_room: bool = False
#     is_interdisciplinary: bool = False
#     connected_departments: List[str] = None
#     max_students: int = 60
#     min_duration_minutes: int = 50
#     max_consecutive_hours: int = 2
#     preferred_days: List[int] = None
    
#     def __post_init__(self):
#         if self.connected_departments is None:
#             self.connected_departments = []
#         if self.preferred_days is None:
#             self.preferred_days = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPCourse from dictionary"""
#         # Convert string course_type to enum
#         if isinstance(data['course_type'], str):
#             # Handle case-insensitive matching and different naming conventions
#             course_type_str = data['course_type'].lower().strip()
#             if course_type_str == 'honors':
#                 data['course_type'] = CourseType.HONORS
#             elif course_type_str == 'minor':
#                 data['course_type'] = CourseType.MINOR
#             else:
#                 try:
#                     data['course_type'] = CourseType(course_type_str)
#                 except ValueError:
#                     # Fallback to core for unknown types
#                     print(f"Warning: Unknown course type '{data['course_type']}', defaulting to 'core'")
#                     data['course_type'] = CourseType.CORE
#         return cls(**data)

# @dataclass 
# class NEPFaculty:
#     """Faculty with NEP 2020 compliant parameters"""
#     id: str
#     name: str
#     department: str
#     designations: str
#     specializations: List[str]
#     courses_can_teach: List[str]
#     max_hours_per_day: int = 6
#     max_hours_per_week: int = 24
#     preferred_time: TimePreference = TimePreference.ANY
#     unavailable_slots: List[Tuple[int, int]] = None
#     research_slots: List[Tuple[int, int]] = None
#     is_visiting: bool = False
#     workload_preference: float = 1.0
    
#     def __post_init__(self):
#         if self.unavailable_slots is None:
#             self.unavailable_slots = []
#         if self.research_slots is None:
#             self.research_slots = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPFaculty from dictionary"""
#         # Rename 'designation' key from JSON to 'designations' for the dataclass
#         if 'designation' in data:
#             data['designations'] = data.pop('designation')
#         # Convert string preferred_time to enum
#         if isinstance(data.get('preferred_time'), str):
#             data['preferred_time'] = TimePreference(data['preferred_time'])
#         return cls(**data)

# @dataclass
# class NEPClassroom:
#     """Classroom with modern facilities"""
#     id: str
#     name: str
#     capacity: int
#     room_type: RoomType
#     department: str
#     equipment: List[str]
#     is_smart_room: bool = False
#     is_ac: bool = False
#     has_projector: bool = True
#     weekly_maintenance: List[Tuple[int, int]] = None
    
#     def __post_init__(self):
#         if self.weekly_maintenance is None:
#             self.weekly_maintenance = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPClassroom from dictionary"""
#         # Convert string room_type to enum
#         if isinstance(data['room_type'], str):
#             data['room_type'] = RoomType(data['room_type'])
#         return cls(**data)

# @dataclass
# class NEPStudentBatch:
#     """Student batch/class with NEP parameters"""
#     id: str
#     name: str
#     department: str
#     semester: int
#     student_count: int
#     core_courses: List[str]
#     elective_courses: List[str]
#     skill_courses: List[str]
#     multidisciplinary_courses: List[str]
#     preferred_morning_hours: bool = True
#     max_hours_per_day: int = 7
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPStudentBatch from dictionary"""
#         return cls(**data)

# @dataclass
# class UserPreferences:
#     """User-configurable preferences"""
#     working_days: int = 5
#     periods_per_day: int = 8
#     lunch_break_period: int = 4
#     max_consecutive_same_subject: int = 2
#     gap_penalty_weight: float = 10.0
#     faculty_preference_weight: float = 15.0
#     workload_balance_weight: float = 20.0
#     room_preference_weight: float = 5.0
#     interdisciplinary_bonus: float = 10.0
#     research_slot_protection: bool = True
#     allow_saturday_classes: bool = False
#     morning_start_time: str = "9:00"
#     evening_end_time: str = "5:00"

# class NEPTimetableGenerator:
#     """Enhanced timetable generator compliant with NEP 2020"""
    
#     def __init__(self, config_json: str = None, user_preferences: UserPreferences = None):
#         self.preferences = user_preferences or UserPreferences()
#         self.days = 6 if self.preferences.allow_saturday_classes else 5
#         self.periods_per_day = self.preferences.periods_per_day
        
#         # Data containers
#         self.courses = {}
#         self.teachers = {}
#         self.classrooms = {}
#         self.student_batches = {}
#         self.departments = set()
        
#         # Generate time slots and timeslots list
#         self.generate_time_slots()
#         self.timeslots = [f"Day{d}_Period{p}" for d in range(self.days) for p in range(self.periods_per_day)]
        
#         self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:self.days]
        
#         # Load configuration if provided
#         if config_json:
#             self.load_from_json(config_json)

#     def generate_time_slots(self):
#         """Generate time slots matching the actual timetable structure"""
#         # Based on your actual timetable screenshot
#         self.time_slots = [
#             "08:00-08:50",
#             "08:50-09:40",
#             "09:45-10:35",
#             "10:35-11:25",
#             "11:30-12:20",
#             "01:30-02:20",
#             "02:20-03:10",
#             "03:15-04:05",
#             "04:10-05:00"
#         ]
#         self.periods_per_day = len(self.time_slots)
#         self.preferences.lunch_break_period = 5 # Lunch is after 5th period
    
#     def get_course_duration_periods(self, course: NEPCourse) -> int:
#         """Calculate how many periods a course requires based on duration"""
#         if course.min_duration_minutes == 240: # 4-hour lab
#             return 4 # Labs take 4 consecutive periods
#         else: # Regular 50-minute classes
#             return 1

#     def load_from_json(self, config_json: str):
#         """Load configuration from JSON string"""
#         try:
#             data = json.loads(config_json)
#         except json.JSONDecodeError as e:
#             print(f"Error: Invalid JSON format provided. Details: {e}")
#             return

#         # Load Courses
#         for course_data in data.get("courses", []):
#             try:
#                 course_obj = NEPCourse.from_dict(course_data)
#                 self.add_course(course_obj)
#             except Exception as e:
#                 print(f"Error loading course {course_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Faculty
#         for faculty_data in data.get("faculty", []):
#             try:
#                 teacher_obj = NEPFaculty.from_dict(faculty_data)
#                 self.add_teacher(teacher_obj)
#             except Exception as e:
#                 print(f"Error loading faculty {faculty_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Classrooms
#         for classroom_data in data.get("classrooms", []):
#             try:
#                 classroom_obj = NEPClassroom.from_dict(classroom_data)
#                 self.add_classroom(classroom_obj)
#             except Exception as e:
#                 print(f"Error loading classroom {classroom_data.get('id', 'unknown')}: {e}")
#                 continue
            
#         # Load Student Batches
#         for batch_data in data.get("student_batches", []):
#             try:
#                 batch_obj = NEPStudentBatch.from_dict(batch_data)
#                 self.add_student_batch(batch_obj)
#             except Exception as e:
#                 print(f"Error loading batch {batch_data.get('id', 'unknown')}: {e}")
#                 continue

#         print("Configuration loaded successfully from JSON.")

#     def add_course(self, course: NEPCourse):
#         """Add course to system"""
#         self.courses[course.id] = course
#         self.departments.add(course.department)
    
#     def add_teacher(self, teacher: NEPFaculty):
#         """Add teacher to system"""
#         # Filter out slots that are outside the configured days/periods
#         if teacher.research_slots:
#             teacher.research_slots = [
#                 (day, period) for day, period in teacher.research_slots 
#                 if day < self.days and period < self.periods_per_day
#             ]
#         if teacher.unavailable_slots:
#             teacher.unavailable_slots = [
#                 (day, period) for day, period in teacher.unavailable_slots
#                 if day < self.days and period < self.periods_per_day
#             ]
        
#         self.teachers[teacher.id] = teacher
#         self.departments.add(teacher.department)
    
#     def add_classroom(self, classroom: NEPClassroom):
#         """Add classroom to system"""
#         if classroom.weekly_maintenance:
#             classroom.weekly_maintenance = [
#                 (day, period) for day, period in classroom.weekly_maintenance
#                 if day < self.days and period < self.periods_per_day
#             ]

#         self.classrooms[classroom.id] = classroom
#         self.departments.add(classroom.department)
    
#     def add_student_batch(self, batch: NEPStudentBatch):
#         """Add student batch to system"""
#         self.student_batches[batch.id] = batch
#         self.departments.add(batch.department)
    
#     def is_break_period(self, period: int) -> bool:
#         """Check if the given period is a designated break period"""
#         return period == self.preferences.lunch_break_period
    
#     def create_initial_timetable(self):
#         """
#         Creates an initial timetable that properly handles lab sessions
#         """
#         timetable = {}
        
#         # Initialize an empty schedule for each batch
#         for batch_id in self.student_batches:
#             timetable[batch_id] = np.full((self.days, self.periods_per_day), None, dtype=object)

#         # First assign all lab courses (they have higher priority due to longer duration)
#         for batch_id, batch in self.student_batches.items():
#             all_courses = (batch.core_courses + batch.elective_courses + 
#                           batch.skill_courses + batch.multidisciplinary_courses)
            
#             lab_courses = [course_id for course_id in all_courses 
#                           if course_id in self.courses and self.courses[course_id].requires_lab]
            
#             for course_id in lab_courses:
#                 course = self.courses[course_id]
#                 duration_periods = self.get_course_duration_periods(course)
                
#                 # Try to find a suitable time slot for the lab
#                 assigned = False
#                 for day in range(self.days):
#                     for start_period in range(self.periods_per_day - duration_periods + 1):
#                         # Check if all required periods are available
#                         if all(timetable[batch_id][day][start_period + i] is None 
#                               for i in range(duration_periods)):
                            
#                             # Find suitable lab room
#                             classroom_id = self.find_suitable_lab_room(course, day, start_period, timetable)
                            
#                             if classroom_id:
#                                 # Assign the lab to all required periods
#                                 for i in range(duration_periods):
#                                     timetable[batch_id][day][start_period + i] = {
#                                         'course_id': course_id,
#                                         'faculty_id': course.faculty_id,
#                                         'classroom_id': classroom_id,
#                                         'is_lab': True
#                                     }
#                                 assigned = True
#                                 break
#                     if assigned:
#                         break

#         # Then assign regular courses
#         for batch_id, batch in self.student_batches.items():
#             all_courses = (batch.core_courses + batch.elective_courses +
#                            batch.skill_courses + batch.multidisciplinary_courses)
            
#             regular_courses = [course_id for course_id in all_courses 
#                                if course_id in self.courses and not self.courses[course_id].requires_lab]
            
#             for course_id in regular_courses:
#                 course = self.courses[course_id]
#                 hours_to_schedule = course.hours_per_week
                
#                 for _ in range(hours_to_schedule):
#                     # Keep trying to find an empty slot
#                     attempts = 0
#                     while attempts < 100:
#                         day = random.randrange(self.days)
#                         period = random.randrange(self.periods_per_day)

#                         # Ensure slot is empty and not during lunch
#                         if (timetable[batch_id][day][period] is None and 
#                             period != self.preferences.lunch_break_period):
                            
#                             classroom_id = self.find_suitable_classroom(course, day, period, timetable)
                            
#                             if classroom_id:
#                                 timetable[batch_id][day][period] = {
#                                     'course_id': course_id,
#                                     'faculty_id': course.faculty_id,
#                                     'classroom_id': classroom_id,
#                                     'is_lab': False
#                                 }
#                                 break
#                         attempts += 1
        
#         return timetable
    
#     def get_course_priority_order(self, courses: List[str]) -> List[str]:
#         """Get NEP 2020 compliant course priority order"""
#         priority_order = []
        
#         # Group courses by type
#         by_type = defaultdict(list)
#         for course_id in courses:
#             if course_id in self.courses:
#                 course_type = self.courses[course_id].course_type
#                 by_type[course_type].append(course_id)
        
#         # NEP priority: Core -> Ability Enhancement -> Skill -> Multi -> Electives
#         type_priority = [
#             CourseType.CORE,
#             CourseType.ABILITY_ENHANCEMENT, 
#             CourseType.SKILL_ENHANCEMENT,
#             CourseType.MULTIDISCIPLINARY,
#             CourseType.ELECTIVE,
#             CourseType.VALUE_ADDED,
#             CourseType.SEMINAR,
#             CourseType.PROJECT,
#             CourseType.HONORS,
#             CourseType.MINOR
#         ]
        
#         for course_type in type_priority:
#             priority_order.extend(by_type[course_type])
        
#         return priority_order
    
#     def find_best_slot(self, course: NEPCourse, batch: NEPStudentBatch, schedule) -> Tuple[Optional[int], Optional[int]]:
#         """Find best time slot considering NEP guidelines"""
#         best_slots = []
        
#         for day in range(self.days):
#             for period in range(self.periods_per_day):
#                 if schedule[day][period] is None and period != self.preferences.lunch_break_period:
#                     score = self.calculate_slot_preference_score(course, batch, day, period, schedule)
#                     best_slots.append((score, day, period))
        
#         if not best_slots:
#             return None, None
        
#         best_slots.sort(reverse=True, key=lambda x: x[0])
#         top_candidates = [slot for slot in best_slots[:5] if slot[0] >= best_slots[0][0] * 0.8]
        
#         if top_candidates:
#             _, day, period = random.choice(top_candidates)
#             return day, period
        
#         return None, None
    
#     def calculate_slot_preference_score(self, course: NEPCourse, batch: NEPStudentBatch, 
#                                      day: int, period: int, schedule) -> float:
#         """Calculate preference score for a time slot"""
#         score = 100.0
        
#         # NEP guideline: Morning classes preferred for core subjects
#         if course.course_type == CourseType.CORE and period < 4:
#             score += 20.0
        
#         # Faculty time preferences
#         teacher = self.teachers[course.faculty_id]
#         if teacher.preferred_time == TimePreference.MORNING and period < 4:
#             score += 15.0
#         elif teacher.preferred_time == TimePreference.AFTERNOON and 4 < period < 7:
#             score += 15.0
        
#         # Avoid research slots
#         if (day, period) in teacher.research_slots:
#             score -= 50.0
        
#         # Course preferred days
#         if course.preferred_days and day in course.preferred_days:
#             score += 10.0
        
#         # Avoid too many consecutive hours
#         consecutive_penalty = self.calculate_consecutive_penalty(schedule, day, period)
#         score -= consecutive_penalty * 5.0
        
#         # Minimize gaps in schedule
#         gap_penalty = self.calculate_gap_penalty(schedule, day, period)
#         score -= gap_penalty * 3.0
        
#         return score
    
#     def calculate_consecutive_penalty(self, schedule, day: int, period: int) -> float:
#         """Calculate penalty for consecutive same subject hours"""
#         if period == 0:
#             return 0.0
        
#         consecutive_count = 1
#         prev_period = period - 1
        
#         while prev_period >= 0 and schedule[day][prev_period] is not None:
#             consecutive_count += 1
#             prev_period -= 1
        
#         return max(0, consecutive_count - self.preferences.max_consecutive_same_subject)
    
#     def calculate_gap_penalty(self, schedule, day: int, period: int) -> float:
#         """Calculate penalty for creating gaps in daily schedule"""
#         penalty = 0.0
        
#         # Check for gaps before this period
#         gaps_before = 0
#         for p in range(period):
#             if schedule[day][p] is None and not self.is_break_period(p):
#                 gaps_before += 1
        
#         # Penalize gaps in middle of schedule
#         if gaps_before > 0:
#             penalty += gaps_before * 2.0
        
#         return penalty
    
#     def find_suitable_classroom(self, course: NEPCourse, day: int, period: int, timetable: dict) -> Optional[str]:
#         """Find suitable classroom based on course requirements"""
#         suitable_rooms = []
        
#         for room_id, room in self.classrooms.items():
#             # Check capacity
#             if room.capacity < course.max_students:
#                 continue
            
#             # Check room type requirements
#             if course.requires_lab and room.room_type not in [RoomType.LAB, RoomType.COMPUTER_LAB]:
#                 continue
            
#             if course.requires_smart_room and not room.is_smart_room:
#                 continue
            
#             # Check availability
#             if self.is_room_available(room_id, day, period, timetable):
#                 pref_score = 0
#                 if room.department == course.department:
#                     pref_score += 10
#                 if course.course_type == CourseType.SEMINAR and room.room_type == RoomType.SEMINAR:
#                     pref_score += 15
                
#                 suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         return None
    
#     def find_suitable_lab_room(self, course: NEPCourse, day: int, start_period: int, timetable: dict) -> Optional[str]:
#         """Find suitable lab room for a lab course"""
#         suitable_rooms = []
#         duration_periods = self.get_course_duration_periods(course)
        
#         for room_id, room in self.classrooms.items():
#             # Check if it's a lab room
#             if room.room_type not in [RoomType.LAB, RoomType.COMPUTER_LAB]:
#                 continue
            
#             # Check capacity
#             if room.capacity < course.max_students:
#                 continue
            
#             # Check availability for all required periods
#             available = True
#             for i in range(duration_periods):
#                 period = start_period + i
#                 if not self.is_room_available(room_id, day, period, timetable):
#                     available = False
#                     break
            
#             if available:
#                 pref_score = 0
#                 if room.department == course.department:
#                     pref_score += 10
                
#                 suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         return None

#     def is_room_available(self, room_id: str, day: int, period: int, timetable: dict) -> bool:
#         """Check if room is available at given time"""
#         room = self.classrooms[room_id]
        
#         # Check maintenance slots
#         if (day, period) in room.weekly_maintenance:
#             return False
        
#         # Check if room is already occupied
#         for batch_id, schedule in timetable.items():
#             if schedule[day][period] is not None:
#                 if schedule[day][period]['classroom_id'] == room_id:
#                     return False
        
#         return True
    
#     def is_faculty_available(self, faculty_id: str, day: int, period: int, timetable: dict) -> bool:
#         """Check if faculty is available"""
#         teacher = self.teachers[faculty_id]
        
#         # Check unavailable slots
#         if (day, period) in teacher.unavailable_slots:
#             return False
        
#         # Check research slots
#         if self.preferences.research_slot_protection and (day, period) in teacher.research_slots:
#             return False
        
#         # Check if already assigned
#         for batch_id, schedule in timetable.items():
#             if schedule[day][period] is not None:
#                 if schedule[day][period]['faculty_id'] == faculty_id:
#                     return False
        
#         # Check daily hour limit
#         daily_hours = self.get_faculty_daily_hours(faculty_id, day, timetable)
#         if daily_hours >= teacher.max_hours_per_day:
#             return False
        
#         return True
    
#     def get_faculty_daily_hours(self, faculty_id: str, day: int, timetable: dict) -> int:
#         """Get current daily hours for faculty"""
#         hours = 0
#         for batch_id, schedule in timetable.items():
#             for period in range(self.periods_per_day):
#                 if schedule[day][period] is not None:
#                     if schedule[day][period]['faculty_id'] == faculty_id:
#                         hours += 1
#         return hours
    
#     def genetic_algorithm_evolution(self, population_size: int = 50, generations: int = 100) -> dict:
#         """Main genetic algorithm with NEP-specific optimizations"""
#         print(f"Initializing NEP-compliant timetable generation...")
#         print(f"Population: {population_size}, Generations: {generations}")
        
#         # Initialize population
#         population = []
#         for _ in range(population_size):
#             individual = self.create_initial_timetable()
#             population.append(individual)
        
#         best_fitness = 0
#         best_timetable = None
        
#         for gen in range(generations):
#             # Calculate fitness
#             fitness_scores = []
#             for individual in population:
#                 fitness = self.calculate_nep_fitness(individual)
#                 fitness_scores.append(fitness)
            
#             # Track best solution
#             max_fitness = max(fitness_scores)
#             if max_fitness > best_fitness:
#                 best_fitness = max_fitness
#                 best_timetable = copy.deepcopy(population[fitness_scores.index(max_fitness)])
#                 print(f"Generation {gen}: New best fitness = {best_fitness:.2f}")
            
#             # Early termination if perfect solution found
#             if best_fitness >= 950: # Near perfect solution
#                 break
            
#             # Selection - Tournament selection with elitism
#             new_population = []
            
#             # Keep best 10% (elitism)
#             elite_count = max(1, population_size // 10)
#             elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elite_count]
#             for i in elite_indices:
#                 new_population.append(copy.deepcopy(population[i]))
            
#             # Tournament selection for remaining
#             while len(new_population) < population_size:
#                 tournament_size = 5
#                 tournament_indices = random.sample(range(population_size), min(tournament_size, population_size))
#                 tournament_fitness = [fitness_scores[i] for i in tournament_indices]
#                 winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
#                 new_population.append(copy.deepcopy(population[winner_idx]))
            
#             # Crossover and Mutation
#             next_population = new_population[:elite_count]
            
#             for i in range(elite_count, population_size, 2):
#                 if i + 1 < population_size:
#                     parent1 = new_population[i]
#                     parent2 = new_population[i + 1]
                    
#                     if random.random() < 0.8: # Crossover probability
#                         child1, child2 = self.nep_crossover(parent1, parent2)
#                     else:
#                         child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                    
#                     # Mutation
#                     child1 = self.nep_mutation(child1, mutation_rate=0.1)
#                     child2 = self.nep_mutation(child2, mutation_rate=0.1)
                    
#                     next_population.extend([child1, child2])
#                 else:
#                     next_population.append(copy.deepcopy(new_population[i]))
            
#             population = next_population[:population_size]
        
#         print(f"Evolution complete. Final best fitness: {best_fitness:.2f}")
#         return best_timetable

#     def calculate_nep_fitness(self, timetable: dict) -> float:
#         """Calculate fitness score with lab-specific constraints"""
#         base_score = 1000.0
#         penalty = 0.0
        
#         # Hard constraint violations
#         penalty += self.check_faculty_conflicts(timetable) * 100
#         penalty += self.check_classroom_conflicts(timetable) * 100
#         penalty += self.check_lab_room_conflicts(timetable) * 150 # Higher penalty for lab conflicts
#         penalty += self.check_workload_violations(timetable) * 80
#         penalty += self.check_course_hour_requirements(timetable) * 60
        
#         # Soft constraints
#         penalty += self.check_faculty_preferences(timetable) * self.preferences.faculty_preference_weight
#         penalty += self.check_schedule_gaps(timetable) * self.preferences.gap_penalty_weight
#         penalty += self.check_workload_balance(timetable) * self.preferences.workload_balance_weight
#         penalty += self.check_consecutive_violations(timetable) * 15
#         penalty += self.check_lunch_violations(timetable) * 25
        
#         # Bonuses
#         bonus = 0.0
#         bonus += self.calculate_interdisciplinary_bonus(timetable)
#         bonus += self.calculate_skill_course_bonus(timetable)
#         bonus += self.calculate_research_protection_bonus(timetable)
        
#         return max(0, base_score - penalty + bonus)
    
#     def check_faculty_conflicts(self, timetable: dict) -> int:
#         """Check for faculty double-booking, considering lab durations"""
#         conflicts = 0
#         faculty_schedule = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         faculty_id = slot['faculty_id']
#                         # Store both period and course info to detect lab conflicts
#                         faculty_schedule[faculty_id][day].append((period, slot['course_id']))
        
#         for faculty_id, days in faculty_schedule.items():
#             for day, period_courses in days.items():
#                 # Sort by period and check for overlaps
#                 period_courses.sort(key=lambda x: x[0])
#                 for i in range(len(period_courses) - 1):
#                     period1, course_id1 = period_courses[i]
#                     period2, course_id2 = period_courses[i + 1]
                    
#                     # Get course durations
#                     course1 = self.courses[course_id1]
#                     course2 = self.courses[course_id2]
#                     duration1 = self.get_course_duration_periods(course1)
                    
#                     # Check if periods overlap
#                     if period1 + duration1 > period2:
#                         conflicts += 1
        
#         return conflicts
    
#     def check_classroom_conflicts(self, timetable: dict) -> int:
#         """Check for classroom double-booking"""
#         conflicts = 0
#         room_schedule = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         room_id = slot['classroom_id']
#                         room_schedule[room_id][day].append(period)
        
#         for room_id, days in room_schedule.items():
#             for day, periods in days.items():
#                 duplicates = len(periods) - len(set(periods))
#                 conflicts += duplicates
        
#         return conflicts
    
#     def check_lab_room_conflicts(self, timetable: dict) -> int:
#         """Check for lab room conflicts considering lab durations"""
#         conflicts = 0
#         lab_room_schedule = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot and 'is_lab' in slot and slot['is_lab']:
#                         room_id = slot['classroom_id']
#                         lab_room_schedule[room_id][day].append((period, slot['course_id']))
        
#         for room_id, days in lab_room_schedule.items():
#             for day, period_courses in days.items():
#                 # Sort by period and check for overlaps
#                 period_courses.sort(key=lambda x: x[0])
#                 for i in range(len(period_courses) - 1):
#                     period1, course_id1 = period_courses[i]
#                     period2, course_id2 = period_courses[i + 1]
                    
#                     # Get course durations
#                     course1 = self.courses[course_id1]
#                     duration1 = self.get_course_duration_periods(course1)
                    
#                     # Check if periods overlap
#                     if period1 + duration1 > period2:
#                         conflicts += 1
        
#         return conflicts

#     def check_workload_violations(self, timetable: dict) -> int:
#         """Check NEP workload guideline violations"""
#         violations = 0
        
#         for faculty_id, faculty in self.teachers.items():
#             weekly_hours = 0
            
#             for batch_id, schedule in timetable.items():
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = schedule[day][period]
#                         if slot and slot['faculty_id'] == faculty_id:
#                             weekly_hours += 1
            
#             if weekly_hours > faculty.max_hours_per_week:
#                 violations += weekly_hours - faculty.max_hours_per_week
            
#             for day in range(self.days):
#                 daily_hours = self.get_faculty_daily_hours(faculty_id, day, timetable)
#                 if daily_hours > faculty.max_hours_per_day:
#                     violations += daily_hours - faculty.max_hours_per_day
        
#         return violations
    
#     def check_course_hour_requirements(self, timetable: dict) -> int:
#         """Check if courses have required weekly hours"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             batch = self.student_batches[batch_id]
#             course_hours = defaultdict(int)
            
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course_hours[slot['course_id']] += 1
            
#             all_courses = (batch.core_courses + batch.elective_courses + 
#                            batch.skill_courses + batch.multidisciplinary_courses)
            
#             for course_id in all_courses:
#                 if course_id in self.courses:
#                     required = self.courses[course_id].hours_per_week
#                     actual = course_hours[course_id]
#                     violations += abs(required - actual)
        
#         return violations
    
#     def check_faculty_preferences(self, timetable: dict) -> int:
#         """Check faculty time preference violations"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         teacher = self.teachers[slot['faculty_id']]
                        
#                         if teacher.preferred_time == TimePreference.MORNING and period >= 4:
#                             violations += 1
#                         elif teacher.preferred_time == TimePreference.AFTERNOON and period < 4:
#                             violations += 1
        
#         return violations
    
#     def check_schedule_gaps(self, timetable: dict) -> int:
#         """Check for gaps in daily schedules"""
#         gaps = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 day_periods = []
#                 for period in range(self.periods_per_day):
#                     if schedule[day][period] is not None:
#                         day_periods.append(period)
                
#                 if len(day_periods) > 1:
#                     first_class = min(day_periods)
#                     last_class = max(day_periods)
                    
#                     for period in range(first_class + 1, last_class):
#                         if period != self.preferences.lunch_break_period and schedule[day][period] is None:
#                             gaps += 1
        
#         return gaps
    
#     def check_workload_balance(self, timetable: dict) -> float:
#         """Check workload balance across faculty"""
#         faculty_loads = defaultdict(int)
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         faculty_loads[slot['faculty_id']] += 1
        
#         if not faculty_loads:
#             return 0.0
        
#         loads = list(faculty_loads.values())
#         avg_load = sum(loads) / len(loads)
#         variance = sum((load - avg_load) ** 2 for load in loads) / len(loads)
        
#         return variance
    
#     def check_consecutive_violations(self, timetable: dict) -> int:
#         """Check for too many consecutive hours violations"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 consecutive_count = 0
#                 prev_subject = None
                
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     current_subject = slot['course_id'] if slot else None
                    
#                     if current_subject == prev_subject and current_subject is not None:
#                         consecutive_count += 1
#                         if consecutive_count > self.preferences.max_consecutive_same_subject:
#                             violations += 1
#                     else:
#                         consecutive_count = 1 if current_subject else 0
                    
#                     prev_subject = current_subject
        
#         return violations
    
#     def check_lunch_violations(self, timetable: dict) -> int:
#         """Check lunch break violations"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 if schedule[day][self.preferences.lunch_break_period] is not None:
#                     violations += 1
        
#         return violations
    
#     def calculate_interdisciplinary_bonus(self, timetable: dict) -> float:
#         """Calculate bonus for interdisciplinary courses"""
#         bonus = 0.0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         if course.is_interdisciplinary or course.course_type == CourseType.MULTIDISCIPLINARY:
#                             bonus += self.preferences.interdisciplinary_bonus
        
#         return bonus
    
#     def calculate_skill_course_bonus(self, timetable: dict) -> float:
#         """Calculate bonus for skill enhancement courses"""
#         bonus = 0.0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         if course.course_type in [CourseType.SKILL_ENHANCEMENT, CourseType.ABILITY_ENHANCEMENT]:
#                             bonus += 5.0
        
#         return bonus
    
#     def calculate_research_protection_bonus(self, timetable: dict) -> float:
#         """Calculate bonus for protecting faculty research time"""
#         bonus = 0.0
        
#         if not self.preferences.research_slot_protection:
#             return bonus
        
#         for faculty_id, teacher in self.teachers.items():
#             research_slots_protected = 0
            
#             for day, period in teacher.research_slots:
#                 if day < self.days:
#                     slot_free = True
#                     for batch_id, schedule in timetable.items():
#                         if schedule[day][period] is not None:
#                             if schedule[day][period]['faculty_id'] == faculty_id:
#                                 slot_free = False
#                                 break
                    
#                     if slot_free:
#                         research_slots_protected += 1
            
#             bonus += research_slots_protected * 5.0
        
#         return bonus
    
#     def nep_crossover(self, parent1: dict, parent2: dict) -> Tuple[dict, dict]:
#         """Perform crossover between two parent timetables"""
#         child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
        
#         if not self.student_batches:
#             return child1, child2
            
#         batch_id_to_cross = random.choice(list(self.student_batches.keys()))
#         day_to_swap = random.randrange(self.days)
        
#         if batch_id_to_cross in child1 and batch_id_to_cross in child2:
#             child1[batch_id_to_cross][day_to_swap] = parent2[batch_id_to_cross][day_to_swap].copy()
#             child2[batch_id_to_cross][day_to_swap] = parent1[batch_id_to_cross][day_to_swap].copy()

#         return child1, child2
    
#     def nep_mutation(self, timetable: dict, mutation_rate: float = 0.1) -> dict:
#         """Perform mutation on a timetable"""
#         mutated = copy.deepcopy(timetable)
        
#         if random.random() < mutation_rate:
#             if not self.student_batches:
#                 return mutated
                
#             batch_id_to_mutate = random.choice(list(self.student_batches.keys()))
            
#             if batch_id_to_mutate in mutated and self.days >= 2:
#                 schedule = mutated[batch_id_to_mutate]
#                 day1, day2 = random.sample(range(self.days), 2)
                
#                 # Swap entire days
#                 temp = schedule[day1].copy()
#                 schedule[day1] = schedule[day2].copy()
#                 schedule[day2] = temp

#         return mutated
    
#     def export_nep_timetable(self, timetable: dict, filename: str = "nep_timetable.json") -> dict:
#         """Export NEP-compliant timetable with detailed metadata"""
#         export_data = {
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "nep_2020_compliant": True,
#                 "total_batches": len(self.student_batches),
#                 "total_faculty": len(self.teachers),
#                 "total_courses": len(self.courses),
#                 "working_days": self.days,
#                 "periods_per_day": self.periods_per_day,
#                 "user_preferences": asdict(self.preferences)
#             },
#             "departments": list(self.departments),
#             "timetables": {},
#             "faculty_schedules": {},
#             "classroom_utilization": {},
#             "course_distribution": {},
#             "analytics": {}
#         }
        
#         # Export batch timetables
#         for batch_id, schedule in timetable.items():
#             batch = self.student_batches[batch_id]
#             batch_data = {
#                 "batch_info": {
#                     "name": batch.name,
#                     "department": batch.department,
#                     "semester": batch.semester,
#                     "student_count": batch.student_count
#                 },
#                 "weekly_schedule": []
#             }
            
#             for day in range(self.days):
#                 day_schedule = {
#                     "day": self.day_names[day],
#                     "periods": []
#                 }
                
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         teacher = self.teachers[slot['faculty_id']]
#                         classroom = self.classrooms[slot['classroom_id']]
                        
#                         period_data = {
#                             "time": self.time_slots[period],
#                             "course": {
#                                 "id": course.id,
#                                 "name": course.name,
#                                 "code": course.code,
#                                 "type": course.course_type.value,
#                                 "credits": course.credits,
#                                 "department": course.department
#                             },
#                             "faculty": {
#                                 "id": teacher.id,
#                                 "name": teacher.name,
#                                 "designation": teacher.designations # Corrected from `teacher.designation`
#                             },
#                             "classroom": {
#                                 "id": classroom.id,
#                                 "name": classroom.name,
#                                 "type": classroom.room_type.value,
#                                 "capacity": classroom.capacity
#                             }
#                         }
#                     else:
#                         if period == self.preferences.lunch_break_period:
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "lunch_break"
#                             }
#                         else:
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "free"
#                             }
                    
#                     day_schedule["periods"].append(period_data)
                
#                 batch_data["weekly_schedule"].append(day_schedule)
            
#             export_data["timetables"][batch.name] = batch_data
        
#         # Generate faculty schedules
#         for faculty_id, teacher in self.teachers.items():
#             faculty_schedule = {
#                 "faculty_info": {
#                     "name": teacher.name,
#                     "department": teacher.department,
#                     "designation": teacher.designations # Corrected from `teacher.designation`
#                 },
#                 "weekly_load": 0,
#                 "schedule": []
#             }
            
#             weekly_hours = 0
            
#             for day in range(self.days):
#                 day_schedule = {
#                     "day": self.day_names[day],
#                     "periods": []
#                 }
                
#                 for period in range(self.periods_per_day):
#                     period_info = {"time": self.time_slots[period], "status": "free"}
                    
#                     # Check if faculty is teaching
#                     for batch_id, schedule in timetable.items():
#                         slot = schedule[day][period]
#                         if slot and slot['faculty_id'] == faculty_id:
#                             course = self.courses[slot['course_id']]
#                             batch = self.student_batches[batch_id]
                            
#                             period_info = {
#                                 "time": self.time_slots[period],
#                                 "status": "teaching",
#                                 "course": course.name,
#                                 "batch": batch.name,
#                                 "classroom": self.classrooms[slot['classroom_id']].name
#                             }
#                             weekly_hours += 1
#                             break
                    
#                     # Check research slots
#                     if (day, period) in teacher.research_slots:
#                         period_info["status"] = "research"
                    
#                     day_schedule["periods"].append(period_info)
                
#                 faculty_schedule["schedule"].append(day_schedule)
            
#             faculty_schedule["weekly_load"] = weekly_hours
#             export_data["faculty_schedules"][teacher.name] = faculty_schedule
        
#         # Calculate analytics
#         export_data["analytics"] = self.calculate_timetable_analytics(timetable)
        
#         # Save to file
#         with open(filename, 'w') as f:
#             json.dump(export_data, f, indent=2, default=str)
        
#         print(f"NEP-compliant timetable exported to {filename}")
#         return export_data
    
#     def calculate_timetable_analytics(self, timetable: dict) -> dict:
#         """Calculate comprehensive timetable analytics"""
#         analytics = {
#             "fitness_score": self.calculate_nep_fitness(timetable),
#             "constraint_violations": {
#                 "faculty_conflicts": self.check_faculty_conflicts(timetable),
#                 "classroom_conflicts": self.check_classroom_conflicts(timetable),
#                 "lab_room_conflicts": self.check_lab_room_conflicts(timetable),
#                 "workload_violations": self.check_workload_violations(timetable),
#                 "lunch_violations": self.check_lunch_violations(timetable)
#             },
#             "faculty_utilization": {},
#             "classroom_utilization": {},
#             "course_type_distribution": defaultdict(int),
#             "department_load_balance": defaultdict(int)
#         }
        
#         # Faculty utilization
#         for faculty_id, teacher in self.teachers.items():
#             weekly_hours = 0
#             for batch_id, schedule in timetable.items():
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = schedule[day][period]
#                         if slot and slot['faculty_id'] == faculty_id:
#                             weekly_hours += 1
            
#             utilization_percentage = (weekly_hours / teacher.max_hours_per_week) * 100
#             analytics["faculty_utilization"][teacher.name] = {
#                 "weekly_hours": weekly_hours,
#                 "max_hours": teacher.max_hours_per_week,
#                 "utilization_percentage": round(utilization_percentage, 2)
#             }
        
#         # Classroom utilization
#         total_slots = self.days * self.periods_per_day
#         for room_id, room in self.classrooms.items():
#             used_slots = 0
#             for batch_id, schedule in timetable.items():
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = schedule[day][period]
#                         if slot and slot['classroom_id'] == room_id:
#                             used_slots += 1
            
#             utilization_percentage = (used_slots / total_slots) * 100
#             analytics["classroom_utilization"][room.name] = {
#                 "used_slots": used_slots,
#                 "total_slots": total_slots,
#                 "utilization_percentage": round(utilization_percentage, 2)
#             }
        
#         # Course type distribution
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         analytics["course_type_distribution"][course.course_type.value] += 1
        
#         return analytics
    
#     def print_nep_timetable_summary(self, timetable: dict):
#         """Print NEP-compliant timetable summary"""
#         print("\n" + "="*80)
#         print("NEP 2020 COMPLIANT TIMETABLE GENERATION SUMMARY")
#         print("="*80)
        
#         analytics = self.calculate_timetable_analytics(timetable)
        
#         print(f"\nOVERALL METRICS:")
#         print(f"    Fitness Score: {analytics['fitness_score']:.2f}/1000")
#         print(f"    Departments: {len(self.departments)}")
#         print(f"    Student Batches: {len(self.student_batches)}")
#         print(f"    Total Courses: {len(self.courses)}")
#         print(f"    Faculty Members: {len(self.teachers)}")
#         print(f"    Classrooms: {len(self.classrooms)}")
        
#         print(f"\nCONSTRAINT VIOLATIONS:")
#         violations = analytics['constraint_violations']
#         print(f"    Faculty Conflicts: {violations['faculty_conflicts']}")
#         print(f"    Classroom Conflicts: {violations['classroom_conflicts']}")
#         print(f"    Lab Room Conflicts: {violations['lab_room_conflicts']}")
#         print(f"    Workload Violations: {violations['workload_violations']}")
#         print(f"    Lunch Break Violations: {violations['lunch_violations']}")
        
#         print(f"\nCOURSE TYPE DISTRIBUTION (NEP 2020):")
#         for course_type, count in analytics['course_type_distribution'].items():
#             print(f"    {course_type.replace('_', ' ').title()}: {count} slots")
        
#         print(f"\nTOP FACULTY UTILIZATION:")
#         faculty_util = analytics['faculty_utilization']
#         sorted_faculty = sorted(faculty_util.items(), key=lambda x: x[1]['utilization_percentage'], reverse=True)
#         for name, util in sorted_faculty[:5]:
#             print(f"    {name}: {util['weekly_hours']}/{util['max_hours']} hrs ({util['utilization_percentage']}%)")
        
#         print(f"\nTOP CLASSROOM UTILIZATION:")
#         room_util = analytics['classroom_utilization']
#         sorted_rooms = sorted(room_util.items(), key=lambda x: x[1]['utilization_percentage'], reverse=True)
#         for name, util in sorted_rooms[:5]:
#             print(f"    {name}: {util['used_slots']}/{util['total_slots']} slots ({util['utilization_percentage']}%)")


# # Web API Integration Functions
# def create_nep_system_from_json(json_input: str, user_preferences: dict = None) -> NEPTimetableGenerator:
#     """Create NEP system from JSON input"""
#     prefs = UserPreferences()
#     if user_preferences:
#         for key, value in user_preferences.items():
#             if hasattr(prefs, key):
#                 setattr(prefs, key, value)
    
#     generator = NEPTimetableGenerator(user_preferences=prefs)
#     generator.load_from_json(json_input)
    
#     return generator

# def generate_timetable_api(json_input: str, user_preferences: dict = None, 
#                            population_size: int = 50, generations: int = 100) -> dict:
#     """Main API function for web integration"""
#     print("Starting NEP 2020 Compliant Timetable Generation...")
    
#     # Create system
#     generator = create_nep_system_from_json(json_input, user_preferences)
    
#     # Generate timetable
#     best_timetable = generator.genetic_algorithm_evolution(population_size, generations)
    
#     if best_timetable:
#         # Export and return result
#         result = generator.export_nep_timetable(best_timetable)
#         generator.print_nep_timetable_summary(best_timetable)
#         return result
#     else:
#         raise Exception("Failed to generate valid timetable. Please check constraints.")

# # Sample data for testing
# def create_sample_nep_data() -> dict:
#     """Create sample NEP 2020 compliant data for testing"""
#     return {
#         "courses": [
#             {
#                 "id": "CS101", "name": "Programming Fundamentals", "code": "CS101",
#                 "credits": 4, "course_type": "core", "hours_per_week": 4,
#                 "department": "Computer Science", "semester": 1, "faculty_id": "F001",
#                 "requires_lab": True, "requires_smart_room": False,
#                 "is_interdisciplinary": False, "max_students": 60,
#                 "min_duration_minutes": 240,
#                 "preferred_days": [0, 2, 4]
#             },
#             {
#                 "id": "MATH101", "name": "Calculus I", "code": "MATH101",
#                 "credits": 4, "course_type": "core", "hours_per_week": 4,
#                 "department": "Mathematics", "semester": 1, "faculty_id": "F002",
#                 "requires_lab": False, "max_students": 80
#             },
#             {
#                 "id": "ENG101", "name": "Communication Skills", "code": "ENG101",
#                 "credits": 3, "course_type": "ability_enhancement", "hours_per_week": 3,
#                 "department": "English", "semester": 1, "faculty_id": "F003",
#                 "requires_smart_room": True, "max_students": 50
#             },
#             {
#                 "id": "ENV101", "name": "Environmental Science", "code": "ENV101",
#                 "credits": 2, "course_type": "multidisciplinary", "hours_per_week": 2,
#                 "department": "Environmental Science", "semester": 1, "faculty_id": "F004",
#                 "is_interdisciplinary": True, "connected_departments": ["Biology", "Chemistry"]
#             }
#         ],
#         "faculty": [
#             {
#                 "id": "F001", "name": "Dr. Rajesh Kumar", "department": "Computer Science",
#                 "designation": "Professor", "specializations": ["Programming", "Software Engineering"],
#                 "courses_can_teach": ["CS101"], "max_hours_per_day": 6, "max_hours_per_week": 20,
#                 "preferred_time": "morning", "research_slots": [[1, 6], [3, 7]]
#             },
#             {
#                 "id": "F002", "name": "Dr. Priya Sharma", "department": "Mathematics",
#                 "designation": "Associate Professor", "specializations": ["Calculus", "Linear Algebra"],
#                 "courses_can_teach": ["MATH101"], "preferred_time": "morning"
#             },
#             {
#                 "id": "F003", "name": "Prof. Anita Singh", "department": "English",
#                 "designation": "Assistant Professor", "specializations": ["Communication", "Literature"],
#                 "courses_can_teach": ["ENG101"], "preferred_time": "afternoon"
#             },
#             {
#                 "id": "F004", "name": "Dr. Kiran Patel", "department": "Environmental Science",
#                 "designation": "Professor", "specializations": ["Ecology", "Climate Change"],
#                 "courses_can_teach": ["ENV101"], "is_visiting": False
#             }
#         ],
#         "classrooms": [
#             {
#                 "id": "R101", "name": "Lecture Hall 1", "capacity": 80,
#                 "room_type": "lecture", "department": "General", "equipment": ["projector", "whiteboard"],
#                 "is_smart_room": True, "is_ac": True
#             },
#             {
#                 "id": "R201", "name": "Computer Lab 1", "capacity": 40,
#                 "room_type": "computer_lab", "department": "Computer Science",
#                 "equipment": ["computers", 'projector'], "is_ac": True
#             },
#             {
#                 "id": "R301", "name": "Seminar Hall", "capacity": 50,
#                 "room_type": "seminar", "department": "General",
#                 "equipment": ["smart_board", "audio_system"], "is_smart_room": True
#             }
#         ],
#         "student_batches": [
#             {
#                 "id": "CS1A", "name": "CS First Year Section A", "department": "Computer Science",
#                 "semester": 1, "student_count": 55,
#                 "core_courses": ["CS101", "MATH101"],
#                 "elective_courses": [],
#                 "skill_courses": [],
#                 "multidisciplinary_courses": ["ENV101"],
#                 "preferred_morning_hours": True
#             },
#             {
#                 "id": "CS1B", "name": "CS First Year Section B", "department": "Computer Science",
#                 "semester": 1, "student_count": 50,
#                 "core_courses": ["CS101", "MATH101"],
#                 "elective_courses": [],
#                 "skill_courses": [],
#                 "multidisciplinary_courses": ["ENV101"]
#             }
#         ]
#     }

# # Main execution for testing
# if __name__ == "__main__":
#     sample_data = create_sample_nep_data()
    
#     user_prefs = {
#         "working_days": 5,
#         "periods_per_day": 8,
#         "lunch_break_period": 4,
#         "faculty_preference_weight": 20.0,
#         "interdisciplinary_bonus": 15.0,
#         "research_slot_protection": True
#     }
    
#     try:
#         result = generate_timetable_api(
#             json.dumps(sample_data), 
#             user_prefs, 
#             population_size=30, 
#             generations=100
#         )
        
#         print(f"\nTimetable generated successfully! 🎉")
#         print(f"Exported to: nep_timetable.json")
        
#     except Exception as e:
#         print(f"Error: {e}")



# import json
# import numpy as np
# import pandas as pd
# from datetime import datetime, timedelta
# import random
# from dataclasses import dataclass, asdict
# from typing import List, Dict, Tuple, Optional, Union
# from collections import defaultdict
# from enum import Enum
# import copy
# import math

# class CourseType(Enum):
#     CORE = "core"
#     ELECTIVE = "elective" 
#     MULTIDISCIPLINARY = "multidisciplinary"
#     SKILL_ENHANCEMENT = "skill_enhancement"
#     VALUE_ADDED = "value_added"
#     ABILITY_ENHANCEMENT = "ability_enhancement"
#     SEMINAR = "seminar"
#     PROJECT = "project"
#     HONORS = "honors"
#     MINOR = "minor"

# class RoomType(Enum):
#     LECTURE = "lecture"
#     LAB = "lab"
#     SEMINAR = "seminar"
#     COMPUTER_LAB = "computer_lab"
#     SMART_CLASSROOM = "smart_classroom"
#     AUDITORIUM = "auditorium"

# class TimePreference(Enum):
#     MORNING = "morning"
#     AFTERNOON = "afternoon"
#     EVENING = "evening"
#     ANY = "any"

# @dataclass
# class NEPCourse:
#     """Enhanced course structure following NEP 2020 guidelines"""
#     id: str
#     name: str
#     code: str
#     credits: int
#     course_type: CourseType
#     hours_per_week: int
#     department: str
#     semester: int
#     faculty_id: str
#     requires_lab: bool = False
#     requires_smart_room: bool = False
#     is_interdisciplinary: bool = False
#     connected_departments: List[str] = None
#     max_students: int = 60
#     min_duration_minutes: int = 50
#     max_consecutive_hours: int = 2
#     preferred_days: List[int] = None
    
#     def __post_init__(self):
#         if self.connected_departments is None:
#             self.connected_departments = []
#         if self.preferred_days is None:
#             self.preferred_days = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPCourse from dictionary"""
#         # Convert string course_type to enum
#         if isinstance(data['course_type'], str):
#             # Handle case-insensitive matching and different naming conventions
#             course_type_str = data['course_type'].lower().strip()
#             if course_type_str == 'honors':
#                 data['course_type'] = CourseType.HONORS
#             elif course_type_str == 'minor':
#                 data['course_type'] = CourseType.MINOR
#             else:
#                 try:
#                     data['course_type'] = CourseType(course_type_str)
#                 except ValueError:
#                     # Fallback to core for unknown types
#                     print(f"Warning: Unknown course type '{data['course_type']}', defaulting to 'core'")
#                     data['course_type'] = CourseType.CORE
#         return cls(**data)

# @dataclass 
# class NEPFaculty:
#     """Faculty with NEP 2020 compliant parameters"""
#     id: str
#     name: str
#     department: str
#     designations: str
#     specializations: List[str]
#     courses_can_teach: List[str]
#     max_hours_per_day: int = 6
#     max_hours_per_week: int = 24
#     preferred_time: TimePreference = TimePreference.ANY
#     unavailable_slots: List[Tuple[int, int]] = None
#     research_slots: List[Tuple[int, int]] = None
#     is_visiting: bool = False
#     workload_preference: float = 1.0
    
#     def __post_init__(self):
#         if self.unavailable_slots is None:
#             self.unavailable_slots = []
#         if self.research_slots is None:
#             self.research_slots = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPFaculty from dictionary"""
#         # Rename 'designation' key from JSON to 'designations' for the dataclass
#         if 'designation' in data:
#             data['designations'] = data.pop('designation')
#         # Convert string preferred_time to enum
#         if isinstance(data.get('preferred_time'), str):
#             data['preferred_time'] = TimePreference(data['preferred_time'])
#         return cls(**data)

# @dataclass
# class NEPClassroom:
#     """Classroom with modern facilities"""
#     id: str
#     name: str
#     capacity: int
#     room_type: RoomType
#     department: str
#     equipment: List[str]
#     is_smart_room: bool = False
#     is_ac: bool = False
#     has_projector: bool = True
#     weekly_maintenance: List[Tuple[int, int]] = None
    
#     def __post_init__(self):
#         if self.weekly_maintenance is None:
#             self.weekly_maintenance = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPClassroom from dictionary"""
#         # Convert string room_type to enum
#         if isinstance(data['room_type'], str):
#             data['room_type'] = RoomType(data['room_type'])
#         return cls(**data)

# @dataclass
# class NEPStudentBatch:
#     """Student batch/class with NEP parameters"""
#     id: str
#     name: str
#     department: str
#     semester: int
#     student_count: int
#     core_courses: List[str]
#     elective_courses: List[str]
#     skill_courses: List[str]
#     multidisciplinary_courses: List[str]
#     preferred_morning_hours: bool = True
#     max_hours_per_day: int = 7
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPStudentBatch from dictionary"""
#         return cls(**data)

# @dataclass
# class UserPreferences:
#     """User-configurable preferences"""
#     working_days: int = 5
#     periods_per_day: int = 8
#     lunch_break_start: int = 4  # Period where lunch starts (0-based index)
#     lunch_break_end: int = 5    # Period where lunch ends (0-based index)
#     max_consecutive_same_subject: int = 2
#     gap_penalty_weight: float = 10.0
#     faculty_preference_weight: float = 15.0
#     workload_balance_weight: float = 20.0
#     room_preference_weight: float = 5.0
#     interdisciplinary_bonus: float = 10.0
#     research_slot_protection: bool = True
#     allow_saturday_classes: bool = False
#     morning_start_time: str = "9:00"
#     evening_end_time: str = "4:30"

# class NEPTimetableGenerator:
#     """Enhanced timetable generator compliant with NEP 2020"""
    
#     def __init__(self, config_json: str = None, user_preferences: UserPreferences = None):
#         self.preferences = user_preferences or UserPreferences()
#         self.days = 6 if self.preferences.allow_saturday_classes else 5
#         self.periods_per_day = self.preferences.periods_per_day
        
#         # Data containers
#         self.courses = {}
#         self.teachers = {}
#         self.classrooms = {}
#         self.student_batches = {}
#         self.departments = set()
        
#         # Generate time slots and timeslots list
#         self.generate_time_slots()
#         self.timeslots = [f"Day{d}_Period{p}" for d in range(self.days) for p in range(self.periods_per_day)]
        
#         self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:self.days]
        
#         # Load configuration if provided
#         if config_json:
#             self.load_from_json(config_json)

#     def generate_time_slots(self):
#         """Generate time slots matching college schedule (9:00 AM to 4:30 PM)"""
#         # College schedule: 9:00-4:30 with lunch 12:00-1:30
#         self.time_slots = [
#             "09:00-10:30",  # 0 - Morning session 1
#             "10:30-12:00",  # 1 - Morning session 2
#             "12:00-01:30",  # 2 - LUNCH BREAK
#             "01:30-03:00",  # 3 - Afternoon session 1  
#             "03:00-04:30",  # 4 - Afternoon session 2
#         ]
        
#         # Update periods per day to match actual schedule
#         self.periods_per_day = len(self.time_slots)
#         self.preferences.lunch_break_start = 2  # Lunch is period 2 (12:00-1:30)
#         self.preferences.lunch_break_end = 2
        
#         print(f"Generated {self.periods_per_day} time slots for college schedule 9:00-4:30")
    
#     def get_course_duration_periods(self, course: NEPCourse) -> int:
#         """Calculate how many periods a course requires based on duration"""
#         if course.requires_lab or course.min_duration_minutes >= 180:  # 3-hour labs
#             return 2  # Lab takes 2 consecutive 1.5-hour periods (3 hours total)
#         else:  # Regular classes
#             return 1  # Regular class takes 1 period (1.5 hours)

#     def is_lunch_period(self, period: int) -> bool:
#         """Check if the given period is lunch break"""
#         return period == self.preferences.lunch_break_start

#     def load_from_json(self, config_json: str):
#         """Load configuration from JSON string"""
#         try:
#             data = json.loads(config_json)
#         except json.JSONDecodeError as e:
#             print(f"Error: Invalid JSON format provided. Details: {e}")
#             return

#         # Load Courses
#         for course_data in data.get("courses", []):
#             try:
#                 course_obj = NEPCourse.from_dict(course_data)
#                 self.add_course(course_obj)
#             except Exception as e:
#                 print(f"Error loading course {course_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Faculty
#         for faculty_data in data.get("faculty", []):
#             try:
#                 teacher_obj = NEPFaculty.from_dict(faculty_data)
#                 self.add_teacher(teacher_obj)
#             except Exception as e:
#                 print(f"Error loading faculty {faculty_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Classrooms
#         for classroom_data in data.get("classrooms", []):
#             try:
#                 classroom_obj = NEPClassroom.from_dict(classroom_data)
#                 self.add_classroom(classroom_obj)
#             except Exception as e:
#                 print(f"Error loading classroom {classroom_data.get('id', 'unknown')}: {e}")
#                 continue
            
#         # Load Student Batches
#         for batch_data in data.get("student_batches", []):
#             try:
#                 batch_obj = NEPStudentBatch.from_dict(batch_data)
#                 self.add_student_batch(batch_obj)
#             except Exception as e:
#                 print(f"Error loading batch {batch_data.get('id', 'unknown')}: {e}")
#                 continue

#         print("Configuration loaded successfully from JSON.")

#     def add_course(self, course: NEPCourse):
#         """Add course to system"""
#         self.courses[course.id] = course
#         self.departments.add(course.department)
    
#     def add_teacher(self, teacher: NEPFaculty):
#         """Add teacher to system"""
#         # Filter out slots that are outside the configured days/periods
#         if teacher.research_slots:
#             teacher.research_slots = [
#                 (day, period) for day, period in teacher.research_slots 
#                 if day < self.days and period < self.periods_per_day
#             ]
#         if teacher.unavailable_slots:
#             teacher.unavailable_slots = [
#                 (day, period) for day, period in teacher.unavailable_slots
#                 if day < self.days and period < self.periods_per_day
#             ]
        
#         self.teachers[teacher.id] = teacher
#         self.departments.add(teacher.department)
    
#     def add_classroom(self, classroom: NEPClassroom):
#         """Add classroom to system"""
#         if classroom.weekly_maintenance:
#             classroom.weekly_maintenance = [
#                 (day, period) for day, period in classroom.weekly_maintenance
#                 if day < self.days and period < self.periods_per_day
#             ]

#         self.classrooms[classroom.id] = classroom
#         self.departments.add(classroom.department)
    
#     def add_student_batch(self, batch: NEPStudentBatch):
#         """Add student batch to system"""
#         self.student_batches[batch.id] = batch
#         self.departments.add(batch.department)
    
#     def is_faculty_available_for_lab(self, faculty_id: str, day: int, start_period: int, duration: int, timetable: dict) -> bool:
#         """Check if faculty is available for a lab session spanning multiple periods"""
#         for i in range(duration):
#             period = start_period + i
#             if not self.is_faculty_available(faculty_id, day, period, timetable):
#                 return False
#         return True

#     def create_initial_timetable(self):
#         """Creates an initial timetable with proper lab scheduling"""
#         timetable = {}
        
#         # Initialize an empty schedule for each batch
#         for batch_id in self.student_batches:
#             timetable[batch_id] = np.full((self.days, self.periods_per_day), None, dtype=object)

#         print("Starting timetable generation...")
#         print(f"Available time slots: {self.time_slots}")
        
#         # Step 1: Assign all lab courses first (higher priority due to longer duration)
#         for batch_id, batch in self.student_batches.items():
#             all_courses = (batch.core_courses + batch.elective_courses + 
#                           batch.skill_courses + batch.multidisciplinary_courses)
            
#             lab_courses = [course_id for course_id in all_courses 
#                           if course_id in self.courses and self.courses[course_id].requires_lab]
            
#             print(f"Batch {batch_id}: Found {len(lab_courses)} lab courses: {lab_courses}")
            
#             # Define available lab slots (avoiding lunch period)
#             available_lab_slots = []
#             for day in range(self.days):
#                 for start_period in range(self.periods_per_day - 1):  # -1 because labs need 2 periods
#                     # Skip if starts at or includes lunch period
#                     if (start_period == self.preferences.lunch_break_start or 
#                         start_period + 1 == self.preferences.lunch_break_start):
#                         continue
                    
#                     # Prefer afternoon slots (periods 3-4: 1:30-4:30 PM)
#                     if start_period >= 3:
#                         available_lab_slots.append((day, start_period, 2))  # priority 2 for afternoon
#                     else:
#                         available_lab_slots.append((day, start_period, 1))  # priority 1 for morning
            
#             # Sort by priority (afternoon first)
#             available_lab_slots.sort(key=lambda x: x[2], reverse=True)
            
#             for course_id in lab_courses:
#                 course = self.courses[course_id]
#                 duration_periods = self.get_course_duration_periods(course)
                
#                 print(f"Scheduling lab {course_id} ({course.name}) - needs {duration_periods} periods")
                
#                 assigned = False
#                 for day, start_period, priority in available_lab_slots:
#                     # Check if we have enough consecutive periods
#                     if start_period + duration_periods > self.periods_per_day:
#                         continue
                    
#                     # Check if all required periods are available for this batch
#                     periods_available = all(
#                         timetable[batch_id][day][start_period + i] is None 
#                         for i in range(duration_periods)
#                     )
                    
#                     if not periods_available:
#                         continue
                    
#                     # Find suitable lab room
#                     classroom_id = self.find_suitable_lab_room(course, day, start_period, duration_periods, timetable)
                    
#                     if classroom_id and self.is_faculty_available_for_lab(course.faculty_id, day, start_period, duration_periods, timetable):
#                         # Assign the lab to all required periods
#                         for i in range(duration_periods):
#                             period = start_period + i
#                             timetable[batch_id][day][period] = {
#                                 'course_id': course_id,
#                                 'faculty_id': course.faculty_id,
#                                 'classroom_id': classroom_id,
#                                 'is_lab': True,
#                                 'lab_session_part': i + 1,  # Track which part of the lab session
#                                 'lab_total_parts': duration_periods
#                             }
                        
#                         print(f"✓ Assigned lab {course_id} to {self.day_names[day]}, periods {start_period}-{start_period + duration_periods - 1}")
#                         print(f"  Time: {self.time_slots[start_period]} - {self.time_slots[start_period + duration_periods - 1]}")
#                         print(f"  Room: {classroom_id}, Faculty: {self.teachers[course.faculty_id].name}")
#                         assigned = True
                        
#                         # Remove this slot from available slots for other courses
#                         available_lab_slots = [slot for slot in available_lab_slots 
#                                              if not (slot[0] == day and 
#                                                    slot[1] >= start_period and 
#                                                    slot[1] < start_period + duration_periods)]
#                         break
                
#                 if not assigned:
#                     print(f"⚠️ WARNING: Could not assign lab {course_id} for batch {batch_id}")

#         # Step 2: Assign regular theory courses
#         for batch_id, batch in self.student_batches.items():
#             all_courses = (batch.core_courses + batch.elective_courses +
#                            batch.skill_courses + batch.multidisciplinary_courses)
            
#             regular_courses = [course_id for course_id in all_courses 
#                                if course_id in self.courses and not self.courses[course_id].requires_lab]
            
#             print(f"Batch {batch_id}: Found {len(regular_courses)} regular courses: {regular_courses}")
            
#             for course_id in regular_courses:
#                 course = self.courses[course_id]
#                 hours_to_schedule = course.hours_per_week
#                 scheduled_hours = 0
                
#                 print(f"Scheduling regular course {course_id} ({course.name}) - needs {hours_to_schedule} hours")
                
#                 # Try to schedule the required hours
#                 attempts = 0
#                 max_attempts = 100
                
#                 while scheduled_hours < hours_to_schedule and attempts < max_attempts:
#                     day = random.randrange(self.days)
#                     period = random.randrange(self.periods_per_day)
                    
#                     # Skip lunch period
#                     if self.is_lunch_period(period):
#                         attempts += 1
#                         continue

#                     # Check if slot is empty
#                     if timetable[batch_id][day][period] is None:
#                         # Find suitable classroom
#                         classroom_id = self.find_suitable_classroom(course, day, period, timetable)
                        
#                         if classroom_id and self.is_faculty_available(course.faculty_id, day, period, timetable):
#                             timetable[batch_id][day][period] = {
#                                 'course_id': course_id,
#                                 'faculty_id': course.faculty_id,
#                                 'classroom_id': classroom_id,
#                                 'is_lab': False
#                             }
#                             scheduled_hours += 1
#                             print(f"✓ Assigned {course_id} to {self.day_names[day]}, period {period} ({self.time_slots[period]})")
                    
#                     attempts += 1
                
#                 if scheduled_hours < hours_to_schedule:
#                     print(f"⚠️ WARNING: Only scheduled {scheduled_hours}/{hours_to_schedule} hours for course {course_id}")
        
#         return timetable
    
#     def find_suitable_lab_room(self, course: NEPCourse, day: int, start_period: int, duration: int, timetable: dict) -> Optional[str]:
#         """Find suitable lab room for a lab course"""
#         suitable_rooms = []
        
#         for room_id, room in self.classrooms.items():
#             # Check if it's a lab room
#             if room.room_type not in [RoomType.LAB, RoomType.COMPUTER_LAB]:
#                 continue
            
#             # Check capacity
#             if room.capacity < course.max_students:
#                 continue
            
#             # Check availability for all required periods
#             available = True
#             for i in range(duration):
#                 period = start_period + i
#                 if period >= self.periods_per_day:
#                     available = False
#                     break
#                 if not self.is_room_available(room_id, day, period, timetable):
#                     available = False
#                     break
            
#             if available:
#                 pref_score = 0
#                 if room.department == course.department:
#                     pref_score += 10
                
#                 suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         # If no dedicated lab room available, try regular rooms with lab capability
#         for room_id, room in self.classrooms.items():
#             if room.capacity >= course.max_students:
#                 available = True
#                 for i in range(duration):
#                     period = start_period + i
#                     if period >= self.periods_per_day or not self.is_room_available(room_id, day, period, timetable):
#                         available = False
#                         break
                
#                 if available:
#                     return room_id
        
#         return None

#     def find_suitable_classroom(self, course: NEPCourse, day: int, period: int, timetable: dict) -> Optional[str]:
#         """Find suitable classroom based on course requirements"""
#         suitable_rooms = []
        
#         for room_id, room in self.classrooms.items():
#             # Check capacity
#             if room.capacity < course.max_students:
#                 continue
            
#             # Check room type requirements
#             if course.requires_lab and room.room_type not in [RoomType.LAB, RoomType.COMPUTER_LAB]:
#                 continue
            
#             if course.requires_smart_room and not room.is_smart_room:
#                 continue
            
#             # Check availability
#             if self.is_room_available(room_id, day, period, timetable):
#                 pref_score = 0
#                 if room.department == course.department:
#                     pref_score += 10
#                 if course.course_type == CourseType.SEMINAR and room.room_type == RoomType.SEMINAR:
#                     pref_score += 15
                
#                 suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         return None

#     def is_room_available(self, room_id: str, day: int, period: int, timetable: dict) -> bool:
#         """Check if room is available at given time"""
#         room = self.classrooms[room_id]
        
#         # Check maintenance slots
#         if (day, period) in room.weekly_maintenance:
#             return False
        
#         # Check if room is already occupied
#         for batch_id, schedule in timetable.items():
#             if schedule[day][period] is not None:
#                 if schedule[day][period]['classroom_id'] == room_id:
#                     return False
        
#         return True
    
#     def is_faculty_available(self, faculty_id: str, day: int, period: int, timetable: dict) -> bool:
#         """Check if faculty is available"""
#         teacher = self.teachers[faculty_id]
        
#         # Check unavailable slots
#         if (day, period) in teacher.unavailable_slots:
#             return False
        
#         # Check research slots
#         if self.preferences.research_slot_protection and (day, period) in teacher.research_slots:
#             return False
        
#         # Check if already assigned
#         for batch_id, schedule in timetable.items():
#             if schedule[day][period] is not None:
#                 if schedule[day][period]['faculty_id'] == faculty_id:
#                     return False
        
#         # Check daily hour limit
#         daily_hours = self.get_faculty_daily_hours(faculty_id, day, timetable)
#         if daily_hours >= teacher.max_hours_per_day:
#             return False
        
#         return True
    
#     def get_faculty_daily_hours(self, faculty_id: str, day: int, timetable: dict) -> int:
#         """Get current daily hours for faculty"""
#         hours = 0
#         for batch_id, schedule in timetable.items():
#             for period in range(self.periods_per_day):
#                 if schedule[day][period] is not None:
#                     if schedule[day][period]['faculty_id'] == faculty_id:
#                         hours += 1
#         return hours
    
#     def genetic_algorithm_evolution(self, population_size: int = 30, generations: int = 50) -> dict:
#         """Main genetic algorithm with lab-aware optimization"""
#         print(f"Initializing NEP-compliant timetable generation...")
#         print(f"Population: {population_size}, Generations: {generations}")
        
#         # Initialize population
#         population = []
#         for i in range(population_size):
#             print(f"Creating individual {i+1}/{population_size}")
#             individual = self.create_initial_timetable()
#             population.append(individual)
        
#         best_fitness = 0
#         best_timetable = None
        
#         for gen in range(generations):
#             # Calculate fitness
#             fitness_scores = []
#             for individual in population:
#                 fitness = self.calculate_nep_fitness(individual)
#                 fitness_scores.append(fitness)
            
#             # Track best solution
#             max_fitness = max(fitness_scores)
#             if max_fitness > best_fitness:
#                 best_fitness = max_fitness
#                 best_timetable = copy.deepcopy(population[fitness_scores.index(max_fitness)])
#                 print(f"Generation {gen}: New best fitness = {best_fitness:.2f}")
            
#             # Early termination if good solution found
#             if best_fitness >= 800:  # Reasonable solution
#                 print(f"Found good solution at generation {gen}")
#                 break
            
#             # Selection and evolution (simplified for lab scheduling)
#             if gen < generations - 1:
#                 population = self.evolve_population(population, fitness_scores)
        
#         print(f"Evolution complete. Final best fitness: {best_fitness:.2f}")
#         return best_timetable

#     def evolve_population(self, population, fitness_scores):
#         """Evolve the population with lab-aware operations"""
#         new_population = []
        
#         # Keep best individuals (elitism)
#         elite_count = max(1, len(population) // 10)
#         elite_indices = sorted(range(len(fitness_scores)), 
#                               key=lambda i: fitness_scores[i], reverse=True)[:elite_count]
        
#         for i in elite_indices:
#             new_population.append(copy.deepcopy(population[i]))
        
#         # Fill rest with mutations of good individuals
#         while len(new_population) < len(population):
#             # Select a good parent
#             parent_idx = random.choice(elite_indices[:len(elite_indices)//2])
#             child = self.lab_aware_mutation(copy.deepcopy(population[parent_idx]))
#             new_population.append(child)
        
#         return new_population

#     def lab_aware_mutation(self, timetable: dict) -> dict:
#         """Mutation that respects lab course structure"""
#         if random.random() < 0.3:  # 30% chance of mutation
#             batch_id = random.choice(list(self.student_batches.keys()))
#             schedule = timetable[batch_id]
            
#             # Find non-lab slots to swap
#             non_lab_slots = []
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot is not None and not slot.get('is_lab', False):
#                         non_lab_slots.append((day, period))
            
#             # Swap two non-lab slots if possible
#             if len(non_lab_slots) >= 2:
#                 (day1, period1), (day2, period2) = random.sample(non_lab_slots, 2)
#                 schedule[day1][period1], schedule[day2][period2] = \
#                     schedule[day2][period2], schedule[day1][period1]
        
#         return timetable

#     def calculate_nep_fitness(self, timetable: dict) -> float:
#         """Calculate fitness score with lab-specific considerations"""
#         base_score = 1000.0
#         penalty = 0.0
        
#         # Check lab assignments (high priority)
#         penalty += self.check_unassigned_labs(timetable) * 300
#         penalty += self.check_lab_continuity(timetable) * 200
        
#         # Standard constraint violations
#         penalty += self.check_faculty_conflicts(timetable) * 100
#         penalty += self.check_classroom_conflicts(timetable) * 100
#         penalty += self.check_course_hour_requirements(timetable) * 60
#         penalty += self.check_lunch_violations(timetable) * 50
        
#         # Bonuses
#         bonus = 0.0
#         bonus += self.calculate_lab_scheduling_bonus(timetable)
        
#         return max(0, base_score - penalty + bonus)

#     def check_unassigned_labs(self, timetable: dict) -> int:
#         """Check for lab courses that weren't assigned"""
#         unassigned = 0
        
#         for batch_id, batch in self.student_batches.items():
#             all_courses = (batch.core_courses + batch.elective_courses +
#                            batch.skill_courses + batch.multidisciplinary_courses)
            
#             lab_courses = [course_id for course_id in all_courses 
#                           if course_id in self.courses and self.courses[course_id].requires_lab]
            
#             for course_id in lab_courses:
#                 assigned = False
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = timetable[batch_id][day][period]
#                         if slot and slot['course_id'] == course_id:
#                             assigned = True
#                             break
#                     if assigned:
#                         break
                
#                 if not assigned:
#                     unassigned += 1
#                     print(f"Warning: Lab course {course_id} not assigned for batch {batch_id}")
        
#         return unassigned

#     def check_lab_continuity(self, timetable: dict) -> int:
#         """Check if lab sessions are properly continuous"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day - 1):  # -1 because we check next period
#                     slot = schedule[day][period]
#                     if slot and slot.get('is_lab', False):
#                         next_slot = schedule[day][period + 1]
#                         # If this is first part of lab, next slot should be same lab
#                         if (slot.get('lab_session_part', 1) == 1 and 
#                             slot.get('lab_total_parts', 1) > 1):
#                             if (not next_slot or 
#                                 next_slot.get('course_id') != slot['course_id'] or
#                                 not next_slot.get('is_lab', False)):
#                                 violations += 1
        
#         return violations

#     def check_faculty_conflicts(self, timetable: dict) -> int:
#         """Check for faculty double-booking"""
#         conflicts = 0
#         faculty_schedule = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         faculty_id = slot['faculty_id']
#                         faculty_schedule[faculty_id][day].append(period)
        
#         for faculty_id, days in faculty_schedule.items():
#             for day, periods in days.items():
#                 # Count duplicates
#                 duplicates = len(periods) - len(set(periods))
#                 conflicts += duplicates
        
#         return conflicts
    
#     def check_classroom_conflicts(self, timetable: dict) -> int:
#         """Check for classroom double-booking"""
#         conflicts = 0
#         room_schedule = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         room_id = slot['classroom_id']
#                         room_schedule[room_id][day].append(period)
        
#         for room_id, days in room_schedule.items():
#             for day, periods in days.items():
#                 duplicates = len(periods) - len(set(periods))
#                 conflicts += duplicates
        
#         return conflicts

#     def check_course_hour_requirements(self, timetable: dict) -> int:
#         """Check if courses have required weekly hours"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             batch = self.student_batches[batch_id]
#             course_hours = defaultdict(int)
            
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course_hours[slot['course_id']] += 1
            
#             all_courses = (batch.core_courses + batch.elective_courses + 
#                            batch.skill_courses + batch.multidisciplinary_courses)
            
#             for course_id in all_courses:
#                 if course_id in self.courses:
#                     required = self.courses[course_id].hours_per_week
#                     actual = course_hours[course_id]
#                     # For labs, convert periods to hours (2 periods = 3 hours)
#                     if self.courses[course_id].requires_lab:
#                         actual_hours = (actual // 2) * 3 + (actual % 2) * 1.5
#                         if abs(required - actual_hours) > 0.5:  # Allow small tolerance
#                             violations += 1
#                     else:
#                         # Regular courses: 1 period = 1.5 hours
#                         actual_hours = actual * 1.5
#                         if abs(required - actual_hours) > 0.5:
#                             violations += 1
        
#         return violations

#     def check_lunch_violations(self, timetable: dict) -> int:
#         """Check lunch break violations"""
#         violations = 0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 if schedule[day][self.preferences.lunch_break_start] is not None:
#                     violations += 1
        
#         return violations

#     def calculate_lab_scheduling_bonus(self, timetable: dict) -> float:
#         """Calculate bonus for proper lab scheduling"""
#         bonus = 0.0
        
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot and slot.get('is_lab', False):
#                         # Bonus for afternoon lab scheduling (preferred)
#                         if period >= 3:  # Afternoon periods
#                             bonus += 10.0
#                         # Bonus for proper lab room usage
#                         room = self.classrooms[slot['classroom_id']]
#                         if room.room_type in [RoomType.LAB, RoomType.COMPUTER_LAB]:
#                             bonus += 15.0
        
#         return bonus

#     def export_nep_timetable(self, timetable: dict, filename: str = "nep_timetable.json") -> dict:
#         """Export NEP-compliant timetable with lab session details"""
#         export_data = {
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "nep_2020_compliant": True,
#                 "total_batches": len(self.student_batches),
#                 "total_faculty": len(self.teachers),
#                 "total_courses": len(self.courses),
#                 "working_days": self.days,
#                 "periods_per_day": self.periods_per_day,
#                 "time_slots": self.time_slots,
#                 "college_hours": f"{self.preferences.morning_start_time} - {self.preferences.evening_end_time}"
#             },
#             "departments": list(self.departments),
#             "timetables": {},
#             "analytics": {}
#         }
        
#         # Export batch timetables
#         for batch_id, schedule in timetable.items():
#             batch = self.student_batches[batch_id]
#             batch_data = {
#                 "batch_info": {
#                     "name": batch.name,
#                     "department": batch.department,
#                     "semester": batch.semester,
#                     "student_count": batch.student_count
#                 },
#                 "weekly_schedule": []
#             }
            
#             for day in range(self.days):
#                 day_schedule = {
#                     "day": self.day_names[day],
#                     "periods": []
#                 }
                
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         teacher = self.teachers[slot['faculty_id']]
#                         classroom = self.classrooms[slot['classroom_id']]
                        
#                         period_data = {
#                             "time": self.time_slots[period],
#                             "course": {
#                                 "id": course.id,
#                                 "name": course.name,
#                                 "code": course.code,
#                                 "type": course.course_type.value,
#                                 "credits": course.credits,
#                                 "department": course.department,
#                                 "is_lab": slot.get('is_lab', False)
#                             },
#                             "faculty": {
#                                 "id": teacher.id,
#                                 "name": teacher.name,
#                                 "designation": teacher.designations
#                             },
#                             "classroom": {
#                                 "id": classroom.id,
#                                 "name": classroom.name,
#                                 "type": classroom.room_type.value,
#                                 "capacity": classroom.capacity
#                             }
#                         }
                        
#                         # Add lab session details if applicable
#                         if slot.get('is_lab', False):
#                             period_data['lab_session'] = {
#                                 "part": slot.get('lab_session_part', 1),
#                                 "total_parts": slot.get('lab_total_parts', 1),
#                                 "is_continuous": True
#                             }
                            
#                     else:
#                         if self.is_lunch_period(period):
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "lunch_break"
#                             }
#                         else:
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "free"
#                             }
                    
#                     day_schedule["periods"].append(period_data)
                
#                 batch_data["weekly_schedule"].append(day_schedule)
            
#             export_data["timetables"][batch.name] = batch_data
        
#         # Calculate analytics
#         export_data["analytics"] = self.calculate_timetable_analytics(timetable)
        
#         # Save to file
#         with open(filename, 'w') as f:
#             json.dump(export_data, f, indent=2, default=str)
        
#         print(f"NEP-compliant timetable exported to {filename}")
#         return export_data

#     def calculate_timetable_analytics(self, timetable: dict) -> dict:
#         """Calculate comprehensive timetable analytics including lab metrics"""
#         analytics = {
#             "fitness_score": self.calculate_nep_fitness(timetable),
#             "constraint_violations": {
#                 "unassigned_labs": self.check_unassigned_labs(timetable),
#                 "lab_continuity_issues": self.check_lab_continuity(timetable),
#                 "faculty_conflicts": self.check_faculty_conflicts(timetable),
#                 "classroom_conflicts": self.check_classroom_conflicts(timetable),
#                 "lunch_violations": self.check_lunch_violations(timetable)
#             },
#             "lab_statistics": {
#                 "total_lab_sessions": 0,
#                 "properly_scheduled_labs": 0,
#                 "lab_rooms_utilized": set(),
#                 "afternoon_lab_sessions": 0
#             },
#             "course_distribution": defaultdict(int),
#             "faculty_utilization": {},
#             "classroom_utilization": {}
#         }
        
#         # Calculate lab statistics
#         for batch_id, schedule in timetable.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         analytics["course_distribution"][course.course_type.value] += 1
                        
#                         if slot.get('is_lab', False):
#                             analytics["lab_statistics"]["total_lab_sessions"] += 1
#                             analytics["lab_statistics"]["lab_rooms_utilized"].add(slot['classroom_id'])
                            
#                             if period >= 3:  # Afternoon periods
#                                 analytics["lab_statistics"]["afternoon_lab_sessions"] += 1
                            
#                             # Check if properly continuous
#                             if (slot.get('lab_session_part', 1) == 1 and 
#                                 period < self.periods_per_day - 1):
#                                 next_slot = schedule[day][period + 1]
#                                 if (next_slot and 
#                                     next_slot.get('course_id') == slot['course_id'] and
#                                     next_slot.get('is_lab', False)):
#                                     analytics["lab_statistics"]["properly_scheduled_labs"] += 1
        
#         # Convert set to count for JSON serialization
#         analytics["lab_statistics"]["lab_rooms_utilized"] = len(analytics["lab_statistics"]["lab_rooms_utilized"])
        
#         return analytics

#     def print_nep_timetable_summary(self, timetable: dict):
#         """Print NEP-compliant timetable summary with lab details"""
#         print("\n" + "="*80)
#         print("NEP 2020 COMPLIANT TIMETABLE GENERATION SUMMARY")
#         print("="*80)
        
#         analytics = self.calculate_timetable_analytics(timetable)
        
#         print(f"\nOVERALL METRICS:")
#         print(f"    Fitness Score: {analytics['fitness_score']:.2f}/1000")
#         print(f"    College Hours: {self.preferences.morning_start_time} - {self.preferences.evening_end_time}")
#         print(f"    Time Slots: {len(self.time_slots)} periods per day")
#         print(f"    Working Days: {self.days}")
        
#         print(f"\nCONSTRAINT VIOLATIONS:")
#         violations = analytics['constraint_violations']
#         print(f"    Unassigned Labs: {violations['unassigned_labs']}")
#         print(f"    Lab Continuity Issues: {violations['lab_continuity_issues']}")
#         print(f"    Faculty Conflicts: {violations['faculty_conflicts']}")
#         print(f"    Classroom Conflicts: {violations['classroom_conflicts']}")
#         print(f"    Lunch Break Violations: {violations['lunch_violations']}")
        
#         print(f"\nLAB SCHEDULING STATISTICS:")
#         lab_stats = analytics['lab_statistics']
#         print(f"    Total Lab Sessions: {lab_stats['total_lab_sessions']}")
#         print(f"    Properly Scheduled Labs: {lab_stats['properly_scheduled_labs']}")
#         print(f"    Afternoon Lab Sessions: {lab_stats['afternoon_lab_sessions']} (preferred)")
#         print(f"    Lab Rooms Utilized: {lab_stats['lab_rooms_utilized']}")
        
#         print(f"\nCOURSE TYPE DISTRIBUTION (NEP 2020):")
#         for course_type, count in analytics['course_distribution'].items():
#             print(f"    {course_type.replace('_', ' ').title()}: {count} sessions")

#         # Print sample timetable for first batch
#         if timetable:
#             first_batch_id = list(timetable.keys())[0]
#             first_batch = self.student_batches[first_batch_id]
#             print(f"\nSAMPLE TIMETABLE - {first_batch.name}:")
#             print("-" * 70)
            
#             schedule = timetable[first_batch_id]
            
#             # Header
#             header = "Time".ljust(12)
#             for day in self.day_names:
#                 header += day.ljust(15)
#             print(header)
#             print("-" * 70)
            
#             # Periods
#             for period in range(self.periods_per_day):
#                 row = self.time_slots[period].ljust(12)
                
#                 for day in range(self.days):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         display_name = course.name
#                         if slot.get('is_lab', False):
#                             part = slot.get('lab_session_part', 1)
#                             total = slot.get('lab_total_parts', 1)
#                             display_name += f" (Lab {part}/{total})"
                        
#                         # Truncate long names
#                         if len(display_name) > 12:
#                             display_name = display_name[:12] + "..."
#                         row += display_name.ljust(15)
#                     elif self.is_lunch_period(period):
#                         row += "LUNCH".ljust(15)
#                     else:
#                         row += "Free".ljust(15)
                
#                 print(row)


# # Web API Integration Functions
# def create_nep_system_from_json(json_input: str, user_preferences: dict = None) -> NEPTimetableGenerator:
#     """Create NEP system from JSON input"""
#     prefs = UserPreferences()
#     if user_preferences:
#         for key, value in user_preferences.items():
#             if hasattr(prefs, key):
#                 setattr(prefs, key, value)
    
#     generator = NEPTimetableGenerator(user_preferences=prefs)
#     generator.load_from_json(json_input)
    
#     return generator

# def generate_timetable_api(json_input: str, user_preferences: dict = None, 
#                            population_size: int = 30, generations: int = 50) -> dict:
#     """Main API function for web integration"""
#     print("Starting NEP 2020 Compliant Timetable Generation with Lab Support...")
    
#     # Create system
#     generator = create_nep_system_from_json(json_input, user_preferences)
    
#     # Generate timetable
#     best_timetable = generator.genetic_algorithm_evolution(population_size, generations)
    
#     if best_timetable:
#         # Export and return result
#         result = generator.export_nep_timetable(best_timetable)
#         generator.print_nep_timetable_summary(best_timetable)
#         return result
#     else:
#         raise Exception("Failed to generate valid timetable. Please check constraints.")

# # Main execution for testing
# if __name__ == "__main__":
#     # Test with your actual data
#     sample_json = json.dumps({
#         "courses": [
#             {
#                 "id": "B23AM3101", "name": "Deep Learning", "code": "B23AM3101",
#                 "credits": 3, "course_type": "core", "hours_per_week": 3,
#                 "department": "AIML", "semester": 5, "faculty_id": "1",
#                 "requires_lab": False, "max_students": 16
#             },
#             {
#                 "id": "B23AM3110", "name": "Deep Learning Lab", "code": "B23AM3110",
#                 "credits": 0, "course_type": "core", "hours_per_week": 3,
#                 "department": "AIML", "semester": 5, "faculty_id": "1",
#                 "requires_lab": True, "max_students": 16, "min_duration_minutes": 180
#             }
#         ],
#         "faculty": [
#             {
#                 "id": "1", "name": "Dr P Ravi Kiran Varma", "department": "CSE",
#                 "designation": "Professor", "specializations": ["Deep Learning"],
#                 "courses_can_teach": ["B23AM3101", "B23AM3110"]
#             }
#         ],
#         "classrooms": [
#             {
#                 "id": "LAB-401", "name": "AI/ML Lab", "capacity": 40,
#                 "room_type": "computer_lab", "department": "CSE", "equipment": []
#             },
#             {
#                 "id": "C101", "name": "C101", "capacity": 70,
#                 "room_type": "lecture", "department": "CSE", "equipment": []
#             }
#         ],
#         "student_batches": [
#             {
#                 "id": "AIML_S5", "name": "AI & ML Semester 5", "department": "AIML",
#                 "semester": 5, "student_count": 16,
#                 "core_courses": ["B23AM3101", "B23AM3110"],
#                 "elective_courses": [], "skill_courses": [], "multidisciplinary_courses": []
#             }
#         ]
#     })
    
#     try:
#         result = generate_timetable_api(sample_json, population_size=20, generations=30)
#         print(f"\nTimetable generated successfully!")
        
#     except Exception as e:
#         print(f"Error: {e}")


# import json
# import numpy as np
# import pandas as pd
# from datetime import datetime, timedelta
# import random
# from dataclasses import dataclass, asdict
# from typing import List, Dict, Tuple, Optional, Union
# from collections import defaultdict
# from enum import Enum
# import copy
# import math

# class CourseType(Enum):
#     CORE = "core"
#     ELECTIVE = "elective" 
#     MULTIDISCIPLINARY = "multidisciplinary"
#     SKILL_ENHANCEMENT = "skill_enhancement"
#     VALUE_ADDED = "value_added"
#     ABILITY_ENHANCEMENT = "ability_enhancement"
#     SEMINAR = "seminar"
#     PROJECT = "project"
#     HONORS = "honors"
#     MINOR = "minor"

# class RoomType(Enum):
#     LECTURE = "lecture"
#     LAB = "lab"
#     SEMINAR = "seminar"
#     COMPUTER_LAB = "computer_lab"
#     SMART_CLASSROOM = "smart_classroom"
#     AUDITORIUM = "auditorium"

# class TimePreference(Enum):
#     MORNING = "morning"
#     AFTERNOON = "afternoon"
#     EVENING = "evening"
#     ANY = "any"

# @dataclass
# class NEPCourse:
#     """Enhanced course structure following NEP 2020 guidelines"""
#     id: str
#     name: str
#     code: str
#     credits: int
#     course_type: CourseType
#     hours_per_week: int
#     department: str
#     semester: int
#     faculty_id: str
#     requires_lab: bool = False
#     requires_smart_room: bool = False
#     is_interdisciplinary: bool = False
#     connected_departments: List[str] = None
#     max_students: int = 60
#     min_duration_minutes: int = 50
#     max_consecutive_hours: int = 2
#     preferred_days: List[int] = None
    
#     def __post_init__(self):
#         if self.connected_departments is None:
#             self.connected_departments = []
#         if self.preferred_days is None:
#             self.preferred_days = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPCourse from dictionary"""
#         if isinstance(data['course_type'], str):
#             course_type_str = data['course_type'].lower().strip()
#             if course_type_str == 'honors':
#                 data['course_type'] = CourseType.HONORS
#             elif course_type_str == 'minor':
#                 data['course_type'] = CourseType.MINOR
#             else:
#                 try:
#                     data['course_type'] = CourseType(course_type_str)
#                 except ValueError:
#                     print(f"Warning: Unknown course type '{data['course_type']}', defaulting to 'core'")
#                     data['course_type'] = CourseType.CORE
#         return cls(**data)

# @dataclass 
# class NEPFaculty:
#     """Faculty with NEP 2020 compliant parameters"""
#     id: str
#     name: str
#     department: str
#     designations: str
#     specializations: List[str]
#     courses_can_teach: List[str]
#     max_hours_per_day: int = 6
#     max_hours_per_week: int = 24
#     preferred_time: TimePreference = TimePreference.ANY
#     unavailable_slots: List[Tuple[int, int]] = None
#     research_slots: List[Tuple[int, int]] = None
#     is_visiting: bool = False
#     workload_preference: float = 1.0
    
#     def __post_init__(self):
#         if self.unavailable_slots is None:
#             self.unavailable_slots = []
#         if self.research_slots is None:
#             self.research_slots = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPFaculty from dictionary"""
#         if 'designation' in data:
#             data['designations'] = data.pop('designation')
#         if isinstance(data.get('preferred_time'), str):
#             data['preferred_time'] = TimePreference(data['preferred_time'])
#         return cls(**data)

# @dataclass
# class NEPClassroom:
#     """Classroom with modern facilities"""
#     id: str
#     name: str
#     capacity: int
#     room_type: RoomType
#     department: str
#     equipment: List[str]
#     is_smart_room: bool = False
#     is_ac: bool = False
#     has_projector: bool = True
#     weekly_maintenance: List[Tuple[int, int]] = None
    
#     def __post_init__(self):
#         if self.weekly_maintenance is None:
#             self.weekly_maintenance = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPClassroom from dictionary"""
#         if isinstance(data['room_type'], str):
#             data['room_type'] = RoomType(data['room_type'])
#         return cls(**data)

# @dataclass
# class NEPStudentBatch:
#     """Student batch/class with NEP parameters"""
#     id: str
#     name: str
#     department: str
#     semester: int
#     student_count: int
#     core_courses: List[str]
#     elective_courses: List[str]
#     skill_courses: List[str]
#     multidisciplinary_courses: List[str]
#     preferred_morning_hours: bool = True
#     max_hours_per_day: int = 7
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPStudentBatch from dictionary"""
#         return cls(**data)

# @dataclass
# class UserPreferences:
#     """User-configurable preferences"""
#     working_days: int = 5
#     periods_per_day: int = 5  # Updated for your schedule
#     lunch_break_start: int = 2  # Period where lunch starts (0-based index)
#     lunch_break_end: int = 2    # Period where lunch ends (0-based index)
#     max_consecutive_same_subject: int = 2
#     gap_penalty_weight: float = 10.0
#     faculty_preference_weight: float = 15.0
#     workload_balance_weight: float = 20.0
#     room_preference_weight: float = 5.0
#     interdisciplinary_bonus: float = 10.0
#     research_slot_protection: bool = True
#     allow_saturday_classes: bool = False
#     morning_start_time: str = "9:00"
#     evening_end_time: str = "4:30"

# class MultiSectionTimetableGenerator:
#     """Enhanced timetable generator for multiple sections with conflict resolution"""
    
#     def __init__(self, config_json: str = None, user_preferences: UserPreferences = None):
#         self.preferences = user_preferences or UserPreferences()
#         self.days = 6 if self.preferences.allow_saturday_classes else 5
#         self.periods_per_day = self.preferences.periods_per_day
        
#         # Data containers
#         self.courses = {}
#         self.teachers = {}
#         self.classrooms = {}
#         self.student_batches = {}
#         self.departments = set()
        
#         # Multi-section management
#         self.global_faculty_schedule = defaultdict(lambda: defaultdict(lambda: None))  # faculty_id -> day -> period -> batch_id
#         self.global_room_schedule = defaultdict(lambda: defaultdict(lambda: None))     # room_id -> day -> period -> batch_id
#         self.synchronized_slots = {}  # For PE/OE synchronization
        
#         # Generate time slots
#         self.generate_time_slots()
#         self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:self.days]
        
#         # Course frequency overrides (for courses that should appear less than hours_per_week)
#         self.course_frequency_override = {
#             "B23AM3101": 2,  # Deep Learning - only 2 times per week instead of 3
#         }
        
#         if config_json:
#             self.load_from_json(config_json)

#     def generate_time_slots(self):
#         """Generate time slots matching college schedule (9:00 AM to 4:30 PM)"""
#         self.time_slots = [
#             "09:00-10:30",  # 0 - Morning session 1
#             "10:30-12:00",  # 1 - Morning session 2
#             "12:00-01:30",  # 2 - LUNCH BREAK
#             "01:30-03:00",  # 3 - Afternoon session 1  
#             "03:00-04:30",  # 4 - Afternoon session 2
#         ]
        
#         self.periods_per_day = len(self.time_slots)
#         self.preferences.lunch_break_start = 2
#         self.preferences.lunch_break_end = 2
        
#         print(f"Generated {self.periods_per_day} time slots for college schedule 9:00-4:30")

#     def load_from_json(self, config_json: str):
#         """Load configuration from JSON string"""
#         try:
#             data = json.loads(config_json)
#         except json.JSONDecodeError as e:
#             print(f"Error: Invalid JSON format provided. Details: {e}")
#             return

#         # Load Courses
#         for course_data in data.get("courses", []):
#             try:
#                 course_obj = NEPCourse.from_dict(course_data)
#                 self.add_course(course_obj)
#             except Exception as e:
#                 print(f"Error loading course {course_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Faculty
#         for faculty_data in data.get("faculty", []):
#             try:
#                 teacher_obj = NEPFaculty.from_dict(faculty_data)
#                 self.add_teacher(teacher_obj)
#             except Exception as e:
#                 print(f"Error loading faculty {faculty_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Classrooms
#         for classroom_data in data.get("classrooms", []):
#             try:
#                 classroom_obj = NEPClassroom.from_dict(classroom_data)
#                 self.add_classroom(classroom_obj)
#             except Exception as e:
#                 print(f"Error loading classroom {classroom_data.get('id', 'unknown')}: {e}")
#                 continue
            
#         # Load Student Batches
#         for batch_data in data.get("student_batches", []):
#             try:
#                 batch_obj = NEPStudentBatch.from_dict(batch_data)
#                 self.add_student_batch(batch_obj)
#             except Exception as e:
#                 print(f"Error loading batch {batch_data.get('id', 'unknown')}: {e}")
#                 continue

#         print("Configuration loaded successfully from JSON.")

#     def add_course(self, course: NEPCourse):
#         """Add course to system"""
#         self.courses[course.id] = course
#         self.departments.add(course.department)
    
#     def add_teacher(self, teacher: NEPFaculty):
#         """Add teacher to system"""
#         if teacher.research_slots:
#             teacher.research_slots = [
#                 (day, period) for day, period in teacher.research_slots 
#                 if day < self.days and period < self.periods_per_day
#             ]
#         if teacher.unavailable_slots:
#             teacher.unavailable_slots = [
#                 (day, period) for day, period in teacher.unavailable_slots
#                 if day < self.days and period < self.periods_per_day
#             ]
        
#         self.teachers[teacher.id] = teacher
#         self.departments.add(teacher.department)
    
#     def add_classroom(self, classroom: NEPClassroom):
#         """Add classroom to system"""
#         if classroom.weekly_maintenance:
#             classroom.weekly_maintenance = [
#                 (day, period) for day, period in classroom.weekly_maintenance
#                 if day < self.days and period < self.periods_per_day
#             ]

#         self.classrooms[classroom.id] = classroom
#         self.departments.add(classroom.department)
    
#     def add_student_batch(self, batch: NEPStudentBatch):
#         """Add student batch to system"""
#         self.student_batches[batch.id] = batch
#         self.departments.add(batch.department)

#     def get_course_duration_periods(self, course: NEPCourse) -> int:
#         """Calculate how many periods a course requires"""
#         if course.requires_lab or course.min_duration_minutes >= 180:
#             return 2  # Lab takes 2 consecutive periods (3 hours total)
#         else:
#             return 1  # Regular class takes 1 period (1.5 hours)

#     def is_lunch_period(self, period: int) -> bool:
#         """Check if the given period is lunch break"""
#         return period == self.preferences.lunch_break_start

#     def get_effective_hours_per_week(self, course_id: str) -> int:
#         """Get effective hours per week considering overrides"""
#         if course_id in self.course_frequency_override:
#             return self.course_frequency_override[course_id]
#         elif course_id in self.courses:
#             return self.courses[course_id].hours_per_week
#         return 1

#     def create_synchronized_elective_slots(self):
#         """Create synchronized time slots for PE and OE across all sections"""
#         print("Creating synchronized elective slots...")
        
#         # Define when PE and OE should be scheduled (same time for all sections)
#         elective_slots = [
#             (1, 1),  # Tuesday, Period 1 (10:30-12:00) - PE
#             (2, 1),  # Wednesday, Period 1 (10:30-12:00) - OE
#         ]
        
#         pe_courses = []
#         oe_courses = []
        
#         # Collect all PE and OE courses
#         for batch_id, batch in self.student_batches.items():
#             for course_id in batch.elective_courses:
#                 if course_id.startswith('PE_I') or course_id == '#PE-I':
#                     pe_courses.append((batch_id, course_id))
#                 elif course_id.startswith('OE_I') or course_id == '#OE-I':
#                     oe_courses.append((batch_id, course_id))
        
#         # Schedule PE courses at same time
#         pe_day, pe_period = elective_slots[0]
#         for batch_id, course_id in pe_courses:
#             if course_id in self.courses:
#                 course = self.courses[course_id]
#                 self.synchronized_slots[(batch_id, course_id)] = (pe_day, pe_period)
                
#                 # Reserve faculty and room for this slot
#                 self.global_faculty_schedule[course.faculty_id][pe_day][pe_period] = batch_id
#                 print(f"Synchronized PE: {course_id} for {batch_id} at {self.day_names[pe_day]} {self.time_slots[pe_period]}")
        
#         # Schedule OE courses at same time
#         oe_day, oe_period = elective_slots[1]
#         for batch_id, course_id in oe_courses:
#             if course_id in self.courses:
#                 course = self.courses[course_id]
#                 self.synchronized_slots[(batch_id, course_id)] = (oe_day, oe_period)
                
#                 # Reserve faculty and room for this slot
#                 self.global_faculty_schedule[course.faculty_id][oe_day][oe_period] = batch_id
#                 print(f"Synchronized OE: {course_id} for {batch_id} at {self.day_names[oe_day]} {self.time_slots[oe_period]}")

#     def create_multi_section_timetable(self):
#         """Create timetables for all sections with conflict resolution"""
#         print("Starting multi-section timetable generation...")
        
#         # Initialize timetables for all batches
#         timetables = {}
#         for batch_id in self.student_batches:
#             timetables[batch_id] = np.full((self.days, self.periods_per_day), None, dtype=object)
        
#         # Step 1: Create synchronized elective slots
#         self.create_synchronized_elective_slots()
        
#         # Step 2: Assign synchronized electives first
#         for batch_id, batch in self.student_batches.items():
#             for course_id in batch.elective_courses:
#                 if (batch_id, course_id) in self.synchronized_slots:
#                     day, period = self.synchronized_slots[(batch_id, course_id)]
#                     course = self.courses[course_id]
                    
#                     # Find suitable classroom
#                     classroom_id = self.find_available_classroom(course, day, period, batch_id)
                    
#                     if classroom_id:
#                         timetables[batch_id][day][period] = {
#                             'course_id': course_id,
#                             'faculty_id': course.faculty_id,
#                             'classroom_id': classroom_id,
#                             'is_lab': False,
#                             'is_synchronized': True
#                         }
                        
#                         # Update global schedules
#                         self.global_room_schedule[classroom_id][day][period] = batch_id
#                         print(f"✓ Assigned synchronized {course_id} for {batch_id}")
        
#         # Step 3: Assign lab courses for each section
#         section_order = list(self.student_batches.keys())
        
#         for batch_id in section_order:
#             batch = self.student_batches[batch_id]
#             print(f"\nScheduling labs for {batch.name}...")
            
#             all_courses = (batch.core_courses + batch.skill_courses + batch.multidisciplinary_courses)
#             lab_courses = [course_id for course_id in all_courses 
#                           if course_id in self.courses and self.courses[course_id].requires_lab]
            
#             for course_id in lab_courses:
#                 course = self.courses[course_id]
#                 duration_periods = self.get_course_duration_periods(course)
                
#                 # Find available lab slot
#                 assigned = False
#                 for day in range(self.days):
#                     for start_period in range(3, self.periods_per_day - 1):  # Prefer afternoon
#                         if self.is_slot_available_for_lab(batch_id, day, start_period, duration_periods, course):
#                             classroom_id = self.find_available_lab_room(course, day, start_period, duration_periods, batch_id)
                            
#                             if classroom_id:
#                                 # Assign lab session
#                                 for i in range(duration_periods):
#                                     period = start_period + i
#                                     timetables[batch_id][day][period] = {
#                                         'course_id': course_id,
#                                         'faculty_id': course.faculty_id,
#                                         'classroom_id': classroom_id,
#                                         'is_lab': True,
#                                         'lab_session_part': i + 1,
#                                         'lab_total_parts': duration_periods
#                                     }
                                    
#                                     # Update global schedules
#                                     self.global_faculty_schedule[course.faculty_id][day][period] = batch_id
#                                     self.global_room_schedule[classroom_id][day][period] = batch_id
                                
#                                 print(f"✓ Assigned lab {course_id} to {self.day_names[day]}, periods {start_period}-{start_period + duration_periods - 1}")
#                                 assigned = True
#                                 break
#                     if assigned:
#                         break
                
#                 if not assigned:
#                     print(f"⚠️ WARNING: Could not assign lab {course_id} for {batch_id}")
        
#         # Step 4: Assign regular theory courses
#         for batch_id in section_order:
#             batch = self.student_batches[batch_id]
#             print(f"\nScheduling theory courses for {batch.name}...")
            
#             all_courses = (batch.core_courses + batch.skill_courses + batch.multidisciplinary_courses)
#             regular_courses = [course_id for course_id in all_courses 
#                                if course_id in self.courses and not self.courses[course_id].requires_lab]
            
#             for course_id in regular_courses:
#                 course = self.courses[course_id]
#                 required_sessions = self.get_effective_hours_per_week(course_id)
#                 scheduled_sessions = 0
                
#                 print(f"Scheduling {course_id} ({course.name}) - needs {required_sessions} sessions")
                
#                 attempts = 0
#                 max_attempts = 50
                
#                 while scheduled_sessions < required_sessions and attempts < max_attempts:
#                     day = random.randrange(self.days)
#                     period = random.randrange(self.periods_per_day)
                    
#                     if (not self.is_lunch_period(period) and 
#                         timetables[batch_id][day][period] is None and
#                         self.is_faculty_available_globally(course.faculty_id, day, period, batch_id) and
#                         not self.has_course_on_day(timetables[batch_id], course_id, day)):
                        
#                         classroom_id = self.find_available_classroom(course, day, period, batch_id)
                        
#                         if classroom_id:
#                             timetables[batch_id][day][period] = {
#                                 'course_id': course_id,
#                                 'faculty_id': course.faculty_id,
#                                 'classroom_id': classroom_id,
#                                 'is_lab': False
#                             }
                            
#                             # Update global schedules
#                             self.global_faculty_schedule[course.faculty_id][day][period] = batch_id
#                             self.global_room_schedule[classroom_id][day][period] = batch_id
                            
#                             scheduled_sessions += 1
#                             print(f"✓ Assigned {course_id} session {scheduled_sessions}/{required_sessions}")
                    
#                     attempts += 1
                
#                 if scheduled_sessions < required_sessions:
#                     print(f"⚠️ WARNING: Only scheduled {scheduled_sessions}/{required_sessions} sessions for {course_id}")
        
#         return timetables

#     def has_course_on_day(self, schedule, course_id: str, day: int) -> bool:
#         """Check if course is already scheduled on given day"""
#         for period in range(self.periods_per_day):
#             slot = schedule[day][period]
#             if slot and slot['course_id'] == course_id:
#                 return True
#         return False

#     def is_slot_available_for_lab(self, batch_id: str, day: int, start_period: int, duration: int, course: NEPCourse) -> bool:
#         """Check if consecutive periods are available for lab"""
#         for i in range(duration):
#             period = start_period + i
#             if (period >= self.periods_per_day or
#                 self.is_lunch_period(period) or
#                 not self.is_faculty_available_globally(course.faculty_id, day, period, batch_id)):
#                 return False
#         return True

#     def is_faculty_available_globally(self, faculty_id: str, day: int, period: int, requesting_batch: str) -> bool:
#         """Check if faculty is available across all sections"""
#         teacher = self.teachers[faculty_id]
        
#         # Check unavailable slots
#         if (day, period) in teacher.unavailable_slots:
#             return False
        
#         # Check research slots
#         if self.preferences.research_slot_protection and (day, period) in teacher.research_slots:
#             return False
        
#         # Check global faculty schedule
#         assigned_batch = self.global_faculty_schedule[faculty_id][day][period]
#         if assigned_batch is not None and assigned_batch != requesting_batch:
#             return False
        
#         return True

#     def find_available_classroom(self, course: NEPCourse, day: int, period: int, batch_id: str) -> Optional[str]:
#         """Find available classroom considering global room schedule"""
#         suitable_rooms = []
        
#         for room_id, room in self.classrooms.items():
#             if (room.capacity >= course.max_students and
#                 not self.is_room_occupied_globally(room_id, day, period, batch_id)):
                
#                 pref_score = 0
#                 if room.department == course.department:
#                     pref_score += 10
#                 if course.requires_smart_room and room.is_smart_room:
#                     pref_score += 15
                
#                 suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         return None

#     def find_available_lab_room(self, course: NEPCourse, day: int, start_period: int, duration: int, batch_id: str) -> Optional[str]:
#         """Find available lab room for consecutive periods"""
#         suitable_rooms = []
        
#         for room_id, room in self.classrooms.items():
#             if (room.room_type in [RoomType.LAB, RoomType.COMPUTER_LAB] and
#                 room.capacity >= course.max_students):
                
#                 # Check availability for all periods
#                 available = True
#                 for i in range(duration):
#                     period = start_period + i
#                     if self.is_room_occupied_globally(room_id, day, period, batch_id):
#                         available = False
#                         break
                
#                 if available:
#                     pref_score = 0
#                     if room.department == course.department:
#                         pref_score += 10
#                     suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         return None

#     def is_room_occupied_globally(self, room_id: str, day: int, period: int, requesting_batch: str) -> bool:
#         """Check if room is occupied across all sections"""
#         room = self.classrooms[room_id]
        
#         # Check maintenance slots
#         if (day, period) in room.weekly_maintenance:
#             return True
        
#         # Check global room schedule
#         assigned_batch = self.global_room_schedule[room_id][day][period]
#         if assigned_batch is not None and assigned_batch != requesting_batch:
#             return True
        
#         return False

#     def generate_multi_section_timetables(self, population_size: int = 20, generations: int = 30) -> dict:
#         """Generate optimized timetables for all sections"""
#         print("Initializing multi-section timetable generation...")
        
#         best_timetables = None
#         best_fitness = 0
        
#         for attempt in range(5):  # Try multiple times to get good solution
#             print(f"\nAttempt {attempt + 1}/5...")
            
#             # Reset global schedules
#             self.global_faculty_schedule = defaultdict(lambda: defaultdict(lambda: None))
#             self.global_room_schedule = defaultdict(lambda: defaultdict(lambda: None))
#             self.synchronized_slots = {}
            
#             # Create timetables
#             timetables = self.create_multi_section_timetable()
            
#             # Calculate fitness
#             fitness = self.calculate_multi_section_fitness(timetables)
            
#             print(f"Fitness: {fitness:.2f}")
            
#             if fitness > best_fitness:
#                 best_fitness = fitness
#                 best_timetables = copy.deepcopy(timetables)
                
#                 # If fitness is good enough, stop
#                 if fitness >= 700:
#                     print(f"Found good solution with fitness {fitness:.2f}")
#                     break
        
#         return best_timetables

#     def calculate_multi_section_fitness(self, timetables: dict) -> float:
#         """Calculate fitness for multi-section timetables"""
#         base_score = 1000.0
#         penalty = 0.0
        
#         # Check for conflicts across sections
#         penalty += self.check_faculty_conflicts_global(timetables) * 200
#         penalty += self.check_room_conflicts_global(timetables) * 200
#         penalty += self.check_synchronized_electives(timetables) * 100
        
#         # Check individual section quality
#         for batch_id, timetable in timetables.items():
#             penalty += self.check_course_requirements_individual(batch_id, timetable) * 50
#             penalty += self.check_lunch_violations_individual(timetable) * 30
        
#         return max(0, base_score - penalty)

#     def check_faculty_conflicts_global(self, timetables: dict) -> int:
#         """Check for faculty conflicts across all sections"""
#         conflicts = 0
#         faculty_usage = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetables.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         faculty_id = slot['faculty_id']
#                         faculty_usage[faculty_id][day].append((period, batch_id))
        
#         # Check for overlapping assignments
#         for faculty_id, days in faculty_usage.items():
#             for day, assignments in days.items():
#                 periods_used = [period for period, batch in assignments]
#                 conflicts += len(periods_used) - len(set(periods_used))
        
#         return conflicts

#     def check_room_conflicts_global(self, timetables: dict) -> int:
#         """Check for room conflicts across all sections"""
#         conflicts = 0
#         room_usage = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetables.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         room_id = slot['classroom_id']
#                         room_usage[room_id][day].append((period, batch_id))
        
#         # Check for overlapping room usage
#         for room_id, days in room_usage.items():
#             for day, assignments in days.items():
#                 periods_used = [period for period, batch in assignments]
#                 conflicts += len(periods_used) - len(set(periods_used))
        
#         return conflicts

#     def check_synchronized_electives(self, timetables: dict) -> int:
#         """Check if PE/OE are properly synchronized"""
#         violations = 0
        
#         # Check PE synchronization
#         pe_slots = {}
#         oe_slots = {}
        
#         for batch_id, schedule in timetables.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course_id = slot['course_id']
#                         if course_id.startswith('PE_I') or course_id == '#PE-I':
#                             pe_slots[batch_id] = (day, period)
#                         elif course_id.startswith('OE_I') or course_id == '#OE-I':
#                             oe_slots[batch_id] = (day, period)
        
#         # Check if all PE courses are at same time
#         if len(pe_slots) > 1:
#             pe_times = list(pe_slots.values())
#             if len(set(pe_times)) > 1:
#                 violations += 1
        
#         # Check if all OE courses are at same time
#         if len(oe_slots) > 1:
#             oe_times = list(oe_slots.values())
#             if len(set(oe_times)) > 1:
#                 violations += 1
        
#         return violations

#     def check_course_requirements_individual(self, batch_id: str, schedule) -> int:
#         """Check course hour requirements for individual batch"""
#         violations = 0
#         batch = self.student_batches[batch_id]
#         course_hours = defaultdict(int)
        
#         for day in range(self.days):
#             for period in range(self.periods_per_day):
#                 slot = schedule[day][period]
#                 if slot:
#                     course_hours[slot['course_id']] += 1
        
#         all_courses = (batch.core_courses + batch.elective_courses + 
#                        batch.skill_courses + batch.multidisciplinary_courses)
        
#         for course_id in all_courses:
#             if course_id in self.courses:
#                 required = self.get_effective_hours_per_week(course_id)
#                 actual = course_hours[course_id]
                
#                 if self.courses[course_id].requires_lab:
#                     # For labs, each session counts as 1 but represents more time
#                     if actual != required:
#                         violations += abs(actual - required)
#                 else:
#                     # For regular courses
#                     if actual != required:
#                         violations += abs(actual - required)
        
#         return violations

#     def check_lunch_violations_individual(self, schedule) -> int:
#         """Check lunch violations for individual schedule"""
#         violations = 0
#         for day in range(self.days):
#             if schedule[day][self.preferences.lunch_break_start] is not None:
#                 violations += 1
#         return violations

#     def export_multi_section_timetable(self, timetables: dict, filename: str = "multi_section_timetable.json") -> dict:
#         """Export multi-section timetable with conflict analysis"""
#         export_data = {
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "nep_2020_compliant": True,
#                 "total_sections": len(timetables),
#                 "working_days": self.days,
#                 "periods_per_day": self.periods_per_day,
#                 "time_slots": self.time_slots,
#                 "college_hours": f"{self.preferences.morning_start_time} - {self.preferences.evening_end_time}",
#                 "special_features": [
#                     "Multi-section conflict resolution",
#                     "Synchronized PE/OE across sections", 
#                     "Deep Learning frequency control (2x per week)",
#                     "Lab session continuity"
#                 ]
#             },
#             "timetables": {},
#             "conflict_analysis": {},
#             "synchronized_courses": {},
#             "analytics": {}
#         }
        
#         # Export each section's timetable
#         for batch_id, schedule in timetables.items():
#             batch = self.student_batches[batch_id]
#             batch_data = {
#                 "batch_info": {
#                     "name": batch.name,
#                     "department": batch.department,
#                     "semester": batch.semester,
#                     "student_count": batch.student_count
#                 },
#                 "weekly_schedule": []
#             }
            
#             for day in range(self.days):
#                 day_schedule = {
#                     "day": self.day_names[day],
#                     "periods": []
#                 }
                
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         teacher = self.teachers[slot['faculty_id']]
#                         classroom = self.classrooms[slot['classroom_id']]
                        
#                         period_data = {
#                             "time": self.time_slots[period],
#                             "course": {
#                                 "id": course.id,
#                                 "name": course.name,
#                                 "code": course.code,
#                                 "type": course.course_type.value,
#                                 "credits": course.credits,
#                                 "department": course.department,
#                                 "is_lab": slot.get('is_lab', False)
#                             },
#                             "faculty": {
#                                 "id": teacher.id,
#                                 "name": teacher.name,
#                                 "designation": teacher.designations
#                             },
#                             "classroom": {
#                                 "id": classroom.id,
#                                 "name": classroom.name,
#                                 "type": classroom.room_type.value,
#                                 "capacity": classroom.capacity
#                             },
#                             "section_specific": {
#                                 "is_synchronized": slot.get('is_synchronized', False),
#                                 "is_lab_session": slot.get('is_lab', False)
#                             }
#                         }
                        
#                         # Add lab session details
#                         if slot.get('is_lab', False):
#                             period_data['lab_session'] = {
#                                 "part": slot.get('lab_session_part', 1),
#                                 "total_parts": slot.get('lab_total_parts', 1)
#                             }
#                     else:
#                         if self.is_lunch_period(period):
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "lunch_break"
#                             }
#                         else:
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "free"
#                             }
                    
#                     day_schedule["periods"].append(period_data)
                
#                 batch_data["weekly_schedule"].append(day_schedule)
            
#             export_data["timetables"][batch.name] = batch_data
        
#         # Analyze conflicts
#         export_data["conflict_analysis"] = {
#             "faculty_conflicts": self.check_faculty_conflicts_global(timetables),
#             "room_conflicts": self.check_room_conflicts_global(timetables),
#             "synchronization_issues": self.check_synchronized_electives(timetables),
#             "total_violations": self.calculate_multi_section_fitness(timetables)
#         }
        
#         # Track synchronized courses
#         pe_oe_schedule = {}
#         for batch_id, schedule in timetables.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot and slot.get('is_synchronized', False):
#                         course_id = slot['course_id']
#                         time_key = f"{self.day_names[day]}_{self.time_slots[period]}"
                        
#                         if time_key not in pe_oe_schedule:
#                             pe_oe_schedule[time_key] = []
                        
#                         pe_oe_schedule[time_key].append({
#                             "section": batch.name,
#                             "course": course_id,
#                             "faculty": self.teachers[slot['faculty_id']].name
#                         })
        
#         export_data["synchronized_courses"] = pe_oe_schedule
        
#         # Calculate analytics
#         export_data["analytics"] = self.calculate_multi_section_analytics(timetables)
        
#         # Save to file
#         with open(filename, 'w') as f:
#             json.dump(export_data, f, indent=2, default=str)
        
#         print(f"Multi-section timetable exported to {filename}")
#         return export_data

#     def calculate_multi_section_analytics(self, timetables: dict) -> dict:
#         """Calculate analytics for multi-section timetables"""
#         analytics = {
#             "overall_fitness": self.calculate_multi_section_fitness(timetables),
#             "section_summaries": {},
#             "resource_utilization": {
#                 "faculty": {},
#                 "classrooms": {},
#                 "labs": {}
#             },
#             "course_frequency_analysis": {},
#             "synchronization_status": {
#                 "pe_courses": [],
#                 "oe_courses": []
#             }
#         }
        
#         # Analyze each section
#         for batch_id, schedule in timetables.items():
#             batch = self.student_batches[batch_id]
            
#             section_stats = {
#                 "total_sessions": 0,
#                 "lab_sessions": 0,
#                 "theory_sessions": 0,
#                 "synchronized_sessions": 0,
#                 "course_distribution": defaultdict(int)
#             }
            
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         section_stats["total_sessions"] += 1
                        
#                         if slot.get('is_lab', False):
#                             section_stats["lab_sessions"] += 1
#                         else:
#                             section_stats["theory_sessions"] += 1
                        
#                         if slot.get('is_synchronized', False):
#                             section_stats["synchronized_sessions"] += 1
                        
#                         course_id = slot['course_id']
#                         section_stats["course_distribution"][course_id] += 1
            
#             analytics["section_summaries"][batch.name] = section_stats
        
#         # Check course frequency compliance (especially Deep Learning = 2x per week)
#         for course_id, expected_freq in self.course_frequency_override.items():
#             course_frequencies = {}
#             for batch_id, schedule in timetables.items():
#                 count = 0
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = schedule[day][period]
#                         if slot and slot['course_id'] == course_id:
#                             count += 1
#                 course_frequencies[batch_id] = count
            
#             analytics["course_frequency_analysis"][course_id] = {
#                 "expected": expected_freq,
#                 "actual": course_frequencies,
#                 "compliant": all(freq == expected_freq for freq in course_frequencies.values())
#             }
        
#         return analytics

#     def print_multi_section_summary(self, timetables: dict):
#         """Print comprehensive summary for multi-section timetables"""
#         print("\n" + "="*80)
#         print("MULTI-SECTION TIMETABLE GENERATION SUMMARY")
#         print("="*80)
        
#         analytics = self.calculate_multi_section_analytics(timetables)
        
#         print(f"\nOVERALL METRICS:")
#         print(f"    Total Sections: {len(timetables)}")
#         print(f"    Overall Fitness: {analytics['overall_fitness']:.2f}/1000")
#         print(f"    College Hours: {self.preferences.morning_start_time} - {self.preferences.evening_end_time}")
#         print(f"    Working Days: {self.days}")
        
#         print(f"\nCONFLICT ANALYSIS:")
#         conflicts = self.check_faculty_conflicts_global(timetables)
#         room_conflicts = self.check_room_conflicts_global(timetables)
#         sync_issues = self.check_synchronized_electives(timetables)
        
#         print(f"    Faculty Conflicts: {conflicts} {'✓' if conflicts == 0 else '✗'}")
#         print(f"    Room Conflicts: {room_conflicts} {'✓' if room_conflicts == 0 else '✗'}")
#         print(f"    Synchronization Issues: {sync_issues} {'✓' if sync_issues == 0 else '✗'}")
        
#         print(f"\nCOURSE FREQUENCY COMPLIANCE:")
#         for course_id, analysis in analytics["course_frequency_analysis"].items():
#             course_name = self.courses[course_id].name if course_id in self.courses else course_id
#             print(f"    {course_name}:")
#             print(f"        Expected: {analysis['expected']} sessions/week")
#             print(f"        Compliant: {'✓' if analysis['compliant'] else '✗'}")
#             for batch_id, actual in analysis["actual"].items():
#                 batch_name = self.student_batches[batch_id].name
#                 print(f"            {batch_name}: {actual} sessions")
        
#         print(f"\nSECTION SUMMARIES:")
#         for section_name, stats in analytics["section_summaries"].items():
#             print(f"    {section_name}:")
#             print(f"        Total Sessions: {stats['total_sessions']}")
#             print(f"        Lab Sessions: {stats['lab_sessions']}")
#             print(f"        Theory Sessions: {stats['theory_sessions']}")
#             print(f"        Synchronized Sessions: {stats['synchronized_sessions']}")
        
#         # Print sample timetable comparison
#         print(f"\nSAMPLE TIMETABLE COMPARISON (Monday):")
#         print("-" * 100)
        
#         # Header
#         header = "Time".ljust(15)
#         for batch_id in list(timetables.keys())[:3]:  # Show up to 3 sections
#             batch_name = self.student_batches[batch_id].name.split(' - ')[-1]  # Get section part
#             header += batch_name.ljust(25)
#         print(header)
#         print("-" * 100)
        
#         # Show Monday schedule
#         for period in range(self.periods_per_day):
#             row = self.time_slots[period].ljust(15)
            
#             for batch_id in list(timetables.keys())[:3]:
#                 schedule = timetables[batch_id]
#                 slot = schedule[0][period]  # Monday = day 0
                
#                 if slot:
#                     course = self.courses[slot['course_id']]
#                     display_name = course.name
#                     if slot.get('is_lab', False):
#                         part = slot.get('lab_session_part', 1)
#                         total = slot.get('lab_total_parts', 1)
#                         display_name += f" (Lab {part}/{total})"
#                     elif slot.get('is_synchronized', False):
#                         display_name += " (SYNC)"
                    
#                     # Truncate long names
#                     if len(display_name) > 22:
#                         display_name = display_name[:22] + "..."
#                     row += display_name.ljust(25)
#                 elif self.is_lunch_period(period):
#                     row += "LUNCH BREAK".ljust(25)
#                 else:
#                     row += "Free".ljust(25)
            
#             print(row)


# # Web API Integration Functions
# def create_multi_section_system_from_json(json_input: str, user_preferences: dict = None) -> MultiSectionTimetableGenerator:
#     """Create multi-section system from JSON input"""
#     prefs = UserPreferences()
#     if user_preferences:
#         for key, value in user_preferences.items():
#             if hasattr(prefs, key):
#                 setattr(prefs, key, value)
    
#     generator = MultiSectionTimetableGenerator(user_preferences=prefs)
#     generator.load_from_json(json_input)
    
#     return generator

# def generate_multi_section_timetable_api(json_input: str, user_preferences: dict = None, 
#                                        population_size: int = 20, generations: int = 30) -> dict:
#     """Main API function for multi-section timetable generation"""
#     print("Starting Multi-Section NEP 2020 Compliant Timetable Generation...")
    
#     # Create system
#     generator = create_multi_section_system_from_json(json_input, user_preferences)
    
#     # Generate timetables
#     best_timetables = generator.generate_multi_section_timetables(population_size, generations)
    
#     if best_timetables:
#         # Export and return result
#         result = generator.export_multi_section_timetable(best_timetables)
#         generator.print_multi_section_summary(best_timetables)
#         return result
#     else:
#         raise Exception("Failed to generate valid multi-section timetable. Please check constraints.")

# # Main execution for testing
# if __name__ == "__main__":
#     # Test with your AIML sections data
#     sample_json = json.dumps({
#         "courses": [
#             # Core courses
#             {"id": "B23AM3101", "name": "Deep Learning", "code": "B23AM3101", "credits": 3, 
#              "course_type": "core", "hours_per_week": 3, "department": "AIML", "semester": 5, 
#              "faculty_id": "1", "requires_lab": False, "max_students": 16},
#             {"id": "B23AM3102", "name": "Computer Networks", "code": "B23AM3102", "credits": 3,
#              "course_type": "core", "hours_per_week": 3, "department": "AIML", "semester": 5,
#              "faculty_id": "3", "requires_lab": False, "max_students": 16},
#             {"id": "B23AM3103", "name": "Natural Language Processing", "code": "B23AM3103", "credits": 3,
#              "course_type": "core", "hours_per_week": 3, "department": "AIML", "semester": 5,
#              "faculty_id": "2", "requires_lab": False, "max_students": 16},
            
#             # Lab courses
#             {"id": "B23AM3110", "name": "Deep Learning Lab", "code": "B23AM3110", "credits": 0,
#              "course_type": "core", "hours_per_week": 1, "department": "AIML", "semester": 5,
#              "faculty_id": "1", "requires_lab": True, "max_students": 16, "min_duration_minutes": 180},
#             {"id": "B23AM3111", "name": "Natural Language Processing Lab", "code": "B23AM3111", "credits": 0,
#              "course_type": "skill_enhancement", "hours_per_week": 1, "department": "AIML", "semester": 5,
#              "faculty_id": "2", "requires_lab": True, "max_students": 16, "min_duration_minutes": 180},
#             {"id": "B23AM3112", "name": "Full Stack Development -2", "code": "B23AM3112", "credits": 0,
#              "course_type": "core", "hours_per_week": 1, "department": "AIML", "semester": 5,
#              "faculty_id": "4", "requires_lab": True, "max_students": 16, "min_duration_minutes": 180},
#             {"id": "B23AM3113", "name": "Tinkering Lab (UI Design using Flutter)", "code": "B23AM3113", "credits": 0,
#              "course_type": "skill_enhancement", "hours_per_week": 1, "department": "AIML", "semester": 5,
#              "faculty_id": "4", "requires_lab": True, "max_students": 16, "min_duration_minutes": 180},
            
#             # Elective courses for each section
#             {"id": "PE_I_A", "name": "Professional Elective A", "code": "PE_I_A", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "5", "requires_lab": False, "max_students": 16},
#             {"id": "PE_I_B", "name": "Professional Elective B", "code": "PE_I_B", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "5", "requires_lab": False, "max_students": 16},
#             {"id": "PE_I_C", "name": "Professional Elective C", "code": "PE_I_C", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "5", "requires_lab": False, "max_students": 16},
            
#             {"id": "OE_I_A", "name": "Open Elective A", "code": "OE_I_A", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "6", "requires_lab": False, "max_students": 16},
#             {"id": "OE_I_B", "name": "Open Elective B", "code": "OE_I_B", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "6", "requires_lab": False, "max_students": 16},
#             {"id": "OE_I_C", "name": "Open Elective C", "code": "OE_I_C", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "6", "requires_lab": False, "max_students": 16},
            
#             # Common courses
#             {"id": "B23AM3114", "name": "Evaluation of Community Service Internship", "code": "B23AM3114", "credits": 1,
#              "course_type": "project", "hours_per_week": 3, "department": "AIML", "semester": 5,
#              "faculty_id": "8", "requires_lab": False, "max_students": 16},
#             {"id": "B23MC3101", "name": "Employability Skills", "code": "B23MC3101", "credits": 0,
#              "course_type": "core", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "8", "requires_lab": False, "max_students": 16}
#         ],
#         "faculty": [
#             {"id": "1", "name": "Dr P Ravi Kiran Varma", "department": "CSE", "designation": "Professor", 
#              "specializations": ["Deep Learning"], "courses_can_teach": ["B23AM3101", "B23AM3110"]},
#             {"id": "2", "name": "Dr. Bh V S Rama Krishnam Raju", "department": "CSE", "designation": "Professor",
#              "specializations": ["Natural Language Processing"], "courses_can_teach": ["B23AM3103", "B23AM3111"]},
#             {"id": "3", "name": "Dr. M S V S Bhadri Raju", "department": "CSE", "designation": "Professor",
#              "specializations": ["Computer Networks"], "courses_can_teach": ["B23AM3102"]},
#             {"id": "4", "name": "Dr. K V Krishnam Raju", "department": "CSE", "designation": "Professor",
#              "specializations": ["Full Stack Development"], "courses_can_teach": ["B23AM3112", "B23AM3113"]},
#             {"id": "5", "name": "Dr. G Mahesh", "department": "CSE", "designation": "Professor",
#              "specializations": ["Professional Electives"], "courses_can_teach": ["PE_I_A", "PE_I_B", "PE_I_C"]},
#             {"id": "6", "name": "Dr. V Chandra Sekhar", "department": "CSE", "designation": "Professor",
#              "specializations": ["Open Electives"], "courses_can_teach": ["OE_I_A", "OE_I_B", "OE_I_C"]},
#             {"id": "8", "name": "Dr. R N V Jagan Mohan", "department": "CSE", "designation": "Associate Professor",
#              "specializations": ["General"], "courses_can_teach": ["B23AM3114", "B23MC3101"]}
#         ],
#         "classrooms": [
#             {"id": "C101", "name": "C101", "capacity": 70, "room_type": "smart_classroom", "department": "CSE", "equipment": []},
#             {"id": "C102", "name": "C102", "capacity": 70, "room_type": "smart_classroom", "department": "CSE", "equipment": []},
#             {"id": "C103", "name": "C103", "capacity": 70, "room_type": "lecture", "department": "CSE", "equipment": []},
#             {"id": "LAB-401", "name": "AI/ML Lab", "capacity": 40, "room_type": "computer_lab", "department": "CSE", "equipment": []},
#             {"id": "LAB-G01", "name": "Computer Lab 1", "capacity": 40, "room_type": "computer_lab", "department": "CSE", "equipment": []},
#             {"id": "LAB-G02", "name": "Computer Lab 2", "capacity": 40, "room_type": "computer_lab", "department": "CSE", "equipment": []}
#         ],
#         "student_batches": [
#             {"id": "AIML_S5_A", "name": "AI & ML Semester 5 - Section A", "department": "AIML", "semester": 5, "student_count": 16,
#              "core_courses": ["B23AM3101", "B23AM3102", "B23AM3103", "B23AM3110", "B23AM3112"],
#              "elective_courses": ["PE_I_A", "OE_I_A"], "skill_courses": ["B23AM3111", "B23AM3113"],
#              "multidisciplinary_courses": ["B23AM3114", "B23MC3101"]},
#             {"id": "AIML_S5_B", "name": "AI & ML Semester 5 - Section B", "department": "AIML", "semester": 5, "student_count": 16,
#              "core_courses": ["B23AM3101", "B23AM3102", "B23AM3103", "B23AM3110", "B23AM3112"],
#              "elective_courses": ["PE_I_B", "OE_I_B"], "skill_courses": ["B23AM3111", "B23AM3113"],
#              "multidisciplinary_courses": ["B23AM3114", "B23MC3101"]},
#             {"id": "AIML_S5_C", "name": "AI & ML Semester 5 - Section C", "department": "AIML", "semester": 5, "student_count": 16,
#              "core_courses": ["B23AM3101", "B23AM3102", "B23AM3103", "B23AM3110", "B23AM3112"],
#              "elective_courses": ["PE_I_C", "OE_I_C"], "skill_courses": ["B23AM3111", "B23AM3113"],
#              "multidisciplinary_courses": ["B23AM3114", "B23MC3101"]}
#         ]
#     })
    
#     try:
#         result = generate_multi_section_timetable_api(sample_json, population_size=15, generations=20)
#         print(f"\nMulti-section timetable generated successfully!")
        
#     except Exception as e:
#         print(f"Error: {e}")
#         import traceback
#         traceback.print_exc()



# import json
# import numpy as np
# import pandas as pd
# from datetime import datetime, timedelta
# import random
# from dataclasses import dataclass, asdict
# from typing import List, Dict, Tuple, Optional, Union
# from collections import defaultdict
# from enum import Enum
# import copy
# import math

# class CourseType(Enum):
#     CORE = "core"
#     ELECTIVE = "elective" 
#     MULTIDISCIPLINARY = "multidisciplinary"
#     SKILL_ENHANCEMENT = "skill_enhancement"
#     VALUE_ADDED = "value_added"
#     ABILITY_ENHANCEMENT = "ability_enhancement"
#     SEMINAR = "seminar"
#     PROJECT = "project"
#     HONORS = "honors"
#     MINOR = "minor"

# class RoomType(Enum):
#     LECTURE = "lecture"
#     LAB = "lab"
#     SEMINAR = "seminar"
#     COMPUTER_LAB = "computer_lab"
#     SMART_CLASSROOM = "smart_classroom"
#     AUDITORIUM = "auditorium"

# class TimePreference(Enum):
#     MORNING = "morning"
#     AFTERNOON = "afternoon"
#     EVENING = "evening"
#     ANY = "any"

# @dataclass
# class NEPCourse:
#     """Enhanced course structure following NEP 2020 guidelines"""
#     id: str
#     name: str
#     code: str
#     credits: int
#     course_type: CourseType
#     hours_per_week: int
#     department: str
#     semester: int
#     faculty_id: str
#     requires_lab: bool = False
#     requires_smart_room: bool = False
#     is_interdisciplinary: bool = False
#     connected_departments: List[str] = None
#     max_students: int = 60
#     min_duration_minutes: int = 50
#     max_consecutive_hours: int = 2
#     preferred_days: List[int] = None
    
#     def __post_init__(self):
#         if self.connected_departments is None:
#             self.connected_departments = []
#         if self.preferred_days is None:
#             self.preferred_days = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPCourse from dictionary"""
#         if isinstance(data['course_type'], str):
#             course_type_str = data['course_type'].lower().strip()
#             if course_type_str == 'honors':
#                 data['course_type'] = CourseType.HONORS
#             elif course_type_str == 'minor':
#                 data['course_type'] = CourseType.MINOR
#             else:
#                 try:
#                     data['course_type'] = CourseType(course_type_str)
#                 except ValueError:
#                     print(f"Warning: Unknown course type '{data['course_type']}', defaulting to 'core'")
#                     data['course_type'] = CourseType.CORE
#         return cls(**data)

# @dataclass 
# class NEPFaculty:
#     """Faculty with NEP 2020 compliant parameters"""
#     id: str
#     name: str
#     department: str
#     designations: str
#     specializations: List[str]
#     courses_can_teach: List[str]
#     max_hours_per_day: int = 6
#     max_hours_per_week: int = 24
#     preferred_time: TimePreference = TimePreference.ANY
#     unavailable_slots: List[Tuple[int, int]] = None
#     research_slots: List[Tuple[int, int]] = None
#     is_visiting: bool = False
#     workload_preference: float = 1.0
    
#     def __post_init__(self):
#         if self.unavailable_slots is None:
#             self.unavailable_slots = []
#         if self.research_slots is None:
#             self.research_slots = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPFaculty from dictionary"""
#         if 'designation' in data:
#             data['designations'] = data.pop('designation')
#         if isinstance(data.get('preferred_time'), str):
#             data['preferred_time'] = TimePreference(data['preferred_time'])
#         return cls(**data)

# @dataclass
# class NEPClassroom:
#     """Classroom with modern facilities"""
#     id: str
#     name: str
#     capacity: int
#     room_type: RoomType
#     department: str
#     equipment: List[str]
#     is_smart_room: bool = False
#     is_ac: bool = False
#     has_projector: bool = True
#     weekly_maintenance: List[Tuple[int, int]] = None
    
#     def __post_init__(self):
#         if self.weekly_maintenance is None:
#             self.weekly_maintenance = []
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPClassroom from dictionary"""
#         if isinstance(data['room_type'], str):
#             data['room_type'] = RoomType(data['room_type'])
#         return cls(**data)

# @dataclass
# class NEPStudentBatch:
#     """Student batch/class with NEP parameters"""
#     id: str
#     name: str
#     department: str
#     semester: int
#     student_count: int
#     core_courses: List[str]
#     elective_courses: List[str]
#     skill_courses: List[str]
#     multidisciplinary_courses: List[str]
#     preferred_morning_hours: bool = True
#     max_hours_per_day: int = 7
    
#     @classmethod
#     def from_dict(cls, data):
#         """Create NEPStudentBatch from dictionary"""
#         return cls(**data)

# @dataclass
# class UserPreferences:
#     """User-configurable preferences"""
#     working_days: int = 5
#     periods_per_day: int = 5  # Updated for your schedule
#     lunch_break_start: int = 2  # Period where lunch starts (0-based index)
#     lunch_break_end: int = 2    # Period where lunch ends (0-based index)
#     max_consecutive_same_subject: int = 2
#     gap_penalty_weight: float = 10.0
#     faculty_preference_weight: float = 15.0
#     workload_balance_weight: float = 20.0
#     room_preference_weight: float = 5.0
#     interdisciplinary_bonus: float = 10.0
#     research_slot_protection: bool = True
#     allow_saturday_classes: bool = False
#     morning_start_time: str = "9:00"
#     evening_end_time: str = "4:30"

# class MultiSectionTimetableGenerator:
#     """Enhanced timetable generator for multiple sections with conflict resolution"""
    
#     def __init__(self, config_json: str = None, user_preferences: UserPreferences = None):
#         self.preferences = user_preferences or UserPreferences()
#         self.days = 6 if self.preferences.allow_saturday_classes else 5
#         self.periods_per_day = self.preferences.periods_per_day
        
#         # Data containers
#         self.courses = {}
#         self.teachers = {}
#         self.classrooms = {}
#         self.student_batches = {}
#         self.departments = set()
        
#         # Multi-section management - Fixed initialization
#         self.global_faculty_schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))  
#         self.global_room_schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))     
#         self.synchronized_slots = {}  # For PE/OE synchronization
        
#         # Generate time slots
#         self.generate_time_slots()
#         self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:self.days]
        
#         # Course frequency overrides (theory courses need 2 sessions per week)
#         self.course_frequency_override = {
#             "B23AM3101": 2,  # Deep Learning - 2 times per week
#             "B23AM3102": 2,  # Computer Networks - 2 times per week  
#             "B23AM3103": 2,  # Natural Language Processing - 2 times per week
#             "#PE-I": 2,      # Professional Elective - 2 times per week
#             "#OE-I": 2,      # Open Elective - 2 times per week
#             "PE_I_A": 2, "PE_I_B": 2, "PE_I_C": 2,  # PE variants
#             "OE_I_A": 2, "OE_I_B": 2, "OE_I_C": 2,  # OE variants
#             # Labs remain 1 session per week (4-hour continuous)
#             "B23AM3110": 1,  # Deep Learning Lab
#             "B23AM3111": 1,  # NLP Lab
#             "B23AM3112": 1,  # Full Stack Development Lab
#             "B23AM3113": 1,  # Tinkering Lab
#         }
        
#         if config_json:
#             self.load_from_json(config_json)

#     def generate_time_slots(self):
#         """Generate time slots matching college schedule (9:00 AM to 4:30 PM)"""
#         self.time_slots = [
#             "09:00-10:30",  # 0 - Morning session 1
#             "10:30-12:00",  # 1 - Morning session 2
#             "12:00-01:30",  # 2 - LUNCH BREAK
#             "01:30-03:00",  # 3 - Afternoon session 1  
#             "03:00-04:30",  # 4 - Afternoon session 2
#         ]
        
#         self.periods_per_day = len(self.time_slots)
#         self.preferences.lunch_break_start = 2
#         self.preferences.lunch_break_end = 2
        
#         print(f"Generated {self.periods_per_day} time slots for college schedule 9:00-4:30")

#     def load_from_json(self, config_json: str):
#         """Load configuration from JSON string"""
#         try:
#             data = json.loads(config_json)
#         except json.JSONDecodeError as e:
#             print(f"Error: Invalid JSON format provided. Details: {e}")
#             return

#         # Load Courses
#         for course_data in data.get("courses", []):
#             try:
#                 course_obj = NEPCourse.from_dict(course_data)
#                 self.add_course(course_obj)
#             except Exception as e:
#                 print(f"Error loading course {course_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Faculty
#         for faculty_data in data.get("faculty", []):
#             try:
#                 teacher_obj = NEPFaculty.from_dict(faculty_data)
#                 self.add_teacher(teacher_obj)
#             except Exception as e:
#                 print(f"Error loading faculty {faculty_data.get('id', 'unknown')}: {e}")
#                 continue

#         # Load Classrooms
#         for classroom_data in data.get("classrooms", []):
#             try:
#                 classroom_obj = NEPClassroom.from_dict(classroom_data)
#                 self.add_classroom(classroom_obj)
#             except Exception as e:
#                 print(f"Error loading classroom {classroom_data.get('id', 'unknown')}: {e}")
#                 continue
            
#         # Load Student Batches
#         for batch_data in data.get("student_batches", []):
#             try:
#                 batch_obj = NEPStudentBatch.from_dict(batch_data)
#                 self.add_student_batch(batch_obj)
#             except Exception as e:
#                 print(f"Error loading batch {batch_data.get('id', 'unknown')}: {e}")
#                 continue

#         print("Configuration loaded successfully from JSON.")

#     def add_course(self, course: NEPCourse):
#         """Add course to system"""
#         self.courses[course.id] = course
#         self.departments.add(course.department)
    
#     def add_teacher(self, teacher: NEPFaculty):
#         """Add teacher to system"""
#         if teacher.research_slots:
#             teacher.research_slots = [
#                 (day, period) for day, period in teacher.research_slots 
#                 if day < self.days and period < self.periods_per_day
#             ]
#         if teacher.unavailable_slots:
#             teacher.unavailable_slots = [
#                 (day, period) for day, period in teacher.unavailable_slots
#                 if day < self.days and period < self.periods_per_day
#             ]
        
#         self.teachers[teacher.id] = teacher
#         self.departments.add(teacher.department)
    
#     def add_classroom(self, classroom: NEPClassroom):
#         """Add classroom to system"""
#         if classroom.weekly_maintenance:
#             classroom.weekly_maintenance = [
#                 (day, period) for day, period in classroom.weekly_maintenance
#                 if day < self.days and period < self.periods_per_day
#             ]

#         self.classrooms[classroom.id] = classroom
#         self.departments.add(classroom.department)
    
#     def add_student_batch(self, batch: NEPStudentBatch):
#         """Add student batch to system"""
#         self.student_batches[batch.id] = batch
#         self.departments.add(batch.department)

#     def get_course_duration_periods(self, course: NEPCourse) -> int:
#         """Calculate how many periods a course requires"""
#         if course.requires_lab or course.min_duration_minutes >= 180:
#             return 2  # Lab takes 2 consecutive periods (3 hours total)
#         else:
#             return 1  # Regular class takes 1 period (1.5 hours)

#     def is_lunch_period(self, period: int) -> bool:
#         """Check if the given period is lunch break"""
#         return period == self.preferences.lunch_break_start

#     def get_effective_hours_per_week(self, course_id: str) -> int:
#         """Get effective hours per week considering overrides"""
#         if course_id in self.course_frequency_override:
#             return self.course_frequency_override[course_id]
#         elif course_id in self.courses:
#             return self.courses[course_id].hours_per_week
#         return 1

#     def create_multi_section_timetable(self):
#         """Create timetables for all sections with conflict resolution"""
#         print("Starting multi-section timetable generation...")
        
#         # Initialize timetables for all batches
#         timetables = {}
#         for batch_id in self.student_batches:
#             timetables[batch_id] = np.full((self.days, self.periods_per_day), None, dtype=object)
        
#         # Step 1: Assign lab courses for each section (highest priority)
#         section_order = list(self.student_batches.keys())
        
#         for batch_id in section_order:
#             batch = self.student_batches[batch_id]
#             print(f"\nScheduling labs for {batch.name}...")
            
#             all_courses = (batch.core_courses + batch.skill_courses + batch.multidisciplinary_courses)
#             lab_courses = [course_id for course_id in all_courses 
#                           if course_id in self.courses and self.courses[course_id].requires_lab]
            
#             for course_id in lab_courses:
#                 course = self.courses[course_id]
#                 duration_periods = self.get_course_duration_periods(course)
                
#                 # Find available lab slot (prefer afternoon slots)
#                 assigned = False
#                 for day in range(self.days):
#                     for start_period in range(3, self.periods_per_day - duration_periods + 1):  # Afternoon slots
#                         if self.is_slot_available_for_lab(batch_id, day, start_period, duration_periods, course):
#                             classroom_id = self.find_available_lab_room(course, day, start_period, duration_periods, batch_id)
                            
#                             if classroom_id:
#                                 # Assign lab session
#                                 for i in range(duration_periods):
#                                     period = start_period + i
#                                     timetables[batch_id][day][period] = {
#                                         'course_id': course_id,
#                                         'faculty_id': course.faculty_id,
#                                         'classroom_id': classroom_id,
#                                         'is_lab': True,
#                                         'lab_session_part': i + 1,
#                                         'lab_total_parts': duration_periods
#                                     }
                                    
#                                     # Update global schedules
#                                     self.global_faculty_schedule[course.faculty_id][day][period] = batch_id
#                                     self.global_room_schedule[classroom_id][day][period] = batch_id
                                
#                                 print(f"✓ Assigned lab {course_id} to {self.day_names[day]}, periods {start_period}-{start_period + duration_periods - 1}")
#                                 assigned = True
#                                 break
#                     if assigned:
#                         break
                
#                 if not assigned:
#                     print(f"⚠️ WARNING: Could not assign lab {course_id} for {batch_id}")
        
#         # Step 2: Assign theory courses (2 sessions per week for core subjects)
#         for batch_id in section_order:
#             batch = self.student_batches[batch_id]
#             print(f"\nScheduling theory courses for {batch.name}...")
            
#             # All theory courses including electives
#             theory_courses = []
#             for course_id in (batch.core_courses + batch.elective_courses + batch.skill_courses + batch.multidisciplinary_courses):
#                 if course_id in self.courses and not self.courses[course_id].requires_lab:
#                     theory_courses.append(course_id)
            
#             for course_id in theory_courses:
#                 course = self.courses[course_id]
#                 required_sessions = self.get_effective_hours_per_week(course_id)
#                 scheduled_sessions = 0
                
#                 print(f"Scheduling {course_id} ({course.name}) - needs {required_sessions} sessions")
                
#                 attempts = 0
#                 max_attempts = 100  # Increased attempts
                
#                 while scheduled_sessions < required_sessions and attempts < max_attempts:
#                     day = random.randrange(self.days)
#                     period = random.randrange(self.periods_per_day)
                    
#                     if (not self.is_lunch_period(period) and 
#                         timetables[batch_id][day][period] is None and
#                         self.is_faculty_available_globally(course.faculty_id, day, period, batch_id) and
#                         not self.has_course_on_day(timetables[batch_id], course_id, day)):
                        
#                         classroom_id = self.find_available_classroom(course, day, period, batch_id)
                        
#                         if classroom_id:
#                             timetables[batch_id][day][period] = {
#                                 'course_id': course_id,
#                                 'faculty_id': course.faculty_id,
#                                 'classroom_id': classroom_id,
#                                 'is_lab': False
#                             }
                            
#                             # Update global schedules
#                             self.global_faculty_schedule[course.faculty_id][day][period] = batch_id
#                             self.global_room_schedule[classroom_id][day][period] = batch_id
                            
#                             scheduled_sessions += 1
#                             print(f"✓ Assigned {course_id} session {scheduled_sessions}/{required_sessions} on {self.day_names[day]} period {period}")
                    
#                     attempts += 1
                
#                 if scheduled_sessions < required_sessions:
#                     print(f"⚠️ WARNING: Only scheduled {scheduled_sessions}/{required_sessions} sessions for {course_id}")
        
#         return timetables

#     def has_course_on_day(self, schedule, course_id: str, day: int) -> bool:
#         """Check if course is already scheduled on given day"""
#         for period in range(self.periods_per_day):
#             slot = schedule[day][period]
#             if slot and slot['course_id'] == course_id:
#                 return True
#         return False

#     def is_slot_available_for_lab(self, batch_id: str, day: int, start_period: int, duration: int, course: NEPCourse) -> bool:
#         """Check if consecutive periods are available for lab"""
#         for i in range(duration):
#             period = start_period + i
#             if (period >= self.periods_per_day or
#                 self.is_lunch_period(period) or
#                 not self.is_faculty_available_globally(course.faculty_id, day, period, batch_id)):
#                 return False
#         return True

#     def is_faculty_available_globally(self, faculty_id: str, day: int, period: int, requesting_batch: str) -> bool:
#         """Check if faculty is available across all sections"""
#         if faculty_id not in self.teachers:
#             return False
            
#         teacher = self.teachers[faculty_id]
        
#         # Check unavailable slots
#         if (day, period) in teacher.unavailable_slots:
#             return False
        
#         # Check research slots
#         if self.preferences.research_slot_protection and (day, period) in teacher.research_slots:
#             return False
        
#         # Check global faculty schedule
#         assigned_batch = self.global_faculty_schedule[faculty_id][day][period]
#         if assigned_batch is not None and assigned_batch != requesting_batch:
#             return False
        
#         return True

#     def find_available_classroom(self, course: NEPCourse, day: int, period: int, batch_id: str) -> Optional[str]:
#         """Find available classroom considering global room schedule"""
#         suitable_rooms = []
        
#         for room_id, room in self.classrooms.items():
#             if (room.capacity >= course.max_students and
#                 not self.is_room_occupied_globally(room_id, day, period, batch_id)):
                
#                 pref_score = 0
#                 if room.department == course.department:
#                     pref_score += 10
#                 if course.requires_smart_room and room.is_smart_room:
#                     pref_score += 15
                
#                 suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         return None

#     def find_available_lab_room(self, course: NEPCourse, day: int, start_period: int, duration: int, batch_id: str) -> Optional[str]:
#         """Find available lab room for consecutive periods"""
#         suitable_rooms = []
        
#         for room_id, room in self.classrooms.items():
#             if (room.room_type in [RoomType.LAB, RoomType.COMPUTER_LAB] and
#                 room.capacity >= course.max_students):
                
#                 # Check availability for all periods
#                 available = True
#                 for i in range(duration):
#                     period = start_period + i
#                     if self.is_room_occupied_globally(room_id, day, period, batch_id):
#                         available = False
#                         break
                
#                 if available:
#                     pref_score = 0
#                     if room.department == course.department:
#                         pref_score += 10
#                     suitable_rooms.append((pref_score, room_id))
        
#         if suitable_rooms:
#             suitable_rooms.sort(reverse=True, key=lambda x: x[0])
#             return suitable_rooms[0][1]
        
#         return None

#     def is_room_occupied_globally(self, room_id: str, day: int, period: int, requesting_batch: str) -> bool:
#         """Check if room is occupied across all sections"""
#         room = self.classrooms[room_id]
        
#         # Check maintenance slots
#         if (day, period) in room.weekly_maintenance:
#             return True
        
#         # Check global room schedule
#         assigned_batch = self.global_room_schedule[room_id][day][period]
#         if assigned_batch is not None and assigned_batch != requesting_batch:
#             return True
        
#         return False

#     def generate_multi_section_timetables(self, population_size: int = 20, generations: int = 30) -> dict:
#         """Generate optimized timetables for all sections"""
#         print("Initializing multi-section timetable generation...")
        
#         best_timetables = None
#         best_fitness = 0
        
#         for attempt in range(5):  # Try multiple times to get good solution
#             print(f"\nAttempt {attempt + 1}/5...")
            
#             # Reset global schedules - Fixed initialization
#             self.global_faculty_schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
#             self.global_room_schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
#             self.synchronized_slots = {}
            
#             # Create timetables
#             timetables = self.create_multi_section_timetable()
            
#             # Calculate fitness
#             fitness = self.calculate_multi_section_fitness(timetables)
            
#             print(f"Fitness: {fitness:.2f}")
            
#             if fitness > best_fitness:
#                 best_fitness = fitness
#                 best_timetables = copy.deepcopy(timetables)
                
#                 # If fitness is good enough, stop
#                 if fitness >= 700:
#                     print(f"Found good solution with fitness {fitness:.2f}")
#                     break
        
#         return best_timetables

#     def calculate_multi_section_fitness(self, timetables: dict) -> float:
#         """Calculate fitness for multi-section timetables"""
#         base_score = 1000.0
#         penalty = 0.0
        
#         # Check for conflicts across sections
#         penalty += self.check_faculty_conflicts_global(timetables) * 200
#         penalty += self.check_room_conflicts_global(timetables) * 200
        
#         # Check individual section quality
#         for batch_id, timetable in timetables.items():
#             penalty += self.check_course_requirements_individual(batch_id, timetable) * 50
#             penalty += self.check_lunch_violations_individual(timetable) * 30
        
#         return max(0, base_score - penalty)

#     def check_faculty_conflicts_global(self, timetables: dict) -> int:
#         """Check for faculty conflicts across all sections"""
#         conflicts = 0
#         faculty_usage = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetables.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         faculty_id = slot['faculty_id']
#                         faculty_usage[faculty_id][day].append((period, batch_id))
        
#         # Check for overlapping assignments
#         for faculty_id, days in faculty_usage.items():
#             for day, assignments in days.items():
#                 periods_used = [period for period, batch in assignments]
#                 conflicts += len(periods_used) - len(set(periods_used))
        
#         return conflicts

#     def check_room_conflicts_global(self, timetables: dict) -> int:
#         """Check for room conflicts across all sections"""
#         conflicts = 0
#         room_usage = defaultdict(lambda: defaultdict(list))
        
#         for batch_id, schedule in timetables.items():
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         room_id = slot['classroom_id']
#                         room_usage[room_id][day].append((period, batch_id))
        
#         # Check for overlapping room usage
#         for room_id, days in room_usage.items():
#             for day, assignments in days.items():
#                 periods_used = [period for period, batch in assignments]
#                 conflicts += len(periods_used) - len(set(periods_used))
        
#         return conflicts

#     def check_course_requirements_individual(self, batch_id: str, schedule) -> int:
#         """Check course hour requirements for individual batch"""
#         violations = 0
#         batch = self.student_batches[batch_id]
#         course_hours = defaultdict(int)
        
#         for day in range(self.days):
#             for period in range(self.periods_per_day):
#                 slot = schedule[day][period]
#                 if slot:
#                     course_hours[slot['course_id']] += 1
        
#         all_courses = (batch.core_courses + batch.elective_courses + 
#                        batch.skill_courses + batch.multidisciplinary_courses)
        
#         for course_id in all_courses:
#             if course_id in self.courses:
#                 required = self.get_effective_hours_per_week(course_id)
#                 actual = course_hours[course_id]
                
#                 if actual != required:
#                     violations += abs(actual - required)
        
#         return violations

#     def check_lunch_violations_individual(self, schedule) -> int:
#         """Check lunch violations for individual schedule"""
#         violations = 0
#         for day in range(self.days):
#             if schedule[day][self.preferences.lunch_break_start] is not None:
#                 violations += 1
#         return violations

#     def export_multi_section_timetable(self, timetables: dict, filename: str = "multi_section_timetable.json") -> dict:
#         """Export multi-section timetable with conflict analysis"""
#         export_data = {
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "nep_2020_compliant": True,
#                 "total_sections": len(timetables),
#                 "working_days": self.days,
#                 "periods_per_day": self.periods_per_day,
#                 "time_slots": self.time_slots,
#                 "college_hours": f"{self.preferences.morning_start_time} - {self.preferences.evening_end_time}",
#                 "special_features": [
#                     "Multi-section conflict resolution",
#                     "Theory courses: 2 sessions per week", 
#                     "Lab courses: 1 session per week (4 hours continuous)",
#                     "Lab session continuity"
#                 ]
#             },
#             "timetables": {},
#             "conflict_analysis": {},
#             "analytics": {}
#         }
        
#         # Export each section's timetable
#         for batch_id, schedule in timetables.items():
#             batch = self.student_batches[batch_id]
#             batch_data = {
#                 "batch_info": {
#                     "name": batch.name,
#                     "department": batch.department,
#                     "semester": batch.semester,
#                     "student_count": batch.student_count
#                 },
#                 "weekly_schedule": []
#             }
            
#             for day in range(self.days):
#                 day_schedule = {
#                     "day": self.day_names[day],
#                     "periods": []
#                 }
                
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         course = self.courses[slot['course_id']]
#                         teacher = self.teachers[slot['faculty_id']]
#                         classroom = self.classrooms[slot['classroom_id']]
                        
#                         period_data = {
#                             "time": self.time_slots[period],
#                             "course": {
#                                 "id": course.id,
#                                 "name": course.name,
#                                 "code": course.code,
#                                 "type": course.course_type.value,
#                                 "credits": course.credits,
#                                 "department": course.department,
#                                 "is_lab": slot.get('is_lab', False)
#                             },
#                             "faculty": {
#                                 "id": teacher.id,
#                                 "name": teacher.name,
#                                 "designation": teacher.designations
#                             },
#                             "classroom": {
#                                 "id": classroom.id,
#                                 "name": classroom.name,
#                                 "type": classroom.room_type.value,
#                                 "capacity": classroom.capacity
#                             },
#                             "section_specific": {
#                                 "is_lab_session": slot.get('is_lab', False)
#                             }
#                         }
                        
#                         # Add lab session details
#                         if slot.get('is_lab', False):
#                             period_data['lab_session'] = {
#                                 "part": slot.get('lab_session_part', 1),
#                                 "total_parts": slot.get('lab_total_parts', 1)
#                             }
#                     else:
#                         if self.is_lunch_period(period):
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "lunch_break"
#                             }
#                         else:
#                             period_data = {
#                                 "time": self.time_slots[period],
#                                 "type": "free"
#                             }
                    
#                     day_schedule["periods"].append(period_data)
                
#                 batch_data["weekly_schedule"].append(day_schedule)
            
#             export_data["timetables"][batch.name] = batch_data
        
#         # Analyze conflicts
#         export_data["conflict_analysis"] = {
#             "faculty_conflicts": self.check_faculty_conflicts_global(timetables),
#             "room_conflicts": self.check_room_conflicts_global(timetables),
#             "total_violations": self.calculate_multi_section_fitness(timetables)
#         }
        
#         # Calculate analytics
#         export_data["analytics"] = self.calculate_multi_section_analytics(timetables)
        
#         # Save to file
#         with open(filename, 'w') as f:
#             json.dump(export_data, f, indent=2, default=str)
        
#         print(f"Multi-section timetable exported to {filename}")
#         return export_data

#     def calculate_multi_section_analytics(self, timetables: dict) -> dict:
#         """Calculate analytics for multi-section timetables"""
#         analytics = {
#             "overall_fitness": self.calculate_multi_section_fitness(timetables),
#             "section_summaries": {},
#             "resource_utilization": {
#                 "faculty": {},
#                 "classrooms": {},
#                 "labs": {}
#             },
#             "course_frequency_analysis": {}
#         }
        
#         # Analyze each section
#         for batch_id, schedule in timetables.items():
#             batch = self.student_batches[batch_id]
            
#             section_stats = {
#                 "total_sessions": 0,
#                 "lab_sessions": 0,
#                 "theory_sessions": 0,
#                 "course_distribution": defaultdict(int)
#             }
            
#             for day in range(self.days):
#                 for period in range(self.periods_per_day):
#                     slot = schedule[day][period]
#                     if slot:
#                         section_stats["total_sessions"] += 1
                        
#                         if slot.get('is_lab', False):
#                             section_stats["lab_sessions"] += 1
#                         else:
#                             section_stats["theory_sessions"] += 1
                        
#                         course_id = slot['course_id']
#                         section_stats["course_distribution"][course_id] += 1
            
#             analytics["section_summaries"][batch.name] = section_stats
        
#         # Check course frequency compliance
#         for course_id, expected_freq in self.course_frequency_override.items():
#             course_frequencies = {}
#             for batch_id, schedule in timetables.items():
#                 count = 0
#                 for day in range(self.days):
#                     for period in range(self.periods_per_day):
#                         slot = schedule[day][period]
#                         if slot and slot['course_id'] == course_id:
#                             count += 1
#                 course_frequencies[batch_id] = count
            
#             analytics["course_frequency_analysis"][course_id] = {
#                 "expected": expected_freq,
#                 "actual": course_frequencies,
#                 "compliant": all(freq == expected_freq for freq in course_frequencies.values())
#             }
        
#         return analytics

#     def print_multi_section_summary(self, timetables: dict):
#         """Print comprehensive summary for multi-section timetables"""
#         print("\n" + "="*80)
#         print("MULTI-SECTION TIMETABLE GENERATION SUMMARY")
#         print("="*80)
        
#         analytics = self.calculate_multi_section_analytics(timetables)
        
#         print(f"\nOVERALL METRICS:")
#         print(f"    Total Sections: {len(timetables)}")
#         print(f"    Overall Fitness: {analytics['overall_fitness']:.2f}/1000")
#         print(f"    College Hours: {self.preferences.morning_start_time} - {self.preferences.evening_end_time}")
#         print(f"    Working Days: {self.days}")
        
#         print(f"\nCONFLICT ANALYSIS:")
#         conflicts = self.check_faculty_conflicts_global(timetables)
#         room_conflicts = self.check_room_conflicts_global(timetables)
        
#         print(f"    Faculty Conflicts: {conflicts} {'✓' if conflicts == 0 else '✗'}")
#         print(f"    Room Conflicts: {room_conflicts} {'✓' if room_conflicts == 0 else '✗'}")
        
#         print(f"\nCOURSE FREQUENCY COMPLIANCE:")
#         for course_id, analysis in analytics["course_frequency_analysis"].items():
#             course_name = self.courses[course_id].name if course_id in self.courses else course_id
#             print(f"    {course_name}:")
#             print(f"        Expected: {analysis['expected']} sessions/week")
#             print(f"        Compliant: {'✓' if analysis['compliant'] else '✗'}")
#             for batch_id, actual in analysis["actual"].items():
#                 batch_name = self.student_batches[batch_id].name
#                 print(f"            {batch_name}: {actual} sessions")
        
#         print(f"\nSECTION SUMMARIES:")
#         for section_name, stats in analytics["section_summaries"].items():
#             print(f"    {section_name}:")
#             print(f"        Total Sessions: {stats['total_sessions']}")
#             print(f"        Lab Sessions: {stats['lab_sessions']}")
#             print(f"        Theory Sessions: {stats['theory_sessions']}")
        
#         # Print sample timetable comparison
#         print(f"\nSAMPLE TIMETABLE COMPARISON (Monday):")
#         print("-" * 100)
        
#         # Header
#         header = "Time".ljust(15)
#         for batch_id in list(timetables.keys())[:3]:  # Show up to 3 sections
#             batch_name = self.student_batches[batch_id].name.split(' - ')[-1]  # Get section part
#             header += batch_name.ljust(25)
#         print(header)
#         print("-" * 100)
        
#         # Show Monday schedule
#         for period in range(self.periods_per_day):
#             row = self.time_slots[period].ljust(15)
            
#             for batch_id in list(timetables.keys())[:3]:
#                 schedule = timetables[batch_id]
#                 slot = schedule[0][period]  # Monday = day 0
                
#                 if slot:
#                     course = self.courses[slot['course_id']]
#                     display_name = course.name
#                     if slot.get('is_lab', False):
#                         part = slot.get('lab_session_part', 1)
#                         total = slot.get('lab_total_parts', 1)
#                         display_name += f" (Lab {part}/{total})"
                    
#                     # Truncate long names
#                     if len(display_name) > 22:
#                         display_name = display_name[:22] + "..."
#                     row += display_name.ljust(25)
#                 elif self.is_lunch_period(period):
#                     row += "LUNCH BREAK".ljust(25)
#                 else:
#                     row += "Free".ljust(25)
            
#             print(row)


# # Web API Integration Functions
# def create_multi_section_system_from_json(json_input: str, user_preferences: dict = None) -> MultiSectionTimetableGenerator:
#     """Create multi-section system from JSON input"""
#     prefs = UserPreferences()
#     if user_preferences:
#         for key, value in user_preferences.items():
#             if hasattr(prefs, key):
#                 setattr(prefs, key, value)
    
#     generator = MultiSectionTimetableGenerator(user_preferences=prefs)
#     generator.load_from_json(json_input)
    
#     return generator

# def generate_multi_section_timetable_api(json_input: str, user_preferences: dict = None, 
#                                        population_size: int = 20, generations: int = 30) -> dict:
#     """Main API function for multi-section timetable generation"""
#     print("Starting Multi-Section NEP 2020 Compliant Timetable Generation...")
    
#     # Create system
#     generator = create_multi_section_system_from_json(json_input, user_preferences)
    
#     # Generate timetables
#     best_timetables = generator.generate_multi_section_timetables(population_size, generations)
    
#     if best_timetables:
#         # Export and return result
#         result = generator.export_multi_section_timetable(best_timetables)
#         generator.print_multi_section_summary(best_timetables)
#         return result
#     else:
#         raise Exception("Failed to generate valid multi-section timetable. Please check constraints.")

# # Main execution for testing
# if __name__ == "__main__":
#     # Test with AIML sections data - using your actual course structure
#     sample_json = json.dumps({
#         "courses": [
#             # Theory courses - 2 sessions per week each
#             {"id": "B23AM3101", "name": "Deep Learning", "code": "B23AM3101", "credits": 3, 
#              "course_type": "core", "hours_per_week": 3, "department": "AIML", "semester": 5, 
#              "faculty_id": "1", "requires_lab": False, "max_students": 60},
#             {"id": "B23AM3102", "name": "Computer Networks", "code": "B23AM3102", "credits": 3,
#              "course_type": "core", "hours_per_week": 3, "department": "AIML", "semester": 5,
#              "faculty_id": "3", "requires_lab": False, "max_students": 60},
#             {"id": "B23AM3103", "name": "Natural Language Processing", "code": "B23AM3103", "credits": 3,
#              "course_type": "core", "hours_per_week": 3, "department": "AIML", "semester": 5,
#              "faculty_id": "2", "requires_lab": False, "max_students": 60},
            
#             # Lab courses - 1 session per week (4 hours continuous)
#             {"id": "B23AM3110", "name": "Deep Learning Lab", "code": "B23AM3110", "credits": 0,
#              "course_type": "core", "hours_per_week": 4, "department": "AIML", "semester": 5,
#              "faculty_id": "1", "requires_lab": True, "max_students": 60, "min_duration_minutes": 240},
#             {"id": "B23AM3111", "name": "Natural Language Processing Lab", "code": "B23AM3111", "credits": 0,
#              "course_type": "skill_enhancement", "hours_per_week": 4, "department": "AIML", "semester": 5,
#              "faculty_id": "2", "requires_lab": True, "max_students": 60, "min_duration_minutes": 240},
#             {"id": "B23AM3112", "name": "Full Stack Development -2", "code": "B23AM3112", "credits": 0,
#              "course_type": "core", "hours_per_week": 4, "department": "AIML", "semester": 5,
#              "faculty_id": "4", "requires_lab": True, "max_students": 60, "min_duration_minutes": 240},
#             {"id": "B23AM3113", "name": "Tinkering Lab (UI Design using Flutter)", "code": "B23AM3113", "credits": 0,
#              "course_type": "skill_enhancement", "hours_per_week": 4, "department": "AIML", "semester": 5,
#              "faculty_id": "4", "requires_lab": True, "max_students": 60, "min_duration_minutes": 240},
            
#             # Elective courses for each section - 2 sessions per week
#             {"id": "PE_I_A", "name": "Professional Elective A", "code": "PE_I_A", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "5", "requires_lab": False, "max_students": 60},
#             {"id": "PE_I_B", "name": "Professional Elective B", "code": "PE_I_B", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "5", "requires_lab": False, "max_students": 60},
#             {"id": "PE_I_C", "name": "Professional Elective C", "code": "PE_I_C", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "5", "requires_lab": False, "max_students": 60},
            
#             {"id": "OE_I_A", "name": "Open Elective A", "code": "OE_I_A", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "6", "requires_lab": False, "max_students": 60},
#             {"id": "OE_I_B", "name": "Open Elective B", "code": "OE_I_B", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "6", "requires_lab": False, "max_students": 60},
#             {"id": "OE_I_C", "name": "Open Elective C", "code": "OE_I_C", "credits": 3,
#              "course_type": "elective", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "6", "requires_lab": False, "max_students": 60},
            
#             # Other courses
#             {"id": "B23AM3114", "name": "Evaluation of Community Service Internship", "code": "B23AM3114", "credits": 1,
#              "course_type": "project", "hours_per_week": 3, "department": "AIML", "semester": 5,
#              "faculty_id": "8", "requires_lab": False, "max_students": 60},
#             {"id": "B23MC3101", "name": "Employability Skills", "code": "B23MC3101", "credits": 0,
#              "course_type": "core", "hours_per_week": 3, "department": "GENERAL", "semester": 5,
#              "faculty_id": "8", "requires_lab": False, "max_students": 60}
#         ],
#         "faculty": [
#             {"id": "1", "name": "Dr P Ravi Kiran Varma", "department": "CSE", "designation": "Professor", 
#              "specializations": ["Deep Learning"], "courses_can_teach": ["B23AM3101", "B23AM3110"],
#              "max_hours_per_week": 16, "max_hours_per_day": 4},
#             {"id": "2", "name": "Dr. Bh V S Rama Krishnam Raju", "department": "CSE", "designation": "Professor",
#              "specializations": ["Natural Language Processing"], "courses_can_teach": ["B23AM3103", "B23AM3111"],
#              "max_hours_per_week": 16, "max_hours_per_day": 4},
#             {"id": "3", "name": "Dr. M S V S Bhadri Raju", "department": "CSE", "designation": "Professor",
#              "specializations": ["Computer Networks"], "courses_can_teach": ["B23AM3102"],
#              "max_hours_per_week": 16, "max_hours_per_day": 4},
#             {"id": "4", "name": "Dr. K V Krishnam Raju", "department": "CSE", "designation": "Professor",
#              "specializations": ["Full Stack Development"], "courses_can_teach": ["B23AM3112", "B23AM3113"],
#              "max_hours_per_week": 16, "max_hours_per_day": 4},
#             {"id": "5", "name": "Dr. G Mahesh", "department": "CSE", "designation": "Professor",
#              "specializations": ["Professional Electives"], "courses_can_teach": ["PE_I_A", "PE_I_B", "PE_I_C"],
#              "max_hours_per_week": 16, "max_hours_per_day": 4},
#             {"id": "6", "name": "Dr. V Chandra Sekhar", "department": "CSE", "designation": "Professor",
#              "specializations": ["Open Electives"], "courses_can_teach": ["OE_I_A", "OE_I_B", "OE_I_C"],
#              "max_hours_per_week": 16, "max_hours_per_day": 4},
#             {"id": "8", "name": "Dr. R N V Jagan Mohan", "department": "CSE", "designation": "Associate Professor",
#              "specializations": ["General"], "courses_can_teach": ["B23AM3114", "B23MC3101"],
#              "max_hours_per_week": 16, "max_hours_per_day": 4}
#         ],
#         "classrooms": [
#             {"id": "C101", "name": "C101", "capacity": 70, "room_type": "smart_classroom", "department": "CSE", "equipment": []},
#             {"id": "C102", "name": "C102", "capacity": 70, "room_type": "smart_classroom", "department": "CSE", "equipment": []},
#             {"id": "C103", "name": "C103", "capacity": 70, "room_type": "lecture", "department": "CSE", "equipment": []},
#             {"id": "LAB-401", "name": "AI/ML Lab", "capacity": 40, "room_type": "computer_lab", "department": "CSE", "equipment": []},
#             {"id": "LAB-G01", "name": "Computer Lab 1", "capacity": 40, "room_type": "computer_lab", "department": "CSE", "equipment": []},
#             {"id": "LAB-G02", "name": "Computer Lab 2", "capacity": 40, "room_type": "computer_lab", "department": "CSE", "equipment": []}
#         ],
#         "student_batches": [
#             {"id": "AIML_S5_A", "name": "AI & ML Semester 5 - Section A", "department": "AIML", "semester": 5, "student_count": 16,
#              "core_courses": ["B23AM3101", "B23AM3102", "B23AM3103", "B23AM3110", "B23AM3112"],
#              "elective_courses": ["PE_I_A", "OE_I_A"], "skill_courses": ["B23AM3111", "B23AM3113"],
#              "multidisciplinary_courses": ["B23AM3114", "B23MC3101"]},
#             {"id": "AIML_S5_B", "name": "AI & ML Semester 5 - Section B", "department": "AIML", "semester": 5, "student_count": 16,
#              "core_courses": ["B23AM3101", "B23AM3102", "B23AM3103", "B23AM3110", "B23AM3112"],
#              "elective_courses": ["PE_I_B", "OE_I_B"], "skill_courses": ["B23AM3111", "B23AM3113"],
#              "multidisciplinary_courses": ["B23AM3114", "B23MC3101"]},
#             {"id": "AIML_S5_C", "name": "AI & ML Semester 5 - Section C", "department": "AIML", "semester": 5, "student_count": 16,
#              "core_courses": ["B23AM3101", "B23AM3102", "B23AM3103", "B23AM3110", "B23AM3112"],
#              "elective_courses": ["PE_I_C", "OE_I_C"], "skill_courses": ["B23AM3111", "B23AM3113"],
#              "multidisciplinary_courses": ["B23AM3114", "B23MC3101"]}
#         ]
#     })
    
#     try:
#         result = generate_multi_section_timetable_api(sample_json, population_size=15, generations=20)
#         print(f"\nMulti-section timetable generated successfully!")
        
#     except Exception as e:
#         print(f"Error: {e}")
#         import traceback
#         traceback.print_exc()

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional, Union
from collections import defaultdict
from enum import Enum
import copy
import math

class CourseType(Enum):
    CORE = "core"
    ELECTIVE = "elective" 
    MULTIDISCIPLINARY = "multidisciplinary"
    SKILL_ENHANCEMENT = "skill_enhancement"
    VALUE_ADDED = "value_added"
    ABILITY_ENHANCEMENT = "ability_enhancement"
    SEMINAR = "seminar"
    PROJECT = "project"
    HONORS = "honors"
    MINOR = "minor"

class RoomType(Enum):
    LECTURE = "lecture"
    LAB = "lab"
    SEMINAR = "seminar"
    COMPUTER_LAB = "computer_lab"
    SMART_CLASSROOM = "smart_classroom"
    AUDITORIUM = "auditorium"

class TimePreference(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    ANY = "any"

@dataclass
class NEPCourse:
    """Enhanced course structure following NEP 2020 guidelines"""
    id: str
    name: str
    code: str
    credits: int
    course_type: CourseType
    hours_per_week: int
    department: str
    semester: int
    faculty_id: str
    requires_lab: bool = False
    requires_smart_room: bool = False
    is_interdisciplinary: bool = False
    connected_departments: List[str] = None
    max_students: int = 60
    min_duration_minutes: int = 50
    max_consecutive_hours: int = 2
    preferred_days: List[int] = None
    
    def __post_init__(self):
        if self.connected_departments is None:
            self.connected_departments = []
        if self.preferred_days is None:
            self.preferred_days = []
    
    @classmethod
    def from_dict(cls, data):
        """Create NEPCourse from dictionary"""
        if isinstance(data['course_type'], str):
            course_type_str = data['course_type'].lower().strip()
            if course_type_str == 'honors':
                data['course_type'] = CourseType.HONORS
            elif course_type_str == 'minor':
                data['course_type'] = CourseType.MINOR
            else:
                try:
                    data['course_type'] = CourseType(course_type_str)
                except ValueError:
                    print(f"Warning: Unknown course type '{data['course_type']}', defaulting to 'core'")
                    data['course_type'] = CourseType.CORE
        return cls(**data)

@dataclass 
class NEPFaculty:
    """Faculty with NEP 2020 compliant parameters"""
    id: str
    name: str
    department: str
    designations: str
    specializations: List[str]
    courses_can_teach: List[str]
    max_hours_per_day: int = 6
    max_hours_per_week: int = 24
    preferred_time: TimePreference = TimePreference.ANY
    unavailable_slots: List[Tuple[int, int]] = None
    research_slots: List[Tuple[int, int]] = None
    is_visiting: bool = False
    workload_preference: float = 1.0
    
    def __post_init__(self):
        if self.unavailable_slots is None:
            self.unavailable_slots = []
        if self.research_slots is None:
            self.research_slots = []
    
    @classmethod
    def from_dict(cls, data):
        """Create NEPFaculty from dictionary"""
        if 'designation' in data:
            data['designations'] = data.pop('designation')
        if isinstance(data.get('preferred_time'), str):
            data['preferred_time'] = TimePreference(data['preferred_time'])
        return cls(**data)

@dataclass
class NEPClassroom:
    """Classroom with modern facilities"""
    id: str
    name: str
    capacity: int
    room_type: RoomType
    department: str
    equipment: List[str]
    is_smart_room: bool = False
    is_ac: bool = False
    has_projector: bool = True
    weekly_maintenance: List[Tuple[int, int]] = None
    
    def __post_init__(self):
        if self.weekly_maintenance is None:
            self.weekly_maintenance = []
    
    @classmethod
    def from_dict(cls, data):
        """Create NEPClassroom from dictionary"""
        if isinstance(data['room_type'], str):
            data['room_type'] = RoomType(data['room_type'])
        return cls(**data)

@dataclass
class NEPStudentBatch:
    """Student batch/class with NEP parameters"""
    id: str
    name: str
    department: str
    semester: int
    student_count: int
    core_courses: List[str]
    elective_courses: List[str]
    skill_courses: List[str]
    multidisciplinary_courses: List[str]
    preferred_morning_hours: bool = True
    max_hours_per_day: int = 7
    
    @classmethod
    def from_dict(cls, data):
        """Create NEPStudentBatch from dictionary"""
        return cls(**data)

@dataclass
class UserPreferences:
    """User-configurable preferences"""
    working_days: int = 5
    periods_per_day: int = 5
    lunch_break_start: int = 2
    lunch_break_end: int = 2
    max_consecutive_same_subject: int = 2
    gap_penalty_weight: float = 10.0
    faculty_preference_weight: float = 15.0
    workload_balance_weight: float = 20.0
    room_preference_weight: float = 5.0
    interdisciplinary_bonus: float = 10.0
    research_slot_protection: bool = True
    allow_saturday_classes: bool = False
    morning_start_time: str = "9:00"
    evening_end_time: str = "4:30"
    period_duration_minutes: int = 90
    short_break_duration_minutes: int = 15
    lunch_break_duration_minutes: int = 60
    custom_schedule: bool = True
    period_configuration: Optional[List[dict]] = None
    break_configuration: Optional[List[dict]] = None

class MultiSectionTimetableGenerator:
    """Enhanced timetable generator for multiple sections with lab and PE/OE synchronization"""
    
    def __init__(self, config_json: str = None, user_preferences: UserPreferences = None):
        self.preferences = user_preferences or UserPreferences()
        self.days = 6 if self.preferences.allow_saturday_classes else 5
        self.periods_per_day = 5 # Fixed based on the time slots in your JSON.
        
        # Data containers
        self.courses = {}
        self.teachers = {}
        self.classrooms = {}
        self.student_batches = {}
        self.departments = set()
        
        # Multi-section management
        self.global_faculty_schedule = {}
        self.global_room_schedule = {}
        self.synchronized_slots = {}
        
        # Generate time slots
        self.time_slots = self.generate_time_slots()
        self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:self.days]
        
        # Course frequency overrides
        self.course_frequency_override = {
            "B23AM3101": 2,  
            "B23AM3102": 2, 
            "B23AM3103": 2, 
            "PE_I_A": 2, "PE_I_B": 2, "PE_I_C": 2, 
            "OE_I_A": 2, "OE_I_B": 2, "OE_I_C": 2,
            "B23AM3110": 1, 
            "B23AM3111": 1, 
            "B23AM3112": 1, 
            "B23AM3113": 1,
            "B23AM3114": 2,
            "B23MC3101": 2
        }
        
        if config_json:
            self.load_from_json(config_json)

    def initialize_global_schedules(self):
        """Initialize global schedules with proper structure"""
        self.global_faculty_schedule = {}
        self.global_room_schedule = {}
        
        for faculty_id in self.teachers.keys():
            self.global_faculty_schedule[faculty_id] = {day: {} for day in range(self.days)}
        
        for room_id in self.classrooms.keys():
            self.global_room_schedule[room_id] = {day: {} for day in range(self.days)}

    def generate_time_slots(self):
        """Generate time slots based on a fixed schedule (to match the log)"""
        return [
            "09:00-10:30",  # 0
            "10:30-12:00",  # 1
            "12:00-01:30",  # 2 - LUNCH BREAK
            "01:30-03:00",  # 3
            "03:00-04:30",  # 4
        ]

    def load_from_json(self, config_json: str):
        """Load configuration from JSON string"""
        try:
            data = json.loads(config_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format provided. Details: {e}")
            return

        for course_data in data.get("courses", []):
            try:
                course_obj = NEPCourse.from_dict(course_data)
                self.add_course(course_obj)
            except Exception as e:
                print(f"Error loading course {course_data.get('id', 'unknown')}: {e}")
                continue

        for faculty_data in data.get("faculty", []):
            try:
                teacher_obj = NEPFaculty.from_dict(faculty_data)
                self.add_teacher(teacher_obj)
            except Exception as e:
                print(f"Error loading faculty {faculty_data.get('id', 'unknown')}: {e}")
                continue

        for classroom_data in data.get("classrooms", []):
            try:
                classroom_obj = NEPClassroom.from_dict(classroom_data)
                self.add_classroom(classroom_obj)
            except Exception as e:
                print(f"Error loading classroom {classroom_data.get('id', 'unknown')}: {e}")
                continue
            
        for batch_data in data.get("student_batches", []):
            try:
                batch_obj = NEPStudentBatch.from_dict(batch_data)
                self.add_student_batch(batch_obj)
            except Exception as e:
                print(f"Error loading batch {batch_data.get('id', 'unknown')}: {e}")
                continue

        print("Configuration loaded successfully from JSON.")

    def add_course(self, course: NEPCourse):
        """Add course to system"""
        self.courses[course.id] = course
        self.departments.add(course.department)
    
    def add_teacher(self, teacher: NEPFaculty):
        """Add teacher to system"""
        if teacher.research_slots:
            teacher.research_slots = [(day, period) for day, period in teacher.research_slots if day < self.days and period < self.periods_per_day]
        if teacher.unavailable_slots:
            teacher.unavailable_slots = [(day, period) for day, period in teacher.unavailable_slots if day < self.days and period < self.periods_per_day]
        
        self.teachers[teacher.id] = teacher
        self.departments.add(teacher.department)
    
    def add_classroom(self, classroom: NEPClassroom):
        """Add classroom to system"""
        if classroom.weekly_maintenance:
            classroom.weekly_maintenance = [(day, period) for day, period in classroom.weekly_maintenance if day < self.days and period < self.periods_per_day]

        self.classrooms[classroom.id] = classroom
        self.departments.add(classroom.department)
    
    def add_student_batch(self, batch: NEPStudentBatch):
        """Add student batch to system"""
        self.student_batches[batch.id] = batch
        self.departments.add(batch.department)

    def get_course_duration_periods(self, course: NEPCourse) -> int:
        """Calculate how many periods a course requires"""
        if (course.requires_lab or 'lab' in course.name.lower() or course.min_duration_minutes >= 180):
            return 2
        else:
            return 1

    def is_lunch_period(self, period: int) -> bool:
        """Check if the given period is lunch break"""
        return period == self.preferences.lunch_break_start

    def get_effective_hours_per_week(self, course_id: str) -> int:
        """Get effective hours per week considering overrides"""
        if course_id in self.course_frequency_override:
            return self.course_frequency_override[course_id]
        elif course_id in self.courses:
            course = self.courses[course_id]
            if (course.requires_lab or 'lab' in course.name.lower()):
                return 1
            return 2
        return 1

    def create_synchronized_pe_oe_slots(self):
        """Create synchronized time slots for PE and OE across all sections"""
        print("Creating synchronized PE/OE slots...")
        
        # PE slots
        pe_day, pe_period = 1, 0 # Tuesday, 9:00-10:30
        for batch_id in self.student_batches:
            pe_courses = [c for c in self.student_batches[batch_id].elective_courses if 'PE_I' in c]
            if pe_courses:
                course_id = pe_courses[0]
                course = self.courses[course_id]
                self.synchronized_slots[(batch_id, course_id)] = (pe_day, pe_period)
                self.update_global_faculty_schedule(course.faculty_id, pe_day, pe_period, f"PE_ALL_SECTIONS_{batch_id}")
                print(f"✓ Assigned synchronized {course_id} for {batch_id}")

        # OE slots
        oe_day, oe_period = 2, 3 # Wednesday, 1:30-3:00 (avoids lunch conflict)
        for batch_id in self.student_batches:
            oe_courses = [c for c in self.student_batches[batch_id].elective_courses if 'OE_I' in c]
            if oe_courses:
                course_id = oe_courses[0]
                course = self.courses[course_id]
                self.synchronized_slots[(batch_id, course_id)] = (oe_day, oe_period)
                self.update_global_faculty_schedule(course.faculty_id, oe_day, oe_period, f"OE_ALL_SECTIONS_{batch_id}")
                print(f"✓ Assigned synchronized {course_id} for {batch_id}")

    def create_multi_section_timetable(self):
        """Create timetables for all sections with conflict resolution"""
        print("Starting multi-section timetable generation...")
        
        timetables = {batch_id: np.full((self.days, self.periods_per_day), None, dtype=object) for batch_id in self.student_batches}
        
        # Step 1: Create synchronized PE/OE slots and populate them
        self.create_synchronized_pe_oe_slots()
        
        for batch_id, batch in self.student_batches.items():
            for course_id, (day, period) in self.synchronized_slots.items():
                if course_id[0] == batch_id:
                    course = self.courses[course_id[1]]
                    faculty_id = course.faculty_id
                    
                    classroom_id = self.find_available_classroom(course, day, period, batch_id)
                    if classroom_id:
                        timetables[batch_id][day][period] = {
                            'course_id': course_id[1],
                            'faculty_id': faculty_id,
                            'classroom_id': classroom_id,
                            'is_lab': False,
                            'is_synchronized': True
                        }
                        self.update_global_room_schedule(classroom_id, day, period, batch_id)

        # Step 2: Assign lab courses (HIGHEST PRIORITY)
        print("\nScheduling labs...")
        lab_courses_to_schedule = []
        for batch_id in self.student_batches:
            batch = self.student_batches[batch_id]
            for course_id in (batch.core_courses + batch.skill_courses + batch.multidisciplinary_courses):
                if course_id in self.courses and (self.courses[course_id].requires_lab or 'lab' in self.courses[course_id].name.lower()):
                    lab_courses_to_schedule.append((batch_id, course_id))

        random.shuffle(lab_courses_to_schedule)
        
        for batch_id, course_id in lab_courses_to_schedule:
            course = self.courses[course_id]
            duration_periods = self.get_course_duration_periods(course)
            assigned = False
            
            shuffled_days = list(range(self.days))
            random.shuffle(shuffled_days)
            
            for day in shuffled_days:
                # Prioritize afternoon slots for labs
                start_periods = [3, 0, 1] 
                random.shuffle(start_periods)

                for start_period in start_periods:
                    if (start_period + duration_periods <= self.periods_per_day and
                        not self.is_lunch_period(start_period) and not self.is_lunch_period(start_period + 1) and
                        self.is_slot_available_for_lab(batch_id, day, start_period, duration_periods, course)):
                        
                        classroom_id = self.find_available_lab_room(course, day, start_period, duration_periods, batch_id)
                        
                        if classroom_id:
                            for i in range(duration_periods):
                                period = start_period + i
                                timetables[batch_id][day][period] = {
                                    'course_id': course_id,
                                    'faculty_id': course.faculty_id,
                                    'classroom_id': classroom_id,
                                    'is_lab': True,
                                    'lab_session_part': i + 1,
                                    'lab_total_parts': duration_periods
                                }
                                self.update_global_faculty_schedule(course.faculty_id, day, period, batch_id)
                                self.update_global_room_schedule(classroom_id, day, period, batch_id)
                            
                            print(f"✓ Assigned lab {course_id} to {batch_id} on {self.day_names[day]}, periods {start_period}-{start_period + duration_periods - 1}")
                            assigned = True
                            break
                if assigned:
                    break
            
            if not assigned:
                print(f"⚠️ WARNING: Could not assign lab {course_id} for {batch_id}")

        # Step 3: Assign theory courses
        section_order = list(self.student_batches.keys())
        random.shuffle(section_order)
        for batch_id in section_order:
            batch = self.student_batches[batch_id]
            print(f"\nScheduling theory courses for {batch.name}...")
            
            theory_courses = [c for c in (batch.core_courses + batch.skill_courses + batch.multidisciplinary_courses) 
                              if c in self.courses and not (self.courses[c].requires_lab or 'lab' in self.courses[c].name.lower())]
            
            for course_id in batch.elective_courses:
                if (batch_id, course_id) not in self.synchronized_slots:
                    theory_courses.append(course_id)
            
            random.shuffle(theory_courses)
            
            for course_id in theory_courses:
                course = self.courses[course_id]
                required_sessions = self.get_effective_hours_per_week(course_id)
                scheduled_sessions = 0
                
                attempts = 0
                while scheduled_sessions < required_sessions and attempts < 100:
                    day = random.randrange(self.days)
                    period = random.randrange(self.periods_per_day)
                    
                    if (timetables[batch_id][day][period] is None and
                        not self.is_lunch_period(period) and
                        self.is_faculty_available_globally(course.faculty_id, day, period, batch_id) and
                        not self.has_course_on_day(timetables[batch_id], course_id, day)):
                        
                        classroom_id = self.find_available_classroom(course, day, period, batch_id)
                        
                        if classroom_id:
                            timetables[batch_id][day][period] = {
                                'course_id': course_id,
                                'faculty_id': course.faculty_id,
                                'classroom_id': classroom_id,
                                'is_lab': False
                            }
                            self.update_global_faculty_schedule(course.faculty_id, day, period, batch_id)
                            self.update_global_room_schedule(classroom_id, day, period, batch_id)
                            scheduled_sessions += 1
                            print(f"✓ Assigned {course_id} session {scheduled_sessions}/{required_sessions} on {self.day_names[day]} period {period}")
                    
                    attempts += 1
                
                if scheduled_sessions < required_sessions:
                    print(f"⚠️ WARNING: Only scheduled {scheduled_sessions}/{required_sessions} sessions for {course_id}")
        
        return timetables

    def update_global_faculty_schedule(self, faculty_id: str, day: int, period: int, batch_id: str):
        """Update global faculty schedule safely"""
        self.global_faculty_schedule.setdefault(faculty_id, {}).setdefault(day, {})[period] = batch_id

    def update_global_room_schedule(self, room_id: str, day: int, period: int, batch_id: str):
        """Update global room schedule safely"""
        self.global_room_schedule.setdefault(room_id, {}).setdefault(day, {})[period] = batch_id

    def has_course_on_day(self, schedule, course_id: str, day: int) -> bool:
        """Check if course is already scheduled on given day"""
        for period in range(self.periods_per_day):
            slot = schedule[day][period]
            if slot and slot['course_id'] == course_id:
                return True
        return False

    def is_slot_available_for_lab(self, batch_id: str, day: int, start_period: int, duration: int, course: NEPCourse) -> bool:
        """Check if consecutive periods are available for lab"""
        for i in range(duration):
            period = start_period + i
            # Check if period is within bounds and not a lunch break
            if (period >= self.periods_per_day or
                self.is_lunch_period(period) or
                # Check for existing booking in this batch
                self.global_faculty_schedule.get(course.faculty_id, {}).get(day, {}).get(period) is not None or
                self.global_room_schedule.get(self.find_available_lab_room(course, day, start_period, duration, batch_id), {}).get(day, {}).get(period) is not None):
                return False
        return True

    def is_faculty_available_globally(self, faculty_id: str, day: int, period: int, requesting_batch: str) -> bool:
        """Check if faculty is available across all sections"""
        if faculty_id not in self.teachers:
            return False
        
        teacher = self.teachers[faculty_id]
        
        if (day, period) in teacher.unavailable_slots:
            return False
        
        if self.preferences.research_slot_protection and (day, period) in teacher.research_slots:
            return False
        
        # Check global faculty schedule
        occupied_by = self.global_faculty_schedule.get(faculty_id, {}).get(day, {}).get(period)
        if occupied_by is not None:
            # Allow synchronized classes to be taught by the same faculty at the same time
            if 'PE_ALL_SECTIONS' in occupied_by or 'OE_ALL_SECTIONS' in occupied_by:
                return True
            return False
        
        return True

    def find_available_classroom(self, course: NEPCourse, day: int, period: int, batch_id: str) -> Optional[str]:
        """Find available classroom considering global room schedule"""
        suitable_rooms = []
        
        for room_id, room in self.classrooms.items():
            if (room.capacity >= self.student_batches[batch_id].student_count and
                not self.is_room_occupied_globally(room_id, day, period, batch_id)):
                
                pref_score = 0
                if room.department == course.department:
                    pref_score += 10
                if course.requires_smart_room and room.is_smart_room:
                    pref_score += 15
                
                suitable_rooms.append((pref_score, room_id))
        
        if suitable_rooms:
            suitable_rooms.sort(reverse=True, key=lambda x: x[0])
            return suitable_rooms[0][1]
        
        return None

    def find_available_lab_room(self, course: NEPCourse, day: int, start_period: int, duration: int, batch_id: str) -> Optional[str]:
        """Find available lab room for consecutive periods"""
        suitable_rooms = []
        
        for room_id, room in self.classrooms.items():
            if room.room_type in [RoomType.LAB, RoomType.COMPUTER_LAB] and room.capacity >= self.student_batches[batch_id].student_count:
                
                available = True
                for i in range(duration):
                    period = start_period + i
                    if self.is_room_occupied_globally(room_id, day, period, batch_id):
                        available = False
                        break
                
                if available:
                    pref_score = 0
                    if room.department == course.department:
                        pref_score += 10
                    suitable_rooms.append((pref_score, room_id))
        
        if suitable_rooms:
            suitable_rooms.sort(reverse=True, key=lambda x: x[0])
            return suitable_rooms[0][1]
        
        return None

    def is_room_occupied_globally(self, room_id: str, day: int, period: int, requesting_batch: str) -> bool:
        """Check if room is occupied across all sections"""
        room = self.classrooms[room_id]
        
        if (day, period) in room.weekly_maintenance:
            return True
        
        if self.global_room_schedule.get(room_id, {}).get(day, {}).get(period) is not None:
            return True
        
        return False

    def generate_multi_section_timetables(self, population_size: int = 20, generations: int = 30) -> dict:
        """Generate optimized timetables for all sections"""
        print("Initializing multi-section timetable generation...")
        
        best_timetables = None
        best_fitness = -1
        
        for attempt in range(5):
            print(f"\nAttempt {attempt + 1}/5...")
            
            self.initialize_global_schedules()
            self.synchronized_slots = {}
            
            timetables = self.create_multi_section_timetable()
            fitness = self.calculate_multi_section_fitness(timetables)
            
            print(f"Fitness: {fitness:.2f}")
            
            if fitness > best_fitness:
                best_fitness = fitness
                best_timetables = copy.deepcopy(timetables)
                
                if fitness >= 700 and self.check_lab_assignment_issues(timetables) == 0:
                    print(f"Found good solution with fitness {fitness:.2f}")
                    break
        
        return best_timetables

    def calculate_multi_section_fitness(self, timetables: dict) -> float:
        """Calculate fitness for multi-section timetables"""
        base_score = 1000.0
        penalty = 0.0
        
        penalty += self.check_faculty_conflicts_global(timetables) * 200
        penalty += self.check_room_conflicts_global(timetables) * 200
        penalty += self.check_lab_assignment_issues(timetables) * 150
        penalty += self.check_pe_oe_synchronization(timetables) * 100
        
        for batch_id, timetable in timetables.items():
            penalty += self.check_course_requirements_individual(batch_id, timetable) * 50
            penalty += self.check_lunch_violations_individual(timetable) * 30
            penalty += self.check_lab_continuity_individual(timetable) * 80
        
        return max(0, base_score - penalty)

    def check_lab_assignment_issues(self, timetables: dict) -> int:
        """Check for lab assignment issues"""
        issues = 0
        
        for batch_id, schedule in timetables.items():
            batch = self.student_batches[batch_id]
            all_courses = (batch.core_courses + batch.skill_courses + batch.multidisciplinary_courses)
            
            lab_courses_in_batch = [c for c in all_courses if c in self.courses and (self.courses[c].requires_lab or 'lab' in self.courses[c].name.lower())]
            
            for course_id in lab_courses_in_batch:
                assigned = any(slot and slot.get('course_id') == course_id and slot.get('is_lab', False) for day_schedule in schedule for slot in day_schedule)
                if not assigned:
                    issues += 1
                    print(f"Warning: Lab course {course_id} not assigned for {batch_id}")
        
        return issues

    def check_lab_continuity_individual(self, schedule) -> int:
        """Check if lab sessions are continuous"""
        violations = 0
        for day in range(self.days):
            periods_with_labs = [p for p, slot in enumerate(schedule[day]) if slot and slot.get('is_lab', False)]
            if periods_with_labs:
                if len(periods_with_labs) == 2 and periods_with_labs[1] - periods_with_labs[0] != 1:
                    violations += 1
                elif len(periods_with_labs) > 2:
                    violations += 1 
        return violations

    def check_pe_oe_synchronization(self, timetables: dict) -> int:
        """Check if PE/OE courses are synchronized across sections"""
        violations = 0
        pe_slots, oe_slots = {}, {}
        
        for batch_id, schedule in timetables.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot and slot.get('is_synchronized', False):
                        if 'PE_I' in slot['course_id']: pe_slots[batch_id] = (day, period)
                        elif 'OE_I' in slot['course_id']: oe_slots[batch_id] = (day, period)
        
        if len(pe_slots) > 1 and len(set(pe_slots.values())) > 1:
            violations += 1
            print("Warning: PE courses not synchronized across sections")
        
        if len(oe_slots) > 1 and len(set(oe_slots.values())) > 1:
            violations += 1
            print("Warning: OE courses not synchronized across sections")
        
        return violations

    def check_faculty_conflicts_global(self, timetables: dict) -> int:
        """Check for faculty conflicts across all sections"""
        conflicts = 0
        faculty_usage = defaultdict(lambda: defaultdict(list))
        
        for batch_id, schedule in timetables.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        faculty_id = slot['faculty_id']
                        if faculty_id in self.teachers:
                             faculty_usage[faculty_id][day].append((period, batch_id))
        
        for faculty_id, days in faculty_usage.items():
            for day, assignments in days.items():
                periods_used = [period for period, batch in assignments]
                if len(periods_used) != len(set(periods_used)):
                    conflicts += 1
        
        return conflicts

    def check_room_conflicts_global(self, timetables: dict) -> int:
        """Check for room conflicts across all sections"""
        conflicts = 0
        room_usage = defaultdict(lambda: defaultdict(list))
        
        for batch_id, schedule in timetables.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        room_id = slot['classroom_id']
                        room_usage[room_id][day].append((period, batch_id))
        
        for room_id, days in room_usage.items():
            for day, assignments in days.items():
                periods_used = [period for period, batch in assignments]
                if len(periods_used) != len(set(periods_used)):
                    conflicts += 1
        
        return conflicts

    def check_course_requirements_individual(self, batch_id: str, schedule) -> int:
        """Check course hour requirements for individual batch"""
        violations = 0
        batch = self.student_batches[batch_id]
        course_hours = defaultdict(int)
        
        for day in range(self.days):
            for period in range(self.periods_per_day):
                slot = schedule[day][period]
                if slot:
                    course_hours[slot['course_id']] += 1
        
        all_courses = (batch.core_courses + batch.elective_courses + batch.skill_courses + batch.multidisciplinary_courses)
        
        for course_id in all_courses:
            if course_id in self.courses:
                required = self.get_effective_hours_per_week(course_id)
                actual = course_hours[course_id]
                if self.courses[course_id].requires_lab:
                    required_periods = self.get_course_duration_periods(self.courses[course_id])
                    if actual < required_periods:
                        violations += required_periods - actual
                else:
                    if actual != required:
                        violations += abs(actual - required)
        
        return violations

    def check_lunch_violations_individual(self, schedule) -> int:
        """Check lunch violations for individual schedule"""
        violations = 0
        for day in range(self.days):
            if schedule[day][self.preferences.lunch_break_start] is not None:
                violations += 1
        return violations

    def export_multi_section_timetable(self, timetables: dict, filename: str = "multi_section_timetable.json") -> dict:
        """Export multi-section timetable with enhanced lab and PE/OE details"""
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "nep_2020_compliant": True,
                "total_sections": len(timetables),
                "working_days": self.days,
                "periods_per_day": self.periods_per_day,
                "time_slots": self.time_slots,
                "college_hours": f"{self.preferences.morning_start_time} - {self.preferences.evening_end_time}",
                "special_features": [
                    "Multi-section conflict resolution",
                    "Lab courses: 3-hour continuous sessions",
                    "PE/OE synchronized across all sections", 
                    "Theory courses: 2 sessions per week",
                    "NEP 2020 compliant structure"
                ]
            },
            "timetables": {},
            "conflict_analysis": {},
            "synchronized_courses": {},
            "lab_scheduling_summary": {},
            "analytics": {}
        }
        
        for batch_id, schedule in timetables.items():
            batch = self.student_batches[batch_id]
            batch_data = {
                "batch_info": {
                    "name": batch.name,
                    "department": batch.department,
                    "semester": batch.semester,
                    "student_count": batch.student_count
                },
                "weekly_schedule": []
            }
            
            for day in range(self.days):
                day_schedule = {
                    "day": self.day_names[day],
                    "periods": []
                }
                
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        course = self.courses[slot['course_id']]
                        teacher = self.teachers[slot['faculty_id']]
                        classroom = self.classrooms[slot['classroom_id']]
                        
                        period_data = {
                            "time": self.time_slots[period],
                            "course": {
                                "id": course.id,
                                "name": course.name,
                                "code": course.code,
                                "type": course.course_type.value,
                                "credits": course.credits,
                                "department": course.department,
                                "is_lab": slot.get('is_lab', False)
                            },
                            "faculty": {
                                "id": teacher.id,
                                "name": teacher.name,
                                "designation": teacher.designations
                            },
                            "classroom": {
                                "id": classroom.id,
                                "name": classroom.name,
                                "type": classroom.room_type.value,
                                "capacity": classroom.capacity
                            },
                            "section_specific": {
                                "is_synchronized": slot.get('is_synchronized', False),
                                "is_lab_session": slot.get('is_lab', False)
                            }
                        }
                        
                        if slot.get('is_lab', False):
                            period_data['lab_session'] = {
                                "part": slot.get('lab_session_part', 1),
                                "total_parts": slot.get('lab_total_parts', 1),
                                "is_continuous": True
                            }
                    else:
                        if self.is_lunch_period(period):
                            period_data = {
                                "time": self.time_slots[period],
                                "type": "lunch_break"
                            }
                        else:
                            period_data = {
                                "time": self.time_slots[period],
                                "type": "free"
                            }
                    
                    day_schedule["periods"].append(period_data)
                
                batch_data["weekly_schedule"].append(day_schedule)
            
            export_data["timetables"][batch.name] = batch_data
        
        export_data["conflict_analysis"] = {
            "faculty_conflicts": self.check_faculty_conflicts_global(timetables),
            "room_conflicts": self.check_room_conflicts_global(timetables),
            "lab_assignment_issues": self.check_lab_assignment_issues(timetables),
            "pe_oe_sync_issues": self.check_pe_oe_synchronization(timetables),
            "overall_fitness": self.calculate_multi_section_fitness(timetables)
        }
        
        synchronized_schedule = {}
        for batch_id, schedule in timetables.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot and slot.get('is_synchronized', False):
                        course_id = slot['course_id']
                        time_key = f"{self.day_names[day]}_{self.time_slots[period]}"
                        
                        if time_key not in synchronized_schedule:
                            synchronized_schedule[time_key] = []
                        
                        synchronized_schedule[time_key].append({
                            "section": self.student_batches[batch_id].name,
                            "course": course_id,
                            "faculty": self.teachers[slot['faculty_id']].name
                        })
        
        export_data["synchronized_courses"] = synchronized_schedule
        
        lab_summary = {}
        for batch_id, schedule in timetables.items():
            batch_name = self.student_batches[batch_id].name
            lab_summary[batch_name] = {"assigned_labs": [], "total_lab_hours": 0}
            
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot and slot.get('is_lab', False) and slot.get('lab_session_part', 1) == 1:
                        lab_info = {
                            "course_id": slot['course_id'],
                            "course_name": self.courses[slot['course_id']].name,
                            "day": self.day_names[day],
                            "time": self.time_slots[period],
                            "duration_periods": slot.get('lab_total_parts', 1),
                            "room": self.classrooms[slot['classroom_id']].name,
                            "room_type": self.classrooms[slot['classroom_id']].room_type.value
                        }
                        lab_summary[batch_name]["assigned_labs"].append(lab_info)
                        lab_summary[batch_name]["total_lab_hours"] += slot.get('lab_total_parts', 1) * 1.5
        
        export_data["lab_scheduling_summary"] = lab_summary
        
        export_data["analytics"] = self.calculate_multi_section_analytics(timetables)
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Multi-section timetable exported to {filename}")
        return export_data

    def calculate_multi_section_analytics(self, timetables: dict) -> dict:
        """Calculate comprehensive analytics for multi-section timetables"""
        analytics = {
            "overall_fitness": self.calculate_multi_section_fitness(timetables),
            "section_summaries": {},
            "lab_scheduling_stats": {
                "total_lab_courses": 0,
                "successfully_scheduled_labs": 0,
                "lab_rooms_utilized": set(),
                "afternoon_lab_sessions": 0
            },
            "synchronization_stats": {
                "pe_synchronized": False,
                "oe_synchronized": False,
                "pe_sections_count": 0,
                "oe_sections_count": 0
            },
            "course_frequency_analysis": {}
        }
        
        for batch_id, schedule in timetables.items():
            batch = self.student_batches[batch_id]
            section_stats = {
                "total_sessions": 0,
                "lab_sessions": 0,
                "theory_sessions": 0,
                "synchronized_sessions": 0,
                "course_distribution": defaultdict(int)
            }
            
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        section_stats["total_sessions"] += 1
                        if slot.get('is_lab', False):
                            section_stats["lab_sessions"] += 1
                            analytics["lab_scheduling_stats"]["lab_rooms_utilized"].add(slot['classroom_id'])
                            if period >= 3:
                                analytics["lab_scheduling_stats"]["afternoon_lab_sessions"] += 1
                        else:
                            section_stats["theory_sessions"] += 1
                        
                        if slot.get('is_synchronized', False):
                            section_stats["synchronized_sessions"] += 1
                        
                        course_id = slot['course_id']
                        section_stats["course_distribution"][course_id] += 1
                        
                        if 'PE_I' in course_id:
                            analytics["synchronization_stats"]["pe_sections_count"] += 1
                        elif 'OE_I' in course_id:
                            analytics["synchronization_stats"]["oe_sections_count"] += 1
            
            analytics["section_summaries"][batch.name] = section_stats
        
        total_lab_courses, scheduled_lab_courses = 0, 0
        for batch_id, batch in self.student_batches.items():
            lab_courses_in_batch = [c for c in (batch.core_courses + batch.skill_courses + batch.multidisciplinary_courses) if c in self.courses and (self.courses[c].requires_lab or 'lab' in self.courses[c].name.lower())]
            total_lab_courses += len(lab_courses_in_batch)
            
            for course_id in lab_courses_in_batch:
                if any(slot and slot.get('course_id') == course_id and slot.get('is_lab', False) for day_schedule in timetables[batch_id] for slot in day_schedule):
                    scheduled_lab_courses += 1
        
        analytics["lab_scheduling_stats"]["total_lab_courses"] = total_lab_courses
        analytics["lab_scheduling_stats"]["successfully_scheduled_labs"] = scheduled_lab_courses
        analytics["lab_scheduling_stats"]["lab_rooms_utilized"] = len(analytics["lab_scheduling_stats"]["lab_rooms_utilized"])
        
        pe_times, oe_times = set(), set()
        for batch_id, schedule in timetables.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot and 'PE_I' in slot['course_id']: pe_times.add((day, period))
                    elif slot and 'OE_I' in slot['course_id']: oe_times.add((day, period))
        
        analytics["synchronization_stats"]["pe_synchronized"] = len(pe_times) <= 1
        analytics["synchronization_stats"]["oe_synchronized"] = len(oe_times) <= 1
        
        for course_id, expected_freq in self.course_frequency_override.items():
            course_frequencies = {}
            for batch_id, schedule in timetables.items():
                count = sum(1 for day_schedule in schedule for slot in day_schedule if slot and slot['course_id'] == course_id)
                course_frequencies[batch_id] = count
            
            analytics["course_frequency_analysis"][course_id] = {
                "expected": expected_freq,
                "actual": course_frequencies,
                "compliant": all(freq == expected_freq for freq in course_frequencies.values())
            }
        
        return analytics

    def print_multi_section_summary(self, timetables: dict):
        """Print comprehensive summary for multi-section timetables"""
        print("\n" + "="*80)
        print("MULTI-SECTION TIMETABLE GENERATION SUMMARY WITH LAB SCHEDULING")
        print("="*80)
        
        analytics = self.calculate_multi_section_analytics(timetables)
        
        print(f"\nOVERALL METRICS:")
        print(f"    Total Sections: {len(timetables)}")
        print(f"    Overall Fitness: {analytics['overall_fitness']:.2f}/1000")
        print(f"    College Hours: {self.preferences.morning_start_time} - {self.preferences.evening_end_time}")
        print(f"    Working Days: {self.days}")
        
        print(f"\nLAB SCHEDULING STATISTICS:")
        lab_stats = analytics['lab_scheduling_stats']
        print(f"    Total Lab Courses: {lab_stats['total_lab_courses']}")
        print(f"    Successfully Scheduled Labs: {lab_stats['successfully_scheduled_labs']}")
        print(f"    Lab Scheduling Success Rate: {(lab_stats['successfully_scheduled_labs']/max(1, lab_stats['total_lab_courses'])*100):.1f}%")
        print(f"    Lab Rooms Utilized: {lab_stats['lab_rooms_utilized']}")
        print(f"    Afternoon Lab Sessions: {lab_stats['afternoon_lab_sessions']} (preferred)")
        
        print(f"\nSYNCHRONIZATION STATUS:")
        sync_stats = analytics['synchronization_stats']
        print(f"    PE Courses Synchronized: {'✓' if sync_stats['pe_synchronized'] else '✗'}")
        print(f"    OE Courses Synchronized: {'✓' if sync_stats['oe_synchronized'] else '✗'}")
        print(f"    PE Sections: {sync_stats['pe_sections_count']}")
        print(f"    OE Sections: {sync_stats['oe_sections_count']}")
        
        print(f"\nCONFLICT ANALYSIS:")
        conflicts = self.check_faculty_conflicts_global(timetables)
        room_conflicts = self.check_room_conflicts_global(timetables)
        lab_issues = self.check_lab_assignment_issues(timetables)
        sync_issues = self.check_pe_oe_synchronization(timetables)
        
        print(f"    Faculty Conflicts: {conflicts} {'✓' if conflicts == 0 else '✗'}")
        print(f"    Room Conflicts: {room_conflicts} {'✓' if room_conflicts == 0 else '✗'}")
        print(f"    Lab Assignment Issues: {lab_issues} {'✓' if lab_issues == 0 else '✗'}")
        print(f"    PE/OE Sync Issues: {sync_issues} {'✓' if sync_issues == 0 else '✗'}")
        
        print(f"\nSECTION SUMMARIES:")
        for section_name, stats in analytics["section_summaries"].items():
            print(f"    {section_name}:")
            print(f"        Total Sessions: {stats['total_sessions']}")
            print(f"        Lab Sessions: {stats['lab_sessions']}")
            print(f"        Theory Sessions: {stats['theory_sessions']}")
            print(f"        Synchronized Sessions: {stats['synchronized_sessions']}")
        
        print(f"\nLAB ASSIGNMENTS BY SECTION:")
        for batch_id, schedule in timetables.items():
            batch_name = self.student_batches[batch_id].name
            print(f"    {batch_name}:")
            
            lab_assignments = []
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot and slot.get('is_lab', False) and slot.get('lab_session_part', 1) == 1:
                        course_name = self.courses[slot['course_id']].name
                        room_name = self.classrooms[slot['classroom_id']].name
                        room_type = self.classrooms[slot['classroom_id']].room_type.value
                        lab_assignments.append(f"{course_name} - {self.day_names[day]} {self.time_slots[period]} - {room_name} ({room_type})")
            
            if lab_assignments:
                for assignment in lab_assignments:
                    print(f"        ✓ {assignment}")
            else:
                print(f"        ⚠️ No lab assignments found")


def create_multi_section_system_from_json(json_input: str, user_preferences: dict = None) -> MultiSectionTimetableGenerator:
    """Create multi-section system from JSON input"""
    prefs = UserPreferences()
    if user_preferences:
        for key, value in user_preferences.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
    
    generator = MultiSectionTimetableGenerator(user_preferences=prefs)
    generator.load_from_json(json_input)
    
    return generator

def generate_multi_section_timetable_api(json_input: str, user_preferences: dict = None, 
                                        population_size: int = 20, generations: int = 30) -> dict:
    """Main API function for multi-section timetable generation"""
    print("Starting Multi-Section NEP 2020 Compliant Timetable Generation with Lab Support...")
    
    generator = create_multi_section_system_from_json(json_input, user_preferences)
    
    best_timetables = generator.generate_multi_section_timetables(population_size, generations)
    
    if best_timetables:
        result = generator.export_multi_section_timetable(best_timetables)
        generator.print_multi_section_summary(best_timetables)
        return result
    else:
        raise Exception("Failed to generate valid multi-section timetable. Please check constraints.")

if __name__ == "__main__":
    print("Multi-Section Timetable Generator with Lab Support Ready")