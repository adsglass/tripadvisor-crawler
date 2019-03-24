# Tripadvisor Crawler using XPath

A simple Python command line tool that scrapes all reviews / info from a given hotel URL and then proceeds to find all nearby hotels and scrapes reviews from those. The tool saves all reviews in a `Pickle` file as a nested dictionary.

I use Scrapy's XPath selectors to parse the HTML. 

## How to use

Simply run `python tripadvisor_crawler.py {url}` from the command line. You'll need to full URL.

## Dependencies

The tool was created in Python 3.6. Following packages are required:

```
Scrapy
Pickle
Argparse
```

## Next steps

Refactor and probably combine with Scrapy's in-built spider functionality.
