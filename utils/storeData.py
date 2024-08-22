import csv
import os 
from datetime import date, datetime

path_to_csv = "today_orders.csv"

def isNewDay(lastDate):
    currDate = date.today().isoformat()
    return currDate != lastDate

def writeIntoFile(report, response, lastDate):
    d = response.split('\n')
    data = [report['company'], d[2], d[3], d[4], report['Sales'], report['Net Profit'], report['Revenue']]


    if isNewDay(lastDate):
        with open(path_to_csv, 'w') as f:
            writer = csv.writer(f)
            writer.writerow("Company", "Order from", "Order Amt.", "Deadline", "Sales", "Net Profit", "Revenue")
            writer.writerow(data)
    else: 
        with open(path_to_csv, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)
    print("Data stored Successfully")
    return 

