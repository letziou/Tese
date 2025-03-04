import re
import numpy as np
from datetime import date, time
from .exam import Exam
from .period import Period
from .room import Room
from .period_hard_constraint import PeriodHardConstraint
from .room_hard_constraint import RoomHardConstraint
from .institutional_weighting import InstitutionalWeighting

class ExamTimetablingProblem:
    def __init__(self, exams, periods, rooms, period_hard_constraints, room_hard_constraints, institutional_weightings):
        self.exams = exams                                              # Exams to be booked
        self.periods = periods                                          # Periods in which exams can be booked
        self.rooms = rooms                                              # Rooms in which exams can be booked
        self.period_hard_constraints = period_hard_constraints          # Hard Constraints associated with periods
        self.room_hard_constraints = room_hard_constraints              # Hard Constraints associated with rooms
        self.institutional_weightings = institutional_weightings        # Institutional weightings for soft constraints

        # Initialize clash matrix
        num_exams = len(exams)
        self.clash_matrix = np.zeros((num_exams, num_exams), dtype=int)

        for i, exam_one in enumerate(exams):
            for j, exam_two in enumerate(exams):
                if i != j:
                    self.clash_matrix[i, j] = len(set(exam_one.students) & set(exam_two.students))

    @classmethod
    def from_file(cls, file_path):  # Reads an ITC2007 problem instance from a file.
        lines_size = cls._read_information(file_path)
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        exam_lines = int(lines_size.get("Exams", 0))
        starting_exam_line = 1
        period_lines = int(lines_size.get("Periods", 0))
        starting_period_line = 2 + exam_lines
        room_lines = int(lines_size.get("Rooms", 0))
        starting_room_line = 3 + exam_lines + period_lines
        periodHard_lines = int(lines_size.get("PeriodHardConstraints", 0))
        starting_periodHard_line = 4 + exam_lines + period_lines + room_lines
        roomHard_lines = int(lines_size.get("RoomHardConstraints", 0))
        starting_roomHard_line = 5 + exam_lines + period_lines + room_lines + periodHard_lines
        weight_lines = int(lines_size.get("InstitutionalWeightings", 0))
        starting_weight_line = 6 + exam_lines + period_lines + room_lines + periodHard_lines + roomHard_lines

        exams = cls._read_exams(lines, starting_exam_line, exam_lines)
        periods = cls._read_periods(lines, starting_period_line, period_lines)
        rooms = cls._read_rooms(lines, starting_room_line, room_lines)
        period_hard_constraints = cls._read_period_hard_constraints(lines, starting_periodHard_line, periodHard_lines)
        room_hard_constraints = cls._read_room_hard_constraints(lines, starting_roomHard_line, roomHard_lines)
        institutional_weightings = cls._read_institutional_weightings(lines, starting_weight_line, weight_lines)
        
        return cls(exams, periods, rooms, period_hard_constraints, room_hard_constraints, institutional_weightings)
        
    @staticmethod
    def _read_information(file_path):  # Extracting information from file
        size = {}

        with open(file_path, 'r') as file:
            lines = file.readlines()  # Reading all lines at once for easier processing
            line_count = len(lines)
            i = 0
            while i < line_count:
                line = lines[i]
                # Using regex to capture bracket pair in order to extract to file
                matches = re.findall(r'\[(.*?):(.*?)\]', line)
                # Checking for size
                if matches:
                    for match in matches:
                        word, value = match[0].strip(), match[1].strip()
                        size[word] = value
                else:
                    if line.startswith('[') and line.endswith(']\n'):
                        parameter_name = line[1:-2].strip()
                        if parameter_name not in size:
                            # Counting lines until next parameter
                            count_lines = 0
                            j = i + 1
                            while j < line_count and not re.findall(r'\[(.*?)]', lines[j]):
                                count_lines += 1
                                j += 1
                            size[parameter_name] = count_lines
                            i = j - 1
                i += 1
        return size
    
    @staticmethod
    def _read_exams(lines, start, exam_lines):
        exams = []
        for index in range(start, start + exam_lines):
            line_data = [int(x.strip()) for x in lines[index].split(',')]
            duration = line_data[0]
            students = line_data[1:]
            exams.append(Exam(len(exams), duration, students))
        return exams
    
    @staticmethod
    def _read_periods(lines, start, period_lines):
        periods = []
        for index in range(start, start + period_lines):
            line_data = lines[index].split(',')
            day, month, year = map(int, line_data[0].split(":"))
            hour, minute, second = map(int, line_data[1].split(":"))
            date_obj = date(year, month, day)
            time_obj = time(hour, minute, second)
            duration = int(line_data[2])
            penalty = int(line_data[3])
            periods.append(Period(len(periods), date_obj, time_obj, duration, penalty))
        return periods
    
    @staticmethod
    def _read_rooms(lines, start, room_lines):
        rooms = []
        for index in range(start, start + room_lines):
            parts = lines[index].split(",")
            capacity = int(parts[0])
            penalty = int(parts[1])
            rooms.append(Room(len(rooms), capacity, penalty))
        return rooms
    
    @staticmethod
    def _read_period_hard_constraints(lines, start, periodHard_lines):
        constraints = []
        for index in range(start, start + periodHard_lines):
            parts = lines[index].split(",")
            exam_one = int(parts[0])
            constraint_type = parts[1].strip()
            exam_two = int(parts[2])
            constraints.append(PeriodHardConstraint(exam_one, constraint_type, exam_two))
        return constraints
    
    @staticmethod
    def _read_room_hard_constraints(lines, start, roomHard_lines):
        constraints = []
        for index in range(start, start + roomHard_lines):
            parts = lines[index].split(",")
            exam = int(parts[0])
            constraint_type = parts[1].strip()
            constraints.append(RoomHardConstraint(exam, constraint_type))
        return constraints
    
    @staticmethod
    def _read_institutional_weightings(lines, start, weight_lines):
        weightings = []
        for index in range(start, start + weight_lines):
            parts = lines[index].split(",")
            weighting_type = parts[0]
            param_one = int(parts[1])

            if weighting_type == "FRONTLOAD":
                param_two = int(parts[2])
                param_three = int(parts[3])
                weightings.append(InstitutionalWeighting.from_three_params(weighting_type, param_one, param_two, param_three))
            else:
                weightings.append(InstitutionalWeighting.from_single_param(weighting_type, param_one))
        
        return weightings