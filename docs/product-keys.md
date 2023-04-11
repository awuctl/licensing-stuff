# Product Keys

There is some funny stuff related to product keys that were discovered over the years of playing with this and a few other things.

The first tool I know of that was capable of decoding and encoding pkey2009 keys was Bob65536's KeyInfo tool. It has been [nuked off of MDL](https://web.archive.org/web/20121026081005/http://forums.mydigitallife.info/threads/37590-Windows-8-Product-Key-Decoding) a long time ago, which is a beautiful statement about how shit these forums are and how much wonderful stuff the admins are willing to just wipe off the internet with no warning. The tool had some weird guesswork in it since as far as I know it was written by reverse engineering some no-fun key validation libraries. Another (a bit better, although not too direct) source of information about this algorithm is the actual patent for it, which can be found [here](https://patents.google.com/patent/US8984293B2).

The keycutter tool was written looking at that patent, the KeyInfo tool and poking Windows a bit (a lot). No one bothered with keys for Office and Visual Studio but they work in pretty much exactly the same way.

The tool can be used to make Windows, Office and Visual Studio keys. Visual Studio does this fully offline so no extra check beyond the validity of the key is done at all.

## Structure

The key is just a huge 128-bit bitfield encoded in base24 (`BCDFGHJKMPQRTVWXY2346789`) where the `N` character's **position** signifies the least significant base24 word of the key.

The bitfield is made up of the following:

 * `20b`: Group ID
 * `30b`: Serial Number
 * `53b`: Security Value (the patent specifies this as two fields)
 * `10b`: Checksum
 * `01b`: Upgrade bit
 * `<1b`: Voodoo magic

You can find the explanations for what these are in the patent. Some key facts:

 * Group IDs are shared between everything that uses 2009 product keys (Windows, Office, Visual Studio);
 * The serial number is sequential (ie. buy a new key, check its serial and you'll see how many keys of that group were sold);
 * The security value is hinted to be a truncated SHA256 HMAC. I don't really know what exactly is hashed and with what key. Only heard rumors that someone out there knows;
 * The checksum is CRC32/MPEG-2;
 * The upgrade bit does change the key and it will be recognized as an upgrade key. As far as I know these are not used anymore;
 * The voodo magic bit is an artifact of the encoding. If the value of the full 128-bit key is small enough (nearly always is), you can encode an extra meaningless bit (called `extra` in keycutter). This lets you make twin keys, more on which later.

## Twin keys

The extra bit explained above can be used to create two keys with exactly the same meaning:

1. Take one key;
2. Decode it;
3. Reencode it with extra set to 1 and an automatic checksum;
4. Done. What you have is the key's evil twin.

These have the same meaning to both the operating system and (for the most part) activation servers. I have not tested it with keys that give you a real activation state but I'd bet something breaks along the way (the key server should be more strict about the bitfield than Windows is).

One fun example is (was) for ServerRdsh: The original key is `NJCF7-PW8QT-3324D-688JX-2YV66` and its twin is `VKCF7-HV62C-944TY-YJ9NF-6Q83G`. Both worked, even though ServerRdsh officially had only one valid key that always gave you activation (non-HWID so the twin working is likely an exception).

## Templates

The keycutter tool allows you to make keys for a given group ID with a template. You can specify any (valid key-alphabet) string up to 18 characters. Example:

```
> python keycutter.py template 0xcda NBBBB-BBBBB-BBBBB-BBB
NBBBB-BBBBB-BBBBB-BBBJK-GJF8Q
NBBBB-BBBBB-BBBBB-BBBQ8-9TPJQ
NBBBB-BBBBB-BBBBB-BBB39-XKXR3
NBBBB-BBBBB-BBBBB-BBB48-82QF3
```
Which are all valid `Windows 10 Enterprise Volume:GVLK` keys. This is an artifact of the thing being a pretty simple encoding scheme for a bitfield. You simply iterate serial numbers with a given group ID and adjust the checksum until you match the template. This is pretty slow in Python so I recommend running this with either PyPy (the JIT makes it a lot faster, but still Python levels of performance) or asking me for the C version of it.

## Fun stuff you can do with product keys

### Tiny Disclaimer

keycutter is not a keygen by any means. Generic keys are freely available from Microsoft (`product.ini`) and keys made by this tool have no more meaning than these.

### Recovering partially censored product keys

People sometimes post product keys online and only censor one or two quintets in the middle. As long as you know the most important values of the key (group, checksum, and at least parts of serial and security, all of which can be read from the label and the partial key), you can iterate over the "missing part" until the checksum is correct.

If you make photos of key stickers often, you can censor just the first 1.5 quintets and you'll be safe against this.

### Cool templates

The coolest template with the easiest-to-memorize keys (it's a fun exercise to write weird looking Windows keys from memory and look at the horror on people's faces when they actually fucking work) is undoubtedly `NBBBB-BBBBB-BBBBB-BBB` (`B` is the base24 equivalent of the value `0` and `N` on the first position also encodes a `0`), though there are a few other cool things you could write. `NYMPH-CRYPT-WHYTF-KKK` and `BVYNG-GF2GT-PVXXY` are some of these. When looking for words to fit in there remember the alphabet and that the `N` can only be used once.

### Funny key(s)

It is common knowledge that Windows likes to break. Most commonly this is due to how terrible it is at validation - it's somewhat good at validating whether state is **technically valid** but absolutely incapable of detecting and acting on if it's actually **sane**. You can make it do anything by giving it the right file in the right format in the right place. It's like a living human organism the fucking thing - unfathomable complexity and great resilience but no mechanism to save it from itself.

It is trivial to drive it insane - one of the many things it absolutely does not understand is null keys. Give Windows a key with the Group ID set to `0` and it will.. choose the edition at random.. What's better, it will choose a different edition depending on what **time and date** you install the key.

A few example funny keys:

 - `NBBBB-BBBBB-BBBBB-BBBB4-3C3YB`
 - `NBBBB-BBBBB-BBBBB-BBBGQ-JTQYB`
 - `NBBBB-BBBBB-BBBBB-BBBVH-7QM7M`
 - `NBBBB-BBBBB-BBBBB-BBBXJ-RXY7M`

## Fun things

### Partner keys / _CountrySpecific Editions

These fun editions of Windows have a neat little "feature" that locks them to a specific (Chinese) language pack. Installing a Pro-/CoreCountrySpecific key will effectively brick your device if the appropriate licenses for it are present in the system. This is also the case with so-called "partner keys".

Partner keys can be found in various tools (the most fun one being `GatherOsState`) and they have the neat little feature that they will also enforce Chinese at boot but they're **not** for the *CountrySpecific editions.

These keys are as follows:
 - Tencent:
    - `D7MXN-HGMTK-3DY7V-T9PTM-KD8DC` (RTM Core Retail)
    - `DYYRT-NY9VP-4CB2F-8VC7H-DRTKR` (RTM Professional Retail)
 - Qihoo:
    - `WCBQD-VN8PB-FH2RR-WPFCX-3RTKM` (RTM Core Retail)
    - `X9NV3-MCH4F-M3G24-2PKR2-BTDT3` (RTM Professional Retail)
 - mstest:
    - nothing interesting.

Again, installing these will make your install BSOD on boot if appropriate licenses are present.

Here are sample policy values associated with these keys:
```xml
<sl:policyInt name="Security-SPP-Reserved-Store-Token-Required" attributes="override-only">0</sl:policyInt>
<sl:policyInt name="Kernel-MUI-Number-Allowed" attributes="reboot-required, override-only">1</sl:policyInt>
<sl:policyInt name="Internet-Browser-License-LicensedPartnerID" attributes="override-only">1</sl:policyInt>
<sl:policyStr name="Security-SPP-Reserved-Windows-Version-V2" attributes="override-only">10.0</sl:policyStr>
<sl:policyStr name="Kernel-MUI-Language-Allowed" attributes="reboot-required, override-only">zh-TW;zh-CN;zh-HK</sl:policyStr>
<sl:policyInt name="Security-SPP-WriteWauMarker">1</sl:policyInt>
<sl:policyStr name="Security-SPP-Reserved-Family" attributes="override-only">Professional</sl:policyStr>
```