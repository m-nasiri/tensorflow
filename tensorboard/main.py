#-----------------------------------------------------------------------------#
#coder: Majid Nasiri
#github: https://github.com/m-nasiri/tensorflow/tensorboard
#date: 2017-December-11
#-----------------------------------------------------------------------------#

"""
    This code is for learning how to visualizing input images/weights/biases/
    activations/loss and accuracy of model while training a model using 
    tensorboard.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# load mnist dataset
mnist = input_data.read_data_sets("./data/", one_hot=True)

# path to save checkpoints
checkpoint_path = "./model/model.ckpt"
log_dir = './log/model/'

# define convolutional neural network
def mnist_model():
    
    tf.reset_default_graph()
    
    # Network Parameters
    nF1 = 32        # number of filters in first convolutional layer
    nF2 = 64        # number of filters in second convolutional layer
    nFc1 = 120      # number of neurans in first fully connected layer
    n_classes = 10  # number of classes 0-9

    # define placeholder for input images and labels
    X = tf.placeholder(tf.float32, shape=[None, 784], name="X")
    x = tf.reshape(X, [-1, 28, 28, 1])
    tf.summary.image('input', x, 3)
    Y = tf.placeholder(tf.float32, shape=[None, 10], name="Y")
    keep_prob = tf.placeholder(tf.float32, name='keep_prob')

    # Convolution Layer 1
    with tf.name_scope('conv1') as scope:
        weights = tf.Variable(tf.truncated_normal([3, 3, 1, nF1], mean=0.0, stddev=0.1), name="weights")
        biases = tf.Variable(tf.constant(0.1, shape=[nF1]), name='biases')
        conv = tf.nn.conv2d(x, weights, strides=[1, 1, 1, 1], padding='SAME')
        relu = tf.nn.relu(conv + biases , name=scope)
        pool = tf.nn.max_pool(relu, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
        tf.summary.histogram("weights", weights)
        tf.summary.histogram("biases", biases)
        tf.summary.histogram("activations", relu)
        
    # Convolution Layer 2
    with tf.name_scope('conv2') as scope:
        weights = tf.Variable(tf.truncated_normal([3, 3, nF1, nF2], mean=0.0, stddev=0.1), name='weights')
        biases = tf.Variable(tf.constant(0.1, shape=[nF2]), name='biases')
        conv = tf.nn.conv2d(pool, weights, strides=[1, 1, 1, 1], padding='SAME')
        relu = tf.nn.relu(conv + biases, name=scope)
        pool = tf.nn.max_pool(relu, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
        tf.summary.histogram("weights", weights)
        tf.summary.histogram("biases", biases)
        tf.summary.histogram("activations", relu)

    # Fully Connected Layer 1
    with tf.name_scope('fc1') as scope:
        weights = tf.Variable(tf.truncated_normal([(7 * 7 * nF2), nFc1], mean=0.0, stddev=0.1), name='weights')
        biases = tf.Variable(tf.constant(0.1, shape=[nFc1]), name='biases')
        pool_flat = tf.reshape(pool, shape=[-1, (7 * 7 * nF2)])
        fc = tf.matmul(pool_flat, weights)
        fc = tf.nn.relu(fc + biases, name=scope)
        tf.summary.histogram("weights", weights)
        tf.summary.histogram("biases", biases)
        tf.summary.histogram("activations", fc)
        fc = tf.nn.dropout(fc, keep_prob= keep_prob)

    
    # Fully Connected Layer 2
    with tf.name_scope('fc2') as scope:
        weights = tf.Variable(tf.truncated_normal([nFc1, n_classes], mean=0.0, stddev=0.1), name='weights')
        biases = tf.Variable(tf.constant(0.1, shape=[n_classes]), name='biases')
        fc = tf.nn.bias_add(tf.matmul(fc, weights), biases)
        logits = tf.nn.softmax(fc, name=scope)
        tf.summary.histogram("weights", weights)
        tf.summary.histogram("biases", biases)
        tf.summary.histogram("activations", fc)


    with tf.name_scope("loss"):
        # this needs to be minimised by adjusting weights and biases
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y), name='loss')
        tf.summary.scalar("loss", loss)
        
    with tf.name_scope("train"):
        # define training step which minimises cross entropy
        optimizer = tf.train.AdamOptimizer(learning_rate = 0.001).minimize(loss)

    with tf.name_scope("accuracy"):
        # argmax gives index of highest entry in vector
        correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(Y, 1), name='correct_prediction')
        
        # get mean of all entries in correct prediction, the higher the better
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name='accuracy')
        tf.summary.scalar("accuracy", accuracy)
        
    merged_summary = tf.summary.merge_all()
    print('The network graph created')
    
    
    # Training Parameters
    n_epoch = 5
    batch_size = 128
    display_step = 10
    
    # Create a session for running operations in the Graph.
    with tf.Session() as sess:
        
        # save all of ckeckpoints (a checkpoint per epoch)
        saver = tf.train.Saver(max_to_keep=4)
    
        # Initialize the variables
        sess.run(tf.global_variables_initializer())
    
        # 
        writer = tf.summary.FileWriter(log_dir)
        writer.add_graph(sess.graph)
    
        log_cnt = 0
        # Train for n_epochs
        for epoch in range(n_epoch):
            
            for itr in range(mnist.train.num_examples//batch_size):
                
                # fetch a batch of train images and labels
                batch_x, batch_y = mnist.train.next_batch(batch_size)
                
                # Run the training step
                feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.6}
                sess.run(optimizer, feed_dict=feed_dict)
                
                if (itr % display_step == 0):
                    log_cnt = log_cnt + 1
                    # Evaluate model on training batch
                    feed_dict={X: batch_x, Y: batch_y, keep_prob: 1.0}
                    loss_val, acc_val, summary = sess.run([loss, accuracy, merged_summary],
                                                          feed_dict=feed_dict)
                    writer.add_summary(summary, log_cnt)
                    
                    print('Epoch', epoch, 'Minibatch loss', loss_val,
                          'Batch Accuracy:', acc_val)
                    
            # save all variables for each epoch
            saver.save(sess, checkpoint_path, global_step=epoch)
        
        # fetch whole test images and labels
        feed_dict={X: mnist.test.images, Y: mnist.test.labels, keep_prob: 1.0}
        
        # feed the model with all test images and labels
        acc_val = sess.run(accuracy, feed_dict=feed_dict)
        print('Test Accuracy:', acc_val)



if __name__ == '__main__':
    
    # run the model to train
    mnist_model()


