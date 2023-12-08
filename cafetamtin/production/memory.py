# Copyright (C) 2023 Robertino Mendes Santiago Junior
# 
# This file is part of CaFE-TaMTIn Approach.
# 
# CaFE-TaMTIn Approach is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# CaFE-TaMTIn Approach is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with CaFE-TaMTIn Approach.  If not, see <http://www.gnu.org/licenses/>.

class Memory:
    
    def __init__(self):
        self.facts = {}
        self.errors = []
        self.facts['valid'] = False
        self.facts['correct'] = False
        
    def add_fact(self, fact, value):
        self.facts[fact] = value

    def get_fact(self, fact):
        return self.facts.get(fact)
    
    def clear_facts(self):
        self.facts = {}
        
    def reset(self):
        self.facts['valid'] = False
        self.facts['correct'] = False
        self.clear_errors()
    
    #def add_error(self, error):
    #    self.errors.append(error)
        
    #def list_errors(self):
    #    return self.errors
    
    def clear_errors(self):
        self.facts['history_errors'] = []