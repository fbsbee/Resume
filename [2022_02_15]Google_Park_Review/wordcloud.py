import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import time
import os
import numpy as np
from PIL import Image

def mask_img(img_path, file_size=(2555, 2275), color = (255, 255, 255)):
    mask = Image.new("RGBA",file_size, color) #(2555,2575)는 사진 크기, (255,255,255)는 색을의미
    image = Image.open(img_path).convert("RGBA")
    x,y = image.size
    mask.paste(image,(0,0,x,y),image)
    mask = np.array(mask)
    return mask

# svg로 파일 다운로드
def plot_cloud(wordcloud, file_name):
    plt.axis("off")
    fig = plt.gcf() #get current figure
    fig.set_size_inches(10,10)
    plt.savefig(file_name + ".svg", dpi=700, format="svg")
    plt.imshow(wordcloud, interpolation="bilinear")

# 파일 경로 반환 함수
def read_file(folder_path):
    return (os.path.join(path, filename) for path, dir_, filenames in os.walk(folder_path) for filename in filenames)

def word_cloud_image(file_path, font_path, background_color='white', max_font_size=60, filename_extenstion='.png', save_folder_path='./', mask=None, colormap='prism'):
    # word count 파일 읽기
    datas = pd.read_csv(file_path)
    datas = datas.to_dict('records')

    # dictionary화
    new_data = {k : v for k, v in map(lambda x : x.values(), datas)}

    # wordcloud 사용 후 파일 저장
    # mask 이미지가 있지 않다면
    if mask is None:
        wc = WordCloud(font_path=font_path,background_color=background_color, max_font_size=max_font_size, colormap=colormap)
    else:
        wc = WordCloud(font_path=font_path,background_color=background_color, max_font_size=max_font_size, colormap=colormap, mask=mask)

    cloud = wc.generate_from_frequencies(new_data)
    # 다운받을 파일 경로
    file_name_slash = file_path.rfind('/') + 1
    file_name_under_bar = file_path.rfind('_')
    file_name = file_path[file_name_slash:file_name_under_bar]
    save_file_path = os.path.join(save_folder_path, file_name+filename_extenstion)
    # 이미지 파일 저장
    cloud.to_file(save_file_path)
    print(f'save file at : {save_file_path}')

if __name__=='__main__':
    # 읽을 파일 경로
    # file_path = 'datasets/after/2022-01-14/haneul_2022-01-14.csv'
    # 읽을 폴더 경로
    folder_path = 'datasets/after/2022-01-18/'
    # 나눔 폰트
    font_path = '/usr/share/fonts/truetype/nanum/NanumSquareB.ttf'
    # 저장할 폴더 경로
    save_folder_path='libs' 
    for file_path in read_file(folder_path):
        word_cloud_image(file_path=file_path, font_path=font_path, save_folder_path=save_folder_path)