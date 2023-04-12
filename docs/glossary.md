# Glossary

For all the things that aren't worth writing too much about but you might want to read up on.

## product.ini

This is a file found in all relatively recent ISO files given out by Microsoft. Open any ISO file and you will find it in `sources/product.ini`. 

This file contains a lot of product keys for pretty much all meaningful editions and channels on the version you're installing. These keys don't ever activate, they are used to **select** an edition.

## pkeyhelper.dll / gatherosstate.exe / setupcore.dll / TransmogProvider.dll keys

These files all contain a set of functions and a small database of product keys that they can query. You can rip the keys straight out of there using even the ol' reliable GNU strings (remember the `-e l` parameter). I have the structure itself written down somewhere. If you're reading this in the future and it's still not here remind me to put it up.


## Product key channel

This is what specifies how a given edition of a product activates or how it is acquired. There are many channels but the most important ones are:

 - Retail
 - [Volume:GVLK](https://learn.microsoft.com/en-us/windows/deployment/volume-activation/plan-for-volume-activation-client#generic-volume-licensing-keys) (*Generic Volume Licensing Key*)
 - [Volume:CSVLK](https://learn.microsoft.com/en-us/windows/deployment/volume-activation/plan-for-volume-activation-client#kms-host-keys) (*Customer-Specific Volume Licensing Key*)
 - [Volume:MAK](https://learn.microsoft.com/en-us/licensing/products-keys-faq#what-is-a-multiple-activation-key--mak-) (*Multiple Activation Key*)
 - OEM:NONSLP (*Non System-locked preinstallation*)
 - OEM:DM (*Digital Marker*)