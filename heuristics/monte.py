import random
import time

import sys
sys.path.append('/home/letziou/5year/tese')

import rr.opt.mcts.simple as mcts
from itc2007_framework import ExamTimetablingProblem, ExamTimetablingSolution, Solution, FeasibilityTester

def run_monte_carlo(*args, **kwargs):
    problem = ExamTimetablingProblem.from_file("/home/letziou/5year/tese/datasets/exam_comp_set12.exam")
    mcts.config_logging(level="INFO")
    root = ITCTreeNode.root(problem)
    sols = mcts.run(root, *args, **kwargs)
    print(sols.best.data)

    e_t_solution = ExamTimetablingSolution(problem, sols.best.data)
    print(e_t_solution.distance_to_feasibility())
    print(e_t_solution.soft_constraint_violations())

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

    def apply(self, period):
        exam = self.exams_left.pop()
        room = random.choice(self.problem.rooms)
        self.exams_assigned[exam] = (period, room)

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
    run_monte_carlo(rng_seed=int(time.time()*1000))


if __name__ == "__main__":
    main()