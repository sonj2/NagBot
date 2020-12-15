import win32api

from datetime import datetime, date, timedelta

from time import sleep

from window_grabber import get_active_window

class AlertSystem:
    def __init__(self, db):
        self.current_block = None
        self.db = db
        self.running = True
        self.near_end = False

    def check_blocks(self, delay=10):
        while self.running:
            now = datetime.now()

            # check if we have entered a Block
            for block in self.db.get_blocks(date.today()):
                if block.start < now and block.end > now:
                    # We are inside a block... check if we already alerted the user
                    # and if not, send an alert.
                    if self.current_block != block:
                        self.near_end = False
                        self.current_block = block #store the current block -
                                                   #used for checking blacklist

                        win32api.MessageBox(0,
                            '''NagBot: You are entering a %s Block running from
                            %s to %s.'''%
                            (block.type,
                            block.start.strftime('%I:%M %p'),
                            block.end.strftime('%I:%M %p')),
                            'Entering Block', 0x00001000)

                    # Otherwise if we are less than a minute from the end of a block
                    # Notify the user that they are approaching the end of the block
                    else:
                        if (block.end - now) < timedelta(minutes=1) and not self.near_end:
                            self.near_end = True

                            win32api.MessageBox(0,
                                '''NagBot: You are approaching the end of a %s Block
                                running from %s to %s.'''%
                                (block.type,
                                block.start.strftime('%I:%M %p'),
                                block.end.strftime('%I:%M %p')),
                                'Off Task', 0x00001000)

                # We are no longer in a block, set current_block to None
                else:
                    self.current_block = None
            sleep(delay)

    # Function that checks if the active window is blacklisted periodically
    # and alerts the user they are going off task if the site is blacklisted
    def check_blacklist(self, delay=10):
        while self.running:
            if self.current_block != None and self.current_block.type == "Work":
                # If the block blacklist is None there is no "Specialized Blacklist"
                # Use the global blacklist
                if self.current_block.blacklist == None:
                    blacklist = self.db.get_blacklist()
                # Otherwise use the Specialized Blackist specific to the current block
                else:
                    blacklist = self.current_block.blacklist

                #grab the active window - uses function form window_grabber.py
                active_win = get_active_window()

                #check the blacklist and make a pop-up if site is blacklisted
                if blacklist.check(active_win):
                    win32api.MessageBox(0,
                        '''NagBot: You are entering a blacklisted site during a
                        Work block! This is a friendly reminder to remain on task.''',
                        'Entering Block', 0x00001000)
            sleep(delay)

    def stop(self):
        self.running = False