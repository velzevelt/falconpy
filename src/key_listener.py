from pynput.keyboard import Key, Listener

class KeyListener:
    should_quit = False
    destroy_on_quit = True
    quit_key = 'q'
    key = None
    listener = None
    
    def handle_quit(self, key):
        self.key = key
        k_string = ''
        try:
            k_string = key.char
        except Exception:
            return True
        
        self.should_quit = k_string == self.quit_key
        return not self.should_quit

    def __init__(self):
        self.listener = Listener(on_press=self.handle_quit)
        self.listener.start()
