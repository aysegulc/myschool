
Myschool.edu.au Scraping Project
-------------------------

This scrapy project is created to scrape performance reports and contact details of primary and secondary schools in Australia. However, the project is now obsolete after a design overhaul.

Scraper creates search urls using Australian zipcodes that are provided in a csv file in resources folder. Spider parses the search results as a dictionary using json library and requests additional data using POST requests.

Scraped items can be saved as json files.


```bash
# save items to json file
scrapy crawl myschool -o myschool_data.json
```
