import time
import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from secrets import secrets

# --| USER CONFIG |--------------------------
METRIC = False  # set to True for metric units
# -------------------------------------------

# ----------------------------
# Define various assets
# ----------------------------
BACKGROUND_BMP = "/bmps/weather_bg.bmp"
ICONS_LARGE_FILE = "/bmps/weather_icons_70px.bmp"
ICONS_SMALL_FILE = "/bmps/weather_icons_20px.bmp"
ICON_MAP = ("01", "02", "03", "04", "09", "10", "11", "13", "50")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
magtag = MagTag()

# ----------------------------
# Backgrounnd bitmap
# ----------------------------
magtag.graphics.set_background(BACKGROUND_BMP)

# ----------------------------
# Weather icons sprite sheet
# ----------------------------
icons_large_bmp, icons_large_pal = adafruit_imageload.load(ICONS_LARGE_FILE)
icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)

# /////////////////////////////////////////////////////////////////////////


def get_data_source_url(api="onecall", location=None):
    """Build and return the URL for the OpenWeather API."""
    if api.upper() == "FORECAST5":
        URL = "https://api.openweathermap.org/data/2.5/forecast?"
        URL += "q=" + location
    elif api.upper() == "ONECALL":
        URL = "https://api.openweathermap.org/data/2.5/onecall?exclude=minutely,hourly,alerts"
        URL += "&lat={}".format(location[0])
        URL += "&lon={}".format(location[1])
    else:
        raise ValueError("Unknown API type: " + api)

    return URL + "&appid=" + secrets["openweather_token"]


def get_latlon():
    """Use the Forecast5 API to determine lat/lon for given city."""
    magtag.url = get_data_source_url(api="forecast5", location=secrets["openweather_location"])
    magtag.json_path = ["city"]
    raw_data = magtag.fetch()
    return raw_data["coord"]["lat"], raw_data["coord"]["lon"]


def get_forecast(location):
    """Use OneCall API to fetch forecast and timezone data."""
    resp = magtag.network.fetch(get_data_source_url(api="onecall", location=location))
    json_data = resp.json()
    return json_data["daily"], json_data["current"]["dt"], json_data["timezone_offset"]


def make_banner(x=0, y=0):
    """Make a single future forecast info banner group."""
    day_of_week = label.Label(terminalio.FONT, text="DAY", color=0x000000)
    day_of_week.anchor_point = (0, 0.5)
    day_of_week.anchored_position = (0, 10)

    icon = displayio.TileGrid(
        icons_small_bmp,
        pixel_shader=icons_small_pal,
        x=25,
        y=0,
        width=1,
        height=1,
        tile_width=20,
        tile_height=20,
    )

    day_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
    day_temp.anchor_point = (0, 0.5)
    day_temp.anchored_position = (50, 10)

    group = displayio.Group(max_size=3, x=x, y=y)
    group.append(day_of_week)
    group.append(icon)
    group.append(day_temp)

    return group


def temperature_text(tempK):
    if METRIC:
        return "{:3.0f}C".format(tempK - 273.15)
    else:
        return "{:3.0f}F".format(32.0 + 1.8 * (tempK - 273.15))


def wind_text(speedms):
    if METRIC:
        return "{:3.0f}m/s".format(speedms)
    else:
        return "{:3.0f}mph".format(2.23694 * speedms)


def update_banner(banner, data):
    """Update supplied forecast banner with supplied data."""
    banner[0].text = DAYS[time.localtime(data["dt"]).tm_wday][:3].upper()
    banner[1][0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    banner[2].text = temperature_text(data["temp"]["day"])

def update_today(data, tz_offset=0):
    """Update today info banner."""
    date = time.localtime(data["dt"])
    sunrise = time.localtime(data["sunrise"] + tz_offset)
    sunset = time.localtime(data["sunset"] + tz_offset)

    today_date.text = "{} {} {}, {}".format(
        DAYS[date.tm_wday].upper(),
        MONTHS[date.tm_mon - 1].upper(),
        date.tm_mday,
        date.tm_year,
    )
    today_icon[0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    today_morn_temp.text = temperature_text(data["temp"]["morn"])
    today_day_temp.text = temperature_text(data["temp"]["day"])
    today_night_temp.text = temperature_text(data["temp"]["night"])
    today_humidity.text = "{:3d}%".format(data["humidity"])
    today_wind.text = wind_text(data["wind_speed"])
    today_sunrise.text = "{:2d}:{:02d} AM".format(sunrise.tm_hour, sunrise.tm_min)
    today_sunset.text = "{:2d}:{:02d} PM".format(sunset.tm_hour - 12, sunset.tm_min)

    month_ = date.tm_mon
    day_ = date.tm_mday
    city_name.text = {
        (1,1): "Bloody Mary Day",
        (1,2): "Cream Puff Day",
        (1,3): "Chocolate Covered Cherry Day",
        (1,4): "Spaghetti Day",
        (1,5): "Whipped Cream Day",
        (1,6): "Shortbread Day",
        (1,7): "Tempura Day",
        (1,8): "English Toffee Day",
        (1,9): "Apricot Day",
        (1,10): "Bittersweet Chocolate Day",
        (1,11): "Hot Toddy Day",
        (1,12): "Marzipan Day",
        (1,13): "Peach Melba Day",
        (1,14): "Hot Pastrami Sandwich Day",
        (1,15): "Fresh Squeezed Juice Day",
        (1,16): "Fig Newton Day",
        (1,17): "Hot Buttered Rum Day",
        (1,18): "Peking Duck Day",
        (1,19): "Popcorn Day",
        (1,20): "Buttercrunch Day",
        (1,21): "Granola Bar Day",
        (1,22): "Blonde Brownie Day",
        (1,23): "Rhubarb Pie Day",
        (1,24): "Peanut Butter Day",
        (1,25): "Irish Coffee Day",
        (1,26): "Peanut Brittle Day",
        (1,27): "Chocolate Cake Day",
        (1,28): "Blueberry Pancake Day",
        (1,29): "Corn Chip Day",
        (1,30): "Croissant Day",
        (1,31): "Brandy Alexander Day",
        (2,1): "Baked Alaska Day",
        (2,2): "Heavenly Hash Day",
        (2,3): "Carrot Cake Day",
        (2,4): "Homemade Soup Day",
        (2,5): "Chocolate Fondue Day",
        (2,6): "Frozen Yogurt Day",
        (2,7): "Fettucine Alfredo Day",
        (2,8): "Molasses Bar Day",
        (2,9): "Bagels and Lox Day",
        (2,10): "Cream Cheese Brownie Day",
        (2,11): "Peppermint Patty Day",
        (2,12): "Plum Pudding Day",
        (2,13): "Tortini Day",
        (2,14): "Cream Filled Chocolates Day",
        (2,15): "InterGumdrop Day",
        (2,16): "Almond Day",
        (2,17): "Cafe Au Lait Day",
        (2,18): "Crab Stuffed Flounder Day",
        (2,19): "Chocolate Mint Day",
        (2,20): "Cherry Pie Day",
        (2,21): "Sticky Bun Day",
        (2,22): "Margarita Day",
        (2,23): "Banana Bread Day",
        (2,24): "Tortilla Chip Day",
        (2,25): "Chocolate Covered Peanuts Day",
        (2,26): "Pistachio Day",
        (2,27): "Kahlua Day",
        (2,28): "Chocolate Souffle Day",
        (2,29): "Surf and Turf Day",
        (3,1): "Peanut Butter Lover’s Day",
        (3,2): "Banana Cream Pie Day",
        (3,3): "Mulled Wine Day",
        (3,4): "Pound Cake Day",
        (3,5): "Cheese Doodle Day",
        (3,6): "Frozen Food Day",
        (3,7): "Crown Roast of Pork Day",
        (3,8): "Peanut Cluster Day",
        (3,9): "Crabmeat Day",
        (3,10): "Blueberry Popover Day",
        (3,11): "Oatmeal-Nut Waffle Day",
        (3,12): "Baked Scallops Day",
        (3,13): "Coconut Torte Day",
        (3,14): "Potato Chip Day",
        (3,15): "Pears Helene Day",
        (3,16): "Artichoke Hearts Day",
        (3,17): "Green Beer Day",
        (3,18): "Lacy Oatmeal Cookie Day",
        (3,19): "Chocolate Carmel Day",
        (3,20): "Ravioli Day",
        (3,21): "French Bread Day",
        (3,22): "Bavarian Crepes Day",
        (3,23): "Chip and Dip Day",
        (3,24): "Chocolate Covered Raisins Day",
        (3,25): "Lobster Newburg Day",
        (3,26): "Nougat Day",
        (3,27): "Spanish Paella Day",
        (3,28): "Black Forest Cake Day",
        (3,29): "Lemon Chiffon Cake Day",
        (3,30): "Turkey Neck Soup Day",
        (3,31): "Clams on the Half Shell Day",
        (4,1): "Sourdough Bread Day",
        (4,2): "Peanut Butter & Jelly Day",
        (4,3): "Chocolate Moose Day",
        (4,4): "Chocolate Milk Powder Day",
        (4,5): "Caramel Day",
        (4,6): "Fresh Tomato Day",
        (4,7): "Coffee Cake Day",
        (4,8): "Empanada Day",
        (4,9): "Chinese Almond Cookie Day",
        (4,10): "Cinnamon Crescent Day",
        (4,11): "Cheese Fondue Day",
        (4,12): "Grilled Cheese Sandwich Day",
        (4,13): "Peach Cobbler Day",
        (4,14): "Pecan Day",
        (4,15): "Glazed Spiral Ham Day",
        (4,16): "Eggs Benedict Day",
        (4,17): "Cheese Ball Day",
        (4,18): "Animal Cracker Day",
        (4,19): "Garlic Day Day",
        (4,20): "Pineapple Upside-Down Cake Day",
        (4,21): "Chocolate-Covered Cashew Day",
        (4,22): "Jelly Bean Day",
        (4,23): "Picnic Day",
        (4,24): "Pigs-in-a-Blanket Day",
        (4,25): "Zucchini Bread Day",
        (4,26): "Pretzel Day",
        (4,27): "Prime Rib Day",
        (4,28): "Blueberry Pie Day",
        (4,29): "Shrimp Scampi Day",
        (4,30): "Oatmeal Cookie Day",
        (5,1): "Chocolate Parfait Day",
        (5,2): "Truffles Day",
        (5,3): "Raspberry Tart Day",
        (5,4): "Candied Orange Peel Day",
        (5,5): "Chocolate Custard Day",
        (5,6): "Crepes Suzette Day",
        (5,7): "Roast Leg of Lamb Day",
        (5,8): "Coconut Cream Pie Day",
        (5,9): "Butterscotch Brownie Day",
        (5,10): "Shrimp Day",
        (5,11): "Mocha Torte Day",
        (5,11): "Eat What You Want Day",
        (5,12): "Nutty Fudge Day",
        (5,13): "Fruit Cocktail Day",
        (5,14): "Buttermilk Biscuit Day",
        (5,15): "Chocolate Chip Day",
        (5,16): "Coquilles St. Jacques Day",
        (5,17): "Cherry Cobbler Day",
        (5,18): "Cheese Soufflé Day",
        (5,19): "Devil’s Food Cake Day",
        (5,20): "Quiche Lorraine Day",
        (5,21): "Strawberries & Cream Day",
        (5,22): "Vanilla Pudding Day",
        (5,23): "Taffy Day",
        (5,24): "Escargot Day",
        (5,25): "Wine Day",
        (5,26): "Cherry Dessert Day",
        (5,27): "Grape Popsicle Day",
        (5,28): "Brisket Day",
        (5,29): "Coq Au Vin Day",
        (5,30): "Macaroon Day",
        (6,1): "Hazelnut Cake Day",
        (6,2): "Rocky Road Day",
        (6,3): "Chocolate Macaroon Day",
        (6,4): "Frozen Yogurt Day",
        (6,5): "Gingerbread Day",
        (6,6): "Applesauce Cake Day",
        (6,7): "Chocolate Ice Cream Day",
        (6,8): "Jelly-filled Doughnut Day",
        (6,9): "Strawberry Rhubarb Pie Day",
        (6,10): "Black Cow Day",
        (6,11): "German Chocolate Day",
        (6,12): "Peanut Butter Cookie Day",
        (6,13): "Lobster Day",
        (6,14): "Strawberry Shortcake Day",
        (6,15): "Kitchen Klutzes of America Day",
        (6,16): "Fudge Day",
        (6,17): "Apple Streudel Day",
        (6,18): "Cherry Tart Day",
        (6,19): "Martini Day",
        (6,20): "Vanilla Milkshake Day",
        (6,21): "Peaches & Cream Day",
        (6,22): "Chocolate Eclair Day",
        (6,23): "Pecan Sandy Day",
        (6,24): "Creamy Pralines Day",
        (6,25): "Strawberry Parfait Day",
        (6,26): "Chocolate Pudding Day",
        (6,27): "Orange Blossom Day",
        (6,28): "Tapioca Day",
        (6,29): "Almond Butter Crunch Day",
        (6,30): "Mai Tai Day",
        (7,1): "Creative Ice Cream Flavor Day",
        (7,2): "Anisette Day",
        (7,3): "Eat Beans Day",
        (7,4): "Barbecued Spareribs Day",
        (7,5): "Graham Cracker Day",
        (7,6): "Fried Chicken Day",
        (7,7): "Strawberry Sundae Day",
        (7,8): "Milk Chocolate with Almonds Day",
        (7,9): "Sugar Cookie Day",
        (7,10): "Pina Colada Day",
        (7,11): "Blueberry Muffin Day",
        (7,12): "Eat Your Jello Day",
        (7,13): "French Fries Day",
        (7,14): "Grand Marnier Day",
        (7,15): "Tapioca Pudding Day",
        (7,16): "Fresh Spinach Day",
        (7,17): "Peach Ice Cream Day",
        (7,18): "Caviar Day",
        (7,19): "Daiquiri Day",
        (7,20): "Lollipop Day",
        (7,21): "Creme Brulee Day",
        (7,22): "PMaple Syrup Day",
        (7,23): "Hot Dog Day",
        (7,24): "Tequila Day",
        (7,25): "Hot Fudge Sundae Day",
        (7,26): "Coffee Milkshake Day",
        (7,27): "Scotch Day",
        (7,28): "Milk Chocolate Day",
        (7,29): "Lasagna Day",
        (7,30): "Cheesecake Day",
        (7,31): "Jump for Jelly Beans Day",
        (8,1): "Raspberry Cream Pie Day",
        (8,2): "Ice Cream Sandwich Day",
        (8,3): "Watermelon Day",
        (8,4): "Chocolate Chip Day",
        (8,5): "Chile Pepper Day",
        (8,6): "Root Beer Float Day",
        (8,7): "Raspberries & Cream Day",
        (8,8): "Frozen Custard Day",
        (8,9): "Rice Pudding Day",
        (8,10): "S’mores Day",
        (8,11): "Raspberry Bombe Day",
        (8,12): "Toasted Almond Bar Day",
        (8,13): "Filet Mignon Day",
        (8,14): "Creamsicle Day",
        (8,15): "Lemon Meringue Pie Day",
        (8,16): "Rum Day",
        (8,17): "Vanilla Custard Day",
        (8,18): "Ice Cream Pie Day",
        (8,19): "Soft Ice Cream Day",
        (8,20): "Lemonade Day",
        (8,21): "Spumoni Day",
        (8,22): "Pecan Torte Day",
        (8,23): "Spongecake Day",
        (8,24): "Peach Pie Day",
        (8,25): "Waffle Day",
        (8,26): "Cherry Popsicle Day",
        (8,27): "Banana Lover’s Day",
        (8,28): "Cherry Turnover Day",
        (8,29): "More Herbs Less Salt Day",
        (8,29): "Lemon Juice Day",
        (8,30): "Marshmallow Toasting Day",
        (8,31): "Trail Mix Day",
        (9,1): "Cherry Popover Day",
        (9,2): "Blueberry Popsicle Day",
        (9,3): "Welsh Rabbit Day",
        (9,4): "Macadamia Nut Day",
        (9,5): "Cheese Pizza Day",
        (9,6): "Coffee Ice Cream Day",
        (9,7): "Napoleon Day",
        (9,8): "Date-Nut Bread Day",
        (9,9): "Steak au Poivre Day",
        (9,10): "Oatmeal Day",
        (9,11): "Hot Cross Bun Day",
        (9,12): "Chocolate Milkshake Day",
        (9,13): "Peanut Day",
        (9,14): "Cream-Filled Donut Day",
        (9,15): "Creme de Menthe Day",
        (9,16): "Homemade Bread Day",
        (9,17): "Apple Dumpling Day",
        (9,18): "Eat A Cranberry Day",
        (9,19): "Butterscotch Pudding Day",
        (9,20): "Rum Punch Day",
        (9,21): "Pecan Cookie Day",
        (9,22): "White Chocolate Day",
        (9,23): "Chocolate Day",
        (9,24): "Cherries Jubilee Day",
        (9,25): "Crab Newberg Day",
        (9,26): "Pancake Day",
        (9,27): "Chocolate Milk Day",
        (9,28): "Strawberry Cream Pie Day",
        (9,29): "Mocha Day",
        (9,30): "Mulled Cider Day",
        (10,1): "World Vegetarian Day",
        (10,2): "French Fried Scallops Day",
        (10,3): "Caramel Custard Day",
        (10,4): "Taco Day",
        (10,5): "Apple Betty Day",
        (10,6): "Noodle Day",
        (10,7): "Frappe Day",
        (10,8): "Fluffernutter Day",
        (10,9): "Dessert Day",
        (10,10): "Angel Food Cake Day",
        (10,11): "Sausage Pizza Day",
        (10,13): "Yorkshire Pudding Day",
        (10,14): "Chocolate Covered Insect Day",
        (10,15): "Mushroom Day",
        (10,16): "Oatmeal Day",
        (10,17): "Pasta Day",
        (10,18): "Chocolate Cupcake Day",
        (10,19): "Seafood Bisque Day",
        (10,20): "Brandied Fruit Day",
        (10,21): "Pumpkin Cheesecake Day",
        (10,22): "Nut Day",
        (10,23): "Boston Cream Pie Day",
        (10,24): "Bologna Day",
        (10,25): "Greasy Foods Day",
        (10,26): "Mincemeat Pie Day",
        (10,27): "Potato Day",
        (10,28): "Chocolate Day",
        (10,29): "Pancake Day",
        (10,30): "Candy Corn Day",
        (10,31): "Caramel Apple Day",
        (11,1): "French Fried Clam Day",
        (11,2): "Deviled Egg Day",
        (11,3): "Sandwich Day",
        (11,4): "Candy Day",
        (11,5): "Doughnut Day",
        (11,6): "Nachos Day",
        (11,7): "Chocolate with Almonds Day",
        (11,8): "Harvey Wallbanger Day",
        (11,9): "Scrapple Day",
        (11,10): "Vanilla Cupcake Day",
        (11,11): "Sundae Day",
        (11,12): "Pizza with the Works Day",
        (11,13): "Indian Pudding Day",
        (11,14): "Guacamole Day",
        (11,15): "Clean Out Your Refrigerator Day",
        (11,16): "Fast Food Day",
        (11,17): "Baklava Day",
        (11,18): "Vichyssoise Day",
        (11,19): "Carbonated Bev Caffeine Day",
        (11,20): "Peanut Butter Fudge Day",
        (11,21): "Stuffing Day",
        (11,22): "Cranberry Relish Day",
        (11,23): "Cashew Day",
        (11,24): "Espresso Day",
        (11,25): "Parfait Day",
        (11,26): "Cake Day",
        (11,27): "Bavarian Cream Pie Day",
        (11,28): "French Toast Day",
        (11,29): "Chocolates Day",
        (11,30): "Mousse Day",
        (12,1): "Eat a Red Apple Day",
        (12,2): "Fritters Day",
        (12,3): "Ice Cream Box Day",
        (12,4): "Cookie Day",
        (12,5): "Sacher Torte Day",
        (12,6): "Gazpacho Day",
        (12,7): "Cotton Candy Day",
        (12,8): "Brownie Day",
        (12,9): "Apple Pie Day",
        (12,10): "Lager Day",
        (12,11): "Noodle-Ring Day",
        (12,12): "Ambrosia Day",
        (12,12): "Gingerbread House Day",
        (12,13): "Cocoa Day",
        (12,14): "Bouillabaisse Day",
        (12,15): "Lemon Cupcake Day",
        (12,16): "Chocolate Covered Anything Day",
        (12,17): "Maple Syrup Day",
        (12,18): "Roast Suckling Pig Day",
        (12,19): "Oatmeal Muffin Day",
        (12,20): "Fried Shrimp Day",
        (12,21): "Hamburger Day",
        (12,22): "Date Nut Bread Day",
        (12,23): "Pfeffernusse Day",
        (12,24): "Egg Nog Day",
        (12,25): "Pumpkin Pie Day",
        (12,26): "Candy Cane Day",
        (12,27): "Fruit Cake Day",
        (12,28): "Chocolate Candy Day",
        (12,29): "Pepper Pot Day",
        (12,30): "Bicarbonate Of Soda Day",
        (12,31): "Champagne Day"
    }[(month_,day_)]
#    city_name.text = str(month_) + "/" + str(day_)


def go_to_sleep(current_time):
    """Enter deep sleep for time needed."""
    # compute current time offset in seconds
    hour, minutes, seconds = time.localtime(current_time)[3:6]
    seconds_since_midnight = 60 * (hour * 60 + minutes) + seconds
    # wake up 15 minutes after midnite
    seconds_to_sleep = (24 * 60 * 60 - seconds_since_midnight) + 15 * 60
    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
    magtag.exit_and_deep_sleep(seconds_to_sleep)


# ===========
# U I
# ===========
today_date = label.Label(terminalio.FONT, text="?" * 30, color=0x000000)
today_date.anchor_point = (0, 0)
today_date.anchored_position = (15, 13)

city_name = label.Label(
    terminalio.FONT, text="?" * 30, color=0x000000
)
city_name.anchor_point = (0, 0)
city_name.anchored_position = (15, 24)

today_icon = displayio.TileGrid(
    icons_large_bmp,
    pixel_shader=icons_small_pal,
    x=10,
    y=40,
    width=1,
    height=1,
    tile_width=70,
    tile_height=70,
)

today_morn_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_morn_temp.anchor_point = (0.5, 0)
today_morn_temp.anchored_position = (118, 59)

today_day_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_day_temp.anchor_point = (0.5, 0)
today_day_temp.anchored_position = (149, 59)

today_night_temp = label.Label(terminalio.FONT, text="+100F", color=0x000000)
today_night_temp.anchor_point = (0.5, 0)
today_night_temp.anchored_position = (180, 59)

today_humidity = label.Label(terminalio.FONT, text="100%", color=0x000000)
today_humidity.anchor_point = (0, 0.5)
today_humidity.anchored_position = (105, 95)

today_wind = label.Label(terminalio.FONT, text="99m/s", color=0x000000)
today_wind.anchor_point = (0, 0.5)
today_wind.anchored_position = (155, 95)

today_sunrise = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
today_sunrise.anchor_point = (0, 0.5)
today_sunrise.anchored_position = (45, 117)

today_sunset = label.Label(terminalio.FONT, text="12:12 PM", color=0x000000)
today_sunset.anchor_point = (0, 0.5)
today_sunset.anchored_position = (130, 117)

today_banner = displayio.Group(max_size=10)
today_banner.append(today_date)
today_banner.append(city_name)
today_banner.append(today_icon)
today_banner.append(today_morn_temp)
today_banner.append(today_day_temp)
today_banner.append(today_night_temp)
today_banner.append(today_humidity)
today_banner.append(today_wind)
today_banner.append(today_sunrise)
today_banner.append(today_sunset)

future_banners = [
    make_banner(x=210, y=18),
    make_banner(x=210, y=39),
    make_banner(x=210, y=60),
    make_banner(x=210, y=81),
    make_banner(x=210, y=102),
]

magtag.splash.append(today_banner)
for future_banner in future_banners:
    magtag.splash.append(future_banner)

# ===========
#  M A I N
# ===========
print("Getting Lat/Lon...")
latlon = get_latlon()
print(secrets["openweather_location"])
print(latlon)

print("Fetching forecast...")
forecast_data, utc_time, local_tz_offset = get_forecast(latlon)

print("Updating...")
update_today(forecast_data[0], local_tz_offset)
for day, forecast in enumerate(forecast_data[1:6]):
    update_banner(future_banners[day], forecast)

print("Refreshing...")
time.sleep(magtag.display.time_to_refresh + 1)
magtag.display.refresh()
time.sleep(magtag.display.time_to_refresh + 1)

print("Sleeping...")
go_to_sleep(utc_time + local_tz_offset)
#  entire code will run again after deep sleep cycle
#  similar to hitting the reset button

