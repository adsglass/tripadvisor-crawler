from scrapy.selector import Selector
import requests
import pickle
import argparse

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help="pass in URL of hotel to scrape")
    args = parser.parse_args()

    return args

def start_scraper(url):
    return collect_reviews(url)

def collect_reviews(url, all_hotels={}, nearby_hotel_urls=[]):
    
    all_hotels.update(parse_reviews(url))
    
    print("saving...")
    
    save_reviews(all_hotels)
    
    if nearby_hotel_urls:
        print("continue to next URL")
        
    else:
        nearby_hotel_urls = get_nearby_businesses(url)
    
    print("scraping nearby hotels")
    print(f"scraping {nearby_hotel_urls[-1]}...")
    url = f'https://www.tripadvisor.co.uk{nearby_hotel_urls[-1]}'
    nearby_hotel_urls.pop()
    print("URLs left to scrape: ", len(nearby_hotel_urls))
    
    if nearby_hotel_urls:
        return collect_reviews(url, all_hotels=all_hotels, nearby_hotel_urls=nearby_hotel_urls)
    
    else:
        print("terminating the scraper...")
        return all_hotels

def parse_reviews(url, acc=[]):
    
    if acc!=[]:
        final_output = acc
    else:
        final_output = []
        
    response = requests.get(url)
    
    d = Selector(response)
    
    content_card = d.xpath("//div[starts-with(@class, 'ui_card hotels-hotel-review-community-content-Card')]")
    
    ind_reviews = content_card.xpath(
        "div[starts-with(@class,'hotels-hotel-review-community-content-review-list-parts-SingleReview__reviewContainer')]")
    
    print("getting review IDs...")
    # get ids for each individual reviews
    review_ids = ind_reviews.xpath("@data-reviewid").extract()
    
    print("starting individual review scrape...")
    final_output.extend(parse_individual_reviews(review_ids, ind_reviews))
    
    try:
        print("moving onto next page...")
        next_page = ind_reviews.xpath("//a[contains(text(), 'Next')]/@href").extract()[0]
        url = f'https://www.tripadvisor.co.uk{next_page}'
        return parse_reviews(url, acc=final_output)
    
    except:
        print("end of pages to scrape")
    
    meta_info = get_hotel_meta_info(d)
    
    all_hotels = {}
    
    all_hotels[str("".join(ind_reviews.xpath("//h1[@id='HEADING']/text()").extract()[0]))] = [final_output, meta_info]
    
    return all_hotels

def save_reviews(all_hotels):
    
    with open('tripadvisor_reviews.pickle', 'wb') as f:
        pickle.dump(all_hotels, f, protocol=pickle.HIGHEST_PROTOCOL)

def get_hotel_meta_info(d):
    
    meta_dict = {}
    
    try:
        meta_dict["amenities"] = d.xpath("//div[starts-with(@class,'hotels-hotel-review-about-with-photos-layout-Group__group')]//text()").extract()
    except:
        meta_dict["amenities"] = "error"
        
    try:
        meta_dict["location"] = d.xpath("//div[starts-with(@class,'hotels-hotel-review-location-layout-LocationColumn__')]//text()").extract()
    except:
        meta_dict["location"] = "error"
    
    return meta_dict

def parse_individual_reviews(review_ids, ind_reviews):
    
    review_list = []
    print("starting page parse...")
    
    for i in review_ids:
        output = {}
        
        review = ind_reviews.xpath(f"//div[@data-reviewid='{i}']")
        
        full_review_link = review.xpath(
            "div//a[starts-with(@class, 'hotels-hotel-review-community-content-review-list-parts')]/@href")[0].extract()
        
        try:
            output["hotel_name"] = str("".join(ind_reviews.xpath("//h1[@id='HEADING']/text()").extract()[0]))
        except:
            output["hotel_name"] = "error"
        
        
        try:
            output["user_name"] = review.xpath("div//a[starts-with(@class,'ui_header_link social-member-MemberEventOnObjectBlock__member')]/text()").extract()[0]
        except:
            output["user_name"] = "error"
        
        try:
            output["profile_link"] = review.xpath(
            "div//a[starts-with(@class, 'ui_header_link social-member-MemberEventOnObject')]/@href").extract()[0]
        except:
            output["profile_link"] = "error"

        
        try:
            output["ratings"] = review.xpath(
                "div//div[starts-with(@class, 'hotels-hotel-review-community-content-review-list-parts-RatingLine__bubbles')]/span/@class")[0].extract()
        except:
            output["ratings"] = "error"
            
        try:
            output["title"] =  review.xpath("div//a[starts-with(@class, 'hotels-hotel-review-community-content-review-list-parts-ReviewTitle__reviewTitleText')]/span/span/text()")[0].extract()
        except:
            output["title"] = "error"
        
        try:
            output["hometown"] = review.xpath("div//span[starts-with(@class, 'default social-member-MemberHometown__hometown')]/text()").extract()[0]
        except:
            output["hometown"] = "error"
        
        try:
            output["date_of_stay"] = review.xpath("div//div[starts-with(@class,'hotels-review-list-parts-EventDate__event_date')]/span/text()").extract()[0].strip()
        except:
            output["date_of_stay"] = "error"
            
        try:
            output["date_of_review"] = review.xpath("div//div[starts-with(@class,'social-member-MemberEventOnObjectBlock__event_type')]/span/text()").extract()[0].strip()
        except:
            output["date_of_review"] = "error"
            
        try:
            output["helpful_votes"] = review.xpath("div//span[starts-with(@class,'social-member-MemberHeaderStats__stat_item')]/span[text()=' helpful votes']/span/text()").extract()[0]
        except:
            output["helpful_votes"] = "error"

            
        try:
            output["helpful_votes"] = review.xpath("div//span[starts-with(@class,'social-member-MemberHeaderStats__stat_item')]/span[text()=' helpful votes']/span/text()").extract()[0]
        except:
            output["helpful_votes"] = "error"
        
        try:
            output["contributions"] = review.xpath("div//span[starts-with(@class,'social-member-MemberHeaderStats__stat_item')]/span[text()=' contributions']/span/text()").extract()[0]
        except:
            output["contributions"] = "error"
        
        output.update(parse_inner_review(full_review_link))
        
        review_list.append(output)
        
    print("page completed!")
        
    return review_list
    

def parse_inner_review(full_review_link):
    
    inner_url = f'https://www.tripadvisor.co.uk/{full_review_link}'
    
    response = requests.get(inner_url)
    
    d = Selector(response)
    
    inner_review_dict = {}
    try:
        inner_review_dict["full_review_text"] = d.xpath("//span[@class='fullText ']/text()").extract()
    except:
        inner_review_dict["full_review_text"] = "error"
    
    try:
        inner_review_dict["trip_type"] = d.xpath("//div[starts-with(@class,'recommend')]/text()").extract()[0].strip()
    except:
        inner_review_dict["trip_type"] = "error"
    
    return inner_review_dict
    

def get_nearby_businesses(url):
    
    print("getting nearby hotels to scrape")
    
    response = requests.get(url)
    
    d = Selector(response)
    
    nearby = d.xpath("//a[starts-with(@class,'hotels-hotel-review-location-NearbyLink__seeNearby')]/@href").extract()
    nearby_hotel = "".join([item for item in nearby if "HotelsNear" in item])
    url = "https://www.tripadvisor.co.uk" + nearby_hotel
    
    response = requests.get(url)
    
    d = Selector(response)
    
    print("getting first set of listings...")
    page_listings = d.xpath("//div[@class='listing_title']/a/@href").extract()
    
    next_page = d.xpath("//a[contains(text(), 'Next')]/@href").extract()[0]
    
    
    while next_page:
        
        print("moving to next page...")
        url = "https://www.tripadvisor.co.uk" + next_page
        response = requests.get(url)
        d = Selector(response)
        
        print("getting more listings...")
        try:
            page_listings.extend(d.xpath("//div[@class='listing_title']/a/@href").extract())
        except:
            pass
        
        print("checking for next page...")
        try:
            print("next page found")
            next_page = d.xpath("//a[contains(text(), 'Next')]/@href").extract()[0]
        except:
            print("no more pages. Ending scrape.")
            next_page = False
            
    
    return list(set(page_listings))

if __name__ == "__main__":
    args = _parse_args()
    start_scraper(args.url)