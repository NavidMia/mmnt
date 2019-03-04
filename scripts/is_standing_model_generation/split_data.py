# This file splits data into training and testing data set
import random

def split_data(base_name, percent_test):
    if base_name[-4:] == ".txt":
        base_name = base_name[:-4]
    if percent_test > 1:
        percent_test = 1
    elif percent_test < 0:
        percent_test = 0

    num_data = sum(1 for line in open(base_name +".txt")) - 1
    num_testing = int(round(num_data*percent_test))

    shuffle_index = list(range(1, num_data))
    random.shuffle(shuffle_index)
    test_idx = shuffle_index[:num_testing]
    with open(base_name +".txt", "r") as all_data, open(
             base_name + "_training.txt", "w") as training_file, open(
             base_name + "_testing.txt", "w") as testing_file:
        for i, line in enumerate(all_data):
            if i == 0:
                training_file.write(line)
                testing_file.write(line)
                continue
            index = int(line.split(",")[0])
            if index in test_idx:
                testing_file.write(line)
            else:
                training_file.write(line)
