import bisect
import random
import time
import copy
import math
import sys
sys.path.append('..')
from itc2007_framework import ExamTimetablingProblem, ExamTimetablingSolution, Solution, FeasibilityTester

class ExamTimetableState:
    def __init__(self, problem, assigned_exams=None):
        self.problem = problem  # ITC2007 problem instance
        self.assigned_exams = assigned_exams or {}
        self.period_remaining_capacity = self.problem.period_capacity
        
        # DSatur data structures
        self.num_exams = len(problem.exams)
        self.unassigned_exams = set(range(self.num_exams))
        self.saturation_degrees = [0] * self.num_exams  # number of distinct adjacent periods
        self.adjacent_periods = [set() for _ in range(self.num_exams)]  # periods used by adjacent exams
                
        if assigned_exams:
            for exam, (period, _) in assigned_exams.items():
                self.unassigned_exams.remove(exam.number)      # Remove exams already assigned
                self.period_remaining_capacity[period] -= len(exam.students)      # Update period capacity for exam assigned
                self._update_saturation(exam.number, period)      # Update saturation for already assigned exams
    
    def is_terminal(self):
        return len(self.unassigned_exams) == 0
    
    def next_exam(self):      # Select the next exam to schedule using the DSatur heuristic.
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
    
    def get_legal_actions(self):      # Creation of branches
        exam_id = self.next_exam()
        if exam_id is None:
            return []
        
        exam = self.problem.exams[exam_id]
        
        solution = Solution(self.problem)
        solution.fill(self.assigned_exams)
        feasibility_tester = FeasibilityTester(self.problem)
        linked_exams = self.problem.exams_with_coincidence(exam)
        actions = []

        if len(linked_exams) > 1:
            for linked_exam in linked_exams:
                if linked_exam != exam and linked_exam.number not in self.unassigned_exams:
                    linked_period = self.assigned_exams[linked_exam][0]
                    single_room = self._find_single_room(solution, exam, linked_period, feasibility_tester)
                    if single_room:
                        actions.append((exam, linked_period, single_room))
                    else:
                        multiple_rooms = self._find_multiple_rooms(solution, exam, linked_period, feasibility_tester)
                        if multiple_rooms:
                            actions.append((exam, linked_period, multiple_rooms))

        if not actions:
            sorted_periods = sorted(      # Sorting periods according to higher capacity
            self.problem.periods,
            key=lambda p: self.period_remaining_capacity[p],
            reverse=True
            )

            for period in sorted_periods:
                if feasibility_tester.feasible_period(solution, exam, period):
                    single_room = self._find_single_room(solution, exam, period, feasibility_tester)
                    if single_room:
                        actions.append((exam, period, single_room))
                    else:
                        multiple_rooms = self._find_multiple_rooms(solution, exam, period, feasibility_tester)
                        if multiple_rooms:
                            actions.append((exam, period, multiple_rooms))
        
        return actions
    
    def _find_single_room(self, solution, exam, period, feasibility_tester):
        students_needed = len(exam.students)
        feasible_rooms = []
        
        for room in self.problem.rooms:
            if self.problem.room_period_full_dictionary[room, period]:
                continue

            room_capacity = feasibility_tester.current_room_capacity(solution, period, room)
            if room_capacity < students_needed:
                continue

            if feasibility_tester.feasible_room(solution, exam, period, room):
                if room_capacity == students_needed:
                    return room
                feasible_rooms.append((room, room_capacity))
        
        if feasible_rooms:      # Find best-fit room (smallest room that fits)
            feasible_rooms.sort(key=lambda x: x[1])   
            return feasible_rooms[0][0]
        
        return None
    
    def _find_multiple_rooms(self, solution, exam, period, feasibility_tester):
        students_needed = len(exam.students)
        all_possible_rooms = []
        
        for room in self.problem.rooms:
            if not self.problem.room_period_full_dictionary[room, period]:
                capacity = feasibility_tester.current_room_capacity(solution, period, room)
                if capacity > 0 and feasibility_tester.feasible_rooms(solution, exam, period, room):
                    all_possible_rooms.append((room, capacity))
        
        if not all_possible_rooms:
            return [random.choice(self.problem.rooms)]
        
        all_possible_rooms.sort(key=lambda x: x[1], reverse=True)
        combined_rooms = []
        combined_capacity = 0
        
        for room, capacity in all_possible_rooms:
            combined_rooms.append(room)
            combined_capacity += capacity
            if combined_capacity >= students_needed:
                return combined_rooms
            
        return [random.choice(self.problem.rooms)]      # If not enough rooms just send random room

    def apply_action(self, action):      # Application of branch
        exam, period, room_info = action
        
        # Create a new state with the additional assignment
        new_assigned = dict(self.assigned_exams)
        new_assigned[exam] = (period, room_info)
        new_state = ExamTimetableState(self.problem, new_assigned)
        
        # Update room fullness if exam is exclusive
        if exam.exclusive:
            if isinstance(room_info, list):
                for room in room_info:
                    new_state.problem.room_period_full_dictionary[(room, period)] = True
            else:
                new_state.problem.room_period_full_dictionary[(room_info, period)] = True
            
        return new_state
    
    def _update_saturation(self, assigned_exam_id, period):      # Update saturation degrees for unassigned exams
        for exam_id in self.unassigned_exams:
            if self.problem.clash_matrix[assigned_exam_id, exam_id] > 0:
                if period not in self.adjacent_periods[exam_id]:
                    self.adjacent_periods[exam_id].add(period)
                    self.saturation_degrees[exam_id] += 1

class TimetableNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action  # Action that led to this state
        self.children = []
        self.visits = 0
        self.untried_actions = self.state.get_legal_actions()
        self.value = (0, 0)  # Lower value = better timetable
        # Ranking System
        self.sorted_children = []
        self.child_rankings = {}
        self.node_id = id(self)

    def __lt__(self, other):
        return self.node_id < other.node_id
    
    def __eq__(self, other):
        return self.node_id == other.node_id
    
    def __hash__(self):
        return hash(self.node_id)
        
    def is_fully_expanded(self):      # Check if all possible child nodes have been created
        return len(self.untried_actions) == 0
        
    def is_terminal(self):      # Check if this node represents a terminal state
        return self.state.is_terminal()
    
    def get_child_value(self, child):      # Function to return child value
        if child.visits == 0:      # Try and force to visit unvisited childs
            return (float('inf'), float('inf'))
        else:
            return (child.value[0] / child.visits, child.value[1] / child.visits)
    
    def update_rankings(self):      # Function to update all rankings
        n = len(self.sorted_children)
        for i, (_, _, child) in enumerate(self.sorted_children):
            rank = i + 1
            self.child_rankings[child] = 1 / rank
    
    def update_child_rank(self, child):
        old_entry = None
        new_value = self.get_child_value(child)

        for i, (value, _, c) in enumerate(self.sorted_children):
            if c is child:
                old_entry = (i, (value, _, c))
                break
        
        if old_entry:
            self.sorted_children.pop(old_entry[0])
        
        bisect.insort(self.sorted_children, (new_value, child.node_id, child))

        self.update_rankings()
        
    def expand(self):      # Creation of a new child node from an untried action
        if not self.untried_actions:
            return None
            
        # Pop an untried action
        action = self.untried_actions.pop()
        
        # Create new state by applying the action
        new_state = self.state.apply_action(action)
        
        # Create new child node
        child = TimetableNode(new_state, parent=self, action=action)
        self.children.append(child)

        child_value = self.get_child_value(child)
        bisect.insort(self.sorted_children, (child_value, child.node_id, child))
        self.update_rankings()

        return child
        
    def best_child(self, exploration_weight=0.1):      # Selection of best child node using UCB1 formula for minimization
        if not self.children:
            return None
        
        def ucb_score(child):
            exploitation = self.child_rankings.get(child, 0)
            exploration = -exploration_weight * math.sqrt(2 * math.log(self.visits) / max(child.visits, 1))

            return -(exploitation + exploration)
            
        return min(self.children, key=ucb_score)


def select_node(node):      # Selection of node for expansion using tree policy
    while not node.is_terminal():
        if not node.is_fully_expanded():
            return node
        else:
            if node.best_child() is None:
                return node.parent
            node = node.best_child()
    return node


def backpropagate(node, hard_result, soft_result):      # Update of node values going up the tree
    while node is not None:
        node.visits += 1
        if hard_result == 0:      # Feasible solution
            current_hard, current_soft = node.value
            node.value = (current_hard + hard_result, current_soft + soft_result)
        else:
            current_hard, current_soft = node.value
            node.value = (current_hard + hard_result, current_soft)

        if node.parent is not None:
            node.parent.update_child_rank(node)

        node = node.parent


def simulate(state):      # Heuristic simulation from the given state to completion
    # Deep copy to avoid modifying the original
    current_state = copy.deepcopy(state)
    
    solution = Solution(current_state.problem)
    feasibility_tester = FeasibilityTester(current_state.problem)
    
    # Heuristic simulation
    while not current_state.is_terminal():
        exam_id = current_state.next_exam()
        if exam_id is None:
            break
            
        exam = current_state.problem.exams[exam_id]
        solution.fill(current_state.assigned_exams)
        students_needed = len(exam.students)
        
        sorted_periods = sorted(current_state.problem.periods, key=lambda p:(
                                    current_state.period_remaining_capacity[p] >= students_needed,
                                    current_state.period_remaining_capacity[p]
                                ), reverse=True)
        
        feasible_periods = []
        for period in sorted_periods:
            if current_state.period_remaining_capacity[period] >= students_needed and feasibility_tester.feasible_period(solution, exam, period):
                feasible_periods.append(period)

        if not feasible_periods:      # If no periods have enough capacity, trying with any remaining capacity
            for period in sorted_periods:
                if feasibility_tester.feasible_period(solution, exam, period):
                    feasible_periods.append(period)

            if not feasible_periods:      # If there are still no periods choose random
                period = random.choice(current_state.problem.periods)
            else:      # Scoring periods by conflict minimization
                period_scores = []
                for period in feasible_periods:
                    conflict_count = 0
                    for adj_exam in range(current_state.num_exams):
                        if current_state.problem.clash_matrix[exam_id, adj_exam] > 0:
                            for assigned_exam, (assigned_period, _) in current_state.assigned_exams.items():
                                if assigned_exam.number == adj_exam and assigned_period == period:
                                    conflict_count += 1
                    period_scores.append((period, conflict_count))
                
                period_scores.sort(key=lambda x: x[1])  # Sort by lowest conflict count
                period = period_scores[0][0]

        else:      # Scoring periods by conflict minimization and remaining capacity
            period_scores = []
            for period in feasible_periods:
                conflict_count = 0
                for adj_exam in range(current_state.num_exams):
                    if current_state.problem.clash_matrix[exam_id, adj_exam] > 0:
                        for assigned_exam, (assigned_period, _) in current_state.assigned_exams.items():
                            if assigned_exam.number == adj_exam and assigned_period == period:
                                conflict_count += 1
                
                capacity_score = current_state.period_remaining_capacity[period] / max(students_needed, 1)
                combined_score = conflict_count - (0.1 * capacity_score)
                period_scores.append((period, combined_score))
            
            period_scores.sort(key=lambda x: x[1])  # Sort by lowest conflict count
            period = period_scores[0][0]
        
        room_selected = current_state._find_single_room(solution, exam, period, feasibility_tester)      # First single room try

        if room_selected is None:
            room_selected = current_state._find_multiple_rooms(solution, exam, period, feasibility_tester)      # Then multiples
        
        # Apply action
        action = (exam, period, room_selected)
        current_state = current_state.apply_action(action)
        
    solution.fill(current_state.assigned_exams)
    return (solution.calculate_score(), solution.calculate_softs(), solution.dictionary_to_list())


def mcts_search(problem, time_budget=7200):
    # Initialize with empty timetable
    initial_state = ExamTimetableState(problem)
    root = TimetableNode(initial_state)
    f_best_score , inf_best_score = None, None
    singleton = False
    start_time = time.time()
    end_time = time.time() + time_budget
    iteration = 0
    try:
        print("Starting Search")
        while time.time() < end_time:
            iteration += 1
            if iteration % 100 == 0:
                elapsed = time.time() - start_time
                if not singleton:
                    print(f"Iteration {iteration}, time elapsed: {elapsed:.1f}s, best infeasible solution: {inf_best_score}")
                else: print(f"Iteration {iteration}, time elapsed: {elapsed:.1f}s, best feasible solution: {f_best_score}")

            # 1. Selection
            node = select_node(root)
            
            # 2. Expansion
            if not node.is_terminal():
                child = node.expand()
                if child:
                    node = child
            else: 
                print("No more expansion steps")
                break
            
            # 3. Simulation
            score, soft_score, data = simulate(node.state)
            if score == 0:
                elapsed = time.time() - start_time
                if not singleton: 
                    print(f"Found feasible solution at iteration {iteration} with time elapsed: {elapsed:.1f}s")
                    singleton = True

                if f_best_score == None or soft_score < f_best_score:
                    print(f"New best solution: old best feasible solution={f_best_score} -> new best feasible solution={soft_score} with time elapsed: {elapsed:.1f}s")   
                    f_best_score = soft_score
                    best_data = data 
                
            elif inf_best_score == None or score < inf_best_score:
                elapsed = time.time() - start_time
                print(f"New best solution: old best infeasible solution={inf_best_score} -> new best infeasible solution={score} with time elapsed: {elapsed:.1f}s")
                inf_best_score = score
                best_data = data 
            
            # 4. Backpropagation
            backpropagate(node, score, soft_score)
            
    except KeyboardInterrupt:
        print("Keyboard break")

    # Return feasible solution found during simulation
    if not singleton:
        print(f"Stopped at iteration {iteration}, with best infeasible solution=({inf_best_score})")
    else: print(f"Stopped at iteration {iteration}, with best feasible solution=({f_best_score})")
    return best_data


def run_monte_carlo(input_file, output_file):
    problem = ExamTimetablingProblem.from_file(input_file)
    
    # Run MCTS search
    solution_data = mcts_search(problem)
    
    # Create solution object
    e_t_solution = ExamTimetablingSolution(problem, solution_data)

    # Write results to file
    with open(output_file, "w") as file:
        for booking in solution_data:
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


def main():
    choice = sys.argv[1]
    if choice.lower() == "all":
        for i in range(1,13):
            print(f"Dataset {i}")
            run_monte_carlo(f"../datasets/exam_comp_set{i}.exam", f"../solutions/solution_{i}.txt")
    elif choice.lower().isdigit():
        run_monte_carlo(f"../datasets/exam_comp_set{choice.lower()}.exam", f"../solutions/solution_{choice.lower()}.txt")
    elif choice.lower() == "instances":
        choice = input("Which instance?\n")
        run_monte_carlo(f"../instances/art0{choice.lower()}.exam", f"../solutions/instance_solution_{choice.lower()}.txt")
    else:
        run_monte_carlo(f"../datasets/exam_{choice.lower()}.exam", f"../solutions/solution_{choice.lower()}.txt")


if __name__ == "__main__":
    main()
