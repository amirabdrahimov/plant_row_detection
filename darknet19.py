'''
DarkNet-19 model is used to classify ImageNet-1000 images for a certain epoch. Once this model is trained, the learned weight parameters will be used
for the object detection model which we'll call as Yolo Net here. All except the last few layers are the same.
'''

import torch
import torch.nn as NN
from torch.optim import Adam, lr_scheduler
import cfg

class Darknet19(NN.Module):
    '''
    Darknet-19 architecture.
    '''

    def _initialize_weights(self):
        '''
        Weight initialization module.
        '''
        for m in self.modules():

            if isinstance(m, NN.Conv2d):
                NN.init.kaiming_normal_(m.weight, mode='fan_out')
                if m.bias is not None:
                    NN.init.constant_(m.bias, 0.5)
            elif isinstance(m, NN.BatchNorm2d):
                NN.init.constant_(m.weight, 1)
                NN.init.constant_(m.bias, 0.5)

    def __init__(self, num_classes, init_weights=True):
        
        self.num_classes = num_classes

        super(Darknet19, self).__init__()

        #configuration of the layers in terms of (kernel_size, filter_channel_output). 'M' stands for maxpooling.
        self.cfgs = {
            'yolo':[(3,32), 'M', (3,64), 'M', (3,128), (1,64), (3,128), 'M', (3,256), (1,128), (3,256), 'M', (3,512),
                    (1,256), (3,256), (1,256), (3,512), 'M', (3,1024), (1,512), (3,1024), (1,512), (3,1024), 
                    (1, self.num_classes)]
        }

        layers = []
        in_channels = 3
        

        for l in self.cfgs['yolo']:
            
            padding_value = 1
            
            if l == 'M':
                layers += [NN.MaxPool2d(kernel_size=2, stride=2)]
            else:
                if l[0] == 1: #if the filter size is 1, no padding is required. Else, the input dimension will increase by 1.
                    padding_value = 0
                conv2d = NN.Conv2d(in_channels, l[1], kernel_size=l[0], padding=padding_value)

                #for the last convolution layer. No activation function.
                if l[1] == self.num_classes:
                    #AdaptiveMaxPool infers the input size parameters on its own whereas MaxPool requires us to supply the input parameters.
                    layers += [conv2d, NN.AdaptiveMaxPool2d(output_size = self.num_classes)]
                    break

                layers += [conv2d, NN.BatchNorm2d(num_features=l[1]), NN.LeakyReLU(inplace=True)]
                in_channels = l[1]

        self.classification = NN.Sequential(*layers)
        
         
        if init_weights:
            self._initialize_weights()
    
    
    def calculate_accuracy(self, network_output, target):
        '''
        Calculates the accuracy of the predictions.
        '''
        num_data = target.size()[0]
        correct_predictions = torch.sum(network_output==target)
        
        accuracy = (correct_predictions*100/num_data)
        
        return accuracy
        
    
    def forward(self, input_x):

        x = self.classification(input_x)
   
        return x
    
    


darknet19 = Darknet19(num_classes=cfg.ImgNet_num_of_class, init_weights=True)

ImgNet_optimizer = Adam(darknet19.parameters(), lr = cfg.ImgNet_learning_rate)
ImgNet_lr_decay = lr_scheduler.ExponentialLR(ImgNet_optimizer, gamma=cfg.ImgNet_learning_rate_decay)
ImgNet_criterion = NN.CrossEntropyLoss() #cross entropy expects a raw unnormalized input (No need to softmax the output of the network)


if torch.cuda.is_available():
    
    darknet19 = darknet19.cuda()