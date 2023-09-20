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

class Rule:
    
    def __init__(self, name, condition, action, message=None, image=None, tutor_emotion=None):
        self.name = name
        self.condition = condition
        self.action = action
        self.message = message
        self.image = image
        self.tutor_emotion = tutor_emotion

    def evaluate(self, working_memory):
        if self.condition(working_memory):
            self.action(working_memory, self.name, self.message, self.image, self.tutor_emotion)
            
    def __eq__(self, other):
        if isinstance(other, Rule):
            return (self.condition == other.condition and self.action == other.action)
        return False
            