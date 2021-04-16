import cProfile
import copy
import pstats
import time

from Grid import Grid, Point
from csp import Constraint, CSP
from typing import Dict, List, Optional
import pprint


def count_time(fun):
    start_time = time.time()
    result = fun
    finish_time = time.time()
    print("Time:", finish_time - start_time)
    return result


def results(solution, problem, grid, show_grid=False):
    if solution is None or len(solution) == 0:
        print("No solution!")
    else:
        print("Steps", problem.steps)
        pprint.pprint(len(solution))
        # pprint.pprint(solution)
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
    grid = Grid(40, 40)
    grid.random_points(3)  # n
    grid.generate_connections()
    variables: List[Point] = grid.points
    domains: Dict[Point, List[str]] = {}
    for variable in variables:
        domains[variable] = ["red", "green", "blue"]
    csp: CSP[Point, str] = CSP(variables, domains)
    for connection in grid.connections:
        csp.add_constraint(GridColoringConstraint(connection[0], connection[1]))

    for lcv in [False, True]:
        for mcv in [False, True]:
            for single in [True, False]:
                if mcv:
                    print("MCV", end=" ")
                if lcv:
                    print("LCV", end=" ")


                print("SINGLE" if single else "ALL")

                # bt_csp = copy.copy(csp)
                #
                # start_time = time.time()
                # solution_bt: Optional[Dict[Point, str]] = bt_csp.backtracking_search(single=single, lcv=lcv,
                #                                                                      mcv=mcv)
                #
                # print("Time:", (time.time() - start_time)*1000)
                # print("BT", bt_csp.steps, "Solutions:", len(solution_bt))
                # # results(solution_bt, bt_csp, grid,True)
                # fc_csp = copy.copy(csp)
                #
                # start_time = time.time()
                # solution_fc: Optional[Dict[Point, str]] = fc_csp.forward_checking(domains=csp.domains, single=single,
                #                                                                   lcv=lcv, mcv=mcv)
                # print("Time:", (time.time() - start_time)*1000)
                # print("FC", fc_csp.steps, "Solutions:", len(solution_fc))
                # # results(solution_fc, fc_csp)

                mac_csp = copy.copy(csp)

                start_time = time.time()
                solution_mac: Optional[Dict[Point, str]] = mac_csp.maintain_arc_consistency(domains=csp.domains,
                                                                                            single=single, lcv=lcv,
                                                                                            mcv=mcv)
                print("Time:", (time.time() - start_time)*1000)
                print("MAC:", mac_csp.steps, "Solutions:", len(solution_mac))
                # results(solution_mac, mac_csp)
