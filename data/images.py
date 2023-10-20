from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import requests
from PIL import Image
from tqdm import tqdm

def get_image(img_result,file_name,index):
    try:
        WebDriverWait(driver,8).until(EC.element_to_be_clickable(img_result))
        img_result.click()
        time.sleep(3)

        actual_imgs = driver.find_elements(
                by=By.XPATH,
                
                value="//*[@id='Sva75c']/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]"
            )
        #print(actual_imgs)
        src = ''

        for actual_img in actual_imgs:
            if 'https://encrypted' in actual_img.get_attribute('src'):
                pass
            elif 'http' in actual_img.get_attribute('src'):
                src += actual_img.get_attribute('src')
                break
            else:
                pass

        for actual_img in actual_imgs:
            if src == '' and 'base' in actual_img.get_attribute('src'):
                src += actual_img.get_attribute('src')
    
        if 'https://' in src:
            file_path = './images/' + str(index) + '.' + file_name + '.jpeg'
            try:
                result = requests.get(src, allow_redirects=True, timeout=10)
                open(file_path, 'wb').write(result.content)
                #print(result)
                img = Image.open(file_path)
                img = img.convert('RGB')
                img.save(file_path, 'JPEG')
                locations['image_location'].append(file_path)
                #print('Image saved from https.')
  
            except:
                pass
    except :
        pass


df = pd.read_excel('master_data copy.xlsx')
df = df[['year','make','model']][2540:]
df['search'] = df['make']+' ' + df.model.astype(str) + ' ' + df.year.fillna(2023).astype(int).astype(str) 
locations = {'image_location':[]}
driver = webdriver.Chrome()
index=2336
for search_term in tqdm(df.search.values.ravel()):
    index+=1
    driver.get('https://www.google.com/imghp')
    search_bar = driver.find_element(By.NAME, "q")

    search_bar.send_keys(search_term)
    search_bar.send_keys(Keys.RETURN)
    current_url = driver.current_url
    #print("Current URL:", current_url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    img_results = driver.find_elements(
            by=By.XPATH,
            value="//img[contains(@class,'rg_i Q4LuWd')]"
        )
    for img_result in img_results[:1]:
        file_name = search_term
        get_image(img_result,file_name,index)
        time.sleep(1)

    




driver.quit()