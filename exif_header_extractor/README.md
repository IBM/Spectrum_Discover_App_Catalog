EXIF Header Extractor
==============
This application will extract exif information from jpg, jpeg, tiff files.
For each file provided from the work message, it will be opened as binary
read. It will extract the relevant information based on the tags provided
on the work message.


Available tags for jpg, jpeg files
==============
At the time of writing, the below tags are available.
This may not be an all inclusive list, but will be updated accordingly.
```
exif_aperturevalue
exif_colorspace
exif_componentsconfiguration
exif_customrendered
exif_datetimedigitized
exif_datetimeoriginal
exif_exifimagelength
exif_exifimagewidth
exif_exifversion
exif_exposurebiasvalue
exif_exposuremode
exif_exposureprogram
exif_exposuretime
exif_flash
exif_flashpixversion
exif_fnumber
exif_focallength
exif_focalplaneresolutionunit
exif_focalplanexresolution
exif_focalplaneyresolution
exif_interoperabilityoffset
exif_isospeedratings
exif_meteringmode
exif_scenecapturetype
exif_shutterspeedvalue
exif_subsectime
exif_subsectimedigitized
exif_subsectimeoriginal
exif_usercomment
exif_whitebalance
gps_gpsversionid
image_datetime
image_exifoffset
image_gpsinfo
image_make
image_model
image_orientation
image_resolutionunit
image_software
image_xresolution
image_ycbcrpositioning
image_yresolution
interoperability_interoperabilityindex
interoperability_interoperabilityversion
jpegthumbnail
thumbnail_compression
thumbnail_jpeginterchangeformat
thumbnail_jpeginterchangeformatlength
thumbnail_resolutionunit
thumbnail_xresolution
thumbnail_yresolution
```


Available tags for tiff files
==============
This may not be an all inclusive list, but will be updated accordingly.
```
image_subfiletype
image_imagewidth
image_imagelength
image_bitspersample
image_compression
image_photometricinterpretation
image_documentname
image_stripoffsets
image_orientation
image_samplesperpixel
image_rowsperstrip
image_stripbytecounts
image_xresolution
image_yresolution
image_planarconfiguration
image_resolutionunit
image_extrasamples
image_intercolorprofile
```


Finding tags manually
==============
To manually find what tags your file has, you can run something along the lines of:
```
python3 -m pip install exifread
python3
import exifread
with open('<file_name>', 'rb') as fd:
  print(exifread.process_file(fd))
```

Spectrum Discover Tag Integration
==============
From the above manual process, you will notice that the tags have uppercase and spaces in the names.
We convert the tags to lowercase and replace spaces with underscores in order to be supported within IBM Spectrum Discover.