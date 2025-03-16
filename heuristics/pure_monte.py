import random
import time

import sys
sys.path.append('/home/letziou/5year/tese')

import rr.opt.mcts.simple as mcts
from itc2007_framework import ExamTimetablingProblem, ExamTimetablingSolution, Solution

def run_monte_carlo(*args, **kwargs):
    problem = ExamTimetablingProblem.from_file("/home/letziou/5year/tese/datasets/exam_comp_set12.exam")
    solution = Solution(problem)
    mcts.config_logging(level="INFO")
    root = ITCTreeNode.root(solution)
    sols = mcts.run(root, *args, **kwargs)
    
    e_t_solution = ExamTimetablingSolution(problem, sols.best.data)
    print(f"Hard Constraints Value -> {e_t_solution.distance_to_feasibility()}")
    print(f"Soft Constraints Value -> {e_t_solution.soft_constraint_violations()}")

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
    run_monte_carlo(rng_seed=int(time.time()*1000))

if __name__ == "__main__":
    main()