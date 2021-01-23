# foodholidays

created utility based on results from https://scottroberts.org/complete-listing-of-national-food-days/
I took the libery of choosing one holiday when multiple holidays were available.  A few days were not assigned
in September so I took some days where multiple holidays were listed on other days and choose one for the NONE days.

The usage is:
```bash
foodholiday.py
(returns todays holiday)
foodholiday.py 1 23
(returns 1/23 holiday)
from foodholiday import food_of_day
food_of_day()  # returns todays holiday
food_of_day(month=1,day=23)  # returns holiday for 1/23
```