import tkinter
from functools import partial

class TextHintEntry(tkinter.Entry):

    """An Entry that does an autocomplete search for a connected option box"""
     
    def set_option_box_hint_list(self, option_box, option_box_var, hint_list):
        self.number_times = 0
        """Set the connected option box and list of options"""
        self._hint_list = hint_list
        self._option_box = option_box
        self._option_box_var = option_box_var
        self.bind("<KeyRelease>", self.handle_keyrelease)
        self.current_index = 0
        self.matching_hints = []
        self._MAX_MATCHES = 10
        self.determine_hints()
        
    def determine_hints(self):
        """Determine the matching options in the option box"""
        self.current_index = 0
        #print "*** Determining new hints ***" + str(self.number_times)
        #self.number_times += 1
        self.matching_hints = []
        current_entry_text = self.get().lower()
        print("Current text is '%s'" % current_entry_text)
        for hint in self._hint_list:
            print("Looking for text in '%s'" % hint)        
            if hint.lower().find(current_entry_text) >= 0:
                self.matching_hints.append(hint)
        
        print("Found %i matches" % len(self.matching_hints))
        print(self.matching_hints)
        self._option_box["menu"].delete(0, tkinter.END)
        current_index =  0
        for hint in self.matching_hints[:self._MAX_MATCHES]:
            self._option_box["menu"].add_command(label=hint, command=partial(self.menu_clicked, current_index))
            current_index += 1
        self.set_option_box_value()
    
    def menu_clicked(self, index):
        self.current_index = index
        self.set_option_box_value()
    
    def set_option_box_value(self):
        """Set the option box current value"""
        if self.matching_hints:
            self._option_box_var.set(self.matching_hints[self.current_index])
        else:
            self._option_box_var.set(None)
            
    def handle_keyrelease(self, event):
        """Handle what happens when a key is pressed"""
        # Special events are only up and down
        print("--In Keyrelease event handler--" + str(self.number_times))
        self.number_times += 1
        if event.keysym == "Up":
            if len(self.matching_hints) > 0:
                print("Special case up arrow")
                self.current_index = (self.current_index + 1) % len(self.matching_hints)
                self.set_option_box_value()
        elif event.keysym == "Down":
            if len(self.matching_hints) > 0:
                print("Special case down arrow")
                self.current_index = (self.current_index + 1) % len(self.matching_hints)
                self.set_option_box_value()
        else:
            self.determine_hints()
