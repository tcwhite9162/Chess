import time

class ClockManager:
    def __init__(self, starting_time, increment):
        self.times         = {'w': starting_time, 'b': starting_time}
        self.increment     = increment 
        self.last_update   = time.time()
        self.active_color  = 'w'
        self.running       = False
        self.clock_started = False

    def update(self):
        if not self.running:
            return
        
        current_time = time.time()
        elapsed_time = current_time - self.last_update

        self.times[self.active_color] -= elapsed_time
        self.last_update = current_time

    def switch_turn(self):
        self.update()

        self.times[self.active_color] += self.increment

        self.active_color = 'b' if self.active_color == 'w' else 'w'
        self.last_update  = time.time()

    def pause(self):
        self.update()
        self.running = False

    def unpause(self):
        self.last_update = time.time()
        self.running = True

    def get_time(self, color):
        self.update()
        return max(0, self.times[color])
    
    def is_flagged(self, color):
        return self.get_time(color) <= 1
    
    def __repr__(self):
        return f'black: {self.times['b']}    white: {self.times['w']}'