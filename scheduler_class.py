import numpy as np
import entry_class as etr


class Scheduler:
    def __init__(self, queue, priority_queue, entries, frame):
        self.common_queue = queue
        self.priority_queue = priority_queue
        self.entries = entries
        self.frame = frame
        self.frame_left = self.frame

        self.time_counter = 0
        self.current_entry = None

        self.idle_percentage = 0
        self.avg_common_queue_len = 0
        self.avg_priority_queue_len = 0
        self.common_waiting_times = list()
        self.priority_waiting_times = list()

        self.closest_deadline_entry = etr.Entry(0, False, np.Infinity, 0, 0)
        self.total_common_expired_entries = 0
        self.total_priority_expired_entries = 0

    def run(self):
        common_queue_len_sum = 0
        priority_queue_len_sum = 0

        idle_time = 0

        while True:
            self.check_times_list()

            if self.current_entry is not None and self.current_entry.is_completed():
                if self.closest_deadline_entry == self.current_entry:
                    self.closest_deadline_entry = None
                if self.current_entry.priority:
                    self.priority_waiting_times.append(self.current_entry.waiting_time)
                else:
                    self.common_waiting_times.append(self.current_entry.waiting_time)
                self.current_entry = None

            is_deadline = self.check_deadline()
            if is_deadline:
                self.process_expired_entry()
            self.closest_deadline_entry = self.find_closest_deadline_entry()

            if self.frame_left == self.frame:
                self.current_entry = self.dequeue_entry_from_queues()

            if len(self.entries) == 0 and self.common_queue.is_empty() and self.priority_queue.is_empty() \
                    and self.current_entry is None:
                break

            next_action_time = self.find_next_action_time()
            time_to_next_action = next_action_time - self.time_counter
            if self.current_entry is not None:
                self.current_entry.ms_left -= time_to_next_action
            else:
                idle_time += time_to_next_action

            self.common_queue.add_waiting_time(time_to_next_action)
            self.priority_queue.add_waiting_time(time_to_next_action)

            common_queue_len_sum += self.common_queue.get_queue_length() * time_to_next_action
            priority_queue_len_sum += self.priority_queue.get_queue_length() * time_to_next_action

            self.frame_left -= time_to_next_action
            if self.frame_left == 0:
                self.frame_left = self.frame
            self.time_counter = next_action_time

        self.idle_percentage = idle_time / self.time_counter * 100
        self.avg_common_queue_len = common_queue_len_sum / self.time_counter
        self.avg_priority_queue_len = priority_queue_len_sum / self.time_counter

    def check_times_list(self):
        if len(self.entries) == 0:
            return False
        closest_time = self.entries[0].enqueue_time
        if closest_time == self.time_counter:
            entry = self.entries.popleft()
            if entry.priority:
                self.priority_queue.enqueue(entry)
            else:
                self.common_queue.enqueue(entry)
            if self.closest_deadline_entry is None or entry.deadline < self.closest_deadline_entry.deadline:
                self.closest_deadline_entry = entry
            return True
        return False

    def dequeue_entry_from_queues(self):
        next_entry = self.priority_queue.deque(self.current_entry)
        if next_entry != self.current_entry:
            if self.current_entry is not None:
                if self.current_entry.priority:
                    self.priority_queue.retrieve(self.current_entry)
                else:
                    self.common_queue.retrieve(self.current_entry)
            return next_entry
        next_entry = self.common_queue.deque(self.current_entry)
        if next_entry != self.current_entry:
            if self.current_entry is not None:
                self.common_queue.retrieve(self.current_entry)
        return next_entry

    def find_next_action_time(self):
        enqueue_time = np.Infinity
        if len(self.entries) > 0:
            enqueue_time = self.entries[0].enqueue_time

        entry_complete_time = np.Infinity
        if self.current_entry is not None:
            entry_complete_time = self.time_counter + self.current_entry.ms_left

        closest_deadline = np.Infinity
        if self.closest_deadline_entry is not None:
            closest_deadline = self.closest_deadline_entry.deadline

        return min(enqueue_time, entry_complete_time, closest_deadline, self.frame_left + self.time_counter)

    def check_deadline(self):
        if self.closest_deadline_entry is None:
            return False
        if self.time_counter == self.closest_deadline_entry.deadline:
            return True
        return False

    def process_expired_entry(self):
        if self.closest_deadline_entry.priority:
            if self.closest_deadline_entry == self.current_entry:
                self.current_entry = None
            else:
                self.priority_queue.remove_entry(self.closest_deadline_entry)
            self.total_priority_expired_entries += 1
            self.priority_waiting_times.append(self.closest_deadline_entry.waiting_time)
        else:
            if self.closest_deadline_entry == self.current_entry:
                self.current_entry = None
            else:
                self.common_queue.remove_entry(self.closest_deadline_entry)
            self.total_common_expired_entries += 1
            self.common_waiting_times.append(self.closest_deadline_entry.waiting_time)

    def find_closest_deadline_entry(self):
        priority_min = self.priority_queue.get_closest_deadline_entry()
        common_min = self.common_queue.get_closest_deadline_entry()
        entries = [self.current_entry, priority_min, common_min]
        min_entry = entries[0]
        for index in range(len(entries)):
            if entries[index] is None:
                continue
            if min_entry is None:
                min_entry = entries[index]
            if entries[index].deadline < min_entry.deadline:
                min_entry = entries[index]
        return min_entry
