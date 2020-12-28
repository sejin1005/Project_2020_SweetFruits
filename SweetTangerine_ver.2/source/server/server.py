import socket
import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt
from torchvision import datasets, models, transforms
import os
import time 

from elasticsearch import Elasticsearch
import datetime
import json

fruitsname = None

# use Model_Run.py
# Referenced by https://tutorials.pytorch.kr/beginner/transfer_learning_tutorial.html
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

data_dir = 'data/test'
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),
                                          data_transforms[x])
                  for x in ['train', 'val']}
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=8,
                                             shuffle=True, num_workers=8)
              for x in ['train', 'val']}
dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
class_names = image_datasets['train'].classes

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def imshow(inp, title=None):
    """Imshow for Tensor."""
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(0.001)


def visualize_model(model, num_images=2):
    global fruitsname    
    was_training = model.training
    model.eval()
    images_so_far = 0
    fig = plt.figure()

    with torch.no_grad():
        for i, (inputs, labels) in enumerate(dataloaders['val']):
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            for j in range(inputs.size()[0]):
                images_so_far += 1
              
                fruitsname = class_names[preds[j]]

                if images_so_far == num_images:
                    model.train(mode=was_training)
                    return
        model.train(mode=was_training)

model = torch.load('fruits_model.pt')

model.eval()

# return buffer from received socket
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def run():
    torch.multiprocessing.freeze_support()
    visualize_model(model)

# datetime
def utc_time():  
	return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

# elasticsearch mapping
def make_index_API():
        with open('elk_test_002.json', 'r') as f:

            mapping = json.load(f)

if __name__ == '__main__':
	HOST=''
	PORT=8494

	# init elasticsearch
	es = Elasticsearch('localhost:9200')
	make_index_API()

	# tcp init
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	print('Socket created')
	# bind server
	s.bind((HOST,PORT))
	print('Socket bind complete')
	# wait server
	s.listen(10)
	print('Socket now listening')

	conn,addr=s.accept()

	while True: 
		# tcp socket
		# referenced by https://j-remind.tistory.com/58

		try:
            # client에서 받은 stringData의 크기 (==(str(len(stringData))).encode().ljust(16))
            length = recvall(conn, 16)
            stringData = recvall(conn, int(length))
            data = np.fromstring(stringData, dtype = 'uint8')

            # decoding
            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)

            # crop lcd, fruits region
            frame1 = frame[500:800, 700:1100]
            frame2 = frame[400:520, 600:1000]

            # save image
            cv2.imwrite('./data/test/val/testset/test.jpg', frame1)
            cv2.imwrite('./data/lcd/test.jpg' ,frame)

            # classification
            run()

            # receive weight, sweetie data from client
            data = conn.recv(1024)
            data = data.decode()
            data = data.split(" ")
            #print(fruitsname)
            #print('recv: ',data)

            # send classification fruits name
            conn.send(fruitsname.encode())

            # mapping data
            doc = {"date":utc_time(),
                "name" : fruitsname,
                "weight": float(data[0]),
                "sugar_content": int(data[1])}

            # create elasticsearch index, PUT data
            res = es.index(index='pyelk5', body=doc)
            time.sleep(5)

        except:
            print("close server")
            print("disconnected client")
	        s.close()
            conn.close()
            break
		
