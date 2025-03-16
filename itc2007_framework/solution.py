from typing import List, Dict
from .exam import Exam
from .period import Period
from .room import Room
from .booking import Booking
from .exam_timetabling_problem import ExamTimetablingProblem
from .exam_timetabling_solution import ExamTimetablingSolution

class Solution:
    def __init__(self, problem: ExamTimetablingProblem):
        self.fitness = -1      # Initial fitness of solution
        self.problem = problem      # Contains problem from ExamTimetablingProblem containing the information on exams, rooms, periods, constraints and weightings
        self.bookings: Dict[Exam, tuple] = {}     # Dictionary for tracking exam-period-room assignments
        self.pre_association: Dict[Period, Dict[Room, List[Exam]]] = {      # Nested Dictionary that keeps track of which exams are pre-assigned to specific period-room combinations
            period: {room: [] for room in problem.rooms} 
            for period in problem.periods
        }

    def __str__(self) -> str:
        return f"Solution(id={self.id}, fitness={self.fitness})"
    
    def assigned_examinations(self) -> int:      # Returns number of assigned exams
        return len(self.bookings)
    
    def exam_count(self) -> int:      # Returns number of exams within the problem
        return len(self.problem.exams)
    
    def room_count(self) -> int:      # Returns number of rooms within problem
        return len(self.problem.rooms)
    
    def period_count(self) -> int:      # Returns number of periods within problem
        return len(self.problem.periods)
    
    def set_exam(self, period: Period, room: Room, exam: Exam):      # Booking exam to period and room
        self.bookings[exam] = (period, room)
        self.pre_association[period][room].append(exam)

    def unset_period_room_exam(self, period: Period, room: Room, exam: Exam):      # Removing exam from schedule 
        if exam in self.bookings:
            del self.bookings[exam]
        
        if period in self.pre_association and room in self.pre_association[period]:
            if exam in self.pre_association[period][room]:
                self.pre_association[period][room].remove(exam)

    def unset_exam(self, exam: Exam):      # Removing exam from schedule
        if exam in self.bookings:
            period, room = self.bookings[exam]

            del self.bookings[exam]

            if period in self.pre_association and room in self.pre_association[period]:
                if exam in self.pre_association[period][room]:
                    self.pre_association[period][room].remove(exam)
    
    def period_from(self, exam: Exam) -> Period:      # Returns the period where an exam is scheduled
        return self.bookings[exam][0] if exam in self.bookings else None
    
    def room_from(self, exam: Exam) -> Room:      # Returns the room where an exam is scheduled
        return self.bookings[exam][1] if exam in self.bookings else None
    
    def is_exam_set_to(self, period: Period, room: Room, exam: Exam) -> bool:      # Checks if an exam is set to a specific period and room
        return (self.bookings[exam][0] == period and self.bookings[exam][1] == room) if exam in self.bookings else False

    def exams_from_period_room(self, period: Period, room: Room) -> List[Exam]:      # Returns all exams assigned to a specific period and room
        return self.pre_association[period][room] if period in self.pre_association and room in self.pre_association[period] else []
    
    def exams_from_period(self, period: Period) -> List[Exam]:      # Returns all exams assigned to a specific period
        exams = []

        if period in self.pre_association:
            for room in self.pre_association[period]:
                exams.extend(self.pre_association[period][room])
        
        return exams
    
    def dictionary_to_list(self) -> List[Booking]:
        return [Booking(exam, period, room) for exam, (period, room) in self.bookings.items()]
    
    def calculate_score(self) -> int:
        bookings = self.dictionary_to_list()
        solution = ExamTimetablingSolution(self.problem, bookings)
        return solution.distance_to_feasibility()
    
    def fill(self, dictionary):
        # Clearing existing bookings and pre_associations
        self.bookings = {}
        self.pre_association = {
            period: {room: [] for room in self.problem.rooms} 
            for period in self.problem.periods
        }

        for exam, (period, room) in dictionary.items():
            self.set_exam(period, room, exam)
