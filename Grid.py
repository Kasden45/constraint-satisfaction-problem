import math
import numpy as np
from shapely.geometry import LineString
from typing import List, Dict
from matplotlib import collections  as mc, ticker
import pylab as plt
import random


def count_distance(p1, p2):
    return math.dist([p1.x, p1.y], [p2.x, p2.y])

def flatten(l_of_ls):
    #print(l_of_ls)
    result = []
    for l in l_of_ls:
        result.extend(l)

    return result


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def coords(self):
        return self.x, self.y

    def __str__(self):
        return "({},{})".format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)


class Grid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points: List[Point] = []
        self.connections: (Point, Point) = []  # (p1, p2)

    def random_points(self, n):
        for i in range(n):
            while True:
                x = random.randint(0,self.x)
                y = random.randint(0, self.y)
                new_point = Point(x, y)
                if new_point not in self.points:
                    self.points.append(new_point)
                    break


    def generate_connections(self):
        distances: Dict[Point, List[(Point, float)]] = {}
        for point in self.points:
            distances[point] = []
            for other_point in self.points:
                if other_point != point:
                    distances[point].append((other_point, count_distance(point, other_point)))
            distances[point].sort(key=lambda p: p[1], reverse=False)

        while len(flatten([self.possible_connections(point) for point in self.points])) != 0:
            point = random.choice(list(distances.keys()))
            options = self.possible_connections(point)
            if len(options) == 0:
                continue
            for dest in distances[point]:
                if dest[0] in options:
                    self.connections.append((point, dest[0]))
                    break

        for connection in self.connections:
            print(connection[0], connection[1])

    def possible_connections(self, checked_point):
        possible = []
        for p in [point for point in self.points if point != checked_point]:
            if not self.check_intersect((p, checked_point)):

                exists = False
                for connection in self.connections:
                    if (connection[0].coords() == checked_point.coords() and connection[1].coords() == p.coords()) or (connection[0].coords() == p.coords() and connection[1].coords() == checked_point.coords()):
                        exists = True
                        break
                if not exists:
                    possible.append(p)
        return possible

    def check_intersect(self, new_line):  # (p1, p2)
        for connection in self.connections:
            if connection[0] not in [new_line[0], new_line[1]] and connection[1] not in [new_line[0], new_line[1]]:
                line = LineString([connection[0].coords(), connection[1].coords()])
                other = LineString([new_line[0].coords(), new_line[1].coords()])
                if line.intersects(other):
                    return True
        return False

    def draw_grid(self, colors: Dict[Point, str] = None):
        if colors is None:
            colors = {}

        fig, ax = plt.subplots()
        circles = []
        plt.grid()

        lines = []
        for connection in self.connections:
            lines.append([connection[0].coords(), connection[1].coords()])
        lc = mc.LineCollection(lines, colors=["blue"], linewidths=1)
        for point, color in colors.items():
            circles.append(plt.Circle(point.coords(), 0.3, color=color, fill=True))
        ax.add_collection(lc)

        for circle in circles:
            ax.add_patch(circle)
        ax.invert_yaxis()
        c = np.array(["black"])

        ax.margins(0.1)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

        plt.ylim([-1, self.y+1])
        plt.xlim([-1, self.x+1])
        plt.draw()
        plt.waitforbuttonpress(0)
