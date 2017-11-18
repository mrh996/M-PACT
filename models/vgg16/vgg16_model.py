" VGG16 + LSTM MODEL IMPLEMENTATION FOR USE WITH TENSORFLOW "

import os
import sys
sys.path.append('../..')

import tensorflow as tf
import numpy      as np

from vgg16_preprocessing import preprocess
from layers_utils        import *



class VGG16():

    def __init__(self, verbose=True):
        """
        Args:
            :verbose: Setting verbose command
        """
        self.verbose=verbose
        self.name = 'vgg16'
        print "vgg16 initialized"

    def _LSTM(self, inputs, seq_length, feat_size, cell_size=1024):
        """
        Args:
            :inputs:       List of length input_dims where each element is of shape [batch_size x feat_size]
            :seq_length:   Length of output sequence
            :feat_size:    Size of input to LSTM
            :cell_size:    Size of internal cell (output of LSTM)

        Return:
            :lstn_outputs:  Output list of length seq_length where each element is of shape [batch_size x cell_size]
        """

        # Unstack input tensor to match shape:
        # list of n_time_steps items, each item of size (batch_size x featSize)

        inputs = tf.unstack(inputs, seq_length, axis=0)

        # LSTM cell definition
        lstm_cell            = tf.contrib.rnn.BasicLSTMCell(cell_size)
        lstm_outputs, states = tf.contrib.rnn.static_rnn(lstm_cell, inputs, dtype=tf.float32)

        # Condense output shape from:
        # list of n_time_steps itmes, each item of size (batch_size x cell_size)
        # To:
        # Tensor: [(n_time_steps x 1), cell_size] (Specific to our case)
        lstm_outputs = tf.stack(lstm_outputs)
        lstm_outputs = tf.reshape(lstm_outputs,[-1,cell_size])

        return lstm_outputs


    def inference(self, inputs, is_training, input_dims, output_dims, seq_length, scope, k, j, weight_decay=0.0, return_layer='logits'):

        """
        Args:
            :inputs:       Input to model of shape [Frames x Height x Width x Channels]
            :is_training:  Boolean variable indicating phase (TRAIN OR TEST)
            :input_dims:   Length of input sequence
            :output_dims:  Integer indicating total number of classes in final prediction
            :seq_length:   Length of output sequence from LSTM
            :scope:        Scope name for current model instance
            :k:            Width of sliding window (temporal width) 
            :j:            Integer number of disjoint sets the sliding window over the input has generated 
            :return_layer: String matching name of a layer in current model
            :weight_decay: Double value of weight decay
    
        Return:
            :layers[return_layer]: The requested layer's output tensor
        """

        ############################################################################
        #                       Creating VGG 16 Network Layers                     #
        ############################################################################

        if self.verbose:
            print('Generating VGG16 network layers')
        
        # END IF

        # Must exist within current model directory
        data_dict = np.load('models/vgg16/vgg16.npy').item()

        if is_training:
            keep_prob = 0.5
        else:
            keep_prob = 1.0

        # END IF

        with tf.name_scope(scope, 'vgg16', [inputs]):
            layers = {}

            layers['conv1'] = conv_layer(input_tensor=inputs,
                           filter_dims=[3,3,64],
                           stride_dims=[1,1],
                           name='conv1',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv1_1'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv1_1'][1]))

            layers['conv2'] = conv_layer(input_tensor=layers['conv1'],
                           filter_dims=[3,3,64],
                           stride_dims=[1,1],
                           name='conv2',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv1_2'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv1_2'][1]))

            layers['pool2'] = max_pool_layer(layers['conv2'],
                               filter_dims=[2,2],
                               stride_dims=[2,2],
                               name='pool2',
                               padding='VALID')

            layers['conv3'] = conv_layer(input_tensor=layers['pool2'],
                           filter_dims=[3,3,128],
                           stride_dims=[1,1],
                           name='conv3',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv2_1'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv2_1'][1]))

            layers['conv4'] = conv_layer(input_tensor=layers['conv3'],
                           filter_dims=[3,3,128],
                           stride_dims=[1,1],
                           name='conv4',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv2_2'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv2_2'][1]))

            layers['pool4'] = max_pool_layer(layers['conv4'],
                               filter_dims=[2,2],
                               stride_dims=[2,2],
                               name='pool4',
                               padding='VALID')

            layers['conv5'] = conv_layer(input_tensor=layers['pool4'],
                           filter_dims=[3,3,256],
                           stride_dims=[1,1],
                           name='conv5',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv3_1'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv3_1'][1]))

            layers['conv6'] = conv_layer(input_tensor=layers['conv5'],
                           filter_dims=[3,3,256],
                           stride_dims=[1,1],
                           name='conv6',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv3_2'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv3_2'][1]))

            layers['conv7'] = conv_layer(input_tensor=layers['conv6'],
                           filter_dims=[3,3,256],
                           stride_dims=[1,1],
                           name='conv7',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv3_3'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv3_3'][1]))

            layers['pool7'] =  max_pool_layer(layers['conv7'],
                               filter_dims=[2,2],
                               stride_dims=[2,2],
                               name='pool7',
                               padding='VALID')

            layers['conv8'] = conv_layer(input_tensor=layers['pool7'],
                           filter_dims=[3,3,512],
                           stride_dims=[1,1],
                           name='conv8',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv4_1'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv4_1'][1]))

            layers['conv9'] = conv_layer(input_tensor=layers['conv8'],
                           filter_dims=[3,3,512],
                           stride_dims=[1,1],
                           name='conv9',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv4_2'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv4_2'][1]))

            layers['conv10'] = conv_layer(input_tensor=layers['conv9'],
                           filter_dims=[3,3,512],
                           stride_dims=[1,1],
                           name='conv10',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv4_3'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv4_3'][1]))

            layers['pool10'] = max_pool_layer(layers['conv10'],
                               filter_dims=[2,2],
                               stride_dims=[2,2],
                               name='pool7',
                               padding='VALID')

            layers['conv11'] = conv_layer(input_tensor=layers['pool10'],
                           filter_dims=[3,3,512],
                           stride_dims=[1,1],
                           name='conv11',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv5_1'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv5_1'][1]))

            layers['conv12'] = conv_layer(input_tensor=layers['conv11'],
                           filter_dims=[3,3,512],
                           stride_dims=[1,1],
                           name='conv12',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv5_2'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv5_2'][1]))

            layers['conv13'] = conv_layer(input_tensor=layers['conv12'],
                           filter_dims=[3,3,512],
                           stride_dims=[1,1],
                           name='conv13',
                           weight_decay=weight_decay,
                           padding='SAME',
                           non_linear_fn=tf.nn.relu,
                           kernel_init=tf.constant_initializer(data_dict['conv5_3'][0]),
                           bias_init=tf.constant_initializer(data_dict['conv5_3'][1]))

            layers['pool13'] = max_pool_layer(layers['conv13'],
                               filter_dims=[2,2],
                               stride_dims=[2,2],
                               name='pool13',
                               padding='VALID')

            layers['fc6'] = fully_connected_layer(input_tensor=layers['pool13'],
                                      out_dim=4096,
                                      name='fc6',
                                      weight_decay=weight_decay,
                                      non_linear_fn=tf.nn.relu,
                                      weight_init=tf.constant_initializer(data_dict['fc6'][0]),
                                      bias_init=tf.constant_initializer(data_dict['fc6'][1]))

            layers['drop6'] = tf.nn.dropout(layers['fc6'], keep_prob=keep_prob)

            layers['fc7'] = fully_connected_layer(input_tensor=layers['drop6'],
                                      out_dim=4096,
                                      name='fc7',
                                      weight_decay=weight_decay,
                                      non_linear_fn=tf.nn.relu,
                                      weight_init=tf.constant_initializer(data_dict['fc7'][0]),
                                      bias_init=tf.constant_initializer(data_dict['fc7'][1]))

            layers['drop7'] = tf.nn.dropout(layers['fc7'], keep_prob=keep_prob)

            feat_size=4096
            rnn_inputs = tf.reshape(layers['drop7'], [seq_length, input_dims/seq_length,  4096])

            layers['rnn_outputs'] = self._LSTM(rnn_inputs, seq_length, feat_size=4096, cell_size=1024)



            layers['drop8'] = tf.nn.dropout(layers['rnn_outputs'], keep_prob=keep_prob)

            if output_dims == data_dict['fc8'][0].shape[1]:
                layers['logits'] = fully_connected_layer(input_tensor=layers['drop8'],
                                          out_dim=output_dims,
                                          name='logits',
                                          weight_decay=weight_decay,
                                          non_linear_fn=None,
                                          weight_init=tf.constant_initializer(data_dict['fc8'][0]),
                                          bias_init=tf.constant_initializer(data_dict['fc8'][1]))
            else:
                layers['logits'] = fully_connected_layer(input_tensor=layers['drop8'],
                                          out_dim=output_dims,
                                          name='logits',
                                          weight_decay=weight_decay,
                                          non_linear_fn=None)

            # END IF
        
        # END WITH
            
        return layers[return_layer]


    """ Function to return loss calculated on given network """
    def loss(self, logits, labels):
        """
        Args:
            :logits: Unscaled logits returned from final layer in model 
            :labels: True labels corresponding to loaded data 
        """

        labels = tf.cast(labels, tf.int64)

        cross_entropy_loss = tf.losses.sparse_softmax_cross_entropy(labels=labels[:labels.shape[0].value/2],
                                                                    logits=logits[:logits.shape[0].value/2,:])

        return cross_entropy_loss


    def preprocess(self, index, data, labels, size, is_training):
        """
        Args:
            :index:       Integer indicating the index of video frame from the text file containing video lists
            :data:        Data loaded from HDF5 files
            :labels:      Labels for loaded data
            :size:        List detailing values of height and width for final frames
            :is_training: Boolean value indication phase (TRAIN OR TEST)
        """

        return preprocess(index, data,labels, size, is_training)
