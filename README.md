# raspmarker

When using random markers:

`python kivy_GUI.py 1`

When using markers from input:

`python kivy_GUI.py 0`

It defaults to using input markers, so the `0` is redundant.

---

This now works:
- You need to run the `python kivy_GUI.py` command first in one terminal instance (while in the venv).
- In another terminal instance you can `python mqtt_marker_handler.py`, also venv. 
If you start these in the wrong order, the MQTT marker handler throws a fit.

