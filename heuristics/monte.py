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
    sols = mcts.run(root, *args, **kwargs, time_limit=3600)
    e_t_solution = ExamTimetablingSolution(problem, sols.best.data)

    with open(output_file, "w") as file:
        file.write(f"{sols.best.data}\n")
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
        root.upper_bound = None
        return root

    def copy(self):
        clone = mcts.TreeNode.copy(self)
        clone.exams_left = list(self.exams_left)
        clone.exams_assigned = dict(self.exams_assigned)
        clone.problem = self.problem
        clone.upper_bound = None
        return clone

    def branches(self):
        if len(self.exams_left) == 0:
            return []
        
        exams = [exam for exam in self.exams_left if exam not in self.exams_assigned]
        exam = exams.pop()
        solution = Solution(self.problem)
        solution.fill(self.exams_assigned)
        feasibility_tester = FeasibilityTester(self.problem)
        
        feasible_periods = [
            period for period in self.problem.periods
            if feasibility_tester.feasible_period(solution, exam, period)
        ]
        return feasible_periods

    # Random choice room
    #def apply(self, period):
    #    exam = self.exams_left.pop()
    #    room = random.choice(self.problem.rooms)
    #    self.exams_assigned[exam] = (period, room)

    def apply(self, period):
        exam = self.exams_left.pop()
        solution = Solution(self.problem)
        solution.fill(self.exams_assigned)
        feasibility_tester = FeasibilityTester(self.problem)
        
        feasible_rooms = []
        room_selected = None

        for room in self.problem.rooms:
            if feasibility_tester.feasible_room(solution, exam, period, room):
                room_capacity = feasibility_tester.current_room_capacity(solution, period, room)
                if room_capacity == len(exam.students):     # If room capacity is exact for exam then the room is picked
                    room_selected = room
                feasible_rooms.append((room, room_capacity))

        if not feasible_rooms:  # What to do in this case Infeasible?
            return  
        
        # Sorting by smallest capacity and choosing first one
        feasible_rooms.sort(key=lambda x: x[1])
        if room_selected is None:
            room_selected = feasible_rooms[0][0]

        self.exams_assigned[exam] = (period, room_selected)
        

    def simulate(self):
        node = self.copy()
        while len(node.exams_left) > 0:
            node.apply(random.choice(node.problem.periods))  # monte carlo simulation
        
        solution = Solution(node.problem)
        solution.fill(node.exams_assigned)
        return mcts.Solution(
            value=(solution.calculate_score()),
            data=solution.dictionary_to_list(),
        )

    #def bound(self):
    #    if self.upper_bound is None:
    #        bound = self.total_value
    #        capacity = self.capacity_left
    #        for item in reversed(self.items_left):
    #            if item.weight <= capacity:
    #                bound += item.value
    #                capacity -= item.weight
    #            else:
    #                bound += item.value * capacity / item.weight
    #                break
    #        self.upper_bound = bound
    #    return self.upper_bound * -1  # flip bound
    

def main():
    choice = input("Would you like to run mcts on just one of the 12 datasets or all?\n")
    if choice.lower() == "all":
        for i in range(1,13):
            print(f"Dataset {i}")
            run_monte_carlo(f"../datasets/exam_comp_set{i}.exam", f"../solutions/check{i}.txt", rng_seed=int(time.time()*1000))
    elif 0 <= int(choice.lower()) < 13:
        run_monte_carlo(f"../datasets/exam_comp_set{choice.lower()}.exam", f"../solutions/check{choice.lower()}.txt", rng_seed=int(time.time()*1000))


if __name__ == "__main__":
    main()