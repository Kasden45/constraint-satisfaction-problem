from typing import Generic, TypeVar, Dict, List
from abc import abstractmethod

V = TypeVar('V')
D = TypeVar('D')


class Constraint(Generic[V, D]):
    def __init__(self, variables: List[V]):
        self.variables = variables

    @abstractmethod
    def satisfied(self, assignment: Dict[V, D]) -> bool:
        pass

class Arc(Generic[V, D]):
    def __init__(self, x: V, y: V, constraint: Constraint):
        self.x = x
        self.y = y
        self.constraint = constraint

class CSP(Generic[V, D]):
    def __init__(self, variables: List[V], domains: Dict[V, List[D]]):
        self.variables: List[V] = variables
        self.domains: Dict[V, List[D]] = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Variable must have a domain!")

    def add_constraint(self, constraint: Constraint[V, D]):
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("No variable in CSP")
            else:
                self.constraints[variable].append(constraint)

    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True

    def backtracking_search(self, assignment={}, single=False):
        results = []
        if len(assignment) == len(self.variables):
            if single:
                return assignment
            return [assignment]

        unassigned: List[V] = [v for v in self.variables if v not in assignment]
        first: V = unassigned[0]
        for value in self.domains[first]:
            local_assignment = assignment.copy()
            local_assignment[first] = value
            if self.consistent(first, local_assignment):
                result = self.backtracking_search(local_assignment, single=single)
                if result is not None:
                    if single:
                        return result
                    results.extend(result)

        if single:
            return None
        if results is not None and len(results) != 0:
            return results
        else:
            return None

    def ac3(self):
        pass

    def remove_inconsistent(self, arc: Arc, assignment):
        removed = False
        localassignment = assignment.copy()
        for xv in self.domains[arc.x]:
            localassignment[arc.x] = xv
            for yv in self.domains[arc.y]:
                localassignment[arc.y] = yv
                if arc.constraint.satisfied(localassignment):
                    break
            self.domains[arc.x].remove(xv)
            removed = True
        return removed



