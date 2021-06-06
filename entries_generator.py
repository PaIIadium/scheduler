import entry_class as etr
import numpy as np
import collections


class Generator:

    def __init__(self, time, frequency, fq_1, fq_2, fq_3, priority_fraction, duration):
        self.time = time
        self.frequency = frequency
        self.fq_1 = fq_1
        self.fq_2 = fq_2
        self.fq_3 = fq_3
        self.priority_fraction = priority_fraction
        self.duration = duration

    def generate(self):
        frequency_1 = self.frequency * self.fq_1
        frequency_2 = self.frequency * self.fq_2
        frequency_3 = self.frequency * self.fq_3

        interval_1 = 1.0 / frequency_1
        interval_2 = 1.0 / frequency_2
        interval_3 = 1.0 / frequency_3

        amount_1 = round(frequency_1 * self.time)
        amount_2 = round(frequency_2 * self.time)
        amount_3 = round(frequency_3 * self.time)

        generated_intervals_1 = np.random.exponential(interval_1, int(amount_1))
        generated_intervals_2 = np.random.exponential(interval_2, int(amount_2))
        generated_intervals_3 = np.random.exponential(interval_3, int(amount_3))

        entries = np.concatenate((self.create_entries(generated_intervals_1, frequency_1, self.duration),
                                  self.create_entries(generated_intervals_2, frequency_2, self.duration),
                                  self.create_entries(generated_intervals_3, frequency_3, self.duration)))

        return collections.deque(sorted(entries, key=lambda entry: entry.enqueue_time))

    def create_entries(self, intervals, frequency, avg_duration):
        result = list()
        time = 0
        for i in intervals:
            duration = np.random.uniform(avg_duration - 5, avg_duration + 5)
            deadline = time + duration * 10
            priority_random = np.random.uniform(0, 1)
            priority = True if priority_random < self.priority_fraction else False

            entry = etr.Entry(duration, priority, deadline, frequency, time)
            result.append(entry)
            time += i
        return np.array(result)
