import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


class SOFTMAX:
    def __init__(self, images, labels):
        self.images = images
        self.labels = labels
    def accuracy(self, predictions, labels):
        return (100.0 * np.sum(np.argmax(predictions, 1) == np.argmax(labels, 1)) / predictions.shape[0])

    def constru_SOFTMAX(self, images_val, labels_val, images_test, labels_test):
    	X = tf.placeholder(tf.float32, [None, 784], name='image')
    	Y = tf.placeholder(tf.float32, [None, 10], name='label')
    
        W = tf.Variable(tf.truncated_normal([784, 10], stddev=0.1), name="weight")
        b = tf.Variable(tf.zeros([10]), name="bias")

        # Set up the hyperparameters
        learning_rate = 0.01	
        momentum = 0.4
        training_epochs = 1000
        
        # start to train the model, maximize the log-likelihood / minimize the cost
        logits = tf.add(tf.matmul(X, W), b)
        cost_batch = tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y)
        cost = tf.reduce_mean(cost_batch)
        
        optimizer = tf.train.MomentumOptimizer(learning_rate, momentum)
        train_op = optimizer.minimize(cost)
        
        log_likelihood_train = -tf.reduce_mean(cost_batch)
        log_likelihood_valid = -tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
            logits=tf.add(tf.matmul(images_val, W), b), labels=labels_val))

        # Calculate the predition with softmax
        train_predition = tf.nn.softmax(logits)
        valid_prediction = tf.nn.softmax(tf.add(tf.matmul(images_val, W), b))
        test_prediction = tf.nn.softmax(tf.add(tf.matmul(images_test, W), b))

        sess = tf.InteractiveSession()
        init = tf.initialize_all_variables()
        sess.run(init)

        result = np.zeros(shape=(5, training_epochs))
        log_likelihood_max = -float("inf")
        lilelihood_overfitting = False
        lilelihood_oscillation = 0


        print "leraning rate:" + repr(learning_rate)
    	for epoch in range(training_epochs):
            # Train the model
	        for i in xrange(300):
	            batch_xs = self.images[i * 50: (i + 1) * 50]
	            batch_ys = self.labels[i * 50: (i + 1) * 50]
	            cost_np, _ = sess.run([cost, train_op], feed_dict={X: batch_xs, Y: batch_ys})
            
	        likelihood_train, predictions_train = sess.run([log_likelihood_train, train_predition], 
	        	feed_dict={X: self.images, Y:self.labels})
	        accuracy_train = self.accuracy(predictions_train, self.labels)
	        likelihood_val = log_likelihood_valid.eval()
	        accuracy_val = self.accuracy(valid_prediction.eval(), labels_val)

	        result[0, epoch] = epoch + 1
	        result[1, epoch] = (100 - accuracy_val) * 1000 / 100
	        result[2, epoch] = (100 - accuracy_train) * 15000 / 100
	        result[3, epoch] = likelihood_train
	        result[4, epoch] = likelihood_val
	   
	        if(epoch % 50 == 0):
	        	print ("Epoch:%04d, Train Accuracy=%0.4f, Eval Accuracy=%0.4f, log_likelyhood_train:%0.6f, log_likelyhood_val:%0.6f" %
	        		(epoch+1, accuracy_train, accuracy_val, likelihood_train, likelihood_val))

            # When the log-likelihood reaches at maximum, use the early stopping to stop the training
	        if(log_likelihood_max < likelihood_val):
	        	log_likelihood_max = likelihood_val
	        	lilelihood_oscillation = 0
	        elif(log_likelihood_max - likelihood_val > 0):
	        	lilelihood_oscillation += 1

	        if(lilelihood_overfitting == False):
	        	if(lilelihood_oscillation >= 15):
	        	    lilelihood_overfitting = True
	        	    print "Likelihood overfitting"
	        	    print ("Epoch:%04d, Train Accuracy=%0.4f, Eval Accuracy=%0.4f, log_likelyhood_train:%0.6f, log_likelyhood_val:%0.6f" % 
		               (epoch+1, accuracy_train, accuracy_val, likelihood_train, likelihood_val))
	        	    accuracy_test = self.accuracy(test_prediction.eval(), labels_test)
	        	    print ("Test Accuracy=%0.4f" % (accuracy_test))
	        	    print 'Test_Error: ' + repr((100 - accuracy_test) * 2720 / 100)

	        	    plt.plot(result[0,:epoch], result[1,:epoch],'b-', label='Validation Error')
	        	    plt.plot(result[0,:epoch], result[2,:epoch],'r-', label = 'Training Error')
	        	    plt.legend(loc = 'upper right', numpoints = 1)
	        	    plt.xlabel('Number of Epochs')
	        	    plt.ylabel('Number of Errors')
	        	    plt.savefig('err_early')
	        	    plt.close()
                    	        	    
	        	    plt.plot(result[0,:epoch], result[3,:epoch],'b-', label = 'Log-likelihood_Training')
	        	    plt.plot(result[0,:epoch], result[4,:epoch],'r-', label = 'Log-likelihood_Validation')
	        	    plt.legend(loc = 'lower right', numpoints = 1)
	        	    plt.xlabel('Number of Epochs')
	        	    plt.ylabel('Log-likelihood')
	        	    plt.savefig('log_early')
	        	    plt.close()
        
        # Compute the test errors after the complete training process 
        print "Complete:"
        accuracy_test = self.accuracy(test_prediction.eval(), labels_test)
        print ("Test Accuracy=%0.4f" % (accuracy_test))
        print 'Test_Error: ' + repr((100 - accuracy_test) * 2720 / 100)

    	plt.plot(result[0,:], result[1,:],'b-', label='Validation Error')
    	plt.plot(result[0,:], result[2,:],'r-', label = 'Training Error')
    	plt.legend(loc = 'upper right', numpoints = 1)
    	plt.xlabel('Number of Epochs')
    	plt.ylabel('Number of Errors')
        plt.savefig('err')
        plt.close()

    	plt.plot(result[0,:], result[3,:],'b-', label = 'Log-likelihood_Training')
    	plt.plot(result[0,:], result[4,:],'r-', label = 'Log-likelihood_Validation')
    	plt.legend(loc = 'lower right', numpoints = 1)
    	plt.xlabel('Number of Epochs')
    	plt.ylabel('Log-likelihood')
        plt.savefig('log')
        plt.close()


with np.load("notMNIST.npz") as data:
    images , labels = data["images"], data["labels"]

# Reshape the imput data 
images_in = images.reshape(784,18720).T.astype("float32")
labels_in = np.zeros([18720,10]).astype("float32")
index = 0
for i in labels:
    labels_in[index, i] = 1
    index +=1

# The input data is divided by 255 so as to normalize the data in the range of 0 - 1 and reduce the error
softmax = SOFTMAX(images_in[:15000,:]/255, labels_in[:15000,:])
softmax.constru_SOFTMAX(images_in[15000:16000,:]/255, labels_in[15000:16000,:], images_in[16000:18720,:]/255, labels_in[16000:18720,:])
