# How to use

If you ended up in this repo without any knowledge of Windows: first of all, how? and second - don't worry.

If you would like to just make a few keys to impress your friends, follow the section below. If you'd like to know a bit more on how this part of licensing works, read the whole thing.

## How do I make a key?

### Prerequisites

You will need:

 - `keycutter.py`, `pkeyconfig.py` and (optionally) `keymaker.py`
 - Any Product Key Configuration (pkeyconfig.xrm-ms) file;

#### keycutter??

Clone/download this repository.

#### Product Key Configuration??

You can take it from your own Windows installation. It's in `C:\Windows\System32\spp\tokens\pkeyconfig`. In there you will find (usually) three files - `pkeyconfig.xrm-ms` is the important one here.

There are also Visual Studio and Office ones. You can look for them somewhere in their installation directory.

### Create your product key

Open your favorite terminal and move to where you have `keycutter`, `pkeyconfig` and (if needed) `keymaker`.

For this example, let's make a `Windows 10 Enterprise Volume:GVLK` key. This type of key would be used to make a host activate with a KMS server.

#### Find the edition group ID

```
> python pkeyconfig.py [pkeyconfig.xrm-ms path] "Enterprise Volume"
[3290]: "Win 10 RTM Enterprise Volume:GVLK" - Enterprise
[3291]: "Win 10 RTM Enterprise Volume:MAK" - Enterprise
[3679]: "Win 10 RTM AnalogOneCoreEnterprise Volume:MAK" - AnalogOneCoreEnterprise
```

From this we can see that the group id for this type of key is `3290`. Time to make a key:

```
> python keycutter.py encode 3290 [serial] [security]
GNDRK-BFH4C-B2H8X-K8TCB-3GPJQ
```

You can choose an almost arbitrary value for both `serial` and `security`. It is customary to use low values for `serial`.

You now have a working product key. Have fun.

#### Just make all of them..

You can also just specify the whole pkeyconfig to create keys for all ranges found in it. This can be done as follows:

```
> python keymaker.py [pkeyconfig.xrm-ms path] [format]
...
```

The format is either `text` or `json`. They are usually gigantic so make sure you have something to read these with (eg. Notepad++/less/vim for text, Firefox for json).
