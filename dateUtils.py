months={'January':'01','February':'02','March':'03',
        'April':'04', 'May':'05','June':'06',
        'July':'07','August':'08','September':'09',
        'October':'10','Novmber':'11','November':11,'December':'12'}

def dateConver(datalist):
    dates = []
    for data in datalist:
        dataArray = data.split(" ")
        month = months[dataArray[1]]
        dates.append("{}-{}-{}".format(dataArray[2],month,dataArray[0].zfill(2)))
    #print(dates)
    return dates

def dateConver2(datalist):
    dates = []
    for data in datalist:
        dataArray = data.strip().split("/")
        dates.append("{}-{}-{}".format(dataArray[2],dataArray[1],dataArray[0]))
    return dates

#判断日期是否在范围内(yyyy-mm-dd)
def checkDateRange(lower,upper,date):
    if lower<date<upper:
        return True
    else:
        return False





