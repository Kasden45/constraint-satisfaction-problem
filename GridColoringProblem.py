import copy

from Grid import Grid, Point
from csp import Constraint, CSP
from typing import Dict, List, Optional
import pprint


def results(solution, problem, grid, show_grid=False):
    if solution is None or len(solution) == 0:
        print("No solution!")
    else:
        print("Steps", problem.steps)
        pprint.pprint(len(solution))
        #pprint.pprint(solution)
        if show_grid:
            if isinstance(solution, list):
                for sol in solution:
                    grid.draw_grid(sol)
            else:
                grid.draw_grid(solution)

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
    grid.random_points(11)  # n
    grid.generate_connections()
    variables: List[Point] = grid.points
    domains: Dict[Point, List[str]] = {}
    for variable in variables:
        domains[variable] = ["red", "green", "blue", "yellow"]
    csp: CSP[Point, str] = CSP(variables, domains)
    for connection in grid.connections:
        csp.add_constraint(GridColoringConstraint(connection[0], connection[1]))
    # solution = csp.maintain_arc_consistency(domains=csp.domains, lcv=True, mcv=True)
    # solution = csp.forward_checking(domains=csp.domains, lcv=True, mcv=True)
    # solution: Optional[List[Dict[Point, str]]] = csp.backtracking_search(single=False, lcv=False, mcv=True)
    # single = False
    # lcv = True
    # mcv = True
    #
    # mac_csp = copy.copy(csp)
    # solution_mac: Optional[Dict[Point, str]] = mac_csp.maintain_arc_consistency(domains=csp.domains, single=single, lcv=lcv,
    #                                                                                mcv=mcv)
    # fc_csp = copy.copy(csp)
    # solution_fc: Optional[Dict[Point, str]] = fc_csp.forward_checking(domains=csp.domains, single=single, lcv=lcv, mcv=mcv)
    # bt_csp = copy.copy(csp)
    # solution_bt: Optional[Dict[Point, str]] = bt_csp.backtracking_search(single=single, lcv=lcv, mcv=mcv)
    #
    # results(solution_bt, bt_csp, grid)
    # results(solution_fc, fc_csp, grid)
    # results(solution_mac, mac_csp, grid)
    # """
    #     WITHOUT MCV
    # """
    # mcv = False
    # mac_csp = copy.copy(csp)
    # solution_mac: Optional[Dict[Point, str]] = mac_csp.maintain_arc_consistency(domains=csp.domains, single=single, lcv=lcv,
    #                                                                                mcv=mcv)
    # fc_csp = copy.copy(csp)
    # solution_fc: Optional[Dict[Point, str]] = fc_csp.forward_checking(domains=csp.domains, single=single, lcv=lcv, mcv=mcv)
    # bt_csp = copy.copy(csp)
    # solution_bt: Optional[Dict[Point, str]] = bt_csp.backtracking_search(single=single, lcv=lcv, mcv=mcv)
    #
    # results(solution_bt, bt_csp, grid)
    # results(solution_fc, fc_csp, grid)
    # results(solution_mac, mac_csp, grid)

    for lcv in [True, False]:
        for mcv in [True, False]:
            for single in [True, False]:
                print("mcv", mcv)
                print("lcv", lcv)
                print("single solution", single)
                mac_csp = copy.copy(csp)
                solution_mac: Optional[Dict[Point, str]] = mac_csp.maintain_arc_consistency(domains=csp.domains,
                                                                                               single=single, lcv=lcv,
                                                                                               mcv=mcv)
                print("MAC", mac_csp.steps)
                # results(solution_mac, mac_csp)

                fc_csp = copy.copy(csp)
                solution_fc: Optional[Dict[Point, str]] = fc_csp.forward_checking(domains=csp.domains, single=single,
                                                                                     lcv=lcv, mcv=mcv)
                print("FC", fc_csp.steps)
                # results(solution_fc, fc_csp)
                bt_csp = copy.copy(csp)
                solution_bt: Optional[Dict[Point, str]] = bt_csp.backtracking_search(single=single, lcv=lcv,
                                                                     mcv=mcv)
                print("BT", bt_csp.steps)



