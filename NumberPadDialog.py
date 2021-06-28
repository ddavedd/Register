import tkinter
from functools import partial

class NumberPadDialog:
    def __init__(self):
        self.keys = [[7,8,9],[4,5,6],[1,2,3],[0,"."],
                     ["Clear", "Done"]]
        self.current_number_label = None
        
        num_pad_window = tkinter.Toplevel()
        self.number_entry = tkinter.Entry(num_pad_window)
        self.number_entry.grid(row=0, column=0, columnspan=3)        
        
        row_number = 1
        for row in self.keys:
            column_number = 0
            for number in row:
                button = tkinter.Button(num_pad_window, text=str(number), \
                                            command=partial(self._button_pushed, number))
                button.config(width=6, height=4)
                button.grid(row=row_number, column=column_number)
                column_number += 1
            row_number += 1
        
        
    def _button_pushed(self, button_value):
        
        print(button_value)