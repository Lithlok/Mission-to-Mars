# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser)
        }
    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the Mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the Browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')

        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the paragraph text
        news_title = slide_elem.find('div', class_= 'content_title').get_text()
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p

# JPL Space Images Featured Image

def featured_image(browser):
    # Visit URL
    # url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        #img_url_rel = img_soup.select_one('').get('src')
    
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

# Mars Facts
def mars_facts():
    
    try:
        df = pd.read_html('https://space-facts.com/mars/')[0]
    except BaseException:
        return None

    df.columns=['Description', 'value']
    df.set_index('Description', inplace=True)

    return df.to_html(classes="table table-striped")
    #return mars_facts

# Hemispheres
def hemispheres(browser):

    url = 'https://marshemispheres.com/'
    browser.visit(url)
# List to hold the images and titles.
    hemisphere_image_urls = []

# Retrieve the image urls and titles for each hemisphere.
    for i in range(4):
    # create hemispheres dictionary
        hemispheres = {}
        browser.find_by_css('a.product-item h3')[i].click()
        element = browser.find_link_by_text('Sample').first
        img_url = element['href']
        title = browser.find_by_css("h2.title").text
        hemispheres["img_url"] = img_url
        hemispheres["title"] = title
        # hemisphere_data = scrape_hemisphere(browser.html)
        hemisphere_image_urls.append(hemispheres)
        browser.back()
    return hemisphere_image_urls

# Scrape
def scrape_hemisphere(html_text):
    hemi_soup = soup(html_text, "html.parser")
    # Try/ Except
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")
    except AttributeError:
        title_elem = None
        sample_elem = None
    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }
    return hemispheres

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())