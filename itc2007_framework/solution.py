from typing import List, Dict, Union
from .exam import Exam
from .period import Period
from .room import Room
from .booking import Booking
from .exam_timetabling_problem import ExamTimetablingProblem
from .exam_timetabling_solution import ExamTimetablingSolution

class Solution:
    def __init__(self, problem: ExamTimetablingProblem):
        self.problem = problem      # Contains problem from ExamTimetablingProblem containing the information on exams, rooms, periods, constraints and weightings
        self.bookings: Dict[Exam, tuple] = {}     # Dictionary for tracking exam-period-room assignments
        self.pre_association: Dict[Period, Dict[Room, List[Exam]]] = {      # Nested Dictionary that keeps track of which exams are pre-assigned to specific period-room combinations
            period: {room: [] for room in problem.rooms} 
            for period in problem.periods
        }

    def __str__(self) -> str:
        return f"Solution(id={self.id})"
    
    def assigned_examinations(self) -> int:      # Returns number of assigned exams
        return len(self.bookings)
    
    def exam_count(self) -> int:      # Returns number of exams within the problem
        return len(self.problem.exams)
    
    def room_count(self) -> int:      # Returns number of rooms within problem
        return len(self.problem.rooms)
    
    def period_count(self) -> int:      # Returns number of periods within problem
        return len(self.problem.periods)
    
    def set_exam(self, period: Period, rooms, exam: Exam):      # Booking exam to period and room
        self.bookings[exam] = (period, rooms)
        if hasattr(rooms, '__iter__'):
            for room in rooms:
                self.pre_association[period][room].append(exam)
        else:
            self.pre_association[period][rooms].append(exam)
    
    def is_exam_set_to(self, period: Period, room: Room, exam: Exam) -> bool:      # Checks if an exam is set to a specific period and room
        return (self.bookings[exam][0] == period and self.bookings[exam][1] == room) if exam in self.bookings else False
    
    def period_from(self, exam: Exam) -> Period:      # Returns the period where an exam is scheduled
        return self.bookings[exam][0] if exam in self.bookings else None
    
    def rooms_from(self, exam: Exam) -> List[Room]:      # Returns the rooms where an exam is scheduled
        return self.bookings[exam][1] if exam in self.bookings else None
    
    def room_from(self, exam: Exam) -> Union[Room, List[Room]]:      # Returns rooms (or first room for compatibility)
        rooms = self.rooms_from(exam)
        if rooms and isinstance(rooms, list) and len(rooms) > 0:
            return rooms[0]  # Return first room for backward compatibility
        return rooms

    def exams_from_period_room(self, period: Period, room: Room) -> List[Exam]:      # Returns all exams assigned to a specific period and room
        return self.pre_association[period][room] if period in self.pre_association and room in self.pre_association[period] else []
    
    def exams_from_period(self, period: Period) -> List[Exam]:      # Returns all exams assigned to a specific period
        exams = []

        if period in self.pre_association:
            for room in self.pre_association[period]:
                exams.extend(self.pre_association[period][room])
        
        return exams
    
    def dictionary_to_list(self) -> List[Booking]:      # Returns a list of Booking objects
        return [Booking(exam, period, room) for exam, (period, room) in self.bookings.items()]
    
    def calculate_score(self) -> int:      # Returns the feasibility score
        bookings = self.dictionary_to_list()
        solution = ExamTimetablingSolution(self.problem, bookings)
        return solution.distance_to_feasibility()
    
    def calculate_score_periods(self) -> int:      # Returns the feasibility score of period constraints
        bookings = self.dictionary_to_list()
        solution = ExamTimetablingSolution(self.problem, bookings)
        return solution.distance_to_feasibility_period()
    
    def calculate_softs(self) -> int:      # Returns the fitness of the solution
        bookings = self.dictionary_to_list()
        solution = ExamTimetablingSolution(self.problem, bookings)
        return solution.soft_constraint_violations()
    
    def fill(self, dictionary):
        # Clearing existing bookings and pre_associations
        self.bookings = {}
        self.pre_association = {
            period: {room: [] for room in self.problem.rooms} 
            for period in self.problem.periods
        }

        for exam, (period, room) in dictionary.items():
            self.set_exam(period, room, exam)
