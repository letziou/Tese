from dataclasses import dataclass

@dataclass(frozen=True)
class InstitutionalWeighting:
    weightingType: str          # institutional weight that can be TWOINAROW, TWOINADAY, PERIODSPREAD, NONMIXEDDURATIONS or FRONTLOAD
    paramOne: int               # the parameter of the institutional weight or if FRONTLOAD number of largest exams
    paramTwo: int = -1          # -1 or if FRONTLOAD number of last periods to take into account
    paramThree: int = -1        # -1 or if FRONTLOAD the penalty

    @classmethod
    def from_single_param(cls, weightingType: str, paramOne: int):  # Creation of an InstitutionalWeighting with only one parameter
        if weightingType == "FRONTLOAD":
            raise ValueError(f"{weightingType} requires 3 parameters.")
        return cls(weightingType, paramOne)

    @classmethod
    def from_three_params(cls, weightingType: str, paramOne: int, paramTwo: int, paramThree: int):  # Creation of an InstitutionalWeighting with three parameters (FRONTLOAD)
        if weightingType != "FRONTLOAD":
            raise ValueError(f"{weightingType} only requires 1 parameter.")
        return cls(weightingType, paramOne, paramTwo, paramThree)
