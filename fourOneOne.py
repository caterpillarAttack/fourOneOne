#!/usr/bin/python3
import multiprocessing as mp
import requests as rq
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import itertools as it
import dataGen as dg
import math
#add sys and allow for pipeline functionality and verbose triggers
#non existant postal code
# page = rq.get("https://www.canada411.ca/search/pc/1/-/cZQQstZQQciZQQpvZQQpcZA0A1B9")
#invalid postal code
# page = rq.get("https://www.canada411.ca/search/pc/1/-/cZQQstZQQciZQQpvZQQpcZA0A1Bk")
#working postal code
# link = "https://www.canada411.ca/search/pc/1/-/cZQQstZQQciZQQpvZQQpcZA0A1B0"


class fourOneOne(dg.dataGen):
    def __init__(self):
        self.delay_print('Yellow Pages/411 object created.\n')

    def getPage(self, link):
        """
        This will likely get ported to its own class specifically for dealing with
        stubborn servers. The other benefit, is that the class could have
        its own methods to deal with timeouts and lockouts such as proxy rotation.
        return getObj
        """
        # https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
        # excellent description of what is going on here. Need to read more about those
        # mount points as they may prove to be useful for enhancing Portia.
        retry_strategy = Retry(
        total=100,
        status_forcelist=[429, 500, 502, 503, 504, 104],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = rq.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        page = http.get(link, timeout=100)
        try:
            page.raise_for_status()
            return page
        except rq.exceptions.HTTPError as e:
            print("###ERROR:", e)
            raise(e)

    def computeLinks(self):
        #this could likely be ported over to the datagen class, as a general method, and
        #be changed as needed. computeLinks(arg blagh) then glue it together.
        """
        Returns an iterable object of 411.ca reverse postal code lookup links, for
        every theoretical postal code in Canada.
        NOTE* Some pages will lead to possible invalid codes or listings that
        do not exist
        return iterable, string
        """
        linkStart = "https://www.canada411.ca/search/pc/1/-/cZQQstZQQciZQQpvZQQpcZ"
        return (linkStart + postCode for postCode in self.computeCodes()[0]), '411.txt'

    def geoLocation(self, number):
        """
        If possible, this function fetches the latitude and longitude of corresponding
        to a phone number other wise it returns two empty string values.
        return string, string
        """
        locateLink = 'http://mobile.canada411.ca/search/?stype=re&what='
        page = self.getPage(locateLink + number.replace('-', ''))
        soup = BeautifulSoup(page.content, 'html.parser')
        page.close()
        coordinates = [line.split(':')[7].split(']},')[0].replace('[', '') for line in str(soup.find('script', {'class' : 'jsMapResource'}).contents[0]).splitlines() if 'coordinates' in line]
        if len(coordinates) < 1:
            return str(), str()
        else:
            latitude, longitude = coordinates[0].split(',')
            return str(latitude).strip(), str(longitude).strip()

    def providerCheck(self, number):
        #Could not reproduce: BUG* There is an issue with provider checks on numbers that have multiple listsings
        # within the yellow pages. This doesnt seem to happen very often, but we likely need a
        # better way of dealing with this. Possible fix may exist in the form of searching
        # for their names directly with the following link.
        # https://www.canada411.ca/res/5812246688/Lydia-Turmel https://www.canada411.ca/res/PHONENUMBER/FirstName-Lastname #this appears to default to the french language version.
        # so before we patch, we need to replace the empty spaces with -
        # this link may work for brute phone search https://www.yellowpages.ca/search/re/1/5812246688/Toronto+ON
        """
        This fuction returns which telecom provider is associated with a phone number
        as well as the type of number it is associated with. Currently, most of the
        data is associated with either landlines or cell phone numbers.
        return string, string
        """
        checkLink = "https://canada411.yellowpages.ca/fs/1-"
        # print(checkLink + number)
        #NOTE* CHECK WHICH COUNTRY THE NUMBER IS LOCATED IN
        #there are some bugs in here if its fetching an american provider for some reason.
        page = self.getPage(checkLink + number)
        soup = BeautifulSoup(page.content, 'html.parser')
        page.close()
        # https://linuxhint.com/find_children_nodes_beautiful_soup/
        #bug here if there are no children
        try:
            provider, connectionType, *_ = (child.text.strip() for child in soup.find('ul', {'class' : 'phone__details'}).findChildren('li'))
            _, provider,  _, connectionType = provider.split(": ") + connectionType.split(": ")
        except:
            provider = str()
            connectionType = str()
        return provider, connectionType

    def pageParser(self, pageContent, postCode):
        """
        This function formats and parses the data found on the multiple entry reverse postal
        code lookup pages. It returns a generator object, as it only grabs at most 15 entries
        per page.
        return iterable
        """
        #NOTE* SMALL BUG BUT MAKE SURE THE AREACODE CORRESPONDS WITH THE PROVINCE'S AREACODE
        # STARTING LETTER, THERE IS SOME GARBAGE VALUES IN HERE APPARENTLY.
        #this returns results on a per page basis
        for adr, phone, name in (zip(pageContent.find_all('span', {'class': 'adr',}),
                                pageContent.find_all('span', {'class': 'c411Phone',}),
                                pageContent.find_all('h2', {'class': 'c411ListedName',}))):
            city, province = adr.contents[0][:-10].strip(), adr.contents[0][-10:][:2]
            phone = phone.contents[0].replace("(", "").replace(") ", "-")
            name = name.a.contents[0]
            # provider, connection = self.providerCheck(str(phone), str(name))
            provider, connection = self.providerCheck(str(phone))
            latitude, longitude = self.geoLocation(str(phone))
            # clean this up, as its kind of ugly.
            yield str(postCode), str(phone), str(connection), str(provider), str(city), str(province), str(latitude), str(longitude),  str(name)

    def individualParser(self, pageContent, link):
        """
        This function handles the case of where there is a single listing for a reverse postal code lookup,
        and returns the postal code, phone number, city, province, and name of the listing.
        return iterable
        #[['Montréal QC', '819-563-1233', 'Landline', 'Bell Canada', '441 Du President Kennedy 2', '07', '45.50666427612305', '-73.57035064697266', 'Sui Khien Trinh']]

        """
        city = str(pageContent.find('div', {'class' : 'c411Address vcard__address'}).contents[0][:-10].strip())
        province = str(pageContent.find('div', {'class' : 'c411Address vcard__address'}).contents[0][-10:-8].strip())
        postCode = str(pageContent.find('div', {'class' : 'c411Address vcard__address'}).contents[0][-6:].strip())
        name = str(pageContent.find('h1', {'class' : 'vcard__name'}).contents[0])
        phone = str(pageContent.find('span', {'class' : 'vcard__label'}).contents[0].replace('(','').replace(") ", "-"))
        provider, connection = self.providerCheck(str(phone))
        provider = str(provider)
        connection = str(connection)
        latitude, longitude = self.geoLocation(str(phone))
        return [[postCode, phone, connection, provider, city, province, latitude, longitude, name]]

    def performLookup(self, link):
        """
        Performs a reverse postal code lookup on the provided 411.ca link.
        TBD, what gets included here, ie geolocation data.
        returns iterator
        """
        page = self.getPage(link)
        # BUG* There is some kind of fault going on here. Where pages are missing this check and being passed
        # To the later function calls resulting in an error. Page.text should still return some data,
        # even if the page we were looking for doesnt have anything on it.
        if "We didn't find any result" in page.text or 'Postal code entered is of wrong format' in page.text:
            return 1, link
        soup = BeautifulSoup(page.content, 'html.parser')
        page.close()
        if soup.find('div', {'class' : 'c411ResultsTop'}) == None:
            output = self.individualParser(soup, link)
            soup.decompose()
            #debugging code
            # print(output)
            return output, link
        #we can ditch result count, nevermind, it would be a good idea to check against it to make sure we got everyone.
        resultCount, *_, postCode = soup.find('div', {'class' : 'c411ResultsTop'}).text.strip().replace(':', '').split(" ")
        soup.decompose()
        # print(link)
        resultCount = resultCount.replace(',', '')
        pageLinkGenerator = (link.replace('/1/', '/' + str(pageNum) + '/') for pageNum in range(1, math.ceil(int(resultCount) / 15) + 1))
        perPageGenerators = []
        for pageNumLink in pageLinkGenerator:
            page = self.getPage(pageNumLink)
            soup = BeautifulSoup(page.content, 'html.parser')
            page.close()
            perPageGenerators.append(self.pageParser(soup, postCode))

        #debugging code
        # resultHit = 0
        # for entry in it.chain.from_iterable(perPageGenerators):
        #     print(entry)
        #     resultHit += 1
        # if int(resultCount) != (resultHit):
        #     raise('Incomplete grab.')

        # perhaps restructure this function to factor in for phone numbers?
        collection = [list(entry) for entry in it.chain.from_iterable(perPageGenerators)]
        if int(len(collection)) == int(resultCount):
            return collection, link
        elif int(len(collection)) != int(resultCount):
            raise RuntimeError('Incomplete grab.')


def postalGrab():
    totalLinks = 'totalLinks.txt'
    #create one of these if it does not exist
    completedLinks = 'completedLinks.txt'
    progress = open(completedLinks, 'a')
    taskLinks = 'taskLinks.txt'
    test = fourOneOne()
    test.toFile(test.computeLinks()[0], totalLinks, "w")
    with mp.Pool(20, maxtasksperchild=5) as p:
        #possibly convert this into a generator in itself, and string everything together and pass it to the write
        #to file thing. This may introduce problems regarding what needs to be taken out of the progress stack.
        for thing in p.imap(test.performLookup, test.progressLoader(totalLinks, completedLinks, taskLinks), 5):
            if not isinstance(thing[0], int):
                #writing to file happens here.
                test.toCSV(thing[0], '411DumpTest.csv')
            #write this to completed file after iteration cycle
            print(thing[1])
            progress.write(thing[1] + '\n')
    progress.close()

if __name__ == '__main__':
    postalGrab()
