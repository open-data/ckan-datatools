#-*- coding:UTF-8 -*-
class FieldException(Exception):
    def __init__(self,field):
        super().__init__("Something is wrong with field ", field)
        self.field = field
        
    def parsed(self):
        return self.parsed.split()[:0]
    
class NestedKeyword(Exception):
    pass

class EmptyFieldException(Exception):
    pass