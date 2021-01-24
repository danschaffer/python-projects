#!/usr/bin/env python3
import argparse
import datetime
import sys

def food_of_day_interval(month=None, day=None, interval=1):
    now = datetime.datetime.now()
    year = now.year
    if not month:
        month = now.month
    if not day:
        day = now.day
    for counter in range(interval):
        date = datetime.datetime(year=year,month=month, day=day) + datetime.timedelta(days=counter)
        month0 = date.month
        day0 = date.day
        print(f"{date.strftime('%a')} {month0}/{day0} {food_of_day(month0, day0)}")

def food_of_day(month=None, day=None):
    if month is None or day is None:
        now = datetime.datetime.now()
        month = now.month
        day = now.day
    return {
        (1,1): "National Bloody Mary Day",
        (1,2): "National Cream Puff Day",
        (1,3): "National Chocolate Covered Cherry Day",
        (1,4): "National Spaghetti Day",
        (1,5): "National Whipped Cream Day",
        (1,6): "National Shortbread Day",
        (1,7): "National Tempura Day",
        (1,8): "National English Toffee Day",
        (1,9): "National Apricot Day",
        (1,10): "National Bittersweet Chocolate Day",
        (1,11): "National Hot Toddy Day",
        (1,12): "National Marzipan Day",
        (1,13): "National Peach Melba Day",
        (1,14): "National Hot Pastrami Sandwich Day",
        (1,15): "National Fresh Squeezed Juice Day",
        (1,16): "National Fig Newton Day",
        (1,17): "National Hot Buttered Rum Day",
        (1,18): "National Peking Duck Day",
        (1,19): "National Popcorn Day",
        (1,20): "National Buttercrunch Day",
        (1,21): "National Granola Bar Day",
        (1,22): "National Blonde Brownie Day",
        (1,23): "National Rhubarb Pie Day",
        (1,24): "National Peanut Butter Day",
        (1,25): "National Irish Coffee Day",
        (1,26): "National Peanut Brittle Day",
        (1,27): "National Chocolate Cake Day",
        (1,28): "National Blueberry Pancake Day",
        (1,29): "National Corn Chip Day",
        (1,30): "National Croissant Day",
        (1,31): "National Brandy Alexander Day",
        (2,1): "National Baked Alaska Day",
        (2,2): "National Heavenly Hash Day",
        (2,3): "National Carrot Cake Day",
        (2,4): "National Homemade Soup Day",
        (2,5): "National Chocolate Fondue Day",
        (2,6): "National Frozen Yogurt Day",
        (2,7): "National Fettucine Alfredo Day",
        (2,8): "National Molasses Bar Day",
        (2,9): "National Bagels and Lox Day",
        (2,10): "National Cream Cheese Brownie Day",
        (2,11): "National Peppermint Patty Day",
        (2,12): "National Plum Pudding Day",
        (2,13): "National Tortini Day",
        (2,14): "National Cream Filled Chocolates Day",
        (2,15): "National International Gumdrop Day",
        (2,16): "National Almond Day",
        (2,17): "National Cafe Au Lait Day",
        (2,18): "National Crab Stuffed Flounder Day",
        (2,19): "National Chocolate Mint Day",
        (2,20): "National Cherry Pie Day",
        (2,21): "National Sticky Bun Day",
        (2,22): "National Margarita Day",
        (2,23): "National Banana Bread Day",
        (2,24): "National Tortilla Chip Day",
        (2,25): "National Chocolate Covered Peanuts Day",
        (2,26): "National Pistachio Day",
        (2,27): "National Kahlua Day",
        (2,28): "National Chocolate Souffle Day",
        (2,29): "National Surf and Turf Day",
        (3,1): "National Peanut Butter Lover’s Day",
        (3,2): "National Banana Cream Pie Day",
        (3,3): "National Mulled Wine Day",
        (3,4): "National Pound Cake Day",
        (3,5): "National Cheese Doodle Day",
        (3,6): "National Frozen Food Day",
        (3,7): "National Crown Roast of Pork Day",
        (3,8): "National Peanut Cluster Day",
        (3,9): "National Crabmeat Day",
        (3,10): "National Blueberry Popover Day",
        (3,11): "National Oatmeal-Nut Waffle Day",
        (3,12): "National Baked Scallops Day",
        (3,13): "National Coconut Torte Day",
        (3,14): "National Potato Chip Day",
        (3,15): "National Pears Helene Day",
        (3,16): "National Artichoke Hearts Day",
        (3,17): "National Green Beer Day",
        (3,18): "National Lacy Oatmeal Cookie Day",
        (3,19): "National Chocolate Carmel Day",
        (3,20): "National Ravioli Day",
        (3,21): "National French Bread Day",
        (3,22): "National Bavarian Crepes Day",
        (3,23): "National Chip and Dip Day",
        (3,24): "National Chocolate Covered Raisins Day",
        (3,25): "National Lobster Newburg Day",
        (3,26): "National Nougat Day",
        (3,27): "National Spanish Paella Day",
        (3,28): "National Black Forest Cake Day",
        (3,29): "National Lemon Chiffon Cake Day",
        (3,30): "National Turkey Neck Soup Day",
        (3,31): "National Clams on the Half Shell Day",
        (4,1): "National Sourdough Bread Day",
        (4,2): "National Peanut Butter & Jelly Day",
        (4,3): "National Chocolate Moose Day",
        (4,4): "National Chocolate Milk Powder Day",
        (4,5): "National Caramel Day",
        (4,6): "National Fresh Tomato Day",
        (4,7): "National Coffee Cake Day",
        (4,8): "National Empanada Day",
        (4,9): "National National Chinese Almond Cookie Day",
        (4,10): "Cinnamon Crescent Day",
        (4,11): "National Cheese Fondue Day",
        (4,12): "Grilled Cheese Sandwich Day",
        (4,13): "National Peach Cobbler Day",
        (4,14): "National Pecan Day",
        (4,15): "Glazed Spiral Ham Day",
        (4,16): "National Eggs Benedict Day",
        (4,17): "National Cheese Ball Day",
        (4,18): "National Animal Cracker Day",
        (4,19): "National Garlic Day Day",
        (4,20): "National Pineapple Upside-Down Cake Day",
        (4,21): "Chocolate-Covered Cashew Truffle Day",
        (4,22): "Jelly Bean Day",
        (4,23): "National Picnic Day",
        (4,24): "Pigs-in-a-Blanket Day",
        (4,25): "National Zucchini Bread Day",
        (4,26): "National Pretzel Day",
        (4,27): "Prime Rib Day",
        (4,28): "National Blueberry Pie Day",
        (4,29): "National Shrimp Scampi Day",
        (4,30): "National Oatmeal Cookie Day",
        (5,1): "National Chocolate Parfait Day",
        (5,2): "National Truffles Day",
        (5,3): "National Raspberry Tart Day",
        (5,4): "National Candied Orange Peel Day",
        (5,5): "National Chocolate Custard Day",
        (5,6): "National Crepes Suzette Day",
        (5,7): "National Roast Leg of Lamb Day",
        (5,8): "National Coconut Cream Pie Day",
        (5,9): "National Butterscotch Brownie Day",
        (5,10): "National Shrimp Day",
        (5,11): "National Mocha Torte Day",
        (5,11): "Eat What You Want Day",
        (5,12): "National Nutty Fudge Day",
        (5,13): "National Fruit Cocktail Day",
        (5,14): "National Buttermilk Biscuit Day",
        (5,15): "National Chocolate Chip Day",
        (5,16): "National Coquilles St. Jacques Day",
        (5,17): "National Cherry Cobbler Day",
        (5,18): "National Cheese Soufflé Day",
        (5,19): "National Devil’s Food Cake Day",
        (5,20): "National Quiche Lorraine Day",
        (5,21): "National Strawberries & Cream Day",
        (5,22): "National Vanilla Pudding Day",
        (5,23): "National Taffy Day",
        (5,24): "National Escargot Day",
        (5,25): "National Wine Day",
        (5,26): "National Cherry Dessert Day",
        (5,27): "National Grape Popsicle Day",
        (5,28): "National Brisket Day",
        (5,29): "National Coq Au Vin Day",
        (5,30): "National Macaroon Day",
        (6,1): "National Hazelnut Cake Day",
        (6,2): "National Rocky Road Day",
        (6,3): "National Chocolate Macaroon Day",
        (6,4): "National Frozen Yogurt Day",
        (6,5): "National Gingerbread Day",
        (6,6): "National Applesauce Cake Day",
        (6,7): "National Chocolate Ice Cream Day",
        (6,8): "National Jelly-filled Doughnut Day",
        (6,9): "National Strawberry Rhubarb Pie Day",
        (6,10): "National Black Cow Day",
        (6,11): "National German Chocolate Day",
        (6,12): "National Peanut Butter Cookie Day",
        (6,13): "National Lobster Day",
        (6,14): "National Strawberry Shortcake Day",
        (6,15): "National Kitchen Klutzes of America Day",
        (6,16): "National Fudge Day",
        (6,17): "National Apple Streudel Day",
        (6,18): "National Cherry Tart Day",
        (6,19): "National Martini Day",
        (6,20): "National Vanilla Milkshake Day",
        (6,21): "National Peaches & Cream Day",
        (6,22): "National Chocolate Eclair Day",
        (6,23): "National Pecan Sandy Day",
        (6,24): "National Creamy Pralines Day",
        (6,25): "National Strawberry Parfait Day",
        (6,26): "National Chocolate Pudding Day",
        (6,27): "National Orange Blossom Day",
        (6,28): "National Tapioca Day",
        (6,29): "National Almond Butter Crunch Day",
        (6,30): "National Mai Tai Day",
        (7,1): "National Creative Ice Cream Flavor Day",
        (7,2): "National Anisette Day",
        (7,3): "National Eat Beans Day",
        (7,4): "National Barbecued Spareribs Day",
        (7,5): "National Graham Cracker Day",
        (7,6): "National Fried Chicken Day",
        (7,7): "National Strawberry Sundae Day",
        (7,8): "National Milk Chocolate with Almonds Day",
        (7,9): "National Sugar Cookie Day",
        (7,10): "National Pina Colada Day",
        (7,11): "National Blueberry Muffin Day",
        (7,12): "National Eat Your Jello Day",
        (7,13): "National French Fries Day",
        (7,14): "National Grand Marnier Day",
        (7,15): "National Tapioca Pudding Day",
        (7,16): "National Fresh Spinach Day",
        (7,17): "National Peach Ice Cream Day",
        (7,18): "National Caviar Day",
        (7,19): "National Daiquiri Day",
        (7,20): "National Lollipop Day",
        (7,21): "National Creme Brulee Day",
        (7,22): "National PMaple Syrup Day",
        (7,23): "National Hot Dog Day",
        (7,24): "National Tequila Day",
        (7,25): "National Hot Fudge Sundae Day",
        (7,26): "National Coffee Milkshake Day",
        (7,27): "National Scotch Day",
        (7,28): "National Milk Chocolate Day",
        (7,29): "National Lasagna Day",
        (7,30): "National Cheesecake Day",
        (7,31): "National Jump for Jelly Beans Day",
        (8,1): "National Raspberry Cream Pie Day",
        (8,2): "National Ice Cream Sandwich Day",
        (8,3): "National Watermelon Day",
        (8,4): "National Chocolate Chip Day",
        (8,5): "National Chile Pepper Day",
        (8,6): "National Root Beer Float Day",
        (8,7): "National Raspberries & Cream Day",
        (8,8): "National Frozen Custard Day",
        (8,9): "National Rice Pudding Day",
        (8,10): "National S’mores Day",
        (8,11): "National Raspberry Bombe Day",
        (8,12): "National Toasted Almond Bar Day",
        (8,13): "National Filet Mignon Day",
        (8,14): "National Creamsicle Day",
        (8,15): "National Lemon Meringue Pie Day",
        (8,16): "National Rum Day",
        (8,17): "National Vanilla Custard Day",
        (8,18): "National Ice Cream Pie Day",
        (8,19): "National Soft Ice Cream Day",
        (8,20): "National Lemonade Day",
        (8,21): "National Spumoni Day",
        (8,22): "National Pecan Torte Day",
        (8,23): "National Spongecake Day",
        (8,24): "National Peach Pie Day",
        (8,25): "National Waffle Day",
        (8,26): "National Cherry Popsicle Day",
        (8,27): "National Banana Lover’s Day",
        (8,28): "National Cherry Turnover Day",
        (8,29): "National More Herbs Less Salt Day",
        (8,29): "National Lemon Juice Day",
        (8,30): "National Marshmallow Toasting Day",
        (8,31): "National Trail Mix Day",
        (9,1): "National Cherry Popover Day",
        (9,2): "National Blueberry Popsicle Day",
        (9,3): "National Welsh Rabbit Day",
        (9,4): "National Macadamia Nut Day",
        (9,5): "National Cheese Pizza Day",
        (9,6): "National Coffee Ice Cream Day",
        (9,7): "National Napoleon Day",
        (9,8): "National Date-Nut Bread Day",
        (9,9): "National Steak au Poivre Day",
        (9,10): "National Oatmeal Day",
        (9,11): "National Hot Cross Bun Day",
        (9,12): "National Chocolate Milkshake Day",
        (9,13): "National Peanut Day",
        (9,14): "National Cream-Filled Donut Day",
        (9,15): "National Creme de Menthe Day",
        (9,16): "National Homemade Bread Day",
        (9,17): "National Apple Dumpling Day",
        (9,18): "National Eat A Cranberry Day",
        (9,19): "National Butterscotch Pudding Day",
        (9,20): "National Rum Punch Day",
        (9,21): "National Pecan Cookie Day",
        (9,22): "National White Chocolate Day",
        (9,23): "National Chocolate Day",
        (9,24): "National Cherries Jubilee Day",
        (9,25): "National Crab Newberg Day",
        (9,26): "National Pancake Day",
        (9,27): "National Chocolate Milk Day",
        (9,28): "National Strawberry Cream Pie Day",
        (9,29): "National Mocha Day",
        (9,30): "National Mulled Cider Day",
        (10,1): "World Vegetarian Day",
        (10,2): "National French Fried Scallops Day",
        (10,3): "National Caramel Custard Day",
        (10,4): "National Taco Day",
        (10,5): "National Apple Betty Day",
        (10,6): "National Noodle Day",
        (10,7): "National Frappe Day",
        (10,8): "National Fluffernutter Day",
        (10,9): "National Dessert Day",
        (10,10): "National Angel Food Cake Day",
        (10,11): "National Sausage Pizza Day",
        (10,13): "National Yorkshire Pudding Day",
        (10,14): "National Chocolate Covered Insect Day",
        (10,15): "National Mushroom Day",
        (10,16): "National Oatmeal Day",
        (10,17): "National Pasta Day",
        (10,18): "National Chocolate Cupcake Day",
        (10,19): "National Seafood Bisque Day",
        (10,20): "National Brandied Fruit Day",
        (10,21): "National Pumpkin Cheesecake Day",
        (10,22): "National Nut Day",
        (10,23): "National Boston Cream Pie Day",
        (10,24): "National Bologna Day",
        (10,25): "National Greasy Foods Day",
        (10,26): "National Mincemeat Pie Day",
        (10,27): "National Potato Day",
        (10,28): "National Chocolate Day",
        (10,29): "National Pancake Day",
        (10,30): "National Candy Corn Day",
        (10,31): "National Caramel Apple Day",
        (11,1): "National French Fried Clam Day",
        (11,2): "National Deviled Egg Day",
        (11,3): "National Sandwich Day",
        (11,4): "National Candy Day",
        (11,5): "National Doughnut Day",
        (11,6): "National Nachos Day",
        (11,7): "National Bittersweet Chocolate with Almonds Day",
        (11,8): "National Harvey Wallbanger Day",
        (11,9): "National Scrapple Day",
        (11,10): "National Vanilla Cupcake Day",
        (11,11): "National Sundae Day",
        (11,12): "National Pizza with the Works Day",
        (11,13): "National Indian Pudding Day",
        (11,14): "National Guacamole Day",
        (11,15): "National Clean Out Your Refrigerator Day",
        (11,16): "National Fast Food Day",
        (11,17): "National Baklava Day",
        (11,18): "National Vichyssoise Day",
        (11,19): "National Carbonated Beverage with Caffeine Day",
        (11,20): "National Peanut Butter Fudge Day",
        (11,21): "National Stuffing Day",
        (11,22): "National Cranberry Relish Day",
        (11,23): "National Cashew Day",
        (11,24): "National Espresso Day",
        (11,25): "National Parfait Day",
        (11,26): "National Cake Day",
        (11,27): "National Bavarian Cream Pie Day",
        (11,28): "National French Toast Day",
        (11,29): "National Chocolates Day",
        (11,30): "National Mousse Day",
        (12,1): "National Eat a Red Apple Day",
        (12,2): "National Fritters Day",
        (12,3): "National Ice Cream Box Day",
        (12,4): "National Cookie Day",
        (12,5): "National Sacher Torte Day",
        (12,6): "National Gazpacho Day",
        (12,7): "National Cotton Candy Day",
        (12,8): "National Brownie Day",
        (12,9): "National Apple Pie Day",
        (12,10): "National Lager Day",
        (12,11): "National Noodle-Ring Day",
        (12,12): "National Ambrosia Day",
        (12,12): "National Gingerbread House Day",
        (12,13): "National Cocoa Day",
        (12,14): "National Bouillabaisse Day",
        (12,15): "National Lemon Cupcake Day",
        (12,16): "National Chocolate Covered Anything Day",
        (12,17): "National Maple Syrup Day",
        (12,18): "National Roast Suckling Pig Day",
        (12,19): "National Oatmeal Muffin Day",
        (12,20): "National Fried Shrimp Day",
        (12,21): "National Hamburger Day",
        (12,22): "National Date Nut Bread Day",
        (12,23): "National Pfeffernusse Day",
        (12,24): "National Egg Nog Day",
        (12,25): "National Pumpkin Pie Day",
        (12,26): "National Candy Cane Day",
        (12,27): "National Fruit Cake Day",
        (12,28): "National Chocolate Candy Day",
        (12,29): "National Pepper Pot Day",
        (12,30): "National Bicarbonate Of Soda Day",
        (12,31): "National Champagne Day"
    }[(month,day)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='shows the national food of the days')
    parser.add_argument('--day', default='today', help='starting day, default is today or 1/31')
    parser.add_argument('--interval', default='7', help='number of days to show')
    pargs = parser.parse_args()

    if pargs.day == 'today':
        now = datetime.datetime.now()
        month = now.month
        day = now.day
    else:
        month,day = pargs.day.split('/')
    food_of_day_interval(int(month), int(day), int(pargs.interval))
