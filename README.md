#Overview

This project scrapes [edmtrain](edmtrain.com) and stores the events into a
MySQL database. I intended to build off of this project for a personal event 
notification tool.

#How to use

First build the database, just run ```docker build``` and ```docker run```
in the *database/* directory. There is a README there for more info.

Finally, run scraper.py with the corresponding spider that you need.

#Spiders

###EDMTrainSpider
Parent spider, all other spiders inherit from it

###AllFestivalsSpider
Will scrape all events listed under https://edmtrain.com/festivals.

###AllLocationSpider
Scrapes all the events in a given location

###RecentLocationSpider
Scrapes the most recent *x* number of events

#TODO
Need to do some async stuff when disable_redirect is set to ```False```
to cut down on some of the wait time. Maybe get rid of the artificial wait
and hit edmtrain with concurrent requests. 