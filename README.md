## This fork is just a website overhaul

added many controlls etc to the webpage and made it auto detect if the cam is using port 22785 or 22789 also can have many useres view the webpage at same time.

<img width="997" height="939" alt="image" src="https://github.com/user-attachments/assets/9e0815c1-0029-4908-90cb-9389e2b37552" />









# MJPEG Mirror for Suear "Smart" Ear Cleaners  
**Author: Sean Pesce**  

<p align="center">
<img align="center" title="Example clip from MJPEG stream" src="https://github.com/SeanPesce/Suear-Web-Viewer/blob/main/image/example.webp?raw=true" alt="Example clip from MJPEG stream" width="320px">
</p>  


## Overview  
A utility for converting [Suear "smart" earwax cleaner](https://play.google.com/store/apps/details?id=com.i4season.bkCamera) video streams to MJPEG for general-purpose use.  

**NOTE:** This tool has only been tested with the [LEIPUT X6](https://www.amazon.com/Ear-Wax-Removal-Remover-Android%EF%BC%88Black%EF%BC%89/dp/B09KZ8TS7L), but it should work for any product that uses `libWifiCamera.so` and/or the Suear mobile app (`com.i4season.bkCamera` - [Google Play](https://play.google.com/store/apps/details?id=com.i4season.bkCamera)/[iOS](https://apps.apple.com/us/app/suear/id1567383367)/[Direct APK download](https://web.archive.org/web/20230117012623/http://120.79.9.129/ypc/apk/Suear_V1.1.086.apk)) for video streaming in its client implementation. Relevant brands likely include:  

 * [AIDELF](https://www.amazon.com/Wireless-Endoscope-Otoscope-Waterproof-Compatible/dp/B09NLVNXQ8)
 * [BEBIRD](https://www.amazon.com/BEBIRD%C2%AE-Removal-Otoscope-Silicone-Compatible/dp/B08M9G18H3)
 * [Carenart](https://www.amazon.com/Removal-Wireless-Cleaning-Compatible-Android/dp/B09FLM4TD7)
 * [COSLUS](https://www.amazon.com/Ear-Wax-Removal-Tool-Camera/dp/B0BGP843CH)
 * [DEETOK](https://www.amazon.com/Removal-Cleaner-Camera-Otoscope-Android/dp/B0BKTMKZKJ)
 * [DJROLL](https://www.amazon.com/DJROLL-Removal-Endoscope-Wireless-Otoscope/dp/B09BC71914)
 * [Fyobyye](https://www.amazon.com/Removal-Cleaner-Camera-Otoscope-Android/dp/B0BLXM7QPT)
 * [Girug](https://www.amazon.com/Removal-Otoscope-Camera-Cleaner-Android/dp/B0BHT3KPMQ)
 * [Hasako](https://www.amazon.com/Removal-Cleaner-Camera-Candles-Android/dp/B0BKG9SNHJ)
 * [Jaydear](https://www.amazon.com/Removal-Earwax-Remover-Cleaner-Otoscope/dp/B0BBZKCZM3)
 * [Kolrry](https://www.amazon.com/Removal-Cleaner-Cleaning-Remover-Smartphones/dp/B0BDRZXH1X)
 * [LEIPUT](https://www.amazon.com/Ear-Wax-Removal-Remover-Android%EF%BC%88Black%EF%BC%89/dp/B09KZ8TS7L)
 * [Loyker](https://www.amazon.com/Removal-Cleaner-Cleaning-Otoscope-Android/dp/B0B9ZSKC99)
 * [RILIAM](https://www.amazon.com/Removal-Cleaner-Otoscope-Waterproof-Android/dp/B09NRGLGNX)
 * [ROOZADE](https://www.amazon.com/ROOZADE-Roozade-Earpick-Set-Black/dp/B0B63TYY79)
 * [SKFMA](https://www.amazon.com/earwax4ws423-Wireless-Otoscope-Endoscope-new34er4r3/dp/B09VBHG5C8)
 * [WXGTAC](https://www.amazon.com/Removal-Cleaner-Compatible-Android-Accessories/dp/B0BLBT3KP8)
 * [Xlife](https://www.amazon.com/Xlife-Removal-Remover-Blackhead-Cleaner/dp/B09QQ6X99W)
 * [Yaej](https://www.amazon.com/Cleaner-Removal-Cleaning-Otoscope-Android/dp/B09R4T1LZ3)
 * [YEOUEOZ](https://www.amazon.com/Removal-Camera-Cleaning-Compatible-Android/dp/B0B8CY2G43)


...and many, many more. Search for "Suear" on [Amazon](https://www.amazon.com/s?k=suear) for more examples.


## Usage  

 * Power on the Suear device  
 * Connect to the Suear WiFi  
 * Start the stream mirror: `python3 suear_mirror.py --no-ssl`  

With the stream mirror running, you can view the live video in a number of ways:  

 * In a web browser; navigate to `http://127.0.0.1:45100`  
 * In VLC (GUI); go to *Media*→*Open Network Stream...*, set the URL to `http://127.0.0.1:45100/stream`, and then click *Play*  
 * In VLC (command-line); run `vlc http://127.0.0.1:45100/stream`  
 * With ffmpeg; run `ffplay -i http://127.0.0.1:45100/stream`  


## SSL/TLS    

The video stream can also be transported over TLS for security. This document won't walk you through setting up your own [PKI](https://myhomelab.gr/linux/2019/12/13/local-ca-setup.html), but the following command will generate a key pair for encrypting traffic with TLS:  

```
openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out cert.crt -keyout private.key
```

To start the stream mirror over HTTPS, specify the TLS key pair in the shell command:  

```
python3 suear_mirror.py cert.crt private.key
```

The HTTPS stream will then be accessible at `https://127.0.0.1:45100/stream`.  


## Contact  
If you find any bugs, please open a new [GitHub issue](https://github.com/SeanPesce/Suear-Web-Viewer/issues/new).  


## Related Projects  
 * **[Spade Web Viewer](https://github.com/SeanPesce/Spade-Web-Viewer)**, a similar project for the [Axel Glade Spade](https://www.axelglade.com/collections/e) brand of "smart" earwax cleaners.  


## Acknowledgements  
 * **[Damien Corpataux](https://github.com/damiencorpataux)**, whose [MJPEG implementation](https://github.com/damiencorpataux/pymjpeg) was used as a reference for this project.   


## License  

[GNU General Public License v2.0](LICENSE)  


---------------------------------------------

For unrelated inquiries and/or information about me, visit my **[personal website](https://SeanPesce.github.io)**.  

