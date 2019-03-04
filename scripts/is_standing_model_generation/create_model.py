import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

model_name = "c1200_no_bad_v2"
base_folder = "c1200_no_bad/"
base_name = "joint_locations_is_standing_v5"

all_data = np.genfromtxt(base_folder + base_name + ".txt",
                              delimiter=',', skip_header=1)
num_data = np.shape(all_data)[0]
training_percent = 0.8
validation_percent = 0.1
testing_percent = 1-training_percent-validation_percent

all_data = all_data[:,:-3] # Get rid of Background
all_data = np.hstack((all_data[:,:19], all_data[:,25:])) # No LElbow or LWrist
all_data = np.hstack((all_data[:,:10], all_data[:,16:])) # No RElbow or RWrist

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
  tf.keras.layers.Dense(25, activation="relu", input_shape=(14*3,),
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

es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', mode='min',
                    verbose=1, patience=100)
mc = tf.keras.callbacks.ModelCheckpoint('best_model.h5',
                    monitor='val_acc',
                    mode='max', verbose=0,
                    save_best_only=True)
history = model.fit(training_features, training_labels,
        epochs=4001,
        batch_size=32,
        verbose=1,
        validation_data=(validation_features, validation_labels),
        class_weight={0:0.5, 1:1},
        callbacks=[es, mc])
saved_model = tf.keras.models.load_model('best_model.h5')

# Plot training & validation accuracy svalues
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

if (testing_percent > 0):
    test_loss, test_acc = saved_model.evaluate(testing_features, testing_labels)
    print('Test accuracy:', test_acc)
    print('Test loss:', test_loss)
    predictions = np.argmax(saved_model.predict(testing_features), axis=1)
    p_standing_actual_standing = 0
    p_sitting_actual_sitting = 0
    p_standing_actual_sitting = 0
    p_sitting_actual_standing = 0
    total = len(testing_features)
    for i in range(total):
        if predictions[i] == 0 and int(testing_labels[i]) == 0:
            p_standing_actual_standing += 1
        elif predictions[i] == 1 and int(testing_labels[i]) == 1:
            p_sitting_actual_sitting += 1
        elif predictions[i] == 0 and int(testing_labels[i]) == 1:
            p_standing_actual_sitting += 1
        elif predictions[i] == 1 and int(testing_labels[i]) == 0:
            p_sitting_actual_standing += 1
        else:
            print("ERROR CONDITION: " + str(i))
    tot_sitting = p_standing_actual_sitting + p_sitting_actual_sitting
    tot_standing = p_standing_actual_standing + p_sitting_actual_standing
    print("Predicted, actual  , num,\t r-tot,\t r-act")
    print("standing , standing, %d, \t %0.3f,\t %0.3f"
            % (p_standing_actual_standing,
               p_standing_actual_standing/total,
               p_standing_actual_standing/tot_standing))
    print("sitting  , sitting , %d, \t %0.3f,\t %0.3f"
            % (p_sitting_actual_sitting,
               p_sitting_actual_sitting/total,
               p_sitting_actual_sitting/tot_sitting))
    print("standing , sitting , %d, \t %0.3f,\t %0.3f"
            % (p_standing_actual_sitting,
               p_standing_actual_sitting/total,
               p_standing_actual_sitting/tot_sitting))
    print("sitting  , standing, %d, \t %0.3f,\t %0.3f"
            % (p_sitting_actual_standing,
               p_sitting_actual_standing/total,
               p_sitting_actual_standing/tot_standing))

if (input('Press k to save model or anykey otherwise:') == "k"):
    print("Saving model")
    SAVE_MODEL = True
else:
    print("Discarding model")
    SAVE_MODEL = False
# serialize model to JSON
if (SAVE_MODEL):
    model_json = saved_model.to_json()
    with open(base_folder + model_name + ".json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    saved_model.save_weights(base_folder + model_name + ".h5")
    print("Saved model to disk")
