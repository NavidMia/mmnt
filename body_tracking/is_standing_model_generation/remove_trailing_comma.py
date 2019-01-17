file_name = "joint_training"
with open(file_name + ".txt", "r") as input:
    with open(file_name + "_comma_removed.txt", "w") as output:
        for line in input:
            if len(line) > 2:
                if line[-1] == ",":
                    output.write(line[:-1] + "\n")
                elif line[-2] == ",":
                    output.write(line[:-2] + "\n")
                elif line[-3] == ",":
                    output.write(line[:-3] + "\n")
                else:
                    print(line)
                    output.write(line)
            else:
                print(line)
                output.write(line)
