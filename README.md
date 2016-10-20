#Blender Facebook 360

Convenience operators for creating 360 renders for Facebook.

https://facebook360.fb.com/360-photos/

* Enable bounding to constrain settings to work with 360.
* Use the Add Panorama XMP button to tag an existing JPG.

##Installation:

* Use Install From File on the Add-Ons panel to install [facebook_360.py](./dist/facebook_360.py)
* Or, copy the [/src](./src) directory to your add-ons folder

##Build:

Run `python3 make.py` from the project root.

[make.py](./make.py) naively combines files in a list, marking file divisions and stripping redundant `import`
statements. This process depends on the project files using wrapper classes. I would be interested in hearing about a
better way to structure the project that still allowed compiling a single `.py` file for easy installation.

##Testing:

Run tests from project root.

* `python3 -m test.test_xmp`
