import sys
sys.path.append('/home/letziou/5year/tese')

from itc2007_framework import Exam, Period, Room, Booking, ExamTimetablingProblem

from datetime import date, time

problem = ExamTimetablingProblem.from_file("datasets/exam_comp_set12m.exam")

bookings = [
    Booking(exam=Exam(0, 120, 100), period=Period(1, date(2005, 4, 15), time(9, 30), 210, 0), room=Room(101, 200, 0)),
    Booking(exam=Exam(1, 120, 100), period=Period(2, date(2005, 4, 15), time(9, 30), 210, 0), room=Room(102, 200, 0))
]

# To test function exclusion_in_matrix run program then go to line 30 comment the line and re-run program
print(problem.clash_matrix[14][19])

print(problem.type_has_exams("EXAM_COINCIDENCE"))
print(problem.type_has_exams("AFTER"))

print(problem.exams_with_type("EXAM_COINCIDENCE", 3))
print(problem.exams_with_type("EXAM_COINCIDENCE", 60))

print(problem.exams_with_coincidence(problem.exams[2]))
print(problem.exams_with_coincidence(problem.exams[60]))

print(problem.room_exclusivity(problem.exams[13]))
print(problem.room_exclusivity(problem.exams[14]))