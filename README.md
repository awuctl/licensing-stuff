# "Licensing Stuff"

This is a bunch of tools I've used for some time to do morally questionable stuff to Windows Licensing. I don't really have a reason to use them anymore so I hope someone else can have some fun.

## How do I use this?

If you just want to make a product key and don't want to read too much code, go [here](docs/how-to-use.md). 

All tools support the `--help` option, you can read it for a bit of context on the parameters.

## Tools

### keycutter.py

This contains an implementation of the "`msft:rm/algorithm/pkey/2009`" product key algorithm. The tool gives you an API and a commandline tool to encode and decode product keys or find ones matching a specified template. The template function could be written to allow for an **almost** arbitrary key but I didn't have any use for it other than a few funny sets of keys so I never bothered.

A bit of info about product keys [here](docs/product-keys.md).

### pkeyconfig.py

This is a simple API for interacting with data from `pkeyconfig.xrm-ms` files. 

### keymaker.py

This is a tool using `keycutter.py` and `pkeyconfig.py` that creates a plain text or json file with every single 2009 product key for a specified `pkeyconfig.xrm-ms` file.

### skuidmap.py

This is a lookup table between SKU IDs (edition IDs) and edition names. Most of this can be extracted from `winnt.h`, but some values are gone forever and there are many holes. There are other sources for these but they require heavy machinery to dig out. I can elaborate on request.

### store.py

This is a collection of mini tools that can do fun things related to the store.

`store.py content-id <product> <publisher> <platform>` is used for creating a content ID for a given product. This is the UUID which you can find in some files and registry keys related to licensing. This value is calculated with a very simple "formula", which you can read in the `content_id` function.

`store.py query-content <content-id>` is for querying the store for a particular content ID. This will give you information about pretty much any Store product for which you know the content ID, although it's worth knowing that some (particularly Windows-related) content IDs are hidden there and will give you a not-found error despite actually being internally recognized. There is also an option to specify the market and query language; this can get you pricing information or whether a given product is available in another market.

`store.py query-pkeyconfig <pkeyconfig>` is the same as above but it will do it automatically for all editions found in a pkeyconfig file.