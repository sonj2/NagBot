from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from KivyCalendar import CalendarWidget
from kivy.uix.screenmanager import ScreenManager, Screen


class CalendarPage(GridLayout):
    def __init__(self, **kwargs):
        super(CalendarPage, self).__init__(**kwargs)
        self.rows = 2

        self.cal = CalendarWidget()
        self.add_widget(self.cal)

        self.button1 = Button(text="View Schedule", font_size=40)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

    def button1_act(self, instance):
        nag_bot_app.schedule_page.update_date(self.cal.active_date)
        nag_bot_app.screen_manager.current = "Schedule"

class SchedulePage(GridLayout):
    def __init__(self, **kwargs):
        super(SchedulePage, self).__init__(**kwargs)
        self.rows = 2

        self.label = Label(halign="center", valign="middle", font_size=30)
        self.add_widget(self.label)

        self.button1 = Button(text="Back", font_size=40)
        self.button1.bind(on_press=self.button1_act)
        self.add_widget(self.button1)

    def update_date(self, date):
        self.label.text = "Schedule for:" + str(date[1]) + '/' + str(date[0]) + '/' + str(date[2])

    def button1_act(self, instance):
        nag_bot_app.screen_manager.current = "Calendar"




class NagBotApp(App):
    def build(self):

        self.screen_manager = ScreenManager()

        self.calendar_page = CalendarPage()
        screen = Screen(name="Calendar")
        screen.add_widget(self.calendar_page)
        self.screen_manager.add_widget(screen)

        self.schedule_page = SchedulePage()
        screen = Screen(name="Schedule")
        screen.add_widget(self.schedule_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def on_stop(self):
        import sys
        sys.exit()

if __name__ == "__main__":
    nag_bot_app = NagBotApp()
    nag_bot_app.run()