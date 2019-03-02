import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

model_name = "c1200_no_bad_v2"
base_folder = "c1200_no_bad/"
base_name = "joint_locations_is_standing_v5"
SAVE_MODEL = True
# import split_data
# split_data.split_data(base_folder + base_name, 0.2)

all_data = np.genfromtxt(base_folder + base_name + ".txt",
                              delimiter=',', skip_header=1)
num_data = np.shape(all_data)[0]
training_percent = 0.8
validation_percent = 0.1
testing_percent = 1-training_percent-validation_percent
np.random.seed(0)
np.random.shuffle(all_data)
training_data = all_data[:round(num_data*training_percent)]
validation_data = all_data[round(num_data*training_percent):
                         round(num_data*(training_percent+validation_percent))]
testing_data = all_data[round(num_data*(training_percent+validation_percent)):]

training_indexes = training_data[:,0]
training_labels = training_data[:,1]
training_features = training_data[:,2:]

testing_indexes = testing_data[:,0]
testing_labels = testing_data[:,1]
testing_features = testing_data[:,2:]

validation_indexes = validation_data[:,0]
validation_labels = validation_data[:,1]
validation_features = validation_data[:,2:]

reg_lamb = 0.01

model = tf.keras.Sequential([
  tf.keras.layers.Dense(30, activation="relu", input_shape=(19*3,),
                        kernel_regularizer=tf.keras.regularizers.l2(reg_lamb)),
  tf.keras.layers.Dense(10, activation="relu",
                        kernel_regularizer=tf.keras.regularizers.l2(reg_lamb)),
  tf.keras.layers.Dense(5, activation="relu",
                        kernel_regularizer=tf.keras.regularizers.l2(reg_lamb)),
  tf.keras.layers.Dense(2, activation=tf.nn.softmax,
                        kernel_regularizer=tf.keras.regularizers.l2(reg_lamb))
])

sgd = tf.keras.optimizers.SGD(lr=0.005)

model.compile(optimizer = sgd,
              loss ='sparse_categorical_crossentropy',
              metrics =['accuracy'])

history = model.fit(training_features, training_labels,
        epochs=1001, batch_size=64,
        validation_data=(validation_features, validation_labels))

# Plot training & validation accuracy svalues
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

if (testing_percent > 0):
    test_loss, test_acc = model.evaluate(testing_features, testing_labels)

    print('Test accuracy:', test_acc)
    print('Test loss:', test_loss)


# serialize model to JSON
if (SAVE_MODEL):
    model_json = model.to_json()
    with open(base_folder + model_name + ".json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(base_folder + model_name + ".h5")
    print("Saved model to disk")
