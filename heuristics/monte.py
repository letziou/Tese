import random
import time

import sys
sys.path.append('..')

import rr.opt.mcts.simple as mcts
from itc2007_framework import ExamTimetablingProblem, ExamTimetablingSolution, Solution, FeasibilityTester

def run_monte_carlo(input_file, output_file, *args, **kwargs):
    problem = ExamTimetablingProblem.from_file(input_file)
    mcts.config_logging(level="INFO")
    root = ITCTreeNode.root(problem)
    sols = mcts.run(root, *args, **kwargs, time_limit=7200)
    e_t_solution = ExamTimetablingSolution(problem, sols.best.data)

    with open(output_file, "w") as file:
        for booking in sols.best.data:
            file.write(f"{(booking.exam.number, booking.period.number, booking.room.number)}\n")
        file.write(f"Hard constraints -> {e_t_solution.distance_to_feasibility()}\n")
        file.write(f"Conflicting exams -> {e_t_solution.conflicting_exams()}\n")
        file.write(f"Overbooked periods -> {e_t_solution.overbooked_periods()}\n")
        file.write(f"Short Periods -> {e_t_solution.too_short_periods()}\n")
        file.write(f"Period constraints -> {e_t_solution.period_constraint_violations()}\n")
        file.write(f"Room constraints -> {e_t_solution.room_constraint_violations()}\n")
        file.write(f"Soft constraints -> {e_t_solution.soft_constraint_violations()}\n")
        file.write(f"Two in a row -> {e_t_solution.two_in_a_row_penalty()}\n")
        file.write(f"Two in a day -> {e_t_solution.two_in_a_day_penalty()}\n")
        file.write(f"Period spread -> {e_t_solution.period_spread_penalty()}\n")
        file.write(f"Mixed durations -> {e_t_solution.mixed_durations_penalty()}\n")
        file.write(f"Frontload -> {e_t_solution.frontload_penalty()}\n")
        file.write(f"Period penalty -> {e_t_solution.period_penalty()}\n")
        file.write(f"Room penalty -> {e_t_solution.room_penalty()}\n")

class ITCTreeNode(mcts.TreeNode):
    @classmethod
    def root(cls, problem: ExamTimetablingProblem):
        root = cls()
        root.exams_left = problem.exams_by_clashes()
        root.exams_assigned = {}
        root.problem = problem
        root.lower_bound = None
        return root

    def copy(self):
        clone = mcts.TreeNode.copy(self)
        clone.exams_left = list(self.exams_left)
        clone.exams_assigned = dict(self.exams_assigned)
        clone.problem = self.problem
        clone.lower_bound = None
        return clone

    def branches(self):
        if len(self.exams_left) == 0:
            return []
        
        exam = self.exams_left[0]
        #print(exam)
        solution = Solution(self.problem)
        solution.fill(self.exams_assigned)
        feasibility_tester = FeasibilityTester(self.problem)
        
        feasible_periods = [
            period for period in self.problem.periods
            if feasibility_tester.feasible_period(solution, exam, period)
        ]
        return feasible_periods

    # Random choice room
    def simulation_apply(self, period):
        exam = self.exams_left.pop(0)
        room = random.choice(self.problem.rooms)
        self.exams_assigned[exam] = (period, room)

    def apply(self, period):
        exam = self.exams_left.pop(0)
        solution = Solution(self.problem)
        solution.fill(self.exams_assigned)
        feasibility_tester = FeasibilityTester(self.problem)
        
        feasible_rooms = []
        room_selected = None

        for room in self.problem.rooms_exam_dictionary[exam]:
            room_capacity = feasibility_tester.current_room_capacity(solution, period, room)
            if room_capacity < self.problem.smallest_exam:
                self.problem.room_period_full_dictionary[(room, period)] = True
            
            if self.problem.room_period_full_dictionary[(room, period)]:
                continue

            if feasibility_tester.feasible_room(solution, exam, period, room):
                if room_capacity == len(exam.students):     # If room capacity is exact for exam then the room is picked
                    room_selected = room
                    break
                feasible_rooms.append((room, room_capacity))
        
        if not feasible_rooms:  # If no room force one
            feasible_rooms.append((random.choice(self.problem.rooms), 0))
            return 
        
        if room_selected is None:      # If no exact match
            feasible_rooms.sort(key=lambda x: x[1])      # Sorting by smallest capacity and choosing first one
            room_selected = feasible_rooms[0][0]

        self.exams_assigned[exam] = (period, room_selected)
        if exam.exclusive:
            self.problem.room_period_full_dictionary[(room, period)] = True
        

    def simulate(self):
        node = self.copy()
        while len(node.exams_left) > 0:
            node.simulation_apply(random.choice(node.problem.periods))  # monte carlo simulation
        
        solution = Solution(node.problem)
        solution.fill(node.exams_assigned)
        infeas = solution.calculate_score()
        if infeas > 0:
            return mcts.Solution(value=mcts.Infeasible(infeas),
                                 data=solution.dictionary_to_list())
        else:
            return mcts.Solution(
                value=(infeas),
                data=solution.dictionary_to_list(),
        )

    def bound(self):
        if self.lower_bound is None:
            solution = Solution(self.problem)
            solution.fill(self.exams_assigned)
            self.lower_bound = solution.calculate_score()
        return self.lower_bound
    

def main():
    choice = input("Would you like to run mcts on just one of the 12 datasets or all?\n")
    if choice.lower() == "all":
        for i in range(1,13):
            print(f"Dataset {i}")
            run_monte_carlo(f"../datasets/exam_comp_set{i}.exam", f"../solutions/solution_{i}.txt", rng_seed=int(time.time()*1000))
    elif choice.lower().isdigit():
        run_monte_carlo(f"../datasets/exam_comp_set{choice.lower()}.exam", f"../solutions/solution_{choice.lower()}.txt", rng_seed=int(time.time()*1000))
    else:
        run_monte_carlo(f"../datasets/exam_{choice.lower()}.exam", f"../solutions/solution_{choice.lower()}.txt", rng_seed=int(time.time()*1000))

if __name__ == "__main__":
    main()