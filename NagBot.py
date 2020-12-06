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
from kivy.uix.checkbox import CheckBox

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import *

from calendar_ui import CalendarWidget, DatePicker
from time_picker import TimePicker

from database import *
import win32api

import datetime
from copy import copy, deepcopy

import threading
from alerts import AlertSystem

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
        nag_bot_app.schedule_page.gen_schedule()

        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Schedule"
        nag_bot_app.schedule_page.previous_screen = "Calendar"

    #Button 3 - View Blacklist - moves to the BlacklistPage
    def button3_act(self, instance):
        nag_bot_app.blacklist_page.gen_list()

        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Blacklist"
        nag_bot_app.blacklist_page.previous_screen = "Calendar"


class SchedulePage(BoxLayout):
    def __init__(self, **kwargs):
        super(SchedulePage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

        self.date = None
        self.button_to_block = {}

        #Title - "Schedule" at top - left aligned
        self.title = Label(text="Schedule",
            font_size=25,
            halign="left",
            valign="middle",
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

        #generate schedule
        self.gen_schedule(remove=False)

        #Buttons
        self.button1 = Button(text="Add Work/Break Block", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

        self.button2 = Button(text="Back to Calendar", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

    def update_date(self, date):
        self.date = date
        self.title.text = "Schedule " + str(date[1]) + '/' + str(date[0])
        self.title.text += '/' + str(date[2])

    def gen_schedule(self, remove=True):
        self.button_to_block = {}

        #Wrapper widget for schedule - using FloatLayout
        if remove:
            self.scroll.remove_widget(self.float)
        self.float = FloatLayout(size_hint_y=None)
        self.scroll.add_widget(self.float)

        #some variables for making the schedule
        hrs = [12]
        hrs.extend(range(1,13))
        hrs.extend(range(1,13))
        mins = ["00","30"]

        block_size = 90

        #set height of float to fit schedule
        self.float.height = block_size * 2 * len(hrs) + 20

        # y pos for lines - start at 20px (room for label)
        y = self.float.height-20

        #Add lines and time stamps
        is_PM = True
        with self.float.canvas:
            for hr in hrs:
                if hr == 12:
                    is_PM = not is_PM
                for min in mins:
                    Line(points=[0, y, Window.width, y], width=1)

                    if not is_PM:
                        label = Label(text="%d:%s AM"%(hr,min),
                            pos=(-200, y-self.float.height/2 +10),
                            font_size=20)
                    else:
                        label = Label(text="%d:%s PM"%(hr,min),
                            pos=(-200, y-self.float.height/2 +10),
                            font_size=20)

                    self.float.add_widget(label)

                    y -= block_size

        #Add the blocks
        if self.date != None:
            date = datetime.datetime(day=self.date[0], month=self.date[1],
                year=self.date[2])
            day = datetime.date(day=self.date[0], month=self.date[1],
                year=self.date[2])
            blocks = db.get_blocks(day)

            for block in blocks:
                start_delta = (block.start-date).total_seconds()/60

                duration = (block.end-block.start).total_seconds()/60

                start_px = 20 + start_delta*3
                height = duration*3

                text = block.type
                text += block.start.strftime(' %I:%M %p')
                text += block.end.strftime(' - %I:%M %p')

                button = Button(text=text, font_size=20)
                if block.type == "Work":
                    button.background_color = [1, 0, 0, 1] #red RGBA
                    button.bind(on_press=self.work_act)

                elif block.type == "Break":
                    button.background_color = [0, 1, 0, 1] #green RGBA
                    button.bind(on_press=self.break_act)

                else:
                    print("ERROR: Invalid Block Type")

                button.x = 200
                button.y =  self.float.height - start_px - height
                button.size_hint_x = None
                button.size_hint_y = None
                button.width = 300
                button.height = height
                self.float.add_widget(button)

                self.button_to_block[button] = block

                #remove block button
                button = Button(text="X", font_size=20)

                button.x = 100
                button.y =  self.float.height - start_px - height
                button.size_hint_x = None
                button.size_hint_y = None
                button.width = 100
                button.height = height
                button.bind(on_press=self.remove_block)
                self.float.add_widget(button)

                self.button_to_block[button] = block

    def remove_block(self, instance):
        block = self.button_to_block[instance]
        db.remove_block(block.id)
        self.gen_schedule()

    def work_act(self, instance):
        block = self.button_to_block[instance]

        nag_bot_app.to_do_page.update_block(block)
        nag_bot_app.screen_manager.transition.direction = 'up'
        nag_bot_app.screen_manager.current = "To Do List"
        nag_bot_app.to_do_page.previous_screen = "Schedule"

    def break_act(self, instance):
        block = self.button_to_block[instance]

        nag_bot_app.edit_block_page.edit_block(block)

        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Edit Block"
        nag_bot_app.edit_block_page.previous_screen = "Schedule"

    #Button1 - Add Work/Break Block
    def button1_act(self, instance):
        rst_date = datetime.date(day=self.date[0], month=self.date[1],
            year=self.date[2])
        nag_bot_app.edit_block_page.reset(rst_date)

        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Edit Block"
        nag_bot_app.edit_block_page.previous_screen = "Schedule"

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

        self.block = None

        #Block label at top of page
        self.label = Button(text="", font_size=20)
        self.label.size_hint_y = None
        self.label.height = 58
        self.add_widget(self.label)

        #Title "To Do List" under label - left aligned
        self.title = Label(text="To Do List",
            font_size=25,
            halign="left",
            valign="middle",
            padding=(10,0))
        self.title.bind(size=self.title.setter('text_size'))
        self.title.size_hint_y = None
        self.title.height = 58
        self.add_widget(self.title)

        #Scrolling area for list
        self.scroll = ScrollView()
        self.scroll.size_hint_y = None
        self.scroll.height = 400
        self.add_widget(self.scroll)

        #ToDoList content
        self.list = GridLayout(cols=3)
        self.list.size_hint_y = None
        self.list.height = 400
        self.scroll.add_widget(self.list)

        #Buttons
        self.button1 = Button(text="Add Task", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

        self.button2 = Button(text="Edit Work Block", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

        self.button3 = Button(text="Done", font_size=20)
        self.button3.bind(on_press=self.button3_act)
        self.add_widget(self.button3)

    def update_block(self, block):
        self.block = block
        self.update()

    def update(self):
        #update the Block label at top of page
        self.label.text = self.block.type
        self.label.text += self.block.start.strftime(" %m/%d/%Y %I:%M %p")
        self.label.text += self.block.end.strftime(" - %I:%M %p")

        if self.block.type == "Work":
            self.label.background_color = [1, 0, 0, 1] #red RGBA

        elif self.block.type == "Break":
            self.label.background_color = [0, 1, 0, 1] #green RGBA

        #update the actual list
        self.list.clear_widgets()
        self.ui_to_task = {}

        tasks = db.get_tasks(self.block.id)

        if len(tasks) > 5:
            self.list.height = 100 * len(tasks)

        def on_checkbox_active(checkbox, value):
            task = self.ui_to_task[checkbox]
            if value:
                task.completed=True
            else:
                task.competed=False

        #generate list
        for priority in ["High", "Med", "Low"]:
            for task in tasks:
                if task.priority == priority:
                    checkbox = CheckBox(active=task.completed)
                    self.ui_to_task[checkbox] = task
                    checkbox.bind(active=on_checkbox_active)
                    self.list.add_widget(checkbox)
                    description = Label(text=task.description, font_size=20)
                    self.list.add_widget(description)

                    remove = Button(text="Remove", font_size=20)
                    self.ui_to_task[remove] = task
                    remove.bind(on_press=self.remove_task)
                    self.list.add_widget(remove)

    def remove_task(self, button):
        task = self.ui_to_task[button]
        db.remove_task(self.block.id, task.id)
        db.save()
        self.update()

    #Button 1 - Add Task
    def button1_act(self, instance):
        nag_bot_app.add_task_page.set_block(self.block)
        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Add Task"
        nag_bot_app.add_task_page.previous_screen = "To Do List"

    #Button 2 - Edit Work Block
    def button2_act(self, instance):
        nag_bot_app.edit_block_page.edit_block(self.block)

        nag_bot_app.screen_manager.transition.direction = 'down'
        nag_bot_app.screen_manager.current = "Edit Block"
        nag_bot_app.edit_block_page.previous_screen = "To Do List"

    #Button 3 - Done
    def button3_act(self, instance):
        nag_bot_app.screen_manager.transition.direction = 'down'
        nag_bot_app.screen_manager.current = self.previous_screen
        nag_bot_app.screen_manager.get_screen(
            self.previous_screen).previous_screen = "To Do List"


class AddTaskPage(BoxLayout):
    def __init__(self, **kwargs):
        super(AddTaskPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

        self.block = None

        #Title "Add Task" at top of page
        self.title = Label(text="Add Task", font_size=25)
        self.title.size_hint_y = None
        self.title.height = 58
        self.add_widget(self.title)

        #main form inside GridLayout
        self.form = GridLayout(cols=2)
        self.form.size_hint_y = None
        self.form.height = 600
        self.add_widget(self.form)

        label = Label(text="Name:", font_size=20)
        self.form.add_widget(label)
        self.name = TextInput(font_size=20)
        self.form.add_widget(self.name)

        label = Label(text="Priority:", font_size=20)
        self.form.add_widget(label)

        self.dropdown = DropDown()

        for item in ["High", "Med", "Low"]:
            btn = Button(text= item,size_hint_y=None, height=80)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        self.dropbutton = Button(text='SELECT',size_hint_y=None, height=100)
        self.dropbutton.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance,
            x: setattr(self.dropbutton, 'text', x))
        anchor.add_widget(self.dropbutton)
        self.form.add_widget(anchor)

        #additional space fill with labels
        for x in range(4):
            self.form.add_widget(Label())

        #Button
        self.button1 = Button(text="Done", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

    def set_block(self, block):
        self.block = block

    def button1_act(self, instance):
        #provided form is filled out
        if self.name.text != "" and self.dropbutton.text != "SELECT":
            db.add_task(self.block.id, self.name.text,
            self.dropbutton.text)
            db.save()

        nag_bot_app.to_do_page.update()

        nag_bot_app.screen_manager.transition.direction = 'right'
        nag_bot_app.screen_manager.current = "To Do List"

        self.name.text = ""
        self.dropbutton.text = "SELECT"

class BlacklistPage(BoxLayout):
    def __init__(self, **kwargs):
        super(BlacklistPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

        self.specialized = None
        self.ui_to_item = {}

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

        #Blacklist content
        self.list = GridLayout(cols=3)
        self.list.size_hint_y = None
        self.list.height = 500
        self.scroll.add_widget(self.list)

        self.gen_list()

        #Buttons
        self.button1 = Button(text="Add to Blacklist", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

        self.button2 = Button(text="Done", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

    def gen_list(self, specialized=None):
        self.list.clear_widgets()

        self.specialized = specialized
        #Blacklist content
        if specialized == None:
            self.blacklist = db.get_blacklist()
        else:
            self.blacklist = specialized
        self.ui_to_item = {}

        if len(self.blacklist.items) > 5:
            self.list.height = 100 * len(self.blacklist.items)

        def on_checkbox_active(checkbox, value):
            item = self.ui_to_item[checkbox]
            keywords = ", ".join(item.keywords)
            if value:
                item.active=True
            else:
                item.active=False

        for item in self.blacklist.items:
            checkbox = CheckBox(active=item.active)
            self.ui_to_item[checkbox] = item
            checkbox.bind(active=on_checkbox_active)
            self.list.add_widget(checkbox)
            keywords = Label(text=", ".join(item.keywords), font_size=20)
            self.list.add_widget(keywords)

            remove = Button(text="Remove", font_size=20)
            self.ui_to_item[remove] = item
            remove.bind(on_press=self.remove_item)
            self.list.add_widget(remove)

    def remove_item(self, instance):
        item = self.ui_to_item[instance]
        db.remove_blacklist(item.id)
        db.save()
        self.gen_list(specialized=self.specialized)


    #Button1 - Add to Blacklist
    def button1_act(self, instance):
        nag_bot_app.edit_blacklist_page.specialized = self.blacklist
        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Edit Blacklist"
        nag_bot_app.edit_blacklist_page.previous_screen = "Blacklist"

    #Button 2 - Done - go back to previous page
    def button2_act(self, instance):
        nag_bot_app.screen_manager.transition.direction = 'right'
        nag_bot_app.screen_manager.current = self.previous_screen
        nag_bot_app.screen_manager.get_screen(
            self.previous_screen).previous_screen = "Blacklist"


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
        self.dropdown.bind(on_select=lambda instance,
            x: setattr(self.dropbutton, 'text', x))
        anchor.add_widget(self.dropbutton)
        self.form.add_widget(anchor)

        #Start Date
        self.form.add_widget(Label(text="Start Date:", font_size=20))
        self.start_date = DatePicker(size_hint_y=None, height=60)
        self.start_date_anchor = AnchorLayout(anchor_x='center',
            anchor_y='center')
        self.start_date_anchor.add_widget(self.start_date)
        self.form.add_widget(self.start_date_anchor)

        #Start Time
        self.form.add_widget(Label(text="Start Time:", font_size=20))
        self.start_time = TimePicker(size_hint_y=None, height=60)
        self.start_time_anchor = AnchorLayout(anchor_x='center',
            anchor_y='center')
        self.start_time_anchor.add_widget(self.start_time)
        self.form.add_widget(self.start_time_anchor)

        #End Date
        self.form.add_widget(Label(text="End Date:", font_size=20))
        self.end_date = DatePicker(size_hint_y=None, height=60)
        self.end_date_anchor = AnchorLayout(anchor_x='center',
            anchor_y='center')
        self.end_date_anchor.add_widget(self.end_date)
        self.form.add_widget(self.end_date_anchor)

        #End Time
        self.form.add_widget(Label(text="End Time:", font_size=20))
        self.end_time = TimePicker(size_hint_y=None, height=60)
        self.end_time_anchor = AnchorLayout(anchor_x='center',
            anchor_y='center')
        self.end_time_anchor.add_widget(self.end_time)
        self.form.add_widget(self.end_time_anchor)

        #Buttons
        # self.button1 = Button(text="Add Tasks", font_size=20)
        # self.button1.bind(on_press=self.button1_act)
        # self.add_widget(self.button1)

        self.button2 = Button(text="Specialized Blacklist", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

        self.button3 = Button(text="Submit", font_size=20)
        self.button3.bind(on_press=self.button3_act)
        self.add_widget(self.button3)

        self.special_blacklist = None
        self.block = None

    #Button 1 - Add Tasks
    def button1_act(self, instance):
        pass

    #Button 2 - Specialized Blacklist - go to Blacklist screen
    def button2_act(self, instance):
        if self.block == None or self.block.blacklist == None:
            self.special_blacklist = deepcopy(db.get_blacklist())
            nag_bot_app.blacklist_page.gen_list(
                specialized=self.special_blacklist)
        else:
            nag_bot_app.blacklist_page.gen_list(
                specialized=self.block.blacklist)
        nag_bot_app.screen_manager.transition.direction = 'left'
        nag_bot_app.screen_manager.current = "Blacklist"
        nag_bot_app.blacklist_page.previous_screen = "Edit Block"
        pass

    #Button 3 - Submit - add Block, return to previous screen
    def button3_act(self, instance):
        #add Block
        if self.dropbutton.text != "SELECT":
            start_date = self.start_date.text.split('.')
            start_time = self.start_time.text.split(':')
            end_date = self.end_date.text.split('.')
            end_time = self.end_time.text.split(':')

            for x in range(3):
                start_date[x] = int(start_date[x])
                start_time[x] = int(start_time[x])
                end_date[x] = int(end_date[x])
                end_time[x] = int(end_time[x])

            type = self.dropbutton.text
            start = datetime.datetime(start_date[2],start_date[0],start_date[1],
                start_time[0], start_time[1], start_time[1])
            end = datetime.datetime(end_date[2],end_date[0],end_date[1],
                end_time[0], end_time[1], end_time[1])

            try:
                if self.block != None:
                    print("Editing block")
                    db.edit_block(self.block.id, type, start, end)
                    db.save()
                    if self.block.blacklist == None:
                        self.block.blacklist = self.special_blacklist
                else:
                    block = db.add_block(type, start, end)
                    block.blacklist = self.special_blacklist
                    db.save()
                    print("Block Added")
            except EndBeforeStart:
                win32api.MessageBox(0,
                    '''NagBot: Cannot have block end before it starts.
                    The block will not be added.''',
                'End Before Start', 0x00001000)
            except OverlapsExisting:
                win32api.MessageBox(0,
                    '''NagBot: The block you are attempting to add overlaps
                    with an existing block. The block will not be
                    added.''',
                    'Overlaps Existing', 0x00001000)

        #return to previous screen
        nag_bot_app.schedule_page.gen_schedule()
        if self.block != None:
            nag_bot_app.to_do_page.update_block(self.block)

        nag_bot_app.screen_manager.transition.direction = 'right'
        nag_bot_app.screen_manager.current = self.previous_screen
        nag_bot_app.screen_manager.get_screen(
            self.previous_screen).previous_screen = "Edit Block"

    #reset form
    def reset(self,date):
        self.block = None
        self.dropbutton.text = "SELECT"

        self.start_date_anchor.remove_widget(self.start_date)
        self.start_date = DatePicker(size_hint_y=None, height=60,date=date)
        self.start_date_anchor.add_widget(self.start_date)

        self.end_date_anchor.remove_widget(self.end_date)
        self.end_date = DatePicker(size_hint_y=None, height=60, date=date)
        self.end_date_anchor.add_widget(self.end_date)

    def edit_block(self,block):
        self.block = block
        self.dropbutton.text = block.type

        self.start_time.text = block.start.strftime("%H:%M:%S")
        self.end_time.text = block.end.strftime("%H:%M:%S")

        start_date = datetime.date(block.start.year,
            block.start.month,
            block.start.day)
        self.start_date_anchor.remove_widget(self.start_date)
        self.start_date = DatePicker(size_hint_y=None, height=60,
            date=start_date)
        self.start_date_anchor.add_widget(self.start_date)

        end_date = datetime.date(block.end.year,
            block.end.month,
            block.end.day)
        self.end_date_anchor.remove_widget(self.end_date)
        self.end_date = DatePicker(size_hint_y=None, height=60,
            date=end_date)
        self.end_date_anchor.add_widget(self.end_date)



class EditBlacklistPage(BoxLayout):
    def __init__(self, **kwargs):
        super(EditBlacklistPage, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.previous_screen = ""

        #Title "Add/Edit Block" at top of page
        self.title = Label(text="Edit Blacklist", font_size=25)
        self.title.size_hint_y = None
        self.title.height = 58
        self.add_widget(self.title)

        #Keywords
        self.keywords_label = Label(text="Keywords",
            font_size=25,
            halign="left",
            valign="middle",
            padding=(10,0))
        self.keywords_label.bind(size=self.keywords_label.setter(
            'text_size'))
        self.add_widget(self.keywords_label)

        self.keywords = TextInput(font_size=25)
        self.add_widget(self.keywords)

        #Recently Visited Pages
        self.recent_label = Label(text="Recently Visited Pages",
            font_size=25,
            halign="left",
            valign="middle",
            padding=(0,0))
        self.recent_label.bind(size=self.recent_label.setter(
            'text_size'))
        self.add_widget(self.recent_label)

        self.recent_scroll = ScrollView()
        self.recent_scroll.size_hint_y = None
        self.recent_scroll.height = 100
        self.add_widget(self.recent_scroll)

        self.recent_box = BoxLayout(orientation = "vertical")
        self.recent_box.size_hint_y = None
        self.recent_box.height = 500
        self.recent_scroll.add_widget(self.recent_box)

        for x in range(10):
            recent = Label(text="TEST %d"%x,
                font_size=25,
                halign="left",
                valign="top",
                padding=(10,0))
            recent.bind(size=recent.setter(
                'text_size'))
            self.recent_box.add_widget(recent)

        #Common Keywords
        self.common_label = Label(text="Common Keywords",
            font_size=25,
            halign="left",
            valign="middle",
            padding=(10,0))
        self.common_label.bind(size=self.common_label.setter(
            'text_size'))
        self.add_widget(self.common_label)

        self.common_scroll = ScrollView()
        self.common_scroll.size_hint_y = None
        self.common_scroll.height = 100
        self.add_widget(self.common_scroll)

        self.common_box = BoxLayout(orientation = "vertical")
        self.common_box.size_hint_y = None
        self.common_box.height = 500
        self.common_scroll.add_widget(self.common_box)

        for x in range(10):
            common = Label(text="TEST %d"%x,
                font_size=25,
                halign="left",
                valign="top",
                padding=(10,0))
            common.bind(size=common.setter(
                'text_size'))
            self.common_box.add_widget(common)

        #Buttons
        self.button1 = Button(text="Use Common Keywords", font_size=20)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

        self.button2 = Button(text="Reset Recently Visited", font_size=20)
        self.button2.bind(on_press=self.button2_act)
        self.add_widget(self.button2)

        self.button3 = Button(text="Add To Blacklist", font_size=20)
        self.button3.bind(on_press=self.button3_act)
        self.add_widget(self.button3)

        self.specialized = None


    #Button 1 - Use Common Keywords
    def button1_act(self, instance):
        pass

    #Button 2 - Reset Recently Visited
    def button2_act(self, instance):
        pass

    #Button 3 - Add To Blacklist - add keywords to blacklist,
    #return to previous screen
    def button3_act(self, instance):
        if self.specialized == None:
            self.blacklist = db.get_blacklist()
        else:
            self.blacklist = self.specialized

        #add keywords to blacklist
        try:
            self.blacklist.add(self.keywords.text)
            db.save()
        except BlankKeyword:
            pass
        except KeywordAlreadyExists:
            pass

        #update blacklist page
        nag_bot_app.blacklist_page.gen_list(specialized=self.specialized)

        #return to previous screen
        nag_bot_app.screen_manager.transition.direction = 'right'
        nag_bot_app.screen_manager.current = self.previous_screen
        nag_bot_app.screen_manager.get_screen(
            self.previous_screen).previous_screen = "Edit Blackist"

        #reset keyword text
        self.keywords.text = ""

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

        screen = Screen(name="To Do List")
        self.to_do_page = ToDoListPage()
        screen.add_widget(self.to_do_page)
        self.screen_manager.add_widget(screen)

        screen = Screen(name="Add Task")
        self.add_task_page = AddTaskPage()
        screen.add_widget(self.add_task_page)
        self.screen_manager.add_widget(screen)

        screen = Screen(name="Blacklist")
        self.blacklist_page = BlacklistPage()
        screen.add_widget(self.blacklist_page)
        self.screen_manager.add_widget(screen)

        screen = Screen(name="Edit Blacklist")
        self.edit_blacklist_page = EditBlacklistPage()
        screen.add_widget(self.edit_blacklist_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def on_stop(self):
        import sys
        db.save()
        alert_system.stop()
        sys.exit()

def block_alert(alert_system):
    alert_system.check_blocks(delay=5) #number of seconds between checks

def blacklist_alert(alert_system):
    alert_system.check_blacklist(delay=10) # number of seconds between checks

if __name__ == "__main__":
    db = Database()

    db.load()

    alert_system = AlertSystem(db)
    block_thread = threading.Thread(target=block_alert, args=(alert_system,))
    blacklist_thread = threading.Thread(target=blacklist_alert, args=(alert_system,))

    block_thread.start()
    blacklist_thread.start()

    nag_bot_app = NagBotApp()
    nag_bot_app.run()