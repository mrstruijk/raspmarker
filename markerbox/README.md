MarkerBox

Run:

When using random markers:

python markerbox.py 1

When using markers from input:

python markerbox.py

---
# TODO:
1. Make GUI have a third tab: all markers. This is also where MQTT markers can easily be observed.
2. Make MQTT optional
3. Make args be `bool` `bool` `bool` for: use random markers, use GUI, use MQTT.
4. Display better (in both console and GUI) where each marker came from: from LPT? Sent to MQTT? Command from MQTT?


---

Uses GPIO pins:
- IN = 21, 20, 16, 12, 7, 8, 25, 24
- OUT = 26, 19, 13
![Pi pins](https://www.raspberrypi.com/documentation/computers/images/GPIO-Pinout-Diagram-2.png?hash=df7d7847c57a1ca6d5b2617695de6d46):

