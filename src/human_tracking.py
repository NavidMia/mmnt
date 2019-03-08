import tensorflow as tf
from tensorflow.python.keras.models import model_from_json
from tf_pose.common import CocoPart

# Function loads neural network model
# path is the path to the two nural network file
# the two files are a json file and a h5 file
# the two files should have the same name which should be specified by name
path = "models/"
name = "model"

def get_model():
    json_file = open(path + name + ".json", 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    
    # load weights into new model
    loaded_model.load_weights(path + name + ".h5")
    print("Loaded model from disk")
    return loaded_model

# Given a model and a human, will return if it is standing
def is_standing(model, human):
    leg_parts = [CocoPart.RKnee.value,
                CocoPart.RAnkle.value,
                CocoPart.LKnee.value,
                CocoPart.LAnkle.value]
    # If no legs return sitting
    if not any(x in leg_parts for x in human.body_parts):
        return False
    body_parts_not_to_add = [CocoPart.Background.value,
                             CocoPart.RElbow.value,
                             CocoPart.RWrist.value,
                             CocoPart.LElbow.value,
                             CocoPart.LWrist.value]
    joint_data = []
    for value, body_part_name  in enumerate(CocoPart):
        if value in human.body_parts and value not in body_parts_not_to_add:
            body_part = human.body_parts[value]
            joint_data.append(body_part.x)
            joint_data.append(body_part.y)
            joint_data.append(body_part.score)
        elif value not in body_parts_not_to_add:
            joint_data.append(-1)
            joint_data.append(-1)
            joint_data.append(0)
    features = tf.reshape(joint_data, shape=(1, 14*3))
    prediction = model.predict(features, steps=1)[0]
    return (prediction[0] > prediction[1])

def is_hands_above_head(human):
    arm_parts = [CocoPart.RElbow.value,
                 CocoPart.LElbow.value,
                 CocoPart.RWrist.value,
                 CocoPart.LWrist.value]
    vissible_arm_parts = [joint for joint in arm_parts if joint in human.body_parts]
    if vissible_arm_parts == []:
        return False
    head_parts = [CocoPart.Nose.value,
                 CocoPart.Neck.value,
                 CocoPart.REye.value,
                 CocoPart.LEye.value,
                 CocoPart.REar.value,
                 CocoPart.LEar.value]
    vissible_head_parts = [head_part for head_part in head_parts if head_part in human.body_parts]
    if vissible_head_parts == []:
        return False
    head_y_vals = [human.body_parts[part].y for part in vissible_head_parts]
    arm_y_vals = [human.body_parts[part].y for part in vissible_arm_parts]
    # Y values are percent from top of the sceen (0,0) is top left, (1,1) is bottom right
    return min(arm_y_vals) < min(head_y_vals)
