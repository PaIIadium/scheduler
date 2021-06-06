import collections


class Queue:
    def __init__(self, priority):
        self.priority = priority
        self.queue = collections.deque()

    def enqueue(self, entry):
        self.queue.append(entry)

    def deque(self, entry):
        pass

    def retrieve(self, entry):
        pass

    def is_empty(self):
        return True if len(self.queue) == 0 else False

    def add_waiting_time(self, waiting_time):
        for entry in self.queue:
            entry.waiting_time += waiting_time

    def get_queue_length(self):
        return len(self.queue)

    def base_dequeue(self, entry):
        if entry is not None and entry.priority and not self.priority:
            return True
        if len(self.queue) == 0:
            return True
        return False

    def remove_entry(self, entry):
        self.queue.remove(entry)

    def get_closest_deadline_entry(self):
        if self.is_empty():
            return None
        closest_deadline_entry = self.queue[0]
        for index in range(len(self.queue)):
            if self.queue[index].deadline < closest_deadline_entry.deadline:
                closest_deadline_entry = self.queue[index]
        return closest_deadline_entry


class FIFOQueue(Queue):
    def deque(self, entry):
        if self.base_dequeue(entry):
            return entry
        if entry is None or (not entry.priority and self.priority):
            return self.queue.popleft()

        return entry

    def retrieve(self, entry):
        super(FIFOQueue, self).retrieve(entry)
        self.queue.appendleft(entry)


class RMQueue(Queue):
    def deque(self, entry):
        if self.base_dequeue(entry):
            return entry
        max_frequency_entry_index = 0 if entry is None or (not entry.priority and self.priority) else -1
        max_frequency_entry = self.queue[0] if max_frequency_entry_index == 0 else entry
        for index in range(len(self.queue)):
            if self.queue[index].frequency > max_frequency_entry.frequency:
                max_frequency_entry_index = index
                max_frequency_entry = self.queue[index]
        if max_frequency_entry_index != -1:
            del self.queue[max_frequency_entry_index]
        return max_frequency_entry

    def retrieve(self, entry):
        super(RMQueue, self).retrieve(entry)
        self.queue.append(entry)


class EDFQueue(Queue):
    def deque(self, entry):
        if self.base_dequeue(entry):
            return entry
        earliest_deadline_entry_index = 0 if entry is None or (not entry.priority and self.priority) else -1
        earliest_deadline_entry = self.queue[0] if earliest_deadline_entry_index == 0 else entry
        for index in range(len(self.queue)):
            if self.queue[index].deadline < earliest_deadline_entry.deadline:
                earliest_deadline_entry_index = index
                earliest_deadline_entry = self.queue[index]
        if earliest_deadline_entry_index != -1:
            del self.queue[earliest_deadline_entry_index]
        return earliest_deadline_entry

    def retrieve(self, entry):
        super(EDFQueue, self).retrieve(entry)
        self.queue.append(entry)
