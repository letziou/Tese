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
            if hasattr(booking.rooms, '__iter__') and not isinstance(booking.rooms, str):
                room_numbers = [room.number for room in booking.rooms]
                file.write(f"{(booking.exam.number, booking.period.number, room_numbers)}\n")
            else:
                file.write(f"{(booking.exam.number, booking.period.number, booking.rooms.number)}\n")
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
        root.exams_left = []
        root.exams_assigned = {}
        root.problem = problem
        root.lower_bound = None
        # DSatur data structures
        root.num_exams = len(problem.exams)
        root.unassigned_exams = set(range(root.num_exams))
        root.saturation_degrees = [0] * root.num_exams      # tracking saturation degree (number of distinct adjacent colors/periods)
        root.adjacent_periods = [set() for _ in range(root.num_exams)]      # tracking periods used by adjacent exams
        return root

    def copy(self):
        clone = mcts.TreeNode.copy(self)
        clone.exams_left = list(self.exams_left)
        clone.exams_assigned = dict(self.exams_assigned)
        clone.problem = self.problem
        clone.lower_bound = None
        clone.num_exams = self.num_exams
        clone.unassigned_exams = set(self.unassigned_exams)
        clone.saturation_degrees = list(self.saturation_degrees)
        clone.adjacent_periods = [set(periods) for periods in self.adjacent_periods]
        return clone
    
    def next_exam(self):
        if not self.unassigned_exams:
            return None
        
        max_saturation = -1
        max_uncolored_adj = -1
        selected_exam = None

        for exam_id in self.unassigned_exams:
            saturation = self.saturation_degrees[exam_id]

            if saturation > max_saturation:
                max_saturation = saturation
                max_uncolored_adj = -1
                selected_exam = exam_id
            
            if saturation == max_saturation:
                conflicts = sum(1 for i in self.unassigned_exams
                                if i != exam_id and self.problem.clash_matrix[exam_id, i] > 0)
                
                if conflicts > max_uncolored_adj:
                    max_uncolored_adj = conflicts
                    selected_exam = exam_id
        
        return selected_exam

    def branches(self):
        exam_id = self.next_exam()
        if exam_id is None:
            return []
        
        self.exams_left = [self.problem.exams[exam_id]]

        solution = Solution(self.problem)
        solution.fill(self.exams_assigned)
        feasibility_tester = FeasibilityTester(self.problem)

        feasible_periods = [
            period for period in self.problem.periods
            if feasibility_tester.feasible_period(solution, self.problem.exams[exam_id], period)
        ]
        
        return feasible_periods

    def apply(self, period):
        if not self.exams_left:
            print("SHOULD NOT HAPPEN -- apply")
        
        exam = self.exams_left.pop(0)
        exam_id = exam.number

        solution = Solution(self.problem)
        solution.fill(self.exams_assigned)
        feasibility_tester = FeasibilityTester(self.problem)
        students_needed = len(exam.students)
        feasible_rooms = []
        room_selected = None
        
        for room in self.problem.rooms_exam_dictionary[exam]:
            if self.problem.room_period_full_dictionary[(room, period)]:
                continue

            room_capacity = feasibility_tester.current_room_capacity(solution, period, room)
            if room_capacity == 0:
                self.problem.room_period_full_dictionary[(room, period)] = True
                continue

            if feasibility_tester.feasible_room(solution, exam, period, room):
                if room_capacity == students_needed:
                    room_selected = room
                    break
                feasible_rooms.append((room, room_capacity))
        
        if not feasible_rooms and room_selected is None:      # If no feasible rooms, assigning a random room 
            feasible_rooms.append((random.choice(self.problem.rooms), 0))
        
        if room_selected is None:
            single_rooms = [(room, capacity) for room, capacity in feasible_rooms if capacity >= students_needed]
            if single_rooms:
                single_rooms.sort(key=lambda x: x[1])
                room_selected = single_rooms[0][0]
            else:
                room_selected = random.choice(self.problem.rooms)

        if room_selected is not None and feasibility_tester.current_room_capacity(solution, period, room_selected) >= students_needed:
            self.exams_assigned[exam] = (period, room_selected)
            if exam.exclusive:
                self.problem.room_period_full_dictionary[(room_selected, period)] = True
        else:
            multiple_rooms = []
            
            all_possible_rooms = []
            for room in self.problem.rooms:
                print("ENTERED")
                if not self.problem.room_period_full_dictionary[(room, period)]:
                    print("ENTERED")
                    capacity = feasibility_tester.current_room_capacity(solution, period, room)
                    if capacity > 0 and feasibility_tester.feasible_rooms(solution, exam, period, room):
                        print(f"ENTERED--{capacity}")
                        all_possible_rooms.append((room, capacity))
            
            print(all_possible_rooms)
            if all_possible_rooms:
                all_possible_rooms.sort(key=lambda x: x[1], reverse=True)
                
                combined_rooms = []
                combined_capacity = 0
                
                for room, capacity in all_possible_rooms:      # Adding rooms until enough capacity
                    combined_rooms.append(room)
                    combined_capacity += capacity
                    if combined_capacity >= students_needed:
                        multiple_rooms = combined_rooms
                        break
            
            if not multiple_rooms:
                multiple_rooms = [room_selected]
        
            self.exams_assigned[exam] = (period, multiple_rooms)
            if exam.exclusive:
                for room in multiple_rooms:
                    self.problem.room_period_full_dictionary[(room, period)] = True

        self.unassigned_exams.remove(exam_id)

        # Updating saturation degrees
        for adj_exam in range(self.num_exams):
            if adj_exam != exam_id and adj_exam in self.unassigned_exams:
                if self.problem.clash_matrix[exam_id, adj_exam] > 0:
                    if period not in self.adjacent_periods[adj_exam]:
                        self.adjacent_periods[adj_exam].add(period)
                        self.saturation_degrees[adj_exam] += 1

    def simulation_apply(self, period):
        if not self.exams_left:
            print("SHOULD NOT HAPPEN -- simulation_apply")

        exam = self.exams_left.pop(0)
        room = random.choice(self.problem.rooms)
        self.exams_assigned[exam] = (period, room)

        exam_id = exam.number
        self.unassigned_exams.remove(exam_id)

        # Updating saturation degrees
        for adj_exam in range(self.num_exams):
            if adj_exam != exam_id and adj_exam in self.unassigned_exams:
                if self.problem.clash_matrix[exam_id, adj_exam] > 0:
                    if period not in self.adjacent_periods[adj_exam]:
                        self.adjacent_periods[adj_exam].add(period)
                        self.saturation_degrees[adj_exam] += 1

    # Normal simulate
    #def simulate(self):
    #    node = self.copy()
    #
    #    for exam_id in node.unassigned_exams:
    #        node.exams_left.append(node.problem.exams[exam_id])
    #        
    #    while len(node.exams_left) > 0:
    #        node.simulation_apply(random.choice(node.problem.periods))  # monte carlo simulation
    #    
    #    solution = Solution(node.problem)
    #    solution.fill(node.exams_assigned)
    #    infeas = solution.calculate_score()
    #    if infeas > 0:
    #        return mcts.Solution(value=mcts.Infeasible(infeas),
    #                             data=solution.dictionary_to_list())
    #    else:
    #        return mcts.Solution(
    #            value=(infeas),
    #            data=solution.dictionary_to_list(),
    #    )
    
    # Heuristic simulate
    def simulate(self):
        node = self.copy()

        solution = Solution(node.problem)
        solution.fill(node.exams_assigned)
        feasibility_tester = FeasibilityTester(node.problem)

        while solution.calculate_score() == 0:
            exam_id = node.next_exam()
            exam = node.problem.exams[exam_id]

            # Find feasible periods for this exam
            feasible_periods = [
                period for period in node.problem.periods
                if feasibility_tester.feasible_period(solution, exam, period)
            ]

            if not feasible_periods:
                period = random.choice(node.problem.periods)      # If no feasible period, assigning a random period
            else:
                period_scores = []
                for period in feasible_periods:
                    conflict_count = 0
                    for adj_exam in range(node.num_exams):
                        if node.problem.clash_matrix[exam_id, adj_exam] > 0:
                            for assigned_exam, (assigned_period, _) in node.exams_assigned.items():
                                if assigned_exam.number == adj_exam and assigned_period == period:
                                    conflict_count += 1
                    period_scores.append((period, conflict_count))
                
                period_scores.sort(key=lambda x: x[1])
                period = period_scores[0][0]
            
            node.exams_left = [exam]
            node.simulation_apply(period)
            solution.fill(node.exams_assigned)
        
        infeas = len(node.unassigned_exams)
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
    elif choice.lower() == "instances":
        choice = input("Which instance?\n")
        run_monte_carlo(f"../instances/art0{choice.lower()}.exam", f"../solutions/instance_solution_{choice.lower()}.txt", rng_seed=int(time.time()*1000))
    else:
        run_monte_carlo(f"../datasets/exam_{choice.lower()}.exam", f"../solutions/solution_{choice.lower()}.txt", rng_seed=int(time.time()*1000))

if __name__ == "__main__":
    main()