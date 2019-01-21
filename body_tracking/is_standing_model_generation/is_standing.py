from __future__ import absolute_import, division, print_function

import os
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow.contrib.eager as tfe

def parse_csv(line):
  example_defaults = [[0.0]]*19*3  # 18 joints + background (x, y and score)
  example_defaults.insert(0, [0]) # is standing
  example_defaults.insert(0, [0]) # index number
  parsed_line = tf.decode_csv(line, example_defaults)

  # Last 19*3 fields are features, excempt the last
  features = tf.reshape(parsed_line[2:], shape=(19*3,))
  # Last field is the label
  label = tf.reshape(parsed_line[1], shape=())
  # First feild is index
  index = tf.reshape(parsed_line[0], shape=())
  return features, label, index

if __name__ == "__main__":
    tf.enable_eager_execution()

    base_folder = "v3/"
    print("TensorFlow version: {}".format(tf.VERSION))
    print("Eager execution: {}".format(tf.executing_eagerly()))



    print("setting up train_dataset")
    train_dataset = tf.data.TextLineDataset(base_folder
                                        + "joint_locations_training.txt")
    train_dataset = train_dataset.skip(1)             # skip the first header row
    train_dataset = train_dataset.map(parse_csv)      # parse each row
    # train_dataset = train_dataset.shuffle(buffer_size=1000)  # randomize
    train_dataset = train_dataset.batch(32)

    print("view single example")
    # View a single example entry from a batch
    features, label, index = iter(train_dataset).next()
    print("example features:", features[0])
    print("example label:", label[0])
    print("example index:", index[0])

    model = tf.keras.Sequential([
      tf.keras.layers.Dense(100, activation="relu", input_shape=(19*3,)),  # input shape required
      tf.keras.layers.Dense(50, activation="relu"),
      tf.keras.layers.Dense(2)
    ])

    def loss(model, x, y):
      y_ = model(x)
      return tf.losses.sparse_softmax_cross_entropy(labels=y, logits=y_)


    def grad(model, inputs, targets):
      with tf.GradientTape() as tape:
        loss_value = loss(model, inputs, targets)
      return tape.gradient(loss_value, model.variables)


    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01)


    ## Note: Rerunning this cell uses the same model variables

    # keep results for plotting
    train_loss_results = []
    train_accuracy_results = []

    num_epochs = 201

    for epoch in range(num_epochs):
      epoch_loss_avg = tfe.metrics.Mean()
      epoch_accuracy = tfe.metrics.Accuracy()

      # Training loop - using batches of 32
      for x, y, z in train_dataset:
        # Optimize the model
        grads = grad(model, x, y)
        optimizer.apply_gradients(zip(grads, model.variables),
                                  global_step=tf.train.get_or_create_global_step())

        # Track progress
        epoch_loss_avg(loss(model, x, y))  # add current batch loss
        # compare predicted label to actual label
        epoch_accuracy(tf.argmax(model(x), axis=1, output_type=tf.int32), y)

      # end epoch
      train_loss_results.append(epoch_loss_avg.result())
      train_accuracy_results.append(epoch_accuracy.result())

      if epoch % 50 == 0:
        print("Epoch {:03d}: Loss: {:.3f}, Accuracy: {:.3%}".format(epoch,
                                                                    epoch_loss_avg.result(),
                                                                    epoch_accuracy.result()))


    fig, axes = plt.subplots(2, sharex=True, figsize=(12, 8))
    fig.suptitle('Training Metrics')

    axes[0].set_ylabel("Loss", fontsize=14)
    axes[0].plot(train_loss_results)

    axes[1].set_ylabel("Accuracy", fontsize=14)
    axes[1].set_xlabel("Epoch", fontsize=14)
    axes[1].plot(train_accuracy_results)

    plt.show()

    test_dataset = tf.data.TextLineDataset(base_folder +
                                "joint_locations_testing.txt")
    test_dataset = test_dataset.skip(1)             # skip header row
    test_dataset = test_dataset.map(parse_csv)      # parse each row with the funcition created earlier
    # test_dataset = test_dataset.shuffle(1000)       # randomize
    test_dataset = test_dataset.batch(32)           # use the same batch size as the training set
    test_accuracy = tfe.metrics.Accuracy()

    print("tests")
    for (x, y, z) in test_dataset:
      prediction = tf.argmax(model(x), axis=1, output_type=tf.int32)
      print(prediction)
      print(y)
      print(z)
      test_accuracy(prediction, y)

    print("Test set accuracy: {:.3%}".format(test_accuracy.result()))

    # serialize model to JSON
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("model.h5")
    print("Saved model to disk")
