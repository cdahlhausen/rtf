# SLP Requirements Document

# Rivanna Trails Foundation

__Nonprofit overview:__ The Rivanna Trails Foundation (RTF) maintains a trail system in and around Charlottesville

__Contact:__ Nicholas Hamblet, nick.hamblet@gmail.com, 540-426-2538

__Website:__ [http://www.rivannatrails.org/][1]

__System summary:__ A collaborative, web-based platform for managing information about the Rivanna Trail

__Development notes:__ Python/Django.  Nick (the customer) has a CS degree.  Libraries exist that handle GIS data (both processing and visualization), and the intent is to use them to create this system.  Nick has developed some code that may also be of use, however licensing issues will need to be resolved if that code is used.

__Confidentiality notes:__ The standard [course NDA](http://aaronbloomfield.github.io/slp/uva/legal.html) is expected to have to be signed

__Attachments:__ A .kmz file of the current trail can be found [here](attachments/rivanna-trail.kmz); this is a [.kmz file](https://en.wikipedia.org/wiki/Keyhole_Markup_Language), and can be loaded into [Google Earth](https://www.google.com/earth/), among other programs.

## Nonprofit Description and Procedure

The Rivanna Trails Foundation (RTF) is a non-profit corporation founded in 1992 by Charlottesville, Virginia, area citizens with a dream to create a trail system throughout the greenbelt of the Rivanna river and its tributaries. The goal of the foundation is to establish a footpath encircling Charlottesville generally by following the Rivanna River, Meadow Creek, and Moore's Creek.  A map of the existing trail can be found [here][4].

RTF maintains the trail, and ensures proper legal permission to cross the land of the individuals who own the private land that much of the trail crosses.  They consist of a board of directors with about 10 people, and coordinate maintenance work days with many volunteers.

The purpose of this project is to create a system that allows for entering and keeping data on the trail itself: both geographic information about the trail locations as well as additional notes and historical data about the parts of the trail.

## System Description and Features

The trail system is composed of *segments*.  A segment is a part of the trail that could be a few hundred feet or a few miles of trail.  A segment is specified via a series of connected line segments (and possibly curves).  The trail segments rarely change (maybe once or twice a year), and thus editing segments in the proposed system is not necessary.  Segments will be created in an external program, exported to a [KML][2] file, which will be loaded into the proposed system (a different file format for uploading is possible, which can be determined later).  A KML file is an XML file with certain tags and a certain structure, but that contains geographic information.  Thus, editing an existing segment will not exist either.  However, there needs to be a way to "replace" the segment with an updated version (example: making a more accurate segment).

The system will keep track of a number of pieces of information on trail segments.  Examples are: open/closed status (temporary closed, always open, permanently closed, proposed segment, etc.); current conditions, maintenance requests, etc.  The customer will provide additional fields as necessary.  Some of these fields will have a single value (length of segment), others will have multiple entries and thus a history (maintenance jobs, etc.).

The system will have multiple layers of geographic data.  One such layer is the trail segments as described above.  Another will be the land ownership; this is a [GIS][3] file that contains polygons which correspond to property boundaries; each polygon will have associated data with it (parcel ID, parcel size, tax information, owner information, etc.).  This information will be exported from the local government, so the format will be standardized.  This means a KML file upload for this data.  Note, however, that Charlottesville actually consists of two municipalities: the city of Charlottesville and Albemarle County (the latter of which also contains addresses with Charlottesville as the listed town).  While both have GIS data, the formats will be somewhat different between the two.  UVa is largely within Albemarle County, with some parts in the City of Charlottesville.

The system will need to be able to keep data on both trail segments *and* parcels.  Much of this data will be contained in multiple entries, forming a history.  Parcel data can be identified by the Parcel ID, which is unique to the land parcel and does not change.  Some examples of parcel information include: links to the legal documents (the permission given to RTF for the trail to cross what is private property), links to the city/county information for that parcel, permissions given to the RTF by the parcel owner (customer will specify), and a history of interactions with the property owner.

Given the GIS data of the property parcels and the trails, the system can determine a number of things:

- which parts of the trail are on what parcel (geometry libraries exist to do this; please ask if unsure)
- a list of all the parcels a trail segment (or multiple segments) passes through
- a map that colors the parcels based on the permissions granted to RTF
- length of trail segments in a given parcel (or multiple parcels)
- others as specified by the customer

The system should be able to export all the data into a few different formats.  Much of the database can be exported to CSV for data backup.  A KML file with the trail segment data is also necessary.  Other GIS sites may need to load some/all of that data, so having the system provide a non-publicized link that another GIS site can read is also desired.  These links are typically in [WFS][5] or [WMS][6] format; note that converting between WFS (and likely WMS) is a [well-studied problem][7].  This will require allowing specification of which features/layers to include on the exported data.

Other layers are possible (the two described above are the trail segments and the parcel ownership).  Other layer examples: parks, roads, bridges and boardwalks, etc.  These layers can be loaded via a file upload, or by specifying a web URL (many GIS services provide their information that way, again via WFS or WMS formats).  It is unclear at this point if the features for the layer are generic features, or if the features for a layer (intersecting the trail segments with the polygons in a layer) are specific to the type of data being loaded in.

Yet another layer is the data entered into the system (maintenance logs, for example).  This is not a layer that is uploaded via GIS/KML.

For uploading GIS/KML data, each successive upload completely replaces the previous one (so new county parcel data will replace the old data).  This means the DB link will need to be via some constant field (parcel ID), and not to something that will change on each upload.  It is unclear if the trail segments will operate this way (that part may allow uploading a single segment that adds to the existing ones).

Albemarle County GIS data is available [here](http://albemarle.org/department.asp?department=gds&relpage=2910), and Charlottesville City GIS data [here](http://charlottesville.org/Index.aspx?page=1674).  Within the city GIS data, there are a number of layers to be visualized alongside the trail data: bike lanes, contours, parcels, parks, sidewalks, railroads, roads, and water features (wetland, surface water?). Similar county features are of course interesting.  This implies that a city our county GIS upload will have *multiple* layers, and they will have to be separated and treated individually by the system.

The system will have a public side and a private side.  RTF staff will have access to all the information on the private side.  The public side will be what will be shown on the website.  This is really just a different set of export options to KML: some of the data will only export in the "private" version (history of interactions with land owners, for example), while other data will export in both the "public" and "private" versions.  The "public" KML will then be loaded into the website via separate software (not within the system).

There are to be two or three different user levels.  RTF staff (which consists of the board members; about 10) have access to all the information in the system.  Volunteers have limited access and limited editing ability (they can insert some information, but not all; they can't view everything; etc.).  There also needs to be a way to add accounts, which may require an admin user level.

Other features:

- mobile friendly: many of the features (especially volunteer entry of data, such as maintenance requests or photo upload) may be done on a mobile phone while walking the trail; this will also need to be location aware (all of these features can be done via a mobile-friendly website, and do not require a separate app)
    - ability to find the nearest trail segment to the phone's current location
    - ~~put a donate/volunteer link on the mobile page~~
    - can the website "push" information?  imagine if they turn on a option to notify the user as they are near a certain type of feature (distinctive trees), so it repeatedly pulls the GPS data, and then notifies when it is near; likewise, a tour of trail segments could be created (this is an optional feature)
- ~~photo upload: this is not intended to be full featured like Facebook or Instagram, but a basic ability to upload photos of things: trail turns, panoramic photos, maintenance issues, etc.~~
    - ~~Google maps allows street view via custom photos, so using a panoramic photo would be viable~~
- coloring of trail segments: see [here][4] for examples of why this is done; this coloring may be fixed or may depend on what data/view/layers are being shown
- layers need to be easy to make visible or make hidden while working in the system
- ~~create reports based on the data in the system; likewise graphs~~


## Requirements: Minimum

- user authentication, user permissions
- uploading of trail segments
- annotation of trail segments
- export of map data to KML (public and private) and db data to CSV/excel
- visualization of trail

## Requirements: Desired

- uploading of city/county land parcel GIS data, as well as other layers
    - full features with the city/county land parcel GIS data; basic features with other layers
- ~~generation of better reports, graphs, and stats~~ deemed this unnecessary in conversation with Nick
- mobile friendly view
- able to make WMS/WFS data available via export or URL

## Requirements: Optional

- more better features for the other layer types
- "push" of data to the mobile map
- ~~panoramic photo usage in Google maps for custom street view~~ deemed this unnecessary


## Notes

The group must use existing libraries when present (GIS, KML, WMS, WFS, etc.) -- no re-inventing the wheel on these parts!


[1]: http://www.rivannatrails.org/
[2]: https://www.google.com/search?client=ubuntu&channel=fs&q=kml&ie=utf-8&oe=utf-8
[3]: https://en.wikipedia.org/wiki/Geographic_information_system
[4]: http://www.rivannatrails.org/page-952656
[5]: https://en.wikipedia.org/wiki/Web_Feature_Service
[6]: https://en.wikipedia.org/wiki/Web_Map_Service
[7]: https://www.google.com/search?q=convert+wfs+to+kml
