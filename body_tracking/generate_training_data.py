from tf_pose import infer
from tf_pose import common
from tf_pose.common import CocoPart
from tf_pose.estimator import TfPoseEstimator
import numpy as np
import cv2
import os

# TODO: Make run faster. Took 12 hours to 'finish'. Should only take 2 min

display_images = False
with open("joint_locations.txt", "w") as output_file:
    output_file.write("Data Number, is_standing, " +
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
    data_types = ["sitting", "standing"]
    path = './body_tracking/training_images/'
    index = 0
    for data_type in data_types:
        is_standing = 1*(data_type == "standing")
        files = os.listdir(path + data_type)
        for image_name in files:
            img = common.read_imgfile(path + data_type + "/" + image_name,
                                    None, None)
            humans = infer(image=path + data_type + "/" + image_name,
                            model="mobilenet_thin")
            for id,human in enumerate(humans):
                output_file.write(str(index) + ", " + str(is_standing) +", ")
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
                            output_file.write(str(body_part.x) + ", "
                                            + str(body_part.y) + ", "
                                            + str(body_part.score) +", ")
                        else:
                            output_file.write("-1, -1, 0, ")
                output_file.write("\n")
                print("done index: " + str(index))
                index += 1
            if display_images:
                img_joints = TfPoseEstimator.draw_humans(img, humans, imgcopy=False)
                cv2.imshow('Joints',img_joints)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
