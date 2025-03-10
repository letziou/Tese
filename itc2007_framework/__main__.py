from .exam_timetabling_problem import ExamTimetablingProblem
from .exam_timetabling_solution import ExamTimetablingSolution
from .solution import Solution

from .exam import Exam
from .period import Period
from .room import Room
from .booking import Booking
from datetime import date, time

problem = ExamTimetablingProblem.from_file("datasets/exam_comp_set12.exam")

bookings = [
    Booking(exam=Exam(0, 120, 100), period=Period(1, date(2005, 4, 15), time(9, 30), 210, 0), room=Room(101, 200, 0)),
    Booking(exam=Exam(1, 120, 100), period=Period(2, date(2005, 4, 15), time(9, 30), 210, 0), room=Room(102, 200, 0))
]

exam = ExamTimetablingSolution(problem, bookings)

exam = problem.exams[0]
period = problem.periods[0]
room = problem.rooms[0]

exam_1 = problem.exams[1]
period_1 = problem.periods[1]
room_1 = problem.rooms[1]

exam_2 = problem.exams[2]
period_2 = problem.periods[2]
room_2 = problem.rooms[2]

solution = Solution(0, problem)

solution.set_exam(period, room, exam)  # Add the exam
solution.set_exam(period, room_1, exam_1)  # Add the exam

print(solution.exams_from_period_room(period, room))
print(solution.exams_from_period(period))

print(solution.fitness)
solution.fitness = 100
print(solution.fitness)