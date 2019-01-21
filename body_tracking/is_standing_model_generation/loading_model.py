import os
import tensorflow as tf
from is_standing import parse_csv
import tensorflow.contrib.eager as tfe

tf.enable_eager_execution()

json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = tf.keras.models.model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model.h5")
print("Loaded model from disk")

base_folder = "v3/"
test_dataset = tf.data.TextLineDataset(base_folder +
                            "joint_locations_testing.txt")
test_dataset = test_dataset.skip(1)             # skip header row
test_dataset = test_dataset.map(parse_csv)      # parse each row with the funcition created earlier
# test_dataset = test_dataset.shuffle(1000)       # randomize
test_dataset = test_dataset.batch(32)           # use the same batch size as the training set
test_accuracy = tfe.metrics.Accuracy()

print("tests")
for (x, y, z) in test_dataset:
  prediction = tf.argmax(loaded_model(x), axis=1, output_type=tf.int32)
  print(x)
  print(prediction)
  print(y)
  print(z)
  test_accuracy(prediction, y)

print("Test set accuracy: {:.3%}".format(test_accuracy.result()))
