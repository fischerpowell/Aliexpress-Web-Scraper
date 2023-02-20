from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import csv

driver = webdriver.Chrome()
driver.get('https://www.aliexpress.com/w/wholesale-trending-products.html')


usa = False
#Session sometimes opens as a random country with shuffled currency and language.

#Opens Region panel
while not usa:
    driver.find_element(By.XPATH, "//div[@data-role='region-pannel']").click()
    try:
        #Clicks on country option
        driver.find_element(By.XPATH, "//a[@data-role='country']").click()
        usa = True
    except NoSuchElementException:
        pass

#Filters and clicks on United States
driver.find_element(By.XPATH, "//input[@class='filter-input']").send_keys('United States')
driver.find_element(By.XPATH, "//li[@data-name='United States']").click()

#Filters and clicks on english
driver.find_element(By.XPATH, "//span[@data-role='language-input']").click()
driver.find_element(By.XPATH, "//input[@data-role='language-search']").send_keys('English')
driver.find_element(By.XPATH, "//a[@data-locale='en_US']").click()

#Saves and waits for reload
driver.find_element(By.XPATH, "//button[@data-role='save']").click()
sleep(3)


#Finds all of the items on the webpage
#Scrolling should be implemented here to increase the count of scraped items.

items = driver.find_elements(By.XPATH, '//a[contains(@href, "item")]')


#Links is a set so no duplicate links are added, links contains all item links from the main page.
links = set()

for item in items:
    links.add(item.get_attribute('href'))

#Opens csv, titled aliexpress.csv. CSV should be moved or deleted after every use, or implement an id feature.
with open('aliexpress.csv', 'w', newline='') as csvfile:

    #Fieldnames for csv, initializes writer
    fieldnames = ['item', 'item_link', 'sku_title', 'prop_name', 'price', 'img_link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='')
    writer.writeheader()

    #Limit of products to be added to csv.
    limit = 5
    counter = 0
    

    for link in links:
        driver.get(link)   
        try:
            #Scrapes item title and link and writes to csv.
            title = driver.find_element(By.XPATH, '//h1[@class="product-title-text"]').get_attribute('innerHTML')
            sku_properties = driver.find_elements(By.XPATH, "//div[@class='sku-property']")
            # print('------------------------------------------\n' + title + '/' + link)
            writer.writerow({'item' : title, 'item_link' : link})
            #Scrapes property titles and writes to csv
            for prop in sku_properties:
                sku_title = prop.find_element(By.XPATH, './/div[@class="sku-title"]').get_attribute('textContent')
                sku_title_child = prop.find_element(By.XPATH, ".//span[@class='sku-title-value']").get_attribute('textContent')
                sku_title = sku_title.replace(': ' + sku_title_child, '')
                prop_items = prop.find_elements(By.XPATH, ".//li[contains(@class, 'sku-property-item') and not(contains(@class, 'disabled'))]")
                # print('++++++++++\n' + sku_title)
                writer.writerow({'sku_title' : sku_title})
                #Scrapes all property options and writes to csv, along with the price and link to option image.
                for prop_item in prop_items:
                    prop_item.click()
                    img = driver.find_element(By.XPATH, "//img[@class='magnifier-image']").get_attribute('src')
                    prop_item_title = prop.find_element(By.XPATH, ".//span[@class='sku-title-value']").get_attribute('innerHTML')
                    try:
                        price = driver.find_element(By.XPATH, "//span[@class='uniform-banner-box-price']").get_attribute('innerHTML')
                    except NoSuchElementException:
                        price = driver.find_element(By.XPATH, "//span[@class='product-price-value']").get_attribute('innerHTML')
                    # print('/' + prop_item_title + '/' + price + '/' + img)
                    writer.writerow({'prop_name' : prop_item_title, 'price' : price, 'img_link' : img})

                # print('++++++++++')
            # print('------------------------------------------')
            counter += 1
            if counter == limit:
                break
        except NoSuchElementException:
            pass