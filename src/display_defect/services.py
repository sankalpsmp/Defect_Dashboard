import os
import requests
import json
import time 
import datetime


def get_defects():

	date=views/get_date.date

	x = date.split("-")
	new_lst = x[::-1] 
	sent_str = ""
	for i in new_lst:
		sent_str += str(i) + "/"
	sent_str = sent_str[:-1]
	element = datetime.datetime.strptime(sent_str,"%d/%m/%Y") 
	tuple = element.timetuple() 
	timestamp = time.mktime(tuple) 
	timestamp=int(timestamp)*1000

	primt(timestamp)

	url = "https://crucible01.cerner.com/rest-service/reviews-v1/filter/details?fromDate="+str(timestamp)+"&project=SYNAPSE-CR"
