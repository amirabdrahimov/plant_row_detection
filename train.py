from load_data import Load_Dataset, ToTensor
import cfg
from torch.utils.data import DataLoader
import cv2
from label_format import calculate_ground_truth
import numpy as np
from yolo_net import yolo, optimizer, loss, lr_decay #decay rate update
from tqdm import tqdm
from mAP import mAP

training_data = Load_Dataset(resized_image_size=320, transform=ToTensor())

dataloader = DataLoader(training_data, batch_size=1, shuffle=False, num_workers=4)

mAP_object = mAP(box_num_per_grid=cfg.k, feature_size=10, topN_pred=5, anchors_list=training_data.anchors_list)


print(yolo)

for epoch_idx in range(cfg.total_epoch):
    
    epoch_loss = 0
    training_loss = []

    for i, sample in tqdm(enumerate(dataloader)):
        # print(sample["image"].shape)
        # print(sample["label"].shape)
        
        batch_x, batch_y = sample["image"].cuda(), sample["label"].cuda()
        
        optimizer.zero_grad()
        
        #[batch size, feature map width, feature map height, number of anchors, 5 + number of classes]
        outputs = yolo(batch_x) #THE OUTPUTS ARE NOT YET GONE THROUGH THE ACTIVATION FUNCTIONS.
        
        total_loss = loss(predicted_array= outputs, label_array=batch_y)
        mAP_object._collect(predicted_boxes=outputs.detach().cpu().numpy(), gt_boxes=batch_y.cpu().numpy())
        training_loss.append(total_loss.item())
        total_loss.backward()
        optimizer.step()                  
        
        # img_ = np.asarray(np.transpose(batch_x.cpu().numpy()[0], (1,2,0)))
        # img = cv2.cvtColor(img_, cv2.COLOR_BGR2RGB)
        
        # calculated_batch = calculate_ground_truth(subsampled_ratio=32, anchors_list=training_data.anchors_list, resized_image_size=320, 
        #                     network_prediction=outputs.detach().cpu().numpy(), prob_threshold=0.99)
        
        
        # # print("CLASS : " , calculated_batch[0])
        # for k in range(calculated_batch.shape[1]):
        #     # print(int(calculated_batch[0][k][0]), int(calculated_batch[0][k][1]), int(calculated_batch[0][k][2]), int(calculated_batch[0][k][3]))
        #     # try:
            
        #     cv2.putText(img, (str(round(calculated_batch[0][k][0],4))+", "+ str(cfg.classes[int(calculated_batch[0][k][5])])), (int(calculated_batch[0][k][1]), 
        #                                                                           int(calculated_batch[0][k][2])-8), cv2.FONT_HERSHEY_SIMPLEX, 
        #                                                                                                                             0.4, (36,255,12), 2)
        #     cv2.rectangle(img, (int(calculated_batch[0][k][1]), int(calculated_batch[0][k][2])), (int(calculated_batch[0][k][3]), int(calculated_batch[0][k][4])),
        #                 (0,255,0), 1)
        #     # except Exception as e:
        #     #     print(e)
        #     #     pass
            
        # cv2.imshow("img", img)
        # cv2.waitKey(0)
        # break  
        
    
    lr_decay.step() #decay rate update
        # print(total_loss.item())
    meanAP = mAP_object.calculate_meanAP()
    print("MEAN Avg Prec : ", meanAP)
    training_loss = np.average(training_loss)
    print("Epoch %d, \t Loss : %g"%(epoch_idx, training_loss))
    
    
        
    
    

    # img = sample["image"].numpy()[0]
    # print(calculated_batch.shape)
    # calculated_batch = calculate_ground_truth(subsampled_ratio=32, anchors_list=training_data.anchors_list, resized_image_size=320, 
                            # network_prediction=batch_y.cpu().numpy(), prob_threshold=0.85)
    # for k in range(calculated_batch.shape[1]):
    #     print(int(calculated_batch[0][k][0]), int(calculated_batch[0][k][1]), int(calculated_batch[0][k][2]), int(calculated_batch[0][k][3]))
    #     cv2.rectangle(img, (int(calculated_batch[0][k][0]), int(calculated_batch[0][k][1])), (int(calculated_batch[0][k][2]), int(calculated_batch[0][k][3])),
    #                     (255,255,255), 2)
    
    # cv2.imshow("img", img)
    # cv2.waitKey(0)