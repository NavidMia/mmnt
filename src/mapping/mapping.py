import numpy as np
import math

class map:
    def __init__(self):
        self.degrees_per_cell = 90
        self.grid = np.full((int(math.ceil(360.0/self.degrees_per_cell))), 0.5)

        self.p_noise_given_POI = 0.55
        self.p_noise_given_not_POI = 0.45

        self.p_no_noise_given_POI = 0.45
        self.p_no_noise_given_not_POI = 0.55
    #Update map using log odds
    def get_cell_location(self, noise_location):
        return(int(math.floor(noise_location/self.degrees_per_cell)))
    # Get noise location [0,360)
    def update_map_with_noise(self, noise_location):
        # Get noise cell
        noise_cell = self.get_cell_location(noise_location)
        self.grid[noise_cell] = self.logit_inv(
                            math.log(self.p_noise_given_POI
                                    /self.p_noise_given_not_POI)
                            + self.logit(self.grid[noise_cell]))
        no_noise_cells = [no_noise_cell
                            for no_noise_cell in range(self.grid.size)
                            if no_noise_cell not in [noise_cell]]

        for no_noise_cell in no_noise_cells:
            self.grid[no_noise_cell] = self.logit_inv(
                                math.log(self.p_no_noise_given_POI
                                        /self.p_no_noise_given_not_POI)
                                + self.logit(self.grid[no_noise_cell]))

    def update_map_with_no_noise(self):
        for no_noise_cell in range(self.grid.size):
            self.grid[no_noise_cell] = self.logit_inv(
                                math.log(self.p_no_noise_given_POI
                                        /self.p_no_noise_given_not_POI)
                                + self.logit(self.grid[no_noise_cell]))
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

if __name__ == "__main__":
    test_map = map()
    test_map.print_map()
    print("Noise at 45")
    test_map.update_map_with_noise(45)
    test_map.print_map()
    print("Noise at 45")
    test_map.update_map_with_noise(45)
    test_map.print_map()
    print("Noise at 95")
    test_map.update_map_with_noise(95)
    test_map.print_map()
    print("Noise at 95")
    test_map.update_map_with_noise(95)
    test_map.print_map()
    print("No noise")
    test_map.update_map_with_no_noise()
    test_map.print_map()
