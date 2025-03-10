from .exam_timetabling_problem import ExamTimetablingProblem
from .exam_timetabling_solution import ExamTimetablingSolution

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

print(exam)