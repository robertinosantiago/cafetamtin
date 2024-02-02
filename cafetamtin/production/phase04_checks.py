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

from production.memory import Memory

class Phase04Checks:
    def __init__(self) -> None:
        pass
    
    def zero_numbers(self, wm: Memory) -> bool:
        logging.info(f'Executando função: zero_numbers')
        numbers_student = wm.get_fact('numbers_student')
        
        return len(numbers_student) == 0
    
    def long_time(self, wm: Memory) -> bool:
        logging.info(f'Executando função: long_time')
        time = wm.get_fact('timer_response').total_time_seconds()
        max_time = wm.get_fact('average_time')
        
        initial_sums = self.__initial_sums__(wm)        
        student_sums = self.__student_sums__(wm)

        return time > max_time and len(initial_sums) >= len(student_sums)
    
    def three_odd_numbers(self, wm: Memory) -> bool:
        logging.info(f'Executando função: three_odd_numbers')
        numbers = self.__student_numbers__(wm)
                
        for n in numbers:
            if self.__count_odd_numbers__(n) == 3:
                if sum(n) != 15:
                    return True
        
        return False
    
    def two_odd_and_one_even_numbers(self, wm: Memory) -> bool:
        logging.info(f'Executando função: two_odd_and_one_even_numbers')
        numbers = self.__student_numbers__(wm)
        
        for n in numbers:
            if self.__count_odd_numbers__(n) == 2 and self.__count_even_numbers__(n) == 1:
                if sum(n) != 15:
                    return True
            
        return False
    
    def three_even_numbers(self, wm: Memory) -> bool:
        logging.info(f'Executando função: three_even_numbers')
        numbers = self.__student_numbers__(wm)
                
        for n in numbers:
            if self.__count_even_numbers__(n) == 3:
                    if sum(n) != 15:
                        return True
        
        return False
    
    def two_even_and_one_odd_numbers(self, wm: Memory) -> bool:
        logging.info(f'Executando função: two_even_and_one_odd_numbers')
        numbers = self.__student_numbers__(wm)
        
        for n in numbers:
            if self.__count_even_numbers__(n) == 2 and self.__count_odd_numbers__(n) == 1:
                    if sum(n) != 15:
                        return True
            
        return False
    
    def not_five_in_center(self, wm: Memory) -> bool:
        logging.info(f'Executando função: five_not_in_center')
        numbers_student = wm.get_fact('numbers_student')
        
        position = numbers_student.get(5)
        
        if not position:
            return True
        
        if position[0] != 4 or position[1] != 4:
            return True
        
        return False
    
    def not_even_number_in_corners(self, wm: Memory) -> bool:
        logging.info(f'Executando função: not_even_number_in_corners')
        numbers_student : dict = wm.get_fact('numbers_student')
        numbers_even = {}
        
        for key, values in numbers_student.items():
            if key % 2 == 0:
                numbers_even[key] = values
                
        if len(numbers_even) == 0:
            return False
        
        for key, values in numbers_even.items():
            if not self.__position_is_corner__(values):
                return True
        
        return False
    
    def no_sum_fifteen(self, wm: Memory) -> bool:
        logging.info(f'Executando função: no_sum_fifteen')
        #initial_sums = self.__initial_sums__(wm)        
        student_sums = self.__student_sums__(wm)
        
        return len(student_sums) == 0
    
    def __position_is_corner__(self, position : list) -> bool:
        return (position[0] == 3 or position[0] == 5) and (position[1] == 3 or position[1] == 5)
    
    def __count_odd_numbers__(self, numbers: list[int]) -> int:
        count = 0
        for n in numbers:
            if n % 2 == 1:
                count += 1
        return count
    
    def __count_even_numbers__(self, numbers: list[int]) -> int:
        count = 0
        for n in numbers:
            if n % 2 == 0:
                count += 1
        return count    
    
    def __initial_sums__(self, wm: Memory) -> list[str]:
        challenges = wm.get_fact('challenges')
        numbers = self.__initial_numbers__(wm)
        
        keys = []
        for n in numbers:
            key = "".join(map(str, n))
            if challenges.get(key) is not None:
                keys.append(key)
        return keys
    
    def __initial_numbers__(self, wm: Memory) -> list[str]:
        initial_blocks = wm.get_fact('initial_blocks')
        elements = []
        keys = []

        for l in range(2, len(initial_blocks) - 2):
            t = []
            for c in range(2, len(initial_blocks[l]) - 2):
                if initial_blocks[c][l] != 0:
                    t.append(initial_blocks[c][l])
            if len(t) == 3:
                elements.append(t)
            
        for c in range(2, len(initial_blocks) - 2):
            t = []
            for l in range(2, len(initial_blocks[l]) - 2):
                if initial_blocks[c][l] != 0:
                    t.append(initial_blocks[c][l])
            if len(t) == 3:
                elements.append(t)

        t = []
        for c in range(2, len(initial_blocks) - 2):
            if initial_blocks[c][c] != 0:
                t.append(initial_blocks[c][c])
        if len(t) == 3:
            elements.append(t)

        t = []
        for c in range(2, len(initial_blocks) - 2):
            if initial_blocks[c][len(initial_blocks) - 1 - c] != 0:
                t.append(initial_blocks[c][len(initial_blocks) - 1 - c])
        if len(t) == 3:
            elements.append(t)
            
        for n in elements:
            n.sort()
            keys.append(n)
                
        return keys
    
    def __student_sums__(self, wm: Memory) -> list[str]:
        challenges = wm.get_fact('challenges')
        numbers = self.__student_numbers__(wm)
        
        keys = []
        for n in numbers:
            key = "".join(map(str, n))
            if challenges.get(key) is not None:
                keys.append(key)
        return keys
    
    def __student_numbers__(self, wm: Memory) -> list[str]:
        numbers_student = wm.get_fact('numbers_student')
        elements = []
        keys = []
        
        matrix = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        
        for key in numbers_student.keys():
            l,c = numbers_student[key]
            matrix[l-2][c-2] = key
            
        for l in range(1, len(matrix)-1):
            t = []
            for c in range(1, len(matrix[l]) - 1):
                if matrix[l][c] != 0:
                    t.append(matrix[l][c])
            if len(t) == 3:
                elements.append(t)
                
        for c in range(1, len(matrix) -1):
            t = []
            for l in range(1, len(matrix[c]) -1):
                if matrix[l][c] != 0:
                    t.append(matrix[l][c])
            if len(t) == 3:
                elements.append(t)
        
        t = []
        for l in range(1, len(matrix) - 1):
            if matrix[l][l] != 0:
                t.append(matrix[l][l])
        if len(t) == 3:
                elements.append(t)
                
        t = []
        for l in range(len(matrix)-2, 0, -1):
            if matrix[l][len(matrix) - 1 - l] != 0:
                t.append(matrix[l][len(matrix) - 1 - l])
        if len(t) == 3:
                elements.append(t)
        
        for n in elements:
            n.sort()
            keys.append(n)
        
        return keys