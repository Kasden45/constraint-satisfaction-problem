from Grid import Grid, Point
from csp import Constraint, CSP
from typing import Dict, List, Optional
import pprint


class GridColoringConstraint(Constraint[Point, Point]):
    def __init__(self, point1: Point, point2: Point):
        super().__init__([point1, point2])
        self.point1: Point = point1
        self.point2: Point = point2

    def satisfied(self, assignment: Dict[Point, str]):
        if self.point1 not in assignment or self.point2 not in assignment:
            return True
        return assignment[self.point1] != assignment[self.point2]


if __name__ == "__main__":
    grid = Grid(30, 30)
    grid.random_points(3)  # n
    grid.generate_connections()
    variables: List[Point] = grid.points
    domains: Dict[Point, List[str]] = {}
    for variable in variables:
        domains[variable] = ["red", "green", "blue"]
    csp: CSP[Point, str] = CSP(variables, domains)
    for connection in grid.connections:
        csp.add_constraint(GridColoringConstraint(connection[0], connection[1]))

    solution: Optional[List[Dict[Point, str]]] = csp.backtracking_search(single=False)
    if solution is None or len(solution) == 0:
        print("No solution!")
    else:
        pprint.pprint(len(solution))
        pprint.pprint(solution)
        for sol in solution:
            grid.draw_grid(sol)