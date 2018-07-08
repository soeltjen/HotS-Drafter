from __future__ import print_function
import tensorflow as tf
import dataset
import data_load
import matplotlib.pyplot as plt
import numpy as np

# Parameters
base_learning_rate = 0.00005
training_iters = 50000000
batch_size = 1000
display_step = 100
dropout = 0.7

# Network Parameters
n_input = 100 * 2 # Number of possible heroes * number of teams
n_classes = 2 #Team 1 or team 2 win

#Load HotsLogs data
train_matchups, train_results, train_maps, test_matchups, test_results, test_maps = data_load.get_data_winrate_estimator(mmrFilterOff = False, averageMMR = 2500)

#Verify data shape
print( train_matchups.shape )
print( train_results.shape )
print( train_maps.shape )

print( test_matchups.shape )
print( test_results.shape )
print( test_maps.shape )

#Make sure the shapes fit the neural network
X = train_matchups.reshape( -1, 2, 100 )
Y = train_results
maps = train_maps.reshape( -1, 2, 20 )

test_x = test_matchups.reshape( -1, 2, 100 )
test_y = test_results
test_maps = test_maps.reshape( -1, 2, 20 )

#Create datasets
trainSet = dataset.DataSet( X, maps, Y )
testSet = dataset.DataSet( test_x, test_maps, test_y )

print('Dataset created')

# tf Graph input
# Created 20 maps and 100 heroes to avoid having to change the model when a new map or hero is introduced
x = tf.placeholder(tf.float32, [None, 2, 100], name = "x")
m = tf.placeholder(tf.float32, [None, 2, 20], name = "m")
y = tf.placeholder(tf.float32, [None, n_classes])
keep_prob = tf.placeholder(tf.float32)

# Create model
# Heroes from both teams share the same set of weights for the first layers.
# Maps are added as a secondary input that is added to the first layer
# Siamese architecture: feature extraction to characterize the teams on the 4 first layers, followed by classification
def conv_net_siamese(x, maps, weights, biases, dropout):
    with tf.device('/gpu:0'):
        teams = tf.reshape(x, [-1, weights['heroes_w'].get_shape().as_list()[0]])
        teams = tf.matmul(teams, tf.abs(weights['heroes_w']))
        maps = tf.reshape(maps, [-1, weights['maps_w'].get_shape().as_list()[0]])
        teams = tf.multiply(teams, tf.matmul(maps, tf.abs(weights['maps_w'])))
        fc1 = tf.add( teams, biases['b1'] )
        fc1 = tf.nn.relu(fc1)
        fc1 = tf.nn.dropout(fc1, dropout)
        
        fs2 = tf.add(tf.matmul(fc1, weights['heroes_w2']), biases['bw2'])
        fs2 = tf.nn.relu(fs2)
        fs2 = tf.nn.dropout(fs2, dropout)
        
        fs3 = tf.add(tf.matmul(fs2, weights['heroes_w3']), biases['bw3'])
        fs3 = tf.nn.relu(fs3)
        fs3 = tf.nn.dropout(fs3, dropout)
        
        fs4 = tf.add(tf.matmul(fs3, weights['heroes_w4']), biases['bw4'])
        fs4 = tf.nn.relu(fs4)
        fs4 = tf.nn.dropout(fs4, dropout)
    
        fc2 = tf.reshape(fs4, [-1, 256])
        fc2 = tf.add(tf.matmul(fc2, weights['w2']), biases['b2'])
        fc2 = tf.nn.relu(fc2)
        fc2 = tf.nn.dropout(fc2, dropout)
    
        fc3 = fc2
        fc3 = tf.add(tf.matmul(fc3, weights['w3']), biases['b3'])
        fc3 = tf.nn.relu(fc3)
        fc3 = tf.nn.dropout(fc3, dropout)
    
        fc4 = fc3
        fc4 = tf.add(tf.matmul(fc4, weights['w4']), biases['b4'])
        fc4 = tf.nn.relu(fc4)
        fc4 = tf.nn.dropout(fc4, dropout)
        
        fc5 = fc4
        fc5 = tf.add(tf.matmul(fc5, weights['w5']), biases['b5'])
        fc5 = tf.nn.relu(fc5)
        fc5 = tf.nn.dropout(fc5, dropout)
    
        fc6 = fc5
        fc6 = tf.add(tf.matmul(fc6, weights['w6']), biases['b6'])
        fc6 = tf.nn.relu(fc6)
        fc6 = tf.nn.dropout(fc6, dropout)
    
        fc7 = fc6
        fc7 = tf.add(tf.matmul(fc7, weights['w7']), biases['b7'])
        fc7 = tf.nn.relu(fc7)
        fc7 = tf.nn.dropout(fc7, dropout)
        
        fc8 = fc7
        fc8 = tf.add(tf.matmul(fc8, weights['w8']), biases['b8'])
        fc8 = tf.nn.relu(fc8)
        fc8 = tf.nn.dropout(fc8, dropout)
    
        fc9 = fc8
        fc9 = tf.add(tf.matmul(fc9, weights['w9']), biases['b9'])
        fc9 = tf.nn.relu(fc9)
        fc9 = tf.nn.dropout(fc9, dropout)
    
        fc10 = fc9
        fc10 = tf.add(tf.matmul(fc10, weights['w10']), biases['b10'])
        fc10 = tf.nn.relu(fc10)
        fc10 = tf.nn.dropout(fc10, dropout)
        
        out = tf.add(tf.matmul(fc10, weights['out']), biases['out'])
    return out

# Store layers weight & bias
weights = {
    'heroes_w': tf.get_variable( 'hw1', shape=[100, 1024], initializer=tf.contrib.layers.xavier_initializer()),
    'heroes_w2': tf.get_variable( 'hw2', shape=[1024, 512], initializer=tf.contrib.layers.xavier_initializer()),
    'heroes_w3': tf.get_variable( 'hw3', shape=[512, 256], initializer=tf.contrib.layers.xavier_initializer()),
    'heroes_w4': tf.get_variable( 'hw4', shape=[256, 128], initializer=tf.contrib.layers.xavier_initializer()),
    'maps_w': tf.get_variable( 'mw1', shape=[20, 1024], initializer=tf.contrib.layers.xavier_initializer()),
    'w2': tf.get_variable( 'w2', shape=[256, 256], initializer=tf.contrib.layers.xavier_initializer()),
    'w3': tf.get_variable( 'w3', shape=[256, 256], initializer=tf.contrib.layers.xavier_initializer()),
    'w4': tf.get_variable( 'w4', shape=[256, 256], initializer=tf.contrib.layers.xavier_initializer()),
    'w5': tf.get_variable( 'w5', shape=[256, 256], initializer=tf.contrib.layers.xavier_initializer()),
    'w6': tf.get_variable( 'w6', shape=[256, 256], initializer=tf.contrib.layers.xavier_initializer()),
    'w7': tf.get_variable( 'w7', shape=[256, 128], initializer=tf.contrib.layers.xavier_initializer()),
    'w8': tf.get_variable( 'w8', shape=[128, 128], initializer=tf.contrib.layers.xavier_initializer()),
    'w9': tf.get_variable( 'w9', shape=[128, 64], initializer=tf.contrib.layers.xavier_initializer()),
    'w10': tf.get_variable( 'w10', shape=[64, 64], initializer=tf.contrib.layers.xavier_initializer()),
    'out': tf.get_variable( 'wout', shape=[64, n_classes], initializer=tf.contrib.layers.xavier_initializer()),
}

biases = {
    'b1': tf.get_variable( 'b1', shape=[1024], initializer=tf.zeros_initializer()),
    'bw2': tf.get_variable( 'bw2', shape=[512], initializer=tf.zeros_initializer()),
    'bw3': tf.get_variable( 'bw3', shape=[256], initializer=tf.zeros_initializer()),
    'bw4': tf.get_variable( 'bw4', shape=[128], initializer=tf.zeros_initializer()),
    'b2': tf.get_variable( 'b2', shape=[256], initializer=tf.zeros_initializer()),
    'b3': tf.get_variable( 'b3', shape=[256], initializer=tf.zeros_initializer()),
    'b4': tf.get_variable( 'b4', shape=[256], initializer=tf.zeros_initializer()),
    'b5': tf.get_variable( 'b5', shape=[256], initializer=tf.zeros_initializer()),
    'b6': tf.get_variable( 'b6', shape=[256], initializer=tf.zeros_initializer()),
    'b7': tf.get_variable( 'b7', shape=[128], initializer=tf.zeros_initializer()),
    'b8': tf.get_variable( 'b8', shape=[128], initializer=tf.zeros_initializer()),
    'b9': tf.get_variable( 'b9', shape=[64], initializer=tf.zeros_initializer()),
    'b10': tf.get_variable( 'b10', shape=[64], initializer=tf.zeros_initializer()),
    'out': tf.get_variable( 'bout', shape=[n_classes], initializer=tf.zeros_initializer()),
}

# Construct model
pred = tf.nn.softmax(conv_net_siamese(x, m, weights, biases, keep_prob), name="y")

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=conv_net_siamese(x, m, weights, biases, keep_prob), labels=y)
                                                              + 0.001*tf.nn.l2_loss(weights['heroes_w'])
                                                              + 0.001*tf.nn.l2_loss(weights['heroes_w2'])
                                                              + 0.001*tf.nn.l2_loss(weights['heroes_w3'])
                                                              + 0.001*tf.nn.l2_loss(weights['heroes_w4'])
                                                              + 0.001*tf.nn.l2_loss(weights['maps_w'])
                                                              + 0.001*tf.nn.l2_loss(weights['w2'])
                                                              + 0.001*tf.nn.l2_loss(weights['w3'])
                                                              + 0.001*tf.nn.l2_loss(weights['w4'])
                                                              + 0.001*tf.nn.l2_loss(weights['w5'])
                                                              + 0.001*tf.nn.l2_loss(weights['w6'])
                                                              + 0.001*tf.nn.l2_loss(weights['w7'])
                                                              + 0.001*tf.nn.l2_loss(weights['w8'])
                                                              + 0.001*tf.nn.l2_loss(weights['w9'])
                                                              + 0.001*tf.nn.l2_loss(weights['w10'])
                                                              + 0.001*tf.nn.l2_loss(weights['out']))
optimizer = tf.train.AdamOptimizer(learning_rate=base_learning_rate).minimize(cost)

# Evaluate model
correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initializing the variables
init = tf.global_variables_initializer()

print('Parameters initialized')

# Launch the graph
with tf.Session(graph = tf.get_default_graph()) as sess:
    sess.run(init)
    print('Session started')
    step = 1
    #If we want to resume training from a particular point
    saver = tf.train.Saver()
    
    saver.restore(sess,'C:\\Users\\Daniel\\.spyder-py3\\siamese_L2_deep')
    # Keep training until reach max iterations
    while step * batch_size < training_iters:
        batch_x, batch_map, batch_y = trainSet.next_batch( batch_size )
        test_x, test_map, test_y = testSet.next_batch( len(test_matchups) )
        # Run optimization op (backprop)
        with tf.device('/gpu:0'):
            sess.run(optimizer, feed_dict={x: batch_x, m:batch_map, y: batch_y, keep_prob: dropout})
        if step % display_step == 0:
            # Calculate batch loss and accuracy
            loss, acc = sess.run([cost, accuracy], feed_dict={x: batch_x,
                                                              m: batch_map,
                                                              y: batch_y,
                                                              keep_prob: 1.0})
            print("Iter " + str(step*batch_size) + ", Minibatch Loss= " + \
                  "{:.6f}".format(loss) + ", Training Accuracy= " + \
                  "{:.5f}".format(acc))
            
            test_loss, test_acc = sess.run([cost, accuracy], feed_dict={x: test_x,
                                                              m: test_map,
                                                              y: test_y,
                                                              keep_prob: 1.0})
            print("Iter " + str(step*batch_size) + ", Minibatch Loss= " + \
                  "{:.6f}".format(test_loss) + ", Testing Accuracy= " + \
                  "{:.5f}".format(test_acc))
    
    
        if step % (1000000 / batch_size) == 0:
            #Now, save the graph
            saver.save(sess, 'C:\\Users\\Daniel\\.spyder-py3\\siamese_L2_deep')
            #w2 = sess.run(weights['w2'])
            #print(w2)
            
            #w3 = sess.run(weights['w3'])
            #print(w3)
            
            #w4 = sess.run(weights['w4'])aph
            #print(w4)
#            if test_acc > 0.65:
#                break
        step += 1
    
#    test_x, test_map, test_y = testSet.next_batch( batch_size )
#
#    predictions = sess.run(pred, feed_dict={x: test_x,
#                                                                m: test_map,
#                                                                y: test_y})
#    
#    team_1_score = []
#    
#    for game in predictions:
#        team_1_score.append(game[0])
#        team_1_score.append(game[1])
#        
#    plt.hist(team_1_score, bins = (50))
#    plt.xlabel('Winrate distribution')
#    plt.show()
#    
#    score = []
#    counts = []
#    
#    for i in range(0,10):
#        score.append(0)
#        counts.append(0)
#        
#    stratified_acc = []
#    a = 0
#    for game in predictions:
#        if game[0] >= 0.5:
#            counts[int(np.ceil(game[0]*20) - 11)] += 1
#        elif game[1] >= 0.5:
#            counts[int(np.ceil(game[1]*20) - 11)] += 1
#        if test_y[a][0] == 1 and game[0] >= 0.5:
#            score[int(np.ceil(game[0]*20) - 11)] += 1
#        elif test_y[a][1] == 1 and game[1] >= 0.5:
#            score[int(np.ceil(game[1]*20) - 11)] += 1
#        a += 1
#            
#    for i in range(0,10):
#        stratified_acc.append(score[i]/counts[i])
#        
#    xrange = []
#    for i in range(55,105,5):
#        xrange.append(i-2.5)
#        
#    plt.plot(xrange, stratified_acc)
#    plt.ylabel('Accuracy')
#    plt.xlabel('Estimated winrate (%)')
#    plt.xlim(50,100)
#    plt.show()
#    auc = tf.metrics.auc(
#                        test_y,
#                        predictions,
#                        weights=None,
#                        num_thresholds=100,
#                        metrics_collections=None,
#                        updates_collections=None,
#                        curve='ROC',
#                        name='lcl'
#    )
#    
#    lcl_init = tf.local_variables_initializer()
#    sess.run(lcl_init)
#    print(sess.run(auc, feed_dict={x: test_x,
#                                   m: test_map,
#                                   y: test_y}))
#    
#    true_pos = sess.run( 'lcl/true_positives:0' )
#    false_pos = sess.run( 'lcl/false_positives:0' )
#    
#    plt.plot(false_pos/10000, true_pos/10000)
#    plt.plot(np.arange(0, 1.01, 0.01), np.arange(0, 1.01, 0.01))
#    plt.ylabel('Sensibilité')
#    plt.xlabel('1 - Spécificité')
#    plt.show()
    
    print("Optimization Finished!")



    #Now, save the graph
    
    checkpoint_prefix = ("C:\\Users\\Daniel\\.spyder-py3\\graph\\saved_checkpoint")
    saver.save(sess, checkpoint_prefix, global_step=0)
    tf.train.write_graph(sess.graph_def, "C:\\Users\\Daniel\\.spyder-py3\\graph", "input_graph.pb")
    
