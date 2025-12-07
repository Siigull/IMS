This folder locally contains elevation from the EU-DEM dataset. The full one has about 30GB so it is not possible to include.
The files have changed names from something like N4000000E200000 to N40E20 because the names were annoying to look at.
It was the best option in my opinion even though there are better datasets for czechia such as DMR 5G or DMR 4G https://geoportal.cuzk.cz/mGeoportal/?c=vyskopis_A.CZ&f=paticka.CZ.
The problem with these datasets is that they can only be downloaded with small tiles from an api which is annoying to use and rate limited.
So I settled on EU-DEM it was downloaded from https://www.gpxz.io/blog/eudem and it is accurate enough for the resolution of my CA.

The files I have locally are only
    - N40E20.tif (in dataset named N4000000E200000.tif)
    - N50E20.tif (in dataset named N5000000E200000.tif)
to cover the whole of the Czech Republic.


This was the original README included with the downloaded dataset:
```
These files are the same data as the V1.1 EU-DEM dataset, but buffered by a few pixels to allow for seamless reads.

For more information see: https://www.gpxz.io/blog/eudem

Originally downloaded from https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1.1

Access to data is based on a principle of full, open and free access as established by the Copernicus data and information policy Regulation (EU) No 1159/2013 of 12 July 2013. This regulation establishes registration and licensing conditions for GMES/Copernicus users. Free, full and open access to this data set is made on the conditions that:

    When distributing or communicating Copernicus dedicated data and Copernicus service information to the public, users shall inform the public of the source of that data and information.

    Users shall make sure not to convey the impression to the public that the user's activities are officially endorsed by the Union.

    Where that data or information has been adapted or modified, the user shall clearly state this.

    The data remain the sole property of the European Union. Any information and data produced in the framework of the action shall be the sole property of the European Union. Any communication and publication by the beneficiary shall acknowledge that the data were produced "with funding by the European Union".
```