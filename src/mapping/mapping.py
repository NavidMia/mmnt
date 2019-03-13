import numpy as np
import math

import matplotlib.pyplot as plt

import cv2

class map:
    def __init__(self, degrees_per_cell_i):
        self.degrees_per_cell = degrees_per_cell_i
        self.grid = np.full((int(math.ceil(360.0/self.degrees_per_cell))), 0.5)

        self.p_noise_given_POI = 0.6
        self.p_noise_given_not_POI = 0.3

        self.p_no_noise_given_POI = 1 - self.p_noise_given_POI
        self.p_no_noise_given_not_POI = 1 - self.p_noise_given_not_POI

        self.min_percent = 0.1
    #Update map using log odds
    def get_cell_location(self, noise_location):
        cell_loc = int(math.floor(noise_location/self.degrees_per_cell))
        if cell_loc > self.grid.size:
            cell_loc = cell_loc%self.grid.size
        return(cell_loc)

    # Get noise location [0,360)
    def update_map_with_noise(self, noise_location):
        # Get noise cell
        noise_cell = self.get_cell_location(noise_location)
        self.grid[noise_cell] = max(self.logit_inv(
                            math.log(self.p_noise_given_POI
                                    /self.p_noise_given_not_POI)
                            + self.logit(self.grid[noise_cell])),
                            self.min_percent)
        no_noise_cells = [no_noise_cell
                            for no_noise_cell in range(self.grid.size)
                            if no_noise_cell not in [noise_cell]]

        for no_noise_cell in no_noise_cells:
            self.grid[no_noise_cell] = max(self.logit_inv(
                                math.log(self.p_no_noise_given_POI
                                        /self.p_no_noise_given_not_POI)
                                + self.logit(self.grid[no_noise_cell])),
                                self.min_percent)

    def update_map_with_no_noise(self):
        for no_noise_cell in range(self.grid.size):
            self.grid[no_noise_cell] = max(self.logit_inv(
                                math.log(self.p_no_noise_given_POI
                                        /self.p_no_noise_given_not_POI)
                                + self.logit(self.grid[no_noise_cell])),
                                self.min_percent)
    def update_map_with_person(self, person_location):
        pass

    def update_map_with_no_person(self, person_location):
        pass

    def logit(self, p):
        return(math.log(p) - math.log(1-p))
    def logit_inv(self, y):
        return (math.exp(y)/(math.exp(y) + 1))

    def print_map(self):
        print(self.grid)
    def draw_map(self):
        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        sizes = np.ones(self.grid.size)
        grey_col = [str(col) for col in 1 - self.grid]
        plt.close()
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, autopct=None, startangle=90, counterclock = False,
                colors = grey_col)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.draw()
        plt.pause(0.01)

if __name__ == "__main__":
    test_map = map(30)
    input_val = input("Enter degree of noise or n for no noise or p for print, x for exit: ")
    while input_val != 'x':
        if input_val == 'n':
            test_map.update_map_with_no_noise()
        elif input_val == 'p':
            test_map.print_map()
        else:
            try:
               val = int(input_val)
               test_map.update_map_with_noise(val)
            except ValueError:
               print("Invalid Input of:")
               print(input_val)
        test_map.draw_map()
        input_val = input("Enter degree of noise or n for no noise, x for exit: ")
