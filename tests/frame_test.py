import sys
sys.path.append('/home/letziou/5year/tese')

from itc2007_framework import ExamTimetablingProblem, Solution, FeasibilityTester

problem = ExamTimetablingProblem.from_file("datasets/exam_comp_set12m.exam")

solution = Solution(problem)
solution.set_exam(solution.problem.periods[1], solution.problem.rooms[0], solution.problem.exams[14])
solution.set_exam(solution.problem.periods[1], solution.problem.rooms[0], solution.problem.exams[19])

tester = FeasibilityTester(solution.problem)

for period in solution.problem.periods:
    print(tester.feasible_period(solution, solution.problem.exams[5], period))
