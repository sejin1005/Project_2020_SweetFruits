
import cv2
import matplotlib.pyplot as plt
import os
import glob

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

#1. 라즈베리파이 카메라를 통해 lcd 사진 찍기
#   경로: test/lcd.jpg
real_img = cv2.imread("./test/test2.jpg")  # 이미지 파일 읽기

#2. lcd.jpg에서 lcd부분만 좌표값을 통해 자르기
img = real_img.copy()
#img = real_img[850:1000,1050:1600] #lcd 전체 프레임
img = real_img[850:980,1100:1200]

#3. lcd에 저장된 숫자(img)를 영상처리하여 숫자(int)로 변경
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 이미지 흑백처리
img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
plt.figure(figsize=(5, 5))
plt.imshow(img_blur)
plt.show()

ret, img_th = cv2.threshold(img_blur, 100, 255, cv2.THRESH_BINARY_INV)
image, contours, hierachy = cv2.findContours(img_th.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
plt.imshow(image)
plt.show()

#4. lcd값이 30 ----> result1.jpg(3) /  result0.jpg(0)
#   경로:  lcd_result/ result1.jpg
#         lcd_result/ result2.jpg
rects = [cv2.boundingRect(each) for each in contours]

img_result = []
img_for_class = img.copy()
margin_pixel = 0

count = 0
for rect in rects:
    if 0 < rect[0] < 60:
        cv2.rectangle(img, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (255, 0, 0), 2)
        #plt.imshow(img)
        #plt.show()

        img_result.append(
            img_for_class[rect[1] - margin_pixel: rect[1] + rect[3] + margin_pixel,
            rect[0] - margin_pixel: rect[0] + rect[2] + margin_pixel])

for x in range(len(img_result)):
    name = 'result_'+str(x)+'.jpg'
    path = './lcd_value/'+name
    #print(path)
    save = cv2.imwrite(path, img_result[x])

# plt.figure(figsize=(5, 5))
# plt.title('last')
# plt.imshow(img)
# plt.show()

#4. lcd_result 폴더에 값을 읽어와 딥러닝
#28x28 크기의 숫자값 1개 읽어서 딥러닝을 통해 예측한 lcd숫자값 출력
from keras.models import load_model
model = load_model('./model/37-0.3457.hdf5')

images = glob.glob('./lcd_value/*.jpg')
value = ''


for fname in images:
    img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
    ret2, img_gray = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    plt.figure(figsize=(5,5))
    plt.imshow(img_blur)
    plt.show()

    plt.imshow(cv2.resize(img_blur,(28,28)))
    plt.show()

    test_num = cv2.resize(img_blur, (28,28))
    test_num = (test_num > 100) * test_num
    test_num = test_num.astype('float32') / 255.

    plt.imshow(test_num, cmap='Greys', interpolation='nearest')
    test_num = test_num.reshape((1, 28, 28, 1))
    print('The Answer is ', model.predict_classes(test_num))
    value = value + (str(model.predict_classes(test_num)))

value = value.replace(']','')
value = value.replace('[','')
result = value[1] + value[0]

print(result)

#5. value에 저장된 값을 서버에 전송.

