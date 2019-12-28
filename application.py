import os
from flask import Flask, request, render_template
import requests
import json
from random import *

# Set up Yelp API
# Thanks to https://python.gotrained.com/yelp-fusion-api-tutorial/ for instructions on how to use the Yelp API
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")
api_key = os.environ.get("API_KEY")
headers = {'Authorization': 'Bearer %s' % api_key}
url = 'https://api.yelp.com/v3/businesses/search'
params = {'term': 'takeout', 'location': '', 'catergories': 'restaurants',
          'radius': '', 'price': '', 'open_now': True, 'limit': 50, 'offset': 0}

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def apology(message):
    return render_template("apology.html", message=message)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # Ensure that form isn't blank
        if not request.form.get("address"):
            return apology("Please enter your address")
        elif not request.form.get("distance"):
            return apology("Please enter a travel radius")

        # Ensure that distance is positive float <24
        # Thanks to Triptych on Stack Overflow for the idea of a try/except
        # https://stackoverflow.com/questions/1265665/how-can-i-check-if-a-string-represents-an-int-without-using-try-except
        try:
            float(request.form.get("distance"))
        except ValueError:
            return apology("Distance must be greater than 0 and less than 24"), 400
        if float(request.form.get("distance")) <= 0 or float(request.form.get("distance")) >= 24:
            return apology("Distance must be greater than 0 and less than 24"), 400

        # Update Yelp query parameters
        address = request.form.get("address")
        distance = request.form.get("distance")
        radius = int(float(request.form.get("distance")) * 1609.344)  # Convert miles to meters
        price1 = request.form.get("$")
        price2 = request.form.get("$$")
        price3 = request.form.get("$$$")
        price4 = request.form.get("$$$$")
        price = []
        if request.form.get("$") == '$':
            price.append('1')
        if request.form.get("$$") == '$$':
            price.append('2')
        if request.form.get("$$$") == '$$$':
            price.append('3')
        if request.form.get("$$$$") == '$$$$':
            price.append('4')
        price = ','.join(price)
        if price == '':
            price = '1,2,3,4'
        params.update({'location': address, 'radius': radius, 'price': price})

        # Make Yelp query and parse to JSON
        req1 = requests.get(url, params=params, headers=headers)
        parsed1 = json.loads(req1.text)
        if "error" in parsed1:
            return apology(parsed1["error"]["description"]), 400
        else:
            parsed1 = parsed1
        businesses1 = parsed1["businesses"]
        index1_max = len(businesses1) - 1
        if index1_max < 0:
            return apology("Sorry, nothing is open within those parameters. Try expanding your search."), 400
        else:
            index1 = randint(0, index1_max)

        # Do same for second page of Yelp results
        params.update({'offset': 50})
        req2 = requests.get(url, params=params, headers=headers)
        parsed2 = json.loads(req2.text)
        businesses2 = parsed2["businesses"]
        index2_max = len(businesses2) - 1
        if index2_max >= 0:
            index2 = randint(0, index2_max)
        params.update({'offset': 0})

        # Combine two lists
        businesses = businesses1 + businesses2
        index_max = len(businesses1) + len(businesses2) - 1
        index = randint(0, index_max)

        # Prep fields to port to result page
        business = businesses[index]
        bizname = business.get("name")
        bizurl = business.get("url")
        bizimage = business.get("image_url")
        bizaddresslist = business.get("location").get("display_address")
        bizaddress = ', '.join(bizaddresslist)
        bizdistance = format((business.get("distance")/1609.344), '.2f')  # Convert meters to miles
        bizprice = business.get("price")

        # Render result page
        return render_template("result.html", address=address, distance=distance, price1=price1, price2=price2, price3=price3, price4=price4, businesses=businesses, business=business, bizname=bizname, bizurl=bizurl, bizimage=bizimage, bizaddress=bizaddress, bizdistance=bizdistance, bizprice=bizprice)

    else:
        return render_template("index.html")