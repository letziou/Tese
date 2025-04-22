from .exam import Exam
from .period import Period
from .room import Room
from .exam_timetabling_problem import ExamTimetablingProblem
from .solution import Solution 

class FeasibilityTester:
    def __init__(self, problem: ExamTimetablingProblem):
        self.problem = problem

    def feasible_period(self, solution: Solution, assign_exam: Exam, period: Period) -> bool:
        exams = self.problem.exams_with_coincidence(assign_exam)
        if not all(exam.duration <= period.duration for exam in exams):      # Checking if assign_exam or any exam linked by EXAM_COINCIDENCE surpass period's length
            return False
        
        for exam in exams:
            if exam == assign_exam:
                continue
            if solution.period_from(exam) != period and solution.room_from(exam) != None:      # Checking if assign_exam or any exam linked by EXAM_COINCIDENCE is set to another period than the one beign tested (room is checked for when period is returned none)
                return False

        for exam in solution.exams_from_period(period):
            if(self.problem.clash_matrix[exam.number][assign_exam.number] > 0):      # Checking if assign_exam has one or more students that is already assigned in another exam in the period being tested or EXCLUSION constraint
                return False

        for period_constraint in self.problem.exams_with_type("AFTER", assign_exam.number):
            if period_constraint.exam_two == assign_exam.number and solution.period_from(self.problem.exams[period_constraint.exam_one]) != None and solution.period_from(self.problem.exams[period_constraint.exam_one]).number <= period.number:      # Checking if period for assign_exam is AFTER another exam from constraint
                return False
            if period_constraint.exam_one == assign_exam.number and solution.period_from(self.problem.exams[period_constraint.exam_two]) != None and solution.period_from(self.problem.exams[period_constraint.exam_two]).number >= period.number:      # Another exam must occur AFTER assign_exam
                return False 

        return True
    
    def feasible_room(self, solution: Solution, assign_exam: Exam, period: Period, room: Room) -> bool:
        capacity = self.current_room_capacity(solution, period, room)
        if len(assign_exam.students) > capacity:      # Checking if exam can fit in room
            return False

        if self.problem.room_exclusivity(assign_exam) and capacity != room.capacity:      # Checks if exam has room constraint and is fully available
            return False

        for constraint in self.problem.room_hard_constraints:      # Checking if other exams allocated have EXCLUSIVE
            if(solution.is_exam_set_to(period, room, self.problem.exams[constraint.exam_number])):
                return False
            
        return True
    
    def feasible_rooms(self, solution: Solution, assign_exam: Exam, period: Period, room: Room) -> bool:
        capacity = self.current_room_capacity(solution, period, room)
        if self.problem.room_exclusivity(assign_exam) and capacity != room.capacity:      # Checks if exam has room constraint and is fully available
            return False

        for constraint in self.problem.room_hard_constraints:      # Checking if other exams allocated have EXCLUSIVE
            if(solution.is_exam_set_to(period, room, self.problem.exams[constraint.exam_number])):
                return False
            
        return True
    
    def current_room_capacity(self, solution: Solution, period: Period, room: Room) -> int:
        capacity = room.capacity
        for exam in solution.exams_from_period_room(period, room):
            capacity -= len(exam.students)
        return capacity

