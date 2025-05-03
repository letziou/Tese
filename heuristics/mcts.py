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
        
        # DSatur data structures
        self.num_exams = len(problem.exams)
        self.unassigned_exams = set(range(self.num_exams))
        if assigned_exams:
            for exam in assigned_exams:
                self.unassigned_exams.remove(exam.number)
        self.saturation_degrees = [0] * self.num_exams  # number of distinct adjacent periods
        self.adjacent_periods = [set() for _ in range(self.num_exams)]  # periods used by adjacent exams
        
        # Update saturation for already assigned exams
        if assigned_exams:
            for exam, (period, _) in assigned_exams.items():
                self._update_saturation(exam.number, period)
    
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

        actions = []
        for period in self.problem.periods:
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
        self.value = 0  # Lower value = better timetable
        self.untried_actions = self.state.get_legal_actions()
        
    def is_fully_expanded(self):      # Check if all possible child nodes have been created
        return len(self.untried_actions) == 0
        
    def is_terminal(self):      # Check if this node represents a terminal state
        return self.state.is_terminal()
        
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
        return child
        
    def best_child(self, exploration_weight=1.0):      # Selection of best child node using UCB1 formula for minimization
        if not self.children:
            return None
            
        # UCB1 for minimization (lower value is better)
        def ucb_score(child):
            exploitation = child.value / max(child.visits, 1)
            # Negative exploration component for minimization
            exploration = -exploration_weight * math.sqrt(2 * math.log(self.visits) / max(child.visits, 1))
            return exploitation + exploration
            
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


def backpropagate(node, result):      # Update of node values going up the tree
    while node is not None:
        node.visits += 1
        node.value += result
        node = node.parent


def simulate(state):      # Heuristic simulation from the given state to completion
    # Deep copy to avoid modifying the original
    current_state = copy.deepcopy(state)
    
    solution = Solution(current_state.problem)
    solution.fill(current_state.assigned_exams)
    feasibility_tester = FeasibilityTester(current_state.problem)
    
    # Heuristic simulation
    while not current_state.is_terminal():
        exam_id = current_state.next_exam()
        if exam_id is None:
            break
            
        exam = current_state.problem.exams[exam_id]
        
        # Find feasible periods for this exam
        feasible_periods = [
            period for period in current_state.problem.periods
            if feasibility_tester.feasible_period(solution, exam, period)
        ]

        if exam.number == 1:
            print(feasible_periods)
        
        # Select period - either best available or random if none are feasible
        if not feasible_periods:
            period = random.choice(current_state.problem.periods)
        else:
            # Score periods by conflict minimization
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
        
        # Select room - prefer one with capacity close to exam size
        feasible_rooms = []
        room_selected = None
        
        for room in current_state.problem.rooms_exam_dictionary[exam]:
            if current_state.problem.room_period_full_dictionary.get((room, period), False):
                continue
                
            room_capacity = feasibility_tester.current_room_capacity(solution, period, room)
            if room_capacity < current_state.problem.smallest_exam:
                continue
                
            if feasibility_tester.feasible_room(solution, exam, period, room):
                if room_capacity == len(exam.students):
                    room_selected = room
                    break
                feasible_rooms.append((room, room_capacity))
        
        if not feasible_rooms and room_selected is None:  
            # If no feasible room, pick random room
            room_selected = random.choice(current_state.problem.rooms)
        
        if room_selected is None:
            # Sort by smallest capacity and choose first one
            feasible_rooms.sort(key=lambda x: x[1])  
            room_selected = feasible_rooms[0][0]
        
        # Apply action
        action = (exam, period, room_selected)
        current_state = current_state.apply_action(action)
        
    solution.fill(current_state.assigned_exams)
    return (solution.calculate_score(), solution.dictionary_to_list())


def mcts_search(problem, time_budget=7200):
    # Initialize with empty timetable
    initial_state = ExamTimetableState(problem)
    root = TimetableNode(initial_state)
    best_score = sys.maxsize
    end_time = time.time() + time_budget
    iteration = 0
    try:
        print("Starting Search")
        while time.time() < end_time:
            iteration += 1
            if iteration % 100 == 0:
                print(f"Iteration {iteration}, best score: {best_score}")

            # 1. Selection
            node = select_node(root)
            
            # 2. Expansion
            if not node.is_terminal():
                child = node.expand()
                if child:
                    node = child
            else: break
            
            # 3. Simulation
            score, data = simulate(node.state)
            if score == 0: break
            elif score < best_score:
                print(f"New best solution: old_best_score={best_score} -> new_best_score={score}")
                best_score = score
                best_data = data 
            
            # 4. Backpropagation
            backpropagate(node, score)
            
    except KeyboardInterrupt:
        print("Keyboard break")

    # Return feasible solution found during simulation
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
    choice = input("Would you like to run mcts on just one of the 12 datasets or all?\n")
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