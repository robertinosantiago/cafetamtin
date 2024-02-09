#  Copyright (C) 2024 Robertino Mendes Santiago Junior
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

import logging
from datetime import datetime

from production.memory import Memory
from production.eficiency import Eficiency

class Phase02Checks:
    
    def __init__(self):
        pass
    
    def zero_numbers(self, wm: Memory) -> bool:
        logging.debug(f'Executando função: zero_numbers')
        result = wm.get_fact('result')
        return len(result) == 0
    
    def different_three_numbers(self, wm: Memory) -> bool:
        logging.debug(f'Executando função: different_three_numbers')
        result = wm.get_fact('result')
        return len(result) != 3
    
    def three_odd_numbers(self, wm: Memory) -> bool:
        logging.debug(f'Executando função: three_odd_numbers')
        result = wm.get_fact('result')
        if len(result) == 3:
            n1 = result[0]
            n2 = result[1]
            n3 = result[2]
            
            if self.__count_odd_numbers__(n1, n2, n3) == 3:
                return n1 + n2 + n3 != 15
        
        return False
    
    def three_even_numbers(self, wm:Memory) -> bool:
        logging.debug(f'Executando função: three_even_numbers')
        result = wm.get_fact('result')
        if len(result) == 3:
            n1 = result[0]
            n2 = result[1]
            n3 = result[2]
            
            return self.__count_even_numbers__(n1, n2, n3) == 3
        
        return False
    
    def two_even_and_one_odd_numbers(self, wm: Memory) -> bool:
        logging.debug(f'Executando função: two_even_and_one_odd_numbers')
        result = wm.get_fact('result')
        if len(result) == 3:
            n1 = result[0]
            n2 = result[1]
            n3 = result[2]
            
            if self.__count_even_numbers__(n1, n2, n3) == 2 and self.__count_odd_numbers__(n1, n2, n3) == 1:
                return n1 + n2 + n3 != 15
            
        return False
    
    def two_odd_and_one_even_numbers(self, wm: Memory) -> bool:
        logging.debug(f'Executando função: two_odd_and_one_even_numbers')
        result = wm.get_fact('result')
        if len(result) == 3:
            n1 = result[0]
            n2 = result[1]
            n3 = result[2]
            
            return self.__count_odd_numbers__(n1, n2, n3) == 2 and self.__count_even_numbers__(n1, n2, n3) == 1
            
        return False
    
    def many_errors(self, wm: Memory) -> bool:
        logging.debug(f'Executando função: many_errors')
        quantity_errors = wm.get_fact('quantity_errors')
        limit_errors = wm.get_fact('limit_errors')
        
        result = wm.get_fact('result')
        if len(result) == 3:
            if sum(result) == 15:
                wm.add_fact('quantity_errors', 0)
                return False
        
        if (quantity_errors >= limit_errors):
            wm.add_fact('quantity_errors', 0)
            return True
        return False
    
    def long_time(self, wm: Memory) -> bool:
        logging.debug(f'Executando função: long_time')
        result = wm.get_fact('result')
        time = wm.get_fact('timer_response').total_time_seconds()
        max_time = wm.get_fact('average_time')
        
        if len(result) == 3:

            if sum(result) != 15:
                return time > max_time

        return False
    
    def is_correct(self, wm: Memory) -> bool:
        logging.debug(f'Executando função: is_correct')
        result = wm.get_fact('result')
        
        if len(result) == 3:
            return sum(result) == 15
        
        return False
    
    def __count_odd_numbers__(self, *numbers: int) -> int:
        count = 0
        for n in numbers:
            if n % 2 == 1:
                count += 1
        return count
    
    def __count_even_numbers__(self, *numbers: int) -> int:
        count = 0
        for n in numbers:
            if n % 2 == 0:
                count += 1
                
        return count
    
    