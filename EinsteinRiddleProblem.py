from csp import Constraint, CSP
from typing import Dict, List, Optional
import pprint


class Variable:
    def __init__(self, category, name):
        self.name = name
        self.category = category

    def __eq__(self, other):
        return self.name == other.name and self.category == other.category

    def __hash__(self):
        return hash(self.name) ^ hash(self.category)

    def __str__(self):
        return "Var: {}".format(self.name)


class EinsteinUniqueConstraint(Constraint[Variable, int]):
    def __init__(self, variable: Variable):
        super().__init__([variable])
        self.variable: Variable = variable

    def satisfied(self, assignment: Dict[Variable, int]) -> bool:
        for key, value in assignment.items():
            if key.name != self.variable.name and key.category == self.variable.category and value == assignment[self.variable]:
                return False
        return True


class EinsteinNeighbourConstraint(Constraint[Variable, int]):
    def __init__(self, var1: Variable, var2: Variable, where: str):
        super().__init__([var1, var2])
        self.var1: Variable = var1
        self.var2: Variable = var2
        self.where = where

    def satisfied(self, assignment: Dict[Variable, int]) -> bool:
        if self.var1 not in assignment or self.var2 not in assignment:
            return True

        if self.where == "LEFT":  # good direction?
            return assignment[self.var1]+1 == assignment[self.var2]
        elif self.where == "NEXT":
            return abs(assignment[self.var1] - assignment[self.var2]) == 1


class EinsteinSameHouseConstraint(Constraint[Variable, int]):
    def __init__(self, var1: Variable, var2: Variable):
        super().__init__([var1, var2])
        self.var1: Variable = var1
        self.var2: Variable = var2

    def satisfied(self, assignment: Dict[Variable, int]) -> bool:

        if self.var1 not in assignment or self.var2 not in assignment:
            return True
        return assignment[self.var1] == assignment[self.var2]


class EinsteinHouseNumberConstraint(Constraint[Variable, int]):
    def __init__(self, var1: Variable, number: int):
        super().__init__([var1])
        self.var1: Variable = var1
        self.number: int = number

    def satisfied(self, assignment: Dict[Variable, int]) -> bool:
        # print("Number")
        if self.var1 not in assignment:
            return True
        return assignment[self.var1] == self.number


if __name__ == "__main__":
    all_variables = {"color": ["Green", "Blue", "Yellow", "White", "Red"],
                     "tobacco": ["Cigar", "Light", "Cig", "No filter", "Menthol"],
                     "pet": ["Dogs", "Cats", "Horses", "Birds", "Fish"],
                     "nationality": ["Norwegian", "Swede", "German", "Dane", "Englishman"],
                     "drink": ["Tee", "Coffee", "Water", "Beer", "Milk"]}

    var_dict = {}
    for key, value in all_variables.items():
        for name in value:
            var_dict[name] = Variable(key, name)

    variables: List[Variable] = []
    for key, variable in var_dict.items():
        variables.append(variable)

    domains: Dict[Variable, List[int]] = {}
    for variable in variables:
        domains[variable] = [1, 2, 3, 4, 5]
    csp: CSP[Variable, int] = CSP(variables, domains)

    csp.add_constraint(EinsteinHouseNumberConstraint(var_dict["Norwegian"], 1))
    csp.add_constraint(EinsteinSameHouseConstraint(var_dict["Englishman"], var_dict["Red"]))
    csp.add_constraint(EinsteinNeighbourConstraint(var_dict["Green"], var_dict["White"], "LEFT"))
    csp.add_constraint(EinsteinSameHouseConstraint(var_dict["Dane"], var_dict["Tee"]))
    csp.add_constraint(EinsteinNeighbourConstraint(var_dict["Light"], var_dict["Cats"], "NEXT"))
    csp.add_constraint(EinsteinSameHouseConstraint(var_dict["Yellow"], var_dict["Cigar"]))
    csp.add_constraint(EinsteinSameHouseConstraint(var_dict["German"], var_dict["Cig"]))
    csp.add_constraint(EinsteinHouseNumberConstraint(var_dict["Milk"], 3))
    csp.add_constraint(EinsteinNeighbourConstraint(var_dict["Light"], var_dict["Water"], "NEXT"))
    csp.add_constraint(EinsteinSameHouseConstraint(var_dict["No filter"], var_dict["Birds"]))
    csp.add_constraint(EinsteinSameHouseConstraint(var_dict["Swede"], var_dict["Dogs"]))
    csp.add_constraint(EinsteinNeighbourConstraint(var_dict["Norwegian"], var_dict["Blue"], "NEXT"))
    csp.add_constraint(EinsteinNeighbourConstraint(var_dict["Horses"], var_dict["Yellow"], "NEXT"))
    csp.add_constraint(EinsteinSameHouseConstraint(var_dict["Menthol"], var_dict["Beer"]))
    csp.add_constraint(EinsteinSameHouseConstraint(var_dict["Green"], var_dict["Coffee"]))

    for name, val in var_dict.items():
        csp.add_constraint(EinsteinUniqueConstraint(val))

    solution: Optional[Dict[Variable, str]] = csp.backtracking_search(single=False)
    if len(solution) == 0:
        print("No solution!")
    else:
        for _solution in solution:
            for value in set(_solution.values()):
                print(f"{value}:", end=" ")
                values = []
                for k, v in _solution.items():
                    if v == value:
                        values.append(k.name)
                print(values)