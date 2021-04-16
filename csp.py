from typing import Generic, TypeVar, Dict, List
from abc import abstractmethod
import queue
import itertools
import copy

V = TypeVar('V')
D = TypeVar('D')

verbose = False


def print_dicts(printable_dict):
    for k, v in printable_dict.items():
        print(k, v)


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

    def __str__(self):
        return f"ARC:{self.x},{self.y}"


class CSP(Generic[V, D]):
    def __init__(self, variables: List[V], domains: Dict[V, List[D]]):
        self.variables: List[V] = variables
        self.domains: Dict[V, List[D]] = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        self.steps = 0

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

    def forward_checking(self, domains, single=False, assignment={}, lcv=False, mcv=False):
        results = []
        if len(assignment) == len(self.variables):
            if single:
                return assignment
            return [assignment]
        unassigned: List[V] = [v for v in self.variables if v not in assignment]
        # Check mcv heuristic
        if mcv:
            unassigned = self.most_constrained_variable(domains, unassigned)
        first: V = unassigned[0]
        # Values order with or without heuristic
        for value in domains[first] if not lcv else self.lcv(domains, assignment, first):
            mutable_domain = copy.deepcopy(domains)
            local_assignment = assignment.copy()

            local_assignment[first] = value
            self.steps += 1
            mutable_domain[first] = [value]

            if not self.check_fc(mutable_domain, local_assignment, first):
                # Dead end found
                if verbose:
                    print("Assignment:")
                    print_dicts(local_assignment)
                    print("causes dead end, because:")
                    print_dicts(mutable_domain)
                continue
            else:
                # Continue in this direction
                if verbose:
                    print("Modified domains:")
                    for k in mutable_domain.keys():
                        print(k, ": from", domains[k], "to", mutable_domain[k])
                result = self.forward_checking(mutable_domain, single, local_assignment, lcv, mcv)
                if result is not None:
                    if single:
                        return result
                    results.extend(result)
        if single:
            return None
        if len(results) != 0:
            return results
        else:
            return None

    def check_fc(self, domains, assignment, variable):
        # variable already assigned
        unary = []
        neighbours = []
        for c in self.constraints[variable]:
            if len([v for v in c.variables if v not in assignment or v == variable]) > 1:
                # Find all arcs with unassigned neighbours
                arcs = list(itertools.permutations(c.variables, 2))
                arcs = [arc for arc in arcs if arc[0] == variable and arc[1] not in assignment]
                for arc in arcs:
                    new_arc = Arc(arc[0], arc[1], c)
                    neighbours.append(new_arc)
            else:
                unary.append(c)

        # Check unary constraints
        for c in unary:
            if not c.satisfied(assignment):
                if verbose:
                    print("Unary fail")
                return False
        # Check constraints with neighbours
        localassignment = {variable: assignment[variable]}

        for neighbour in neighbours:
            new_domain = copy.deepcopy(domains[neighbour.y])
            for yv in domains[neighbour.y]:
                localassignment[neighbour.y] = yv
                # Remove value from domain if it doesn't satisfy constrain
                if not neighbour.constraint.satisfied(localassignment):
                    new_domain.remove(yv)

            if len(new_domain) == 0:
                # If neighbour out of values -> dead end
                domains[neighbour.y] = new_domain
                if verbose:
                    print("Binary fail")
                return False

            if len(new_domain) != len(domains[neighbour.y]):
                # Update domain
                domains[neighbour.y] = new_domain

            localassignment.pop(neighbour.y, None)
        return True

    def maintain_arc_consistency(self, domains, single=False, assignment={}, lcv=False, mcv=False):
        results = []
        if len(assignment) == len(self.variables):
            if single:
                return assignment
            return [assignment]
        unassigned: List[V] = [v for v in self.variables if v not in assignment]
        if mcv:
            unassigned = self.most_constrained_variable(domains, unassigned)
        first: V = unassigned[0]

        for value in domains[first] if not lcv else self.lcv(domains, assignment, first):
            mutable_domain = copy.deepcopy(domains)
            local_assignment = assignment.copy()

            local_assignment[first] = value
            self.steps += 1
            mutable_domain[first] = [value]
            if not self.ac3(local_assignment, mutable_domain, first):
                if verbose:
                    print("Assignment:")
                    print_dicts(local_assignment)
                    print("causes dead end, because:")
                    print_dicts(mutable_domain)
                # Dead end found
                continue
            else:
                if verbose:
                    print("Modified domains:")
                    for k in mutable_domain.keys():
                        print(k, ": from", domains[k], "to", mutable_domain[k])
                # Continue in this direction
                result = self.maintain_arc_consistency(mutable_domain, single, local_assignment, lcv, mcv)
                if result is not None:
                    # Result found
                    if single:
                        return result
                    results.extend(result)

        if single:
            return None
        if len(results) != 0:
            return results
        else:
            return None

    def backtracking_search(self, assignment={}, single=False, lcv=False, mcv=False):
        results = []
        if len(assignment) == len(self.variables):
            if single:
                return assignment
            return [assignment]

        unassigned: List[V] = [v for v in self.variables if v not in assignment]
        if mcv:
            unassigned = self.most_constrained_variable(self.domains, unassigned)
        first: V = unassigned[0]
        for value in self.domains[first] if not lcv else self.lcv(self.domains, assignment, first):
            local_assignment = assignment.copy()
            local_assignment[first] = value
            self.steps += 1
            if self.consistent(first, local_assignment):
                result = self.backtracking_search(local_assignment, single=single, lcv=lcv, mcv=mcv)
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

    def ac3(self, assignment, domains, first):
        unary = []
        all_arcs = set()
        arcs_queue = set()
        # Find all arcs between variables from constraints
        for v in self.constraints.keys():
            if v == first or v not in assignment.keys():
                for c in self.constraints[v]:
                    if len(c.variables) > 1:
                        arcs = list(itertools.permutations(c.variables, 2))
                        for arc in arcs:
                            new_arc = Arc(arc[0], arc[1], c)
                            all_arcs.add(new_arc)
                            arcs_queue.add(new_arc)
                    else:
                        unary.append(c)

        # Check unary constraints
        for c in unary:
            v = c.variables[0]
            possible = []
            for val in domains[v]:
                a = {v: val}
                if c.satisfied(a):
                    possible.append(val)
            domains[v] = possible
            if len(domains[v]) == 0:
                # If out of values -> dead end
                return False

        while len(arcs_queue) > 0:
            arc = list(arcs_queue)[0]
            arcs_queue.remove(arc)
            if self.remove_inconsistent(arc, assignment, domains):
                if len(domains[arc.x]) == 0:
                    # If neighbour out of values -> dead end
                    return False
                for other_arc in all_arcs:
                    # Add back all arcs related to modified domain
                    if other_arc.x != arc.y and other_arc.y == arc.x:
                        arcs_queue.add(other_arc)
        return True

    def remove_inconsistent(self, arc: Arc, assignment, domains):
        removed = False
        localassignment = assignment.copy()
        # Check which values can be removed from domains
        for xv in domains[arc.x]:
            localassignment[arc.x] = xv
            satisfies = False
            for yv in domains[arc.y]:
                localassignment[arc.y] = yv
                if arc.constraint.satisfied(localassignment):
                    satisfies = True
                    break
                else:
                    pass
            if not satisfies:
                domains[arc.x].remove(xv)
                removed = True
        return removed

    def lcv(self, domains, assignment, variable):
        # Least constraining values heuristic.
        arcs_queue = []
        for c in self.constraints[variable]:
            if len([v for v in c.variables if v not in assignment]) > 1:
                arcs = list(itertools.permutations(c.variables, 2))
                arcs = [arc for arc in arcs if arc[0] == variable]
                for arc in arcs:
                    new_arc = Arc(arc[0], arc[1], c)
                    arcs_queue.append(new_arc)

        # Count how many possible values for neighbours and sort DESC
        localassignment = assignment.copy()
        possible_values = {}
        for xv in domains[variable]:
            localassignment[variable] = xv
            possible_values[xv] = 0
            for neighbour in arcs_queue:
                for yv in domains[neighbour.y]:
                    localassignment[neighbour.y] = yv
                    if neighbour.constraint.satisfied(localassignment):
                        possible_values[xv] += 1
                localassignment.pop(neighbour.y, None)

        new_possible = [k for k, v in sorted(possible_values.items(), key=lambda item: item[1], reverse=True)]
        return new_possible

    def most_constrained_variable(self, domain, unassigned):
        return sorted(unassigned, key=lambda item: len(domain[item]), reverse=False)
