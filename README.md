# WTAN - WindowsToAndroidNotifications

Simple python application that sends your Windows 10 toast notifications to your phone.

Supported channels:
- [ntfy.sh](https://ntfy.sh)
- Telegram (in progress)

---

### How to run the application

Requirements: Python > v3.6 and pip (and pipenv too if you'd like to separate things).

Install dependencies
````commandline
pip install -r requirements.txt
````

Run with python (or just run the .exe from the releases page)
````commandline
python notif.py
````

---
### How to - ntfy

1. Run the application, you should see a screen like below:
![img.png](imgs/img.png)
2. Generate a new ntfy room code by clicking the "Generate random" button.
3. Start listening.
4. Switch over to your Android phone.
5. Install the app ntfy from the PlayStore.
6. You should see something like this:
![](imgs/ntfy1.png)
7. Click the "+" sign.
![](imgs/ntfy2.png)
8. Here, insert the code that was generated by the application (be sure to check the second checkbox if you want notifications while the phone is sleeping).
![](imgs/ntfy4.png)
9.Finally, confirm the prompt and you should have a list of notifications like this that will be updated whenever your Win10 gets a toast notification:
![](imgs/ntfy5.png)
---

### How to - Telegram

UNDER CONSTRUCTION
