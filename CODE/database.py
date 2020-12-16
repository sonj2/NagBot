#The classes that make up the Data Storage for the app

from datetime import datetime, date, timedelta

import pickle

'''
Database contains a Denylist which contains multiple DenyListItems (which contain a keyword list and a boolean for if the item is active).

Database also contains a BlockList which contains multiple Blocks (which contain a type ("Work" or "Break"), as well as a Start datetime and an End datetime,  a ToDoList  and a Denylist  [if type="Work"] ).

ToDoList  contains multiple Tasks (which contain a str description, str priority (High/Med/Low) and a boolean completed)

Database is the primary object and all calls will be made using methods in Database which can then call the appropriate methods in other classes (serves as a Facade). It will also contain a save() method which will save the data (via the pickle library) in the case the app is closed.

'''

class Database:
    def __init__(self):
        self.denylist = Denylist()
        self.block_list = BlockList()

    def get_denylist(self):
        return self.denylist

    def check_denylist(self, site):
        return self.denylist.check(site)

    def add_denylist(self, keywords):
        return self.denylist.add(keywords)

    def remove_denylist(self, id):
        return self.denylist.remove(id)

    def add_block(self, type, start, end):
        return self.block_list.add_block(type, start, end)

    def edit_block(self, id, type, start, end):
        return self.block_list.edit_block(id, type, start, end)

    def remove_block(self, id):
        return self.block_list.remove_block(id)

    def get_block(self, id):
        return self.block_list.get_block(id)

    def get_blocks(self,day):
        return self.block_list.get_blocks(day)

    def get_tasks(self, block_id):
        block = self.get_block(block_id)
        return block.get_tasks()

    def add_task(self, block_id, description, priority, completed=False):
        block = self.get_block(block_id)
        return block.add_task(description, priority, completed)

    def remove_task(self, block_id, task_id):
        block = self.get_block(block_id)
        return block.remove_task(task_id)

    def save(self):
        dbfile = open('data/denylist', 'wb')
        pickle.dump(self.denylist, dbfile)
        dbfile.close()

        dbfile = open('data/block_list', 'wb')
        pickle.dump(self.block_list, dbfile)
        dbfile.close()

    def load(self):
        try:
            dbfile = open('data/denylist', 'rb')
            self.denylist = pickle.load(dbfile)
            dbfile.close()

            dbfile = open('data/block_list', 'rb')
            self.block_list = pickle.load(dbfile)
            dbfile.close()

            return True

        except (OSError, IOError) as e:
            return False

## Exceptions for Denylist

class BlankKeyword(Exception):
    pass

class InvalidId(Exception):
    pass

class KeywordAlreadyExists(Exception):
    pass

## Denylist

class Denylist:
    def __init__(self):
        self.items = [] #array of DenylistItem(s)

    def check(self, site):
        for item in self.items:
            if item.active and item.contains_keyword(site):
                return True
        return False

    def add(self, keywords):
        if keywords == "": # No blank keywords
            raise BlankKeyword

        #perform same processing and check if already exists
        keywords = keywords.replace('\n','')
        keywords = keywords.replace('\t','')
        keywords_list = keywords.split(',')
        for i in range(len(keywords_list)):
            keywords_list[i] = keywords_list[i].strip()

        for item in self.items:
            if item.keywords == keywords_list:
                raise KeywordAlreadyExists

        self.items.append(DenylistItem(len(self.items),keywords))

    def remove(self, id):
        for item in self.items:
            if item.id == id:
                self.items.remove(item)
                return True
        raise InvalidId


class DenylistItem:
    def __init__(self, id, keywords=""):
        if keywords == "": # No blank keywords
            raise BlankKeyword
        else:
            keywords = keywords.replace('\n','')
            keywords = keywords.replace('\t','')
            keywords = keywords.replace(' ','')

            self.keywords = keywords.split(',')

            for i in range(len(self.keywords)):
                self.keywords[i] = self.keywords[i].strip()

            self.active = True
            self.id = id

    def contains_keyword(self, site):
        for word in self.keywords:
            if word.lower() in site.lower():
                return True
        return False

## Exceptions for BlockList

class InvalidType(Exception):
    pass

class EndBeforeStart(Exception):
    pass

class OverlapsExisting(Exception):
    pass

## Blocklist

class BlockList:
    def __init__(self):
        self.blocks = [] #array of Block(s)

    def add_block(self, type, start, end):
        #input validatation
        if type != "Work" and type != "Break":
            raise InvalidType
        if start > end:
            raise EndBeforeStart

        #must not overlap existing block
        for existing in self.blocks:
            start_overlap = start > existing.start and start < existing.end
            end_overlap = end > existing.start and end < existing.end
            complete_overlap = start <= existing.start and end >= existing.end

            if start_overlap or end_overlap or complete_overlap:
                raise OverlapsExisting

        block = Block(len(self.blocks),type, start, end)
        self.blocks.append(block)
        return block

    def edit_block(self, id, type, start, end):
        #input validatation
        if type != "Work" and type != "Break":
            raise InvalidType
        if start > end:
            raise EndBeforeStart

        #must not overlap existing block
        for existing in self.blocks:
            if existing.id == id:
                continue
            else:
                start_overlap = start > existing.start and start < existing.end
                end_overlap = end > existing.start and end < existing.end
                complete_overlap = start <= existing.start and end >= existing.end

                if start_overlap or end_overlap or complete_overlap:
                    raise OverlapsExisting

        block = self.get_block(id)
        block.edit_block(type, start, end)
        return block

    def remove_block(self, id):
        for block in self.blocks:
            if block.id == id:
                self.blocks.remove(block)
                return True
        raise InvalidId

    def get_block(self, id):
        for block in self.blocks:
            if block.id == id:
                return block
        raise InvalidId

    def get_blocks(self,day):
        next_day = day + timedelta(days=1)

        blocks = []
        for block in self.blocks:
            if block.start.date() == day:
                blocks.append(block)
        return blocks

class Block:
    def __init__(self, id, type, start, end, denylist=None):
        #input validatation
        if type != "Work" and type != "Break":
            raise InvalidType
        if start > end:
            raise EndBeforeStart

        self.id = id
        self.type = type #"Work" or "Break"
        self.start = start #datetime
        self.end = end #datetime
        self.to_do = ToDoList() #ToDoList
        self.denylist = denylist #Denylist

    def edit_block(self, type, start, end):
        self.type = type
        self.start = start
        self.end = end

    def get_tasks(self):
        return self.to_do.tasks

    def add_task(self, description, priority, completed):
        return self.to_do.add_task(description, priority, completed)

    def remove_task(self, id):
        return self.to_do.remove_task(id)


class ToDoList:
    def __init__(self):
        self.tasks = [] #array of Tasks(s)

    def add_task(self, description, priority, completed):
        self.tasks.append(Task(len(self.tasks),description, priority, completed))
        return True

    def remove_task(self, id):
        for task in self.tasks:
            if task.id == id:
                self.tasks.remove(task)
                return True
        raise InvalidId

class Task:
    def __init__(self, id, description, priority, completed):
        self.id = id
        self.description = description #string
        self.priority = priority #string
        self.completed = completed #boolean

## Unit Tests
if __name__ == "__main__":
    pass