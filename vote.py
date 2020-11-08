import requests

# first generate a one-time-mail and a corresponding mailbox
res = requests.get("https://anonbox.net/en/")
email = ""
mailbox = ""
for line in res.iter_lines():
    if b"<span style='display: none' class=foobar>" in line:
        str_line = line.decode()
        start = str_line.find("<dd><p>") + 7
        end = str_line.find("<span style='display: none' class=foobar>", start)

        if start == -1 or end == -1:
            print("Error: crawled page changed. Please adapt script.")
            break

        local = str_line[start:end]

        start = str_line.find("</span>", end) + 8
        end = str_line.find("<span></span>", start)

        if start == -1 or end == -1:
            print("Error: crawled page changed. Please adapt script.")
            break

        subdomain = str_line[start:end]
        domain = "anonbox.net"
        email = local + "@" + subdomain + "." + domain

    if b"https://anonbox.net/" in line:
        str_line = line.decode()
        start = str_line.find("<dd><p><a href=\"") + 16
        end = str_line.find("\">", start)

        if start == -1 or end == -1:
            print("Error: crawled page changed. Please adapt script.")
            break

        mailbox = str_line[start:end]
        break

# generate random contact data
res = requests.get("https://randomname.de/?format=json")
person_data = res.json()

firstname = person_data[0]["firstname"]
lastname = person_data[0]["lastname"]
street = person_data[0]["location"]["street"]["name"] + ' ' + str(person_data[0]["location"]["street"]["number"])
zip_code = person_data[0]["location"]["zip"]
city = person_data[0]["location"]["city"]

# get state associated to zip code
res = requests.get("http://api.geonames.org/postalCodeSearchJSON?postalcode=" + zip_code + "&placename=" + city + "&county=DE&maxRows=10&username=nabubot")
city_data = res.json()
state = city_data["postalCodes"][0]["adminName1"]

# perform post request to vote
headers = {'User-Agent': 'Mozilla/5.0'}
payload = {
    'form[wahlkampfteam]': 'Drei90',
    'form[bird]': 'Schwarzhalstaucher',
    'form[repeat]': '',
    'form[vorname]': firstname,
    'form[nachname]': lastname,
    'form[strasse]': street,
    'form[plz]': zip_code,
    'form[ort]': city,
    'form[bundesland]': state,
    'form[email]': email,
    'form[mitglied]': 'nein',
    'form[begruendung]': '',
    'form[submit]': 'submit'
}

session = requests.Session()
session.post('https://vogeldesjahres.de/vorwahl/Schwarzhalstaucher/Drei90/?', headers=headers, data=payload)

res = requests.get(mailbox)
while not res.text:
    res = requests.get(mailbox)

confirm_link = ""
for line in res.iter_lines():
    if b'https://vogeldesjahres.de/confirm/' in line:
        confirm_link = line.decode()

res = requests.get(confirm_link)

success = False
if "Herzlichen Dank für Deine Teilnahme!" in res.text:
    success = True

if success:
    print("Voting successful!")
else:
    print("Error. Please check script.")
