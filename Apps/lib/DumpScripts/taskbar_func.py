import webbrowser

def get_top_cantonese_restaurants():
    """
    Returns a list of top 10 Cantonese restaurants in NYC with their websites.
    
    Returns:
        list: List of dictionaries containing restaurant information
              Each dictionary has 'name' and 'website' keys
    """
    restaurants = [
        {
            "name": "Jing Fong",
            "website": "www.jingfong.com"
        },
        {
            "name": "Hop Lee Restaurant",
            "website": "No website available"
        },
        {
            "name": "Great NY Noodletown",
            "website": "No website available"
        },
        {
            "name": "Wo Hop",
            "website": "www.wohopnyc.com"
        },
        {
            "name": "Ping's Seafood",
            "website": "No website available"
        },
        {
            "name": "Oriental Garden",
            "website": "No website available"
        },
        {
            "name": "Hwa Yuan",
            "website": "www.hwayuannyc.com"
        },
        {
            "name": "August Gatherings",
            "website": "www.augustgatherings.com"
        },
        {
            "name": "Congee Village",
            "website": "www.congeevillagerestaurants.com"
        },
        {
            "name": "88 Palace",
            "website": "No website available"
        }
    ]
    return restaurants

def display_restaurants():
    """
    Prints formatted list of top Cantonese restaurants and their websites.
    """
    restaurants = get_top_cantonese_restaurants()
    print("\nTop 10 Cantonese Restaurants in NYC:")
    print("-" * 50)
    for i, restaurant in enumerate(restaurants, 1):
        print("{0}. {1:<20} - {2}".format(
            i, 
            restaurant['name'], 
            restaurant['website']
        ))

def open_restaurant_websites():
    """
    Opens available restaurant websites in the default web browser.
    Skips restaurants with no website.
    """
    restaurants = get_top_cantonese_restaurants()
    for restaurant in restaurants:
        if restaurant['website'].lower() != 'no website available':
            website = 'https://' + restaurant['website']
            print("Opening:", restaurant['name'])
            webbrowser.open(website)

if __name__ == "__main__":
    display_restaurants()
    print("\nOpening available websites...")
    open_restaurant_websites()
