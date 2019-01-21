# This file splits data into training and testing data set
import random

num_data = 100
num_testing = 0

first_half = list(range(1, int(num_data/2) + 1))
random.shuffle(first_half)
# training = first_half[:int(num_training/2)]
test = first_half[:int(num_testing/2)]

second_half = list(range(int(num_data/2) + 1, num_data + 1))
random.shuffle(second_half)
# training += second_half[:int(num_training/2)]
test += second_half[:int(num_testing/2)]

with open("v3/joint_locations_v3.txt", "r") as all_data, open(
         "v3/joint_locations_training.txt", "w") as training_file, open(
         "v3/joint_locations_testing.txt", "w") as testing_file:
    for i, line in enumerate(all_data):
        if i == 0:
            training_file.write(line)
            testing_file.write(line)
            continue
        index = int(line.split(",")[0])
        if index in test:
            testing_file.write(line)
        else:
            training_file.write(line)
