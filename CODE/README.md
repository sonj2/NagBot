# NagBot
SD&amp;D project

## The Files

**NagBot.py** - The core of the project, contains the MAIN and the GUI and refeeces the other files. Be sure to install kivy ```conda install kivy``` and ```pip install pywin32``` for Windows pop up notifications.

**window_grabber.py** - used for grabbing the active window. Make sure to install the depedencies mentioned in the comments.

**database.py** - contains the class stucture for storing all info necessary to operate the NagBot app

**alerts.py** - contains the alert system which will notify the user when they are entering/exiting a block and "nag" them if they go off task (vist a denylisted site during a Work Block)

## External Libraries - from Kivy, most likely will not need editing

**calendar_data.py** - dependecy of calendar_ui.py

**calendar_ui.py** - the CalendarWidget & DatePicker widgets used in NagBot.py

**circular_layout.py** - dependecy of time_picker.py

**time_picker.py** - the TimePicker widget used in NagBot.py

## Future Features

The Denylist page should allow users to get suggested keywords by detecting sites visited, listing them and then scanning for common words among the titles

Ability to shift/change the work/break blocks though the notification pop up.

Ability to import / export calendar data and genreate a summary of hours worked / hours spent taking a break

## When using the Denylist

**Note:** when adding keywords to a denylist, realize we look at the Title of the active screen, not the URL. So "youtube" will work but don't put www. or stuff specific to the URL. In Chrome if you hover over the Tab the title
will appear. This is what we check against. Similarly for most apps it will be what appears at the top (upper left) of the window.

## UI Flowchart (UI may differ a bit since we are still in beta)
![](/images/GUI_Flowchart.svg)