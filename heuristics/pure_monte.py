import random
import time

import sys
sys.path.append('..')

import rr.opt.mcts.simple as mcts
from itc2007_framework import ExamTimetablingProblem, ExamTimetablingSolution, Solution

def run_monte_carlo(input_file, output_file, *args, **kwargs):
    problem = ExamTimetablingProblem.from_file(input_file)
    solution = Solution(problem)
    mcts.config_logging(level="INFO")
    root = ITCTreeNode.root(solution)
    sols = mcts.run(root, *args, **kwargs, time_limit=60*60)
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
    def root(cls, solution: Solution):
        root = cls()
        root.exams_left = solution.problem.exams_by_clashes()
        root.solution = solution
        root.upper_bound = None
        return root

    def copy(self):
        clone = mcts.TreeNode.copy(self)
        clone.exams_left = list(self.exams_left)
        clone.solution = self.solution
        clone.upper_bound = None
        return clone

    def branches(self):
       return self.solution.problem.periods if len(self.exams_left) > 0 else [] 

    def apply(self, period):
        exam = self.exams_left.pop()
        self.solution.set_exam(period, random.choice(self.solution.problem.rooms), exam)

    def simulate(self):
        node = self.copy()
        while len(node.exams_left) > 0:
            node.apply(random.choice(node.solution.problem.periods))  # monte carlo simulation
        return mcts.Solution(
            value=(node.solution.calculate_score()),
            data=node.solution.dictionary_to_list(),
        )


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