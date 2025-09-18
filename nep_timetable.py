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

class CourseType(Enum):
    CORE = "core"
    ELECTIVE = "elective" 
    MULTIDISCIPLINARY = "multidisciplinary"
    SKILL_ENHANCEMENT = "skill_enhancement"
    VALUE_ADDED = "value_added"
    ABILITY_ENHANCEMENT = "ability_enhancement"
    SEMINAR = "seminar"
    PROJECT = "project"

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
        # Convert string course_type to enum
        if isinstance(data['course_type'], str):
            data['course_type'] = CourseType(data['course_type'])
        return cls(**data)

@dataclass 
class NEPFaculty:
    """Faculty with NEP 2020 compliant parameters"""
    id: str
    name: str
    department: str
    designation: str
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
        # Convert string preferred_time to enum
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
        # Convert string room_type to enum
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
    periods_per_day: int = 8
    lunch_break_period: int = 4
    max_consecutive_same_subject: int = 2
    gap_penalty_weight: float = 10.0
    faculty_preference_weight: float = 15.0
    workload_balance_weight: float = 20.0
    room_preference_weight: float = 5.0
    interdisciplinary_bonus: float = 10.0
    research_slot_protection: bool = True
    allow_saturday_classes: bool = False
    morning_start_time: str = "9:00"
    evening_end_time: str = "5:00"

class NEPTimetableGenerator:
    """Enhanced timetable generator compliant with NEP 2020"""
    
    def __init__(self, config_json: str = None, user_preferences: UserPreferences = None):
        self.preferences = user_preferences or UserPreferences()
        self.days = 6 if self.preferences.allow_saturday_classes else 5
        self.periods_per_day = self.preferences.periods_per_day
        
        # Data containers
        self.courses = {}
        self.teachers = {}
        self.classrooms = {}
        self.student_batches = {}
        self.departments = set()
        
        # Generate time slots and timeslots list
        self.generate_time_slots()
        self.timeslots = [f"Day{d}_Period{p}" for d in range(self.days) for p in range(self.periods_per_day)]
        
        self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:self.days]
        
        # Load configuration if provided
        if config_json:
            self.load_from_json(config_json)
    
    def generate_time_slots(self):
        """Generate flexible time slots following NEP guidelines"""
        start_hour = int(self.preferences.morning_start_time.split(':')[0])
        
        self.time_slots = []
        for i in range(self.periods_per_day):
            if i < 4:
                hour = start_hour + i
                self.time_slots.append(f"{hour}:00-{hour}:50")
            elif i == 4:
                self.time_slots.append("12:50-1:40 (LUNCH)")
            else:
                hour = 13 + (i - 4)
                self.time_slots.append(f"{hour}:40-{hour+1}:30")
    
    def load_from_json(self, config_json: str):
        """Load configuration from JSON string"""
        try:
            data = json.loads(config_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format provided. Details: {e}")
            return

        # Load Courses
        for course_data in data.get("courses", []):
            course_obj = NEPCourse.from_dict(course_data)
            self.add_course(course_obj)

        # Load Faculty
        for faculty_data in data.get("faculty", []):
            teacher_obj = NEPFaculty.from_dict(faculty_data)
            self.add_teacher(teacher_obj)

        # Load Classrooms
        for classroom_data in data.get("classrooms", []):
            classroom_obj = NEPClassroom.from_dict(classroom_data)
            self.add_classroom(classroom_obj)
            
        # Load Student Batches
        for batch_data in data.get("student_batches", []):
            batch_obj = NEPStudentBatch.from_dict(batch_data)
            self.add_student_batch(batch_obj)

        print("Configuration loaded successfully from JSON.")

    def add_course(self, course: NEPCourse):
        """Add course to system"""
        self.courses[course.id] = course
        self.departments.add(course.department)
    
    def add_teacher(self, teacher: NEPFaculty):
        """Add teacher to system"""
        # Filter out slots that are outside the configured days/periods
        if teacher.research_slots:
            teacher.research_slots = [
                (day, period) for day, period in teacher.research_slots 
                if day < self.days and period < self.periods_per_day
            ]
        if teacher.unavailable_slots:
            teacher.unavailable_slots = [
                (day, period) for day, period in teacher.unavailable_slots
                if day < self.days and period < self.periods_per_day
            ]
        
        self.teachers[teacher.id] = teacher
        self.departments.add(teacher.department)
    
    def add_classroom(self, classroom: NEPClassroom):
        """Add classroom to system"""
        if classroom.weekly_maintenance:
            classroom.weekly_maintenance = [
                (day, period) for day, period in classroom.weekly_maintenance
                if day < self.days and period < self.periods_per_day
            ]

        self.classrooms[classroom.id] = classroom
        self.departments.add(classroom.department)
    
    def add_student_batch(self, batch: NEPStudentBatch):
        """Add student batch to system"""
        self.student_batches[batch.id] = batch
        self.departments.add(batch.department)
    
    def is_break_period(self, period: int) -> bool:
        """Check if the given period is a designated break period"""
        return period == self.preferences.lunch_break_period
    
    # In your NEPTimetableGenerator class, replace the old creation methods with this one.

    def create_initial_timetable(self):
        """
        Creates an initial, complete, but random timetable.
        This method ensures all course hours are scheduled, letting the GA fix clashes.
        """
        timetable = {}
        
        # Initialize an empty schedule for each batch
        for batch_id in self.student_batches:
            timetable[batch_id] = np.full((self.days, self.periods_per_day), None, dtype=object)

        # Place each course the required number of times randomly
        for batch_id, batch in self.student_batches.items():
            all_courses = (batch.core_courses + batch.elective_courses + 
                        batch.skill_courses + batch.multidisciplinary_courses)
            
            for course_id in all_courses:
                if course_id not in self.courses:
                    continue

                course = self.courses[course_id]
                hours_to_schedule = course.hours_per_week
                
                for _ in range(hours_to_schedule):
                    # Keep trying to find an empty slot for this batch
                    attempts = 0
                    while attempts < 100:
                        day = random.randrange(self.days)
                        period = random.randrange(self.periods_per_day)

                        # Ensure it's not a lunch break and the slot is empty for the batch
                        if period != self.preferences.lunch_break_period and timetable[batch_id][day][period] is None:
                            # Find any suitable classroom
                            classroom_id = self.find_suitable_classroom(course, day, period, {})
                            
                            if classroom_id:
                                timetable[batch_id][day][period] = {
                                    'course_id': course_id,
                                    'faculty_id': course.faculty_id,
                                    'classroom_id': classroom_id
                                }
                                break # Move to the next hour for this course
                        attempts += 1
        return timetable
    def get_course_priority_order(self, courses: List[str]) -> List[str]:
        """Get NEP 2020 compliant course priority order"""
        priority_order = []
        
        # Group courses by type
        by_type = defaultdict(list)
        for course_id in courses:
            if course_id in self.courses:
                course_type = self.courses[course_id].course_type
                by_type[course_type].append(course_id)
        
        # NEP priority: Core -> Ability Enhancement -> Skill -> Multi -> Electives
        type_priority = [
            CourseType.CORE,
            CourseType.ABILITY_ENHANCEMENT, 
            CourseType.SKILL_ENHANCEMENT,
            CourseType.MULTIDISCIPLINARY,
            CourseType.ELECTIVE,
            CourseType.VALUE_ADDED,
            CourseType.SEMINAR,
            CourseType.PROJECT
        ]
        
        for course_type in type_priority:
            priority_order.extend(by_type[course_type])
        
        return priority_order
    
    def find_best_slot(self, course: NEPCourse, batch: NEPStudentBatch, schedule) -> Tuple[Optional[int], Optional[int]]:
        """Find best time slot considering NEP guidelines"""
        best_slots = []
        
        for day in range(self.days):
            for period in range(self.periods_per_day):
                if schedule[day][period] is None and period != self.preferences.lunch_break_period:
                    score = self.calculate_slot_preference_score(course, batch, day, period, schedule)
                    best_slots.append((score, day, period))
        
        if not best_slots:
            return None, None
        
        best_slots.sort(reverse=True, key=lambda x: x[0])
        top_candidates = [slot for slot in best_slots[:5] if slot[0] >= best_slots[0][0] * 0.8]
        
        if top_candidates:
            _, day, period = random.choice(top_candidates)
            return day, period
        
        return None, None
    
    def calculate_slot_preference_score(self, course: NEPCourse, batch: NEPStudentBatch, 
                                      day: int, period: int, schedule) -> float:
        """Calculate preference score for a time slot"""
        score = 100.0
        
        # NEP guideline: Morning classes preferred for core subjects
        if course.course_type == CourseType.CORE and period < 4:
            score += 20.0
        
        # Faculty time preferences
        teacher = self.teachers[course.faculty_id]
        if teacher.preferred_time == TimePreference.MORNING and period < 4:
            score += 15.0
        elif teacher.preferred_time == TimePreference.AFTERNOON and 4 < period < 7:
            score += 15.0
        
        # Avoid research slots
        if (day, period) in teacher.research_slots:
            score -= 50.0
        
        # Course preferred days
        if course.preferred_days and day in course.preferred_days:
            score += 10.0
        
        # Avoid too many consecutive hours
        consecutive_penalty = self.calculate_consecutive_penalty(schedule, day, period)
        score -= consecutive_penalty * 5.0
        
        # Minimize gaps in schedule
        gap_penalty = self.calculate_gap_penalty(schedule, day, period)
        score -= gap_penalty * 3.0
        
        return score
    
    def calculate_consecutive_penalty(self, schedule, day: int, period: int) -> float:
        """Calculate penalty for consecutive same subject hours"""
        if period == 0:
            return 0.0
        
        consecutive_count = 1
        prev_period = period - 1
        
        while prev_period >= 0 and schedule[day][prev_period] is not None:
            consecutive_count += 1
            prev_period -= 1
        
        return max(0, consecutive_count - self.preferences.max_consecutive_same_subject)
    
    def calculate_gap_penalty(self, schedule, day: int, period: int) -> float:
        """Calculate penalty for creating gaps in daily schedule"""
        penalty = 0.0
        
        # Check for gaps before this period
        gaps_before = 0
        for p in range(period):
            if schedule[day][p] is None and not self.is_break_period(p):
                gaps_before += 1
        
        # Penalize gaps in middle of schedule
        if gaps_before > 0:
            penalty += gaps_before * 2.0
        
        return penalty
    
    def find_suitable_classroom(self, course: NEPCourse, day: int, period: int, timetable: dict) -> Optional[str]:
        """Find suitable classroom based on course requirements"""
        suitable_rooms = []
        
        for room_id, room in self.classrooms.items():
            # Check capacity
            if room.capacity < course.max_students:
                continue
            
            # Check room type requirements
            if course.requires_lab and room.room_type not in [RoomType.LAB, RoomType.COMPUTER_LAB]:
                continue
            
            if course.requires_smart_room and not room.is_smart_room:
                continue
            
            # Check availability
            if self.is_room_available(room_id, day, period, timetable):
                pref_score = 0
                if room.department == course.department:
                    pref_score += 10
                if course.course_type == CourseType.SEMINAR and room.room_type == RoomType.SEMINAR:
                    pref_score += 15
                
                suitable_rooms.append((pref_score, room_id))
        
        if suitable_rooms:
            suitable_rooms.sort(reverse=True, key=lambda x: x[0])
            return suitable_rooms[0][1]
        
        return None
    
    def is_room_available(self, room_id: str, day: int, period: int, timetable: dict) -> bool:
        """Check if room is available at given time"""
        room = self.classrooms[room_id]
        
        # Check maintenance slots
        if (day, period) in room.weekly_maintenance:
            return False
        
        # Check if room is already occupied
        for batch_id, schedule in timetable.items():
            if schedule[day][period] is not None:
                if schedule[day][period]['classroom_id'] == room_id:
                    return False
        
        return True
    
    def is_faculty_available(self, faculty_id: str, day: int, period: int, timetable: dict) -> bool:
        """Check if faculty is available"""
        teacher = self.teachers[faculty_id]
        
        # Check unavailable slots
        if (day, period) in teacher.unavailable_slots:
            return False
        
        # Check research slots
        if self.preferences.research_slot_protection and (day, period) in teacher.research_slots:
            return False
        
        # Check if already assigned
        for batch_id, schedule in timetable.items():
            if schedule[day][period] is not None:
                if schedule[day][period]['faculty_id'] == faculty_id:
                    return False
        
        # Check daily hour limit
        daily_hours = self.get_faculty_daily_hours(faculty_id, day, timetable)
        if daily_hours >= teacher.max_hours_per_day:
            return False
        
        return True
    
    def get_faculty_daily_hours(self, faculty_id: str, day: int, timetable: dict) -> int:
        """Get current daily hours for faculty"""
        hours = 0
        for batch_id, schedule in timetable.items():
            for period in range(self.periods_per_day):
                if schedule[day][period] is not None:
                    if schedule[day][period]['faculty_id'] == faculty_id:
                        hours += 1
        return hours
    
    def genetic_algorithm_evolution(self, population_size: int = 50, generations: int = 100) -> dict:
        """Main genetic algorithm with NEP-specific optimizations"""
        print(f"Initializing NEP-compliant timetable generation...")
        print(f"Population: {population_size}, Generations: {generations}")
        
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = self.create_initial_timetable()
            population.append(individual)
        
        best_fitness = 0
        best_timetable = None
        
        for gen in range(generations):
            # Calculate fitness
            fitness_scores = []
            for individual in population:
                fitness = self.calculate_nep_fitness(individual)
                fitness_scores.append(fitness)
            
            # Track best solution
            max_fitness = max(fitness_scores)
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_timetable = copy.deepcopy(population[fitness_scores.index(max_fitness)])
                print(f"Generation {gen}: New best fitness = {best_fitness:.2f}")
            
            # Early termination if perfect solution found
            if best_fitness >= 950:  # Near perfect solution
                break
            
            # Selection - Tournament selection with elitism
            new_population = []
            
            # Keep best 10% (elitism)
            elite_count = max(1, population_size // 10)
            elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elite_count]
            for i in elite_indices:
                new_population.append(copy.deepcopy(population[i]))
            
            # Tournament selection for remaining
            while len(new_population) < population_size:
                tournament_size = 5
                tournament_indices = random.sample(range(population_size), min(tournament_size, population_size))
                tournament_fitness = [fitness_scores[i] for i in tournament_indices]
                winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
                new_population.append(copy.deepcopy(population[winner_idx]))
            
            # Crossover and Mutation
            next_population = new_population[:elite_count]
            
            for i in range(elite_count, population_size, 2):
                if i + 1 < population_size:
                    parent1 = new_population[i]
                    parent2 = new_population[i + 1]
                    
                    if random.random() < 0.8:  # Crossover probability
                        child1, child2 = self.nep_crossover(parent1, parent2)
                    else:
                        child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                    
                    # Mutation
                    child1 = self.nep_mutation(child1, mutation_rate=0.1)
                    child2 = self.nep_mutation(child2, mutation_rate=0.1)
                    
                    next_population.extend([child1, child2])
                else:
                    next_population.append(copy.deepcopy(new_population[i]))
            
            population = next_population[:population_size]
        
        print(f"Evolution complete. Final best fitness: {best_fitness:.2f}")
        return best_timetable

    def calculate_nep_fitness(self, timetable: dict) -> float:
        """Calculate fitness score based on NEP 2020 guidelines"""
        base_score = 1000.0
        penalty = 0.0
        
        # Hard constraint violations
        penalty += self.check_faculty_conflicts(timetable) * 100
        penalty += self.check_classroom_conflicts(timetable) * 100
        penalty += self.check_workload_violations(timetable) * 80
        penalty += self.check_course_hour_requirements(timetable) * 60
        
        # Soft constraints
        penalty += self.check_faculty_preferences(timetable) * self.preferences.faculty_preference_weight
        penalty += self.check_schedule_gaps(timetable) * self.preferences.gap_penalty_weight
        penalty += self.check_workload_balance(timetable) * self.preferences.workload_balance_weight
        penalty += self.check_consecutive_violations(timetable) * 15
        penalty += self.check_lunch_violations(timetable) * 25
        
        # Bonuses
        bonus = 0.0
        bonus += self.calculate_interdisciplinary_bonus(timetable)
        bonus += self.calculate_skill_course_bonus(timetable)
        bonus += self.calculate_research_protection_bonus(timetable)
        
        return max(0, base_score - penalty + bonus)
    
    def check_faculty_conflicts(self, timetable: dict) -> int:
        """Check for faculty double-booking"""
        conflicts = 0
        faculty_schedule = defaultdict(lambda: defaultdict(list))
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        faculty_id = slot['faculty_id']
                        faculty_schedule[faculty_id][day].append(period)
        
        for faculty_id, days in faculty_schedule.items():
            for day, periods in days.items():
                duplicates = len(periods) - len(set(periods))
                conflicts += duplicates
        
        return conflicts
    
    def check_classroom_conflicts(self, timetable: dict) -> int:
        """Check for classroom double-booking"""
        conflicts = 0
        room_schedule = defaultdict(lambda: defaultdict(list))
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        room_id = slot['classroom_id']
                        room_schedule[room_id][day].append(period)
        
        for room_id, days in room_schedule.items():
            for day, periods in days.items():
                duplicates = len(periods) - len(set(periods))
                conflicts += duplicates
        
        return conflicts
    
    def check_workload_violations(self, timetable: dict) -> int:
        """Check NEP workload guideline violations"""
        violations = 0
        
        for faculty_id, faculty in self.teachers.items():
            weekly_hours = 0
            
            for batch_id, schedule in timetable.items():
                for day in range(self.days):
                    for period in range(self.periods_per_day):
                        slot = schedule[day][period]
                        if slot and slot['faculty_id'] == faculty_id:
                            weekly_hours += 1
            
            if weekly_hours > faculty.max_hours_per_week:
                violations += weekly_hours - faculty.max_hours_per_week
            
            for day in range(self.days):
                daily_hours = self.get_faculty_daily_hours(faculty_id, day, timetable)
                if daily_hours > faculty.max_hours_per_day:
                    violations += daily_hours - faculty.max_hours_per_day
        
        return violations
    
    def check_course_hour_requirements(self, timetable: dict) -> int:
        """Check if courses have required weekly hours"""
        violations = 0
        
        for batch_id, schedule in timetable.items():
            batch = self.student_batches[batch_id]
            course_hours = defaultdict(int)
            
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        course_hours[slot['course_id']] += 1
            
            all_courses = (batch.core_courses + batch.elective_courses + 
                          batch.skill_courses + batch.multidisciplinary_courses)
            
            for course_id in all_courses:
                if course_id in self.courses:
                    required = self.courses[course_id].hours_per_week
                    actual = course_hours[course_id]
                    violations += abs(required - actual)
        
        return violations
    
    def check_faculty_preferences(self, timetable: dict) -> int:
        """Check faculty time preference violations"""
        violations = 0
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        teacher = self.teachers[slot['faculty_id']]
                        
                        if teacher.preferred_time == TimePreference.MORNING and period >= 4:
                            violations += 1
                        elif teacher.preferred_time == TimePreference.AFTERNOON and period < 4:
                            violations += 1
        
        return violations
    
    def check_schedule_gaps(self, timetable: dict) -> int:
        """Check for gaps in daily schedules"""
        gaps = 0
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                day_periods = []
                for period in range(self.periods_per_day):
                    if schedule[day][period] is not None:
                        day_periods.append(period)
                
                if len(day_periods) > 1:
                    first_class = min(day_periods)
                    last_class = max(day_periods)
                    
                    for period in range(first_class + 1, last_class):
                        if period != self.preferences.lunch_break_period and schedule[day][period] is None:
                            gaps += 1
        
        return gaps
    
    def check_workload_balance(self, timetable: dict) -> float:
        """Check workload balance across faculty"""
        faculty_loads = defaultdict(int)
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        faculty_loads[slot['faculty_id']] += 1
        
        if not faculty_loads:
            return 0.0
        
        loads = list(faculty_loads.values())
        avg_load = sum(loads) / len(loads)
        variance = sum((load - avg_load) ** 2 for load in loads) / len(loads)
        
        return variance
    
    def check_consecutive_violations(self, timetable: dict) -> int:
        """Check for too many consecutive hours violations"""
        violations = 0
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                consecutive_count = 0
                prev_subject = None
                
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    current_subject = slot['course_id'] if slot else None
                    
                    if current_subject == prev_subject and current_subject is not None:
                        consecutive_count += 1
                        if consecutive_count > self.preferences.max_consecutive_same_subject:
                            violations += 1
                    else:
                        consecutive_count = 1 if current_subject else 0
                    
                    prev_subject = current_subject
        
        return violations
    
    def check_lunch_violations(self, timetable: dict) -> int:
        """Check lunch break violations"""
        violations = 0
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                if schedule[day][self.preferences.lunch_break_period] is not None:
                    violations += 1
        
        return violations
    
    def calculate_interdisciplinary_bonus(self, timetable: dict) -> float:
        """Calculate bonus for interdisciplinary courses"""
        bonus = 0.0
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        course = self.courses[slot['course_id']]
                        if course.is_interdisciplinary or course.course_type == CourseType.MULTIDISCIPLINARY:
                            bonus += self.preferences.interdisciplinary_bonus
        
        return bonus
    
    def calculate_skill_course_bonus(self, timetable: dict) -> float:
        """Calculate bonus for skill enhancement courses"""
        bonus = 0.0
        
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        course = self.courses[slot['course_id']]
                        if course.course_type in [CourseType.SKILL_ENHANCEMENT, CourseType.ABILITY_ENHANCEMENT]:
                            bonus += 5.0
        
        return bonus
    
    def calculate_research_protection_bonus(self, timetable: dict) -> float:
        """Calculate bonus for protecting faculty research time"""
        bonus = 0.0
        
        if not self.preferences.research_slot_protection:
            return bonus
        
        for faculty_id, teacher in self.teachers.items():
            research_slots_protected = 0
            
            for day, period in teacher.research_slots:
                if day < self.days:
                    slot_free = True
                    for batch_id, schedule in timetable.items():
                        if schedule[day][period] is not None:
                            if schedule[day][period]['faculty_id'] == faculty_id:
                                slot_free = False
                                break
                    
                    if slot_free:
                        research_slots_protected += 1
            
            bonus += research_slots_protected * 5.0
        
        return bonus
    
    def nep_crossover(self, parent1: dict, parent2: dict) -> Tuple[dict, dict]:
        """Perform crossover between two parent timetables"""
        child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        if not self.student_batches:
            return child1, child2
            
        batch_id_to_cross = random.choice(list(self.student_batches.keys()))
        day_to_swap = random.randrange(self.days)
        
        if batch_id_to_cross in child1 and batch_id_to_cross in child2:
            child1[batch_id_to_cross][day_to_swap] = parent2[batch_id_to_cross][day_to_swap].copy()
            child2[batch_id_to_cross][day_to_swap] = parent1[batch_id_to_cross][day_to_swap].copy()

        return child1, child2
    
    def nep_mutation(self, timetable: dict, mutation_rate: float = 0.1) -> dict:
        """Perform mutation on a timetable"""
        mutated = copy.deepcopy(timetable)
        
        if random.random() < mutation_rate:
            if not self.student_batches:
                return mutated
                
            batch_id_to_mutate = random.choice(list(self.student_batches.keys()))
            
            if batch_id_to_mutate in mutated and self.days >= 2:
                schedule = mutated[batch_id_to_mutate]
                day1, day2 = random.sample(range(self.days), 2)
                
                # Swap entire days
                temp = schedule[day1].copy()
                schedule[day1] = schedule[day2].copy()
                schedule[day2] = temp

        return mutated
    
    def export_nep_timetable(self, timetable: dict, filename: str = "nep_timetable.json") -> dict:
        """Export NEP-compliant timetable with detailed metadata"""
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "nep_2020_compliant": True,
                "total_batches": len(self.student_batches),
                "total_faculty": len(self.teachers),
                "total_courses": len(self.courses),
                "working_days": self.days,
                "periods_per_day": self.periods_per_day,
                "user_preferences": asdict(self.preferences)
            },
            "departments": list(self.departments),
            "timetables": {},
            "faculty_schedules": {},
            "classroom_utilization": {},
            "course_distribution": {},
            "analytics": {}
        }
        
        # Export batch timetables
        for batch_id, schedule in timetable.items():
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
                                "department": course.department
                            },
                            "faculty": {
                                "id": teacher.id,
                                "name": teacher.name,
                                "designation": teacher.designation
                            },
                            "classroom": {
                                "id": classroom.id,
                                "name": classroom.name,
                                "type": classroom.room_type.value,
                                "capacity": classroom.capacity
                            }
                        }
                    else:
                        if period == self.preferences.lunch_break_period:
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
        
        # Generate faculty schedules
        for faculty_id, teacher in self.teachers.items():
            faculty_schedule = {
                "faculty_info": {
                    "name": teacher.name,
                    "department": teacher.department,
                    "designation": teacher.designation
                },
                "weekly_load": 0,
                "schedule": []
            }
            
            weekly_hours = 0
            
            for day in range(self.days):
                day_schedule = {
                    "day": self.day_names[day],
                    "periods": []
                }
                
                for period in range(self.periods_per_day):
                    period_info = {"time": self.time_slots[period], "status": "free"}
                    
                    # Check if faculty is teaching
                    for batch_id, schedule in timetable.items():
                        slot = schedule[day][period]
                        if slot and slot['faculty_id'] == faculty_id:
                            course = self.courses[slot['course_id']]
                            batch = self.student_batches[batch_id]
                            
                            period_info = {
                                "time": self.time_slots[period],
                                "status": "teaching",
                                "course": course.name,
                                "batch": batch.name,
                                "classroom": self.classrooms[slot['classroom_id']].name
                            }
                            weekly_hours += 1
                            break
                    
                    # Check research slots
                    if (day, period) in teacher.research_slots:
                        period_info["status"] = "research"
                    
                    day_schedule["periods"].append(period_info)
                
                faculty_schedule["schedule"].append(day_schedule)
            
            faculty_schedule["weekly_load"] = weekly_hours
            export_data["faculty_schedules"][teacher.name] = faculty_schedule
        
        # Calculate analytics
        export_data["analytics"] = self.calculate_timetable_analytics(timetable)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"NEP-compliant timetable exported to {filename}")
        return export_data
    
    def calculate_timetable_analytics(self, timetable: dict) -> dict:
        """Calculate comprehensive timetable analytics"""
        analytics = {
            "fitness_score": self.calculate_nep_fitness(timetable),
            "constraint_violations": {
                "faculty_conflicts": self.check_faculty_conflicts(timetable),
                "classroom_conflicts": self.check_classroom_conflicts(timetable),
                "workload_violations": self.check_workload_violations(timetable),
                "lunch_violations": self.check_lunch_violations(timetable)
            },
            "faculty_utilization": {},
            "classroom_utilization": {},
            "course_type_distribution": defaultdict(int),
            "department_load_balance": defaultdict(int)
        }
        
        # Faculty utilization
        for faculty_id, teacher in self.teachers.items():
            weekly_hours = 0
            for batch_id, schedule in timetable.items():
                for day in range(self.days):
                    for period in range(self.periods_per_day):
                        slot = schedule[day][period]
                        if slot and slot['faculty_id'] == faculty_id:
                            weekly_hours += 1
            
            utilization_percentage = (weekly_hours / teacher.max_hours_per_week) * 100
            analytics["faculty_utilization"][teacher.name] = {
                "weekly_hours": weekly_hours,
                "max_hours": teacher.max_hours_per_week,
                "utilization_percentage": round(utilization_percentage, 2)
            }
        
        # Classroom utilization
        total_slots = self.days * self.periods_per_day
        for room_id, room in self.classrooms.items():
            used_slots = 0
            for batch_id, schedule in timetable.items():
                for day in range(self.days):
                    for period in range(self.periods_per_day):
                        slot = schedule[day][period]
                        if slot and slot['classroom_id'] == room_id:
                            used_slots += 1
            
            utilization_percentage = (used_slots / total_slots) * 100
            analytics["classroom_utilization"][room.name] = {
                "used_slots": used_slots,
                "total_slots": total_slots,
                "utilization_percentage": round(utilization_percentage, 2)
            }
        
        # Course type distribution
        for batch_id, schedule in timetable.items():
            for day in range(self.days):
                for period in range(self.periods_per_day):
                    slot = schedule[day][period]
                    if slot:
                        course = self.courses[slot['course_id']]
                        analytics["course_type_distribution"][course.course_type.value] += 1
        
        return analytics
    
    def print_nep_timetable_summary(self, timetable: dict):
        """Print NEP-compliant timetable summary"""
        print("\n" + "="*80)
        print("NEP 2020 COMPLIANT TIMETABLE GENERATION SUMMARY")
        print("="*80)
        
        analytics = self.calculate_timetable_analytics(timetable)
        
        print(f"\nOVERALL METRICS:")
        print(f"   Fitness Score: {analytics['fitness_score']:.2f}/1000")
        print(f"   Departments: {len(self.departments)}")
        print(f"   Student Batches: {len(self.student_batches)}")
        print(f"   Total Courses: {len(self.courses)}")
        print(f"   Faculty Members: {len(self.teachers)}")
        print(f"   Classrooms: {len(self.classrooms)}")
        
        print(f"\nCONSTRAINT VIOLATIONS:")
        violations = analytics['constraint_violations']
        print(f"   Faculty Conflicts: {violations['faculty_conflicts']}")
        print(f"   Classroom Conflicts: {violations['classroom_conflicts']}")
        print(f"   Workload Violations: {violations['workload_violations']}")
        print(f"   Lunch Break Violations: {violations['lunch_violations']}")
        
        print(f"\nCOURSE TYPE DISTRIBUTION (NEP 2020):")
        for course_type, count in analytics['course_type_distribution'].items():
            print(f"   {course_type.replace('_', ' ').title()}: {count} slots")
        
        print(f"\nTOP FACULTY UTILIZATION:")
        faculty_util = analytics['faculty_utilization']
        sorted_faculty = sorted(faculty_util.items(), key=lambda x: x[1]['utilization_percentage'], reverse=True)
        for name, util in sorted_faculty[:5]:
            print(f"   {name}: {util['weekly_hours']}/{util['max_hours']} hrs ({util['utilization_percentage']}%)")
        
        print(f"\nTOP CLASSROOM UTILIZATION:")
        room_util = analytics['classroom_utilization']
        sorted_rooms = sorted(room_util.items(), key=lambda x: x[1]['utilization_percentage'], reverse=True)
        for name, util in sorted_rooms[:5]:
            print(f"   {name}: {util['used_slots']}/{util['total_slots']} slots ({util['utilization_percentage']}%)")


# Web API Integration Functions
def create_nep_system_from_json(json_input: str, user_preferences: dict = None) -> NEPTimetableGenerator:
    """Create NEP system from JSON input"""
    prefs = UserPreferences()
    if user_preferences:
        for key, value in user_preferences.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
    
    generator = NEPTimetableGenerator(user_preferences=prefs)
    generator.load_from_json(json_input)
    
    return generator

def generate_timetable_api(json_input: str, user_preferences: dict = None, 
                          population_size: int = 50, generations: int = 100) -> dict:
    """Main API function for web integration"""
    print("Starting NEP 2020 Compliant Timetable Generation...")
    
    # Create system
    generator = create_nep_system_from_json(json_input, user_preferences)
    
    # Generate timetable
    best_timetable = generator.genetic_algorithm_evolution(population_size, generations)
    
    if best_timetable:
        # Export and return result
        result = generator.export_nep_timetable(best_timetable)
        generator.print_nep_timetable_summary(best_timetable)
        return result
    else:
        raise Exception("Failed to generate valid timetable. Please check constraints.")

# Sample data for testing
def create_sample_nep_data() -> dict:
    """Create sample NEP 2020 compliant data for testing"""
    return {
        "courses": [
            {
                "id": "CS101", "name": "Programming Fundamentals", "code": "CS101",
                "credits": 4, "course_type": "core", "hours_per_week": 4,
                "department": "Computer Science", "semester": 1, "faculty_id": "F001",
                "requires_lab": True, "requires_smart_room": False,
                "is_interdisciplinary": False, "max_students": 60,
                "preferred_days": [0, 2, 4]
            },
            {
                "id": "MATH101", "name": "Calculus I", "code": "MATH101",
                "credits": 4, "course_type": "core", "hours_per_week": 4,
                "department": "Mathematics", "semester": 1, "faculty_id": "F002",
                "requires_lab": False, "max_students": 80
            },
            {
                "id": "ENG101", "name": "Communication Skills", "code": "ENG101",
                "credits": 3, "course_type": "ability_enhancement", "hours_per_week": 3,
                "department": "English", "semester": 1, "faculty_id": "F003",
                "requires_smart_room": True, "max_students": 50
            },
            {
                "id": "ENV101", "name": "Environmental Science", "code": "ENV101",
                "credits": 2, "course_type": "multidisciplinary", "hours_per_week": 2,
                "department": "Environmental Science", "semester": 1, "faculty_id": "F004",
                "is_interdisciplinary": True, "connected_departments": ["Biology", "Chemistry"]
            }
        ],
        "faculty": [
            {
                "id": "F001", "name": "Dr. Rajesh Kumar", "department": "Computer Science",
                "designation": "Professor", "specializations": ["Programming", "Software Engineering"],
                "courses_can_teach": ["CS101"], "max_hours_per_day": 6, "max_hours_per_week": 20,
                "preferred_time": "morning", "research_slots": [[1, 6], [3, 7]]
            },
            {
                "id": "F002", "name": "Dr. Priya Sharma", "department": "Mathematics",
                "designation": "Associate Professor", "specializations": ["Calculus", "Linear Algebra"],
                "courses_can_teach": ["MATH101"], "preferred_time": "morning"
            },
            {
                "id": "F003", "name": "Prof. Anita Singh", "department": "English",
                "designation": "Assistant Professor", "specializations": ["Communication", "Literature"],
                "courses_can_teach": ["ENG101"], "preferred_time": "afternoon"
            },
            {
                "id": "F004", "name": "Dr. Kiran Patel", "department": "Environmental Science",
                "designation": "Professor", "specializations": ["Ecology", "Climate Change"],
                "courses_can_teach": ["ENV101"], "is_visiting": False
            }
        ],
        "classrooms": [
            {
                "id": "R101", "name": "Lecture Hall 1", "capacity": 80,
                "room_type": "lecture", "department": "General", "equipment": ["projector", "whiteboard"],
                "is_smart_room": True, "is_ac": True
            },
            {
                "id": "R201", "name": "Computer Lab 1", "capacity": 40,
                "room_type": "computer_lab", "department": "Computer Science",
                "equipment": ["computers", "projector"], "is_ac": True
            },
            {
                "id": "R301", "name": "Seminar Hall", "capacity": 50,
                "room_type": "seminar", "department": "General",
                "equipment": ["smart_board", "audio_system"], "is_smart_room": True
            }
        ],
        "student_batches": [
            {
                "id": "CS1A", "name": "CS First Year Section A", "department": "Computer Science",
                "semester": 1, "student_count": 55,
                "core_courses": ["CS101", "MATH101"],
                "elective_courses": [],
                "skill_courses": [],
                "multidisciplinary_courses": ["ENV101"],
                "preferred_morning_hours": True
            },
            {
                "id": "CS1B", "name": "CS First Year Section B", "department": "Computer Science",
                "semester": 1, "student_count": 50,
                "core_courses": ["CS101", "MATH101"],
                "elective_courses": [],
                "skill_courses": [],
                "multidisciplinary_courses": ["ENV101"]
            }
        ]
    }

# Main execution for testing
if __name__ == "__main__":
    sample_data = create_sample_nep_data()
    
    user_prefs = {
        "working_days": 5,
        "periods_per_day": 8,
        "lunch_break_period": 4,
        "faculty_preference_weight": 20.0,
        "interdisciplinary_bonus": 15.0,
        "research_slot_protection": True
    }
    
    try:
        result = generate_timetable_api(
            json.dumps(sample_data), 
            user_prefs, 
            population_size=30, 
            generations=50
        )
        
        print(f"\nTimetable generated successfully!")
        print(f"Exported to: nep_timetable.json")
        
    except Exception as e:
        print(f"Error: {e}")