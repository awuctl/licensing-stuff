# Details

This will go into a bit more detail on how it all works. 

## What is keycutter

Keycutter is a tool for encoding and decoding `msft:rm/algorithm/pkey/2009` algorithm product keys. If you're under 30, most product keys you've seen in your life are this exact type of product key.

## What even is a product key?

You may remember needing product keys to activate Windows at all. Nowadays they are rarely (but still) used for this purpose.

You will see many product keys just laying around on the [internet](https://massgrave.dev/hwid.html#Supported_Products) and you will notice that they do indeed sometimes work. These are **generic keys**.

### Generic keys

These serve no purpose other than to inform the operating system what edition it is or (by installing it) that it should change into another edition or use a different activation channel (Volume/Retail). Remember that changing editions doesn't necessarily imply an upgrade (like from Home to Pro).

They are taken from Microsoft ([KMS client keys](https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys)), [product.ini](glossary#productini) and from a few [executables](glossary#pkeyhelperdll--gatherosstateexe--setupcoredll-keys).

For the purposes of your own sanity, think of all keys keycutter makes as generic.

## How does a product key work?

When you install a product key (as in run `slmgr.vbs -ipk [key]`) it's decoded into a few values (more on which in the keycutter source) and a few actions can be taken on what they are. You can read up on what these values are [here](product-keys#structure). Here's a more detailed explanation of what they actually are/do.

### Structure

#### Group

This value specifies what product the key is actually for. This will be things like:

 - `Win 10 RTM Professional Retail`
 - `Win 10 RTM Professional Volume:MAK`
 - `Win 10 RTM Enterprise Volume:GVLK`
 - `Office16_HomeBusinessPipcR_PIN`
 - `Visual Studio 2022 RTM  Perpetual All Retail`

Generally this will mean what edition of the product the key is for and by which [channel](glossary#product-key-channel) it activates.

#### Serial

This is the serial number of the key. It is actually sequential so you're able to tell how many keys of a particular type were made (give or take a few hundred or thousand). This value is also used to determine the specific license that a key installs (more on that later).

#### Secret

This is the secret value that determines whether the key is actually completely 100% valid and genuine. It is hinted to be a SHA256 HMAC but the key for this HMAC is obviously neither public nor publicly known.

#### Checksum

This is a CRC32/MPEG-2 checksum truncated to 10 bits. You can see exactly how it's derived in the source.

#### Upgrade bit

This determines whether the key is an upgrade channel key or not. This value doesn't seem to be used anymore and the keys that have this bit work a bit differently.

#### Extra bit

This is an artifact of the encoding, not an actual field. You can encode a tiny bit beyond the specified fields because log2(24^24 * 25) > 114. This can get you twin keys described [here](product-keys#twin-keys).

### Installation

When you decode the product key you will want to know what it's for - that's where `pkeyconfig` (*Product Key Configuration*) comes in.

`pkeyconfig[…].xrm-ms` are files that describe all product keys recognized by a given piece of software. You will find that on Windows it's split into three different files - the regular `pkeyconfig.xrm-ms`, one for keys from older versions of Windows (`downlevel`) and another for CSVLK keys (`csvlk`).

Pkeyconfigs have the following types of information:

 - Configurations:
   - **Configuration ID**
   - Group ID
   - Edition ID
   - Description
   - Key type
 - Key ranges:
   - Ref. **Configuration ID**
   - Part number
   - EULA type
   - is valid?
   - **Start**
   - **End**
 - Public keys:
   - **Group ID**
   - Algorithm
   - Public Key

#### Configuration

This entry describes what a **Group ID** points at.

The Edition ID along with the Description give a pretty solid idea of what the key is for.

Sample configuration definition:

```xml
<Configuration>
    <ActConfigId>{73111121-5638-40f6-bc11-f1d7b0d64300}</ActConfigId>
    <RefGroupId>3290</RefGroupId>
    <EditionId>Enterprise</EditionId>
    <ProductDescription>Win 10 RTM Enterprise Volume:GVLK</ProductDescription>
    <ProductKeyType>Volume:GVLK</ProductKeyType>
    <IsRandomized>false</IsRandomized>
</Configuration>
```

#### Key Range

This entry specifies a single (there can be and usually are many ranges for one config) **range of serial numbers** for product keys of a given **configuration ID**.

Two important values here are **Start** and **End**. These specify the range of serial numbers described by the entry. 

The most interesting value here, ignoring the actual range bounds, is the part number. This is the string you will see on product key stickers and in PidGenX tools and it can tell you a fair bit if you learn to look for them.

Paired with the Configuration this gives you precisely what the key is for and based on these the software can install appropriate licenses for your key. Ultimately it's more important what the range points at, though it is most often exactly what the Configuration says with not much more to add other than the part number.

Having said that, there are a few ranges that add a lot more meaning to what the keys actually do:
 - [Partner keys](product-keys#partner-keys--_countryspecific-editions)
 - Old Pro Education
 - […]

"Old Pro Education" is referring to specific ranges of keys for Windows 10 Pro that were sold as "Pro Education" before Pro Education became its own edition. These would be keys with the following part numbers: `X19-99485`, `X19-99482`, `X19-99498`, `X19-99499`, `X19-99508`, `X19-99520`, `X20-30039`, `X20-30040`, `X20-30049`, `X20-30047`, `X20-30050`, `X20-30053`, `X20-30051`, `X20-30052`, `X20-36699`, `X20-36700`, `X20-36702`, `X20-36701`, `X20-36693`, `X20-36696`, `X18-15587`, `X18-15584`, `X18-95491`, `X18-95458`, `X18-15577`, `X18-15575`, `X18-95498`, `X18-95466`. Installing a key from any of these (supposedly Pro) ranges will automatically migrate to Pro Education.

Sample key range definition:
```xml
<KeyRange>
    <RefActConfigId>{73111121-5638-40f6-bc11-f1d7b0d64300}</RefActConfigId>
    <PartNumber>[TH]X19-98698</PartNumber>
    <EulaType>Volume</EulaType>
    <IsValid>true</IsValid>
    <Start>0</Start>
    <End>999999998</End>
</KeyRange>
```

#### Public key

This specifies the algorithm and algorithm used by a group. This implies that group IDs are shared between both different products (Windows/Office/Visual Studio) and different algorithms (986, 2005, 2009).

The public key value specifies what public key encryption and/or key is used to verify the authenticity of a product key. For 2005 product keys it's an RSA public key blob in a non-standard format. For 2009 keys, it simply says that the keys are verified (only online) with a SHA256 HMAC.

Sample public key entry:

```xml
<PublicKey>
    <GroupId>3290</GroupId>
    <AlgorithmId>msft:rm/algorithm/pkey/2009</AlgorithmId>
    <PublicKeyValue>bXNmdDpwa2V5LzIwMDkvY3J5cHRvcHJvZmlsZS9obWFjL3NoYTI1Ng==</PublicKeyValue>
</PublicKey>
```

Decoded `PublicKeyValue` reads `msft:pkey/2009/cryptoprofile/hmac/sha256`.
