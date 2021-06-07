class Entry:
    def __init__(self, ms_left, priority, deadline, frequency, enqueue_time):
        self.ms_left = ms_left
        self.waiting_time = 0
        self.priority = priority
        self.deadline = deadline
        self.frequency = frequency
        self.enqueue_time = enqueue_time

    def is_completed(self):
        return True if self.ms_left < 0.00001 else False
