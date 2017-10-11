Raw Adsb Folder
--------------------

1) Contains JSON formatted ADSB data. Information about the data fields can be found here https://www.adsbexchange.com/datafields/
2) Each file contains 1 minute's worth of data referencing a particular Zulu Time. 
3) File naming convention should be as follows: yyyy-mm-dd-xxxxZ.json, where xxxx is the 4 digit Zulu Time Code.

--Containing Files

1) Data on June 19th 2016 between the hours of 1pm - 3pm EDT (Very busy congestion of airspace) 


Extracted Features Folder
---------------------------

Contains CSV Files of ADSB data with only features of interest included. Currently we track the Lat, Long, Altitude and Engine Type data fields.

