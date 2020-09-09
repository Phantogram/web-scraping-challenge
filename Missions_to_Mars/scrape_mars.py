import pymongo
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import os
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from webdriver_manager.chrome import ChromeDriverManager
import time


def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)


####################################
########## NASA Mars News ##########
####################################

def nasa_news(browser):
    browser = init_browser()

    # Visit url in browser
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    time.sleep(1)
    
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')


    # Create variables for news title and paragraph text.
    # Assign the text to the variables for reference later.

    # Locate the title
    li_slide = soup.find('li', class_="slide" )

    # Get the news title 
    news_title = li_slide.find('div', class_='content_title').get_text()

    # Get the paragraph text
    news_p = li_slide.find('div', class_='article_teaser_body').get_text()

    # Return results
    return news_title, news_p


#############################################
########## JPL Mars Featured Image ##########
#############################################

def jpl_image(browser):
    browser = init_browser()

    # Visit url in browser
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Direct browser to click 'FULL IMAGE'
    browser.click_link_by_partial_text('FULL IMAGE')

    # Direct browser to click 'more info'
    browser.click_link_by_partial_text('more info')

    # Scrape page into Soup
    jpl_html = browser.html
    soup = bs(jpl_html, 'html.parser')


    # Assign the url string to a featured image variable
    image_url = soup.find('figure', class_='lede').a['href']

    featured_image_url = f'https://www.jpl.nasa.gov{image_url}'

    # Return results
    return featured_image_url


###############################
######### Mars Facts ##########
###############################

def mars_facts():
    browser = init_browser()

    # Assign the url string to mars facts 
    url = "https://space-facts.com/mars/"
    browser.visit(url)

    # Use Pandas to scrape the table containing facts about Mars
    tables = pd.read_html(url)

    # Slice off the dataframe using normal indexing
    mars_profile = tables[0]
    mars_profile.columns = ['Description', 'Mars']
    
    # Set the index to the 'Description' column
    mars_profile.set_index("Description", inplace=True)
    
    mars_html_table = mars_profile.to_html(classes="table table-striped")
    
    # Generate html table from DataFrame
    # Return results
    return mars_html_table



######################################
########## Mars Hemispheres ##########
######################################

def hemi_images(browser):
    browser = init_browser()

    # Obtain high resolution images for each of Mar's hemispheres
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Find hemisphere names and image urls
    hemisphere_names = browser.find_by_css('a.product-item h3')
    hemisphere_names

    hemisphere_image_urls = []

    for i in range(len(hemisphere_names)):
        hemi={}
        hemisphere_names = browser.find_by_css('a.product-item h3')[i].click()
        sample = browser.links.find_by_partial_text('Sample').first['href']
        title = browser.find_by_css('h2.title').text

        # Append to hemi then append to hemi urls
        hemi["title"] = title
        hemi["img_url"] = sample
        browser.back()
        hemisphere_image_urls.append(hemi)

    # Return results
    return hemisphere_image_urls


################################
########## SCRAPE ALL ##########
################################

def scrape_all():
    executable_path = {"executable_path": ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=False)
    news_title, news_p = nasa_news(browser)
    featured_image_url = jpl_image(browser)
    mars_html_table = mars_facts()
    hemisphere_image_urls = hemi_images(browser)

    mars = {
        "news_title": news_title,
        "news_p": news_p,
        "mars_html_table": mars_html_table,
        "featured_image_url": featured_image_url,
        "hemisphere_image_urls": hemisphere_image_urls,
    }

    browser.quit()
    return mars