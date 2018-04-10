#!/usr/bin/env python

# fbLocations.py
# This script will parse through a person's fb data and print our a list of all
# the locations that they've logged into fb from based on the IP addresses in
# their Security session history.

# Christopher Choy
# CMSC 23210 - Usable Security and Privacy
# Problem Set 2, Problem 4
# 9 April 2018

import sys
import re
import json
import urllib2
from bs4 import BeautifulSoup
import geoip2.database

usage = "Usage: $ python fbLocations.py ./path/to/facebook-dataDirectory/ \nExample: $ python fbLocations.py ./facebook-cchoy96/"

# geoip2's Free City Database Path
geoipDBPath = "./GeoLite2-City_Database/GeoLite2-City.mmdb"

# Parses through file to generate List of all login ips
def createIpList(html_doc):
    # Open the html and turn it into soup
    with open(html_doc,'r') as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    # Purge out untinteresting data from soup
    references = soup.find("h2", text=re.compile("IP Addresses"))
    for elm in references.find_previous_siblings():
        elm.extract()
    references.extract()

    references = soup.find("h2", text=re.compile("Datr Authentication Cookie Info"))
    for elm in references.find_next_siblings():
        elm.extract()
    references.extract()

    navhtml = soup.find("div", class_="nav")
    navhtml.extract()

    # Put IPs into a list
    ipList = []
    ipsoup = soup('li')
    for ip in ipsoup:
        ipList.append(ip.text)

    return ipList

# Print the IPs
def printIPs(ipList):
    print("FB Login IP History:")
    for ip in ipList:
        print("\t" + ip)

# Uses login ips to create a list of all locations a user has logged into
def createLocationList(ipList):
    print("Tracing your login ip's...")
    locList = []

    # Poll database for ip -> location info and populate locList
    reader = geoip2.database.Reader(geoipDBPath)
    for ip in ipList:
        response = reader.city(ip)
        _country = "??" if response.country.iso_code is None else response.country.iso_code
        _city = "???" if response.city.name is None else response.city.name
        _state = "unknown" if response.subdivisions.most_specific.name is None else response.subdivisions.most_specific.name
        locList.append("[" + _country + "] " + _city + ", " + _state)

    return list(set(locList))
    # return locList  # to include duplicate locations

def printLocations(locList):
    print("FB Login Location History:")

    if not locList:
        print("\tERR: No valid locations found.")
    else:
        for loc in locList:
            print("\t" + loc)

def main():
    if len(sys.argv) != 2:
        print(usage)
        return

    print("Running fbLocations.py...")

    securityHTML = sys.argv[1] + "html/security.htm"
    ipList = createIpList(securityHTML)
    # printIPs(ipList)
    locList = createLocationList(ipList)
    printLocations(locList)
    
    print("FB Data Script Complete!\n")

main()
