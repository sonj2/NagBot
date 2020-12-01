#set window to not be resizable
from kivy.config import Config
Config.set('graphics', 'resizable', False)

#set window size
from kivy.core.window import Window
Window.size = (500, 800)

#imports
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import *

from calendar_ui import CalendarWidget, DatePicker
from time_picker import TimePicker

class CalendarPage(BoxLayout):
    def __init__(self, **kwargs):
        super(CalendarPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

        #Title "Calendar" at top of page
        self.title = Label(text="Calendar", font_size=25)
        self.title.size_hint_y = None
        self.title.height = 58
        self.add_widget(self.title)

        #Calendar Widget
        self.cal = CalendarWidget()
        self.cal.size_hint_y = None
        self.cal.height = 400
        self.add_widget(self.cal)

        #Buttons
        self.button1 = Button(text="Today", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

        self.button2 = Button(text="View Schedule", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

        self.button3 = Button(text="View Blacklist", font_size=20)
        self.button3.bind(on_press=self.button3_act)
        self.add_widget(self.button3)

    #Button 1 - Today - resets the calendar widget to the current date
    def button1_act(self, instance):
        self.remove_widget(self.cal)
        self.remove_widget(self.button1)
        self.remove_widget(self.button2)
        self.remove_widget(self.button3)

        self.cal = CalendarWidget()
        self.cal.size_hint_y = None
        self.cal.height = 400

        self.add_widget(self.cal)
        self.add_widget(self.button1)
        self.add_widget(self.button2)
        self.add_widget(self.button3)

    #Button 2 - View Schedule - moves to SchedulePage
    def button2_act(self, instance):
        nag_bot_app.schedule_page.update_date(self.cal.active_date)
        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Schedule"
        nag_bot_app.schedule_page.previous_screen = "Calendar"

    #Button 3 - View Blacklist - moves to the BlacklistPage
    def button3_act(self, instance):
        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Blacklist"
        nag_bot_app.blacklist_page.previous_screen = "Calendar"


class SchedulePage(BoxLayout):
    def __init__(self, **kwargs):
        super(SchedulePage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

        #Title - "Schedule" at top - left aligned
        self.title = Label(text="Schedule", font_size=25, halign="left", valign="middle",
                            padding=(10,0))
        self.title.bind(size=self.title.setter('text_size'))
        self.title.size_hint_y = None
        self.title.height = 58
        self.add_widget(self.title)

        #Scrolling area for schedule
        self.scroll = ScrollView()
        self.scroll.size_hint_y = None
        self.scroll.height = 500
        self.add_widget(self.scroll)

        #some variables for making the schedule
        hrs = []
        hrs.extend(range(1,13))
        hrs.extend(range(1,13))
        mins = ["00","30"]

        block_size = 90

        text = ""
        for x in range(1,500):
            text = text + str(x) + '\n'

        #Wrapper widget for schedule - using FloatLayout
        self.float = self.layout = FloatLayout(size_hint_y=None)
        self.float.height = block_size * 2 * len(hrs) + 20
        self.scroll.add_widget(self.float)

        y = self.float.height-20 # y pos for lines - start at 10px (room for label)

        #Add lines and time stamps
        is_PM = False
        with self.float.canvas:
            for hr in hrs:
                if hr == 12:
                    is_PM = not is_PM
                for min in mins:
                    Line(points=[0, y, Window.width, y], width=1)

                    if not is_PM:
                        label = Label(text="%d:%s AM"%(hr,min), pos=(-200,
                                    y-self.float.height/2 +10),
                                    font_size=20)
                    else:
                        label = Label(text="%d:%s PM"%(hr,min), pos=(-200,
                                    y-self.float.height/2 +10),
                                    font_size=20)

                    self.float.add_widget(label)

                    y -= block_size

        #Buttons
        self.button1 = Button(text="Add Work/Break Block", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

        self.button2 = Button(text="Back to Calendar", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

    def update_date(self, date):
        self.title.text = "Schedule " + str(date[1]) + '/' + str(date[0]) + '/' + str(date[2])

    #Button1 - Add Work/Break Block
    def button1_act(self, instance):
        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Edit Block"
        nag_bot_app.edit_block_page.previous_screen = "Schedule"
        pass

    #Button 2 - Back to Calendar - go back to the CalendarPage
    def button2_act(self, instance):
        nag_bot_app.screen_manager.transition.direction = 'right'
        nag_bot_app.screen_manager.current = "Calendar"
        nag_bot_app.calendar_page.previous_screen = "Schedule"


class ToDoListPage(BoxLayout):
    def __init__(self, **kwargs):
        super(ToDoListPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""


class AddTaskPage(BoxLayout):
    def __init__(self, **kwargs):
        super(AddTaskPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""


class BlacklistPage(BoxLayout):
    def __init__(self, **kwargs):
        super(BlacklistPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

        #Title "Blacklist" at top of page
        self.title = Label(text="Blacklist", font_size=25)
        self.title.size_hint_y = None
        self.title.height = 58
        self.add_widget(self.title)

        #Scrolling area for blacklist
        self.scroll = ScrollView()
        self.scroll.size_hint_y = None
        self.scroll.height = 500
        self.add_widget(self.scroll)

        #Buttons
        self.button1 = Button(text="Add to Blacklist", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

        self.button2 = Button(text="Done", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

    #Button1 - Add to Blacklist
    def button1_act(self, instance):
        pass

    #Button 2 - Done - go back to previous page
    def button2_act(self, instance):
        nag_bot_app.screen_manager.transition.direction = 'right'
        nag_bot_app.screen_manager.current = self.previous_screen
        nag_bot_app.screen_manager.get_screen(self.previous_screen).previous_screen = "Blacklist"


class EditBlockPage(BoxLayout):
    def __init__(self, **kwargs):
        super(EditBlockPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

        #Title "Add/Edit Block" at top of page
        self.title = Label(text="Add/Edit Block", font_size=25)
        self.title.size_hint_y = None
        self.title.height = 58
        self.add_widget(self.title)

        #Float layout for form
        self.form = GridLayout(cols=2)
        self.form.size_hint_y = None
        self.form.height = 550
        self.add_widget(self.form)

        #Form elements

        #Dropdown Selection
        label = Label(text="Work/Break:", font_size=20)
        self.form.add_widget(label)

        self.dropdown = DropDown()

        for item in ["Work", "Break"]:
            btn = Button(text= item,size_hint_y=None, height=38)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)

        anchor = AnchorLayout(anchor_x='center', anchor_y='top')
        self.dropbutton = Button(text='SELECT',size_hint_y=None, height=44)
        self.dropbutton.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.dropbutton, 'text', x))
        anchor.add_widget(self.dropbutton)
        self.form.add_widget(anchor)

        #Start Date
        self.form.add_widget(Label(text="Start Date:", font_size=20))
        self.start_date = DatePicker(size_hint_y=None, height=60)
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        anchor.add_widget(self.start_date)
        self.form.add_widget(anchor)

        #Start Time
        self.form.add_widget(Label(text="Start Time:", font_size=20))
        self.start_time = TimePicker(size_hint_y=None, height=60)
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        anchor.add_widget(self.start_time)
        self.form.add_widget(anchor)

        #End Date
        self.form.add_widget(Label(text="End Date:", font_size=20))
        self.end_date = DatePicker(size_hint_y=None, height=60)
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        anchor.add_widget(self.end_date)
        self.form.add_widget(anchor)

        #End Time
        self.form.add_widget(Label(text="End Time:", font_size=20))
        self.end_time = TimePicker(size_hint_y=None, height=60)
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        anchor.add_widget(self.end_time)
        self.form.add_widget(anchor)

        #Buttons
        self.button1 = Button(text="Add Tasks", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

        self.button2 = Button(text="Specialized Blacklist", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

        self.button3 = Button(text="Submit", font_size=20)
        self.button3.bind(on_press=self.button3_act)
        self.add_widget(self.button3)

    #Button 1 - Add Tasks
    def button1_act(self, instance):
        pass

    #Button 2 - Specialized Blacklist - go to Blacklist screen
    def button2_act(self, instance):
        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Blacklist"
        nag_bot_app.blacklist_page.previous_screen = "Edit Block"
        pass

    #Button 3 - Submit - return to previous screen
    def button3_act(self, instance):
        nag_bot_app.screen_manager.transition.direction = 'right'
        nag_bot_app.screen_manager.current = self.previous_screen
        nag_bot_app.screen_manager.get_screen(self.previous_screen).previous_screen = "Edit Block"
        pass

class EditBlacklistPage(BoxLayout):
    def __init__(self, **kwargs):
        super(EditBlacklistPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

class NagBotApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        screen = Screen(name="Calendar")
        self.calendar_page = CalendarPage()
        screen.add_widget(self.calendar_page)
        self.screen_manager.add_widget(screen)

        screen = Screen(name="Schedule")
        self.schedule_page = SchedulePage()
        screen.add_widget(self.schedule_page)
        self.screen_manager.add_widget(screen)

        screen = Screen(name="Edit Block")
        self.edit_block_page = EditBlockPage()
        screen.add_widget(self.edit_block_page)
        self.screen_manager.add_widget(screen)

        screen = Screen(name="Blacklist")
        self.blacklist_page = BlacklistPage()
        screen.add_widget(self.blacklist_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def on_stop(self):
        import sys
        sys.exit()

if __name__ == "__main__":
    nag_bot_app = NagBotApp()
    nag_bot_app.run()