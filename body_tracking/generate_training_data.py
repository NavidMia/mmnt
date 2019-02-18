# Generates joint location text file from images
# In mmnt folder run python generate_training_data.py
# Set FLIP = TRUE if target_size=(432, 368) instead of target_size=(368, 432)
# If SORT = TRUE then images will be displayed and you will have to label them
# display_images prints the values on terminal and displays the image with human joints
from tf_pose import infer
from tf_pose import common
from tf_pose.common import CocoPart
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
import time
import numpy as np
import cv2
import os

display_images = True
start_time = time.time()
# Is standing
# data_types = ["sitting", "standing"]
# path = './body_tracking/training_images/'
# FLIP = False

# Is interesting
# data_types = ["interesting", "not_interesting"]
# path = "./training_images/is_interesting/"
# FLIP = True

# path = "./training_images/is_interesting/"
# data_types = ["a_sitting"]
# store_folder = "human_drawn/"
# FLIP = True
# SORT = True
# display_images = SORT
# variable_name = "standing (0) sitting(1) unknown (2), "

path = "./training_images/"
data_types = ["standing", "sitting", "bad"]
store_folder = "human_drawn/"
FLIP = True
SORT = False
display_images = False
variable_name = "standing (0) sitting(1) unknown (2), "

with open("joint_locations_is_standing_v4.txt", "w") as output_file:
    output_file.write("Data Number, "+  variable_name +
            "Nose x, Nose y, Nose score, " +
            "Neck x, Neck y, Neck score, " +
            "RShoulder x, RShoulder y, RShoulder score, " +
            "RElbow x, RElbow y, RElbow score, " +
            "RWrist x, RWrist y, RWrist score, " +
            "LShoulder x, LShoulder y, LShoulder score, " +
            "LElbow x, LElbow y, LElbow score, " +
            "LWrist x, LWrist y, LWrist score, " +
            "RHip x, RHip y, RHip score, " +
            "RKnee x, RKnee y, RKnee score, " +
            "RAnkle x, RAnkle y, RAnkle score, " +
            "LHip x, LHip y, LHip score, " +
            "LKnee x, LKnee y, LKnee score, " +
            "LAnkle x, LAnkle y, LAnkle score, " +
            "REye x, REye y, REye score, " +
            "LEye x, LEye y, LEye score, " +
            "REar x, REar y, REar score, " +
            "LEar x, LEar y, LEar score, " +
            "Background x, Background y, Background score\n")
    if FLIP:
        e = TfPoseEstimator(get_graph_path("mobilenet_thin"), target_size=(368, 432))
    else:
        e = TfPoseEstimator(get_graph_path("mobilenet_thin"), target_size=(432, 368))
    for is_variable, data_type in enumerate(data_types):
        files = os.listdir(path + data_type)
        files.sort()
        for image_name in files:
            t = time.time()
            split_image_name = image_name.split(".")
            if split_image_name[-1] != "jpg":
                continue
            index = int(image_name.split(".")[0])
            img = common.read_imgfile(path + data_type + "/" + image_name, None, None)
            humans = e.inference(img, resize_to_default=False, upsample_size=4.0)

            for id,human in enumerate(humans):
                if id > 0:
                    print("multiple humans in image: " + image_name)
                output_file.write(str(index) + ", " + str(is_variable))
                for value, body_part_name  in enumerate(CocoPart):
                    if display_images:
                        if value in human.body_parts:
                            body_part = human.body_parts[value]
                            print(str(value) + " " + body_part_name.name
                                  + "- x: " + str(body_part.x)
                                  + " y: " + str(body_part.x)
                                  + " score: " + str(body_part.score))
                        else:
                            print(str(value) + " " + body_part_name.name
                                  + "- x: -1 y: -1 score: 0")
                    else:
                        if value in human.body_parts:
                            body_part = human.body_parts[value]
                            output_file.write(", " + str(body_part.x)
                                            + ", " + str(body_part.y)
                                            + ", " + str(body_part.score))
                        else:
                            output_file.write(", -1, -1, 0")
                output_file.write("\n")
            print("done image: " + image_name
                + " in " + str(time.time() - t) + "s")
            if display_images and not SORT:
                img_joints = TfPoseEstimator.draw_humans(img, humans, imgcopy=False)
                cv2.imwrite(path + data_type + "/" + store_folder + image_name,
                            img_joints)
                # cv2.imshow('Joints',img_joints)
                # cv2.waitKey(0)
                # print("done window")
            if SORT:
                og_image = img.copy()
                img_joints = TfPoseEstimator.draw_humans(img, humans, imgcopy=False)
                cv2.imshow('Joints',img_joints)
                print("On image: l for sitting, i for standing, b for bad")
                key = chr(cv2.waitKey(0) & 255)
                print("Chose key: " + key)
                key_valid = False
                write_location = ""
                while(not key_valid):
                    print("Starting while loop")
                    if key == "i":
                        write_location = path + "standing/" + image_name
                        key_valid = True
                    elif key == "l":
                        write_location = path + "sitting/" + image_name
                        key_valid = True
                    elif key == "b":
                        write_location = path + "bad/" + image_name
                        key_valid = True
                    else:
                        print("INVALID INPUT: " + key)
                        print("On image: l for sitting, i for standing, b for bad")
                        key = chr(cv2.waitKey(0) & 255)

                print("Done while loop")
                cv2.imwrite(write_location, og_image)
                cv2.destroyAllWindows()
print("Total time: " + str(time.time() - start_time) + "s")
