# fourOneOne
A scraper for grabbing information from 411.ca

The intent is to collect as much data as possible from the site that is publically available and create a dataset that can be used for machine learning experiments. Currently, residential information for most of the east coast of Canada has been completed. Admittedly, the scripts have not been touched for awhile and there are several enhancements that I would like to add, so I'm sure there are some broken things. I promise im not a supervillain, I just wanted to grab a lot of information about the kinds of people that live in Canada, what sorts of telecommunication providers they rely on, and it also seemed like a unique benchmark to see what my 3900x could do.

Current Capabilities
- Can look up listings by postal code.
- Grab personal details for postal code, phone number, phone connection type, telecom provider, city, province, street address, geo location information (Latitude and Longitude), and name.
- 

Ideas I currently have are:
- See if I can scrounge JSON data some way.
- Add API functionality and some sort of method to utilize Google to fill in missing geolocation data.
  - I know this is possible with maps, but scraping Google and not paying to use their api is a bit of a grey area.
  - Additionally, getting a low resolution snapshot from maps might be interesting for this data set.
- Build my own connection daemon class that can handle automatic proxy rotation with a vpn service and handle all the request and timeout nonsense.
- Generalize stuff a bit more as things are pretty hardcoded and or use some of the linux text processing commands.
- Throw a full sweep of Canada on Kaggle or something like that once Ive tidied up the information.
- Add some GUI stuff for visualizations that can breakdown the information collected.
- Unit tests.
- Perhaps some sort of fallback that uses image recognition like PyautoGUI to navigate and find useful information should the main scraper bite the dust.
- Port over to a language like Go as an experiment and try to get the memory usage and threading nightmare undercontrol.


Hopefully the video embed works, if it doesnt give it a download to see this monster in action.

![Sample Video](geolocations.webm)

