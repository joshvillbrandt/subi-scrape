import requests
from bs4 import BeautifulSoup
from colorama import Fore
import csv


dealerships = [
    # 'subarupacific',
    # 'timmonssubaru',
    # 'subarusantamonica',
    # 'glendale.subaru',
    # 'renicksubaru',
    # 'subarushermanoaks',
    # 'puente-hills.subaru',
    # 'southcoast.subaru',
    # 'sierra.subaru',
    # 'irvine.subaru',
    # 'ontario-ca.subaru',
    # 'singh.subaru',
    # 'galpin.subaru',
    # 'ladin.subaru',
    # 'sanbernardino.subaru',

    'temecula.subaru',

    # 'kirby-ventura.subaru',
]
vehicles = []

code_names = {
    'GUN': 'WRX, manual',
    'GUO': 'WRX Premium, manual',
    'GUP': 'WRX Premium, CVT',
    'GUQ': 'WRX Limited, manual',
    'GUR': 'WRX Limited, CVT',
    'GUS': 'STI, manual',
    'GUV': 'STI Limited, manual, tall spoiler',
    'GUW': 'STI Limited, manual, low spoiler',
}


def url(dealership):
    return 'http://www.' + dealership + '.com/all-inventory/index.htm?listingConfigId=AUTO-new%2CAUTO-used&compositeType=&year=2016&make=&bodyStyle=&internetPrice=&start=0&sort=&facetbrowse=true&searchLinkText=SEARCH_INVENTORY&showInvTotals=false&showRadius=false&showReset=false&showSubmit=true&facetbrowseGridUnit=BLANK&showSelections=true&dependencies=model%3Amake%2Ccity%3Aprovince%2Ccity%3Astate&suppressAllConditions=compliant'


def parseDescription(section, key):
    dt = section.find('div', 'description').find('dt', text=key)
    if dt:
        return dt.find_next_sibling('dd').text.replace(',', '')
    else:
        return '?'


def parseVehicle(section):
    vehicle = {}
    vehicle['name'] = section.find('h3').find('a').text
    vehicle['code'] = parseDescription(section, 'Model Code:')
    vehicle['color'] = parseDescription(section, 'Exterior Color:')
    vehicle['price'] = section.find('ul', 'pricing').find('span', 'value').text

    vin_section = section.find('dl', 'vin')
    if vin_section:
        vehicle['vin'] = section.find('dl', 'vin').find('dd').text
    else:
        vehicle['vin'] = '?'

    vehicle['status'] = section.find('div', 'badge-in-transit')
    if vehicle['status'] is not None:
        vehicle['status'] = 'in transit'
    else:
        vehicle['status'] = 'inventory'

    # fix name if possible
    if vehicle['code'] in code_names:
        vehicle['name'] = code_names[vehicle['code']]

    return vehicle


def parsePage(document):
    vehicles = []

    vehicleSections = document.find_all('div', 'hproduct')
    for section in vehicleSections:
        vehicle = parseVehicle(section)
        vehicles.append(vehicle)

    return vehicles

for dealership in dealerships:
    r = requests.get(url(dealership))
    dealer_vehicles = parsePage(BeautifulSoup(r.text))

    for vehicle in dealer_vehicles:
        vehicle['dealership'] = dealership
        vehicles.append(vehicle)

print '{}found {} vehicles from {} dealerships{}\n'.format(
    Fore.CYAN,
    len(vehicles),
    len(dealerships),
    Fore.RESET
)

# sorted by least significant thing first
vehicles = sorted(vehicles, key=lambda k: k['color'])
vehicles = sorted(vehicles, key=lambda k: k['price'])
vehicles = sorted(vehicles, key=lambda k: k['code'])

for vehicle in vehicles:
    print('{}{:3}   {:6}   {:17}   {:10}   {:17}   {}{}'.format(
        Fore.GREEN if vehicle['code'] == 'GUV' else Fore.WHITE,
        vehicle['code'],
        vehicle['price'],
        vehicle['vin'],
        vehicle['status'],
        vehicle['dealership'],
        vehicle['color'],
        Fore.RESET,
    ))

# output to file
with open('vehicles.csv', 'wb') as f:
    w = csv.DictWriter(f, vehicles[0].keys())
    w.writeheader()
    for vehicle in vehicles:
        w.writerow(vehicle)
