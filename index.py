import scheduler_class as sch
import entries_generator as gen
import matplotlib.pyplot as plt
import queue_class as q
import numpy as np

MIN_INTERVAL = 0.5
MAX_INTERVAL = 4.75
INTERVAL_STEP = 0.25
ENTRY_DURATION = 8
ENTRIES_NUMBER = 75000


def single_test(interval, entries_number, entry_duration, common_queue, priority_queue):
    frequency = 1 / interval
    total_time = entries_number * interval
    generator = gen.Generator(total_time, frequency, 0.2, 0.3, 0.5, 0.5, entry_duration)
    entries = generator.generate()
    scheduler = sch.Scheduler(common_queue, priority_queue, entries)
    scheduler.run()
    return scheduler


def test(min_interval, max_interval, interval_step, entry_duration, entries_number, common_queue, priority_queue):
    frequencies = list()
    idle_percentages = list()
    expired_entries_percentages = list()

    common_waiting_times = list()
    priority_waiting_times = list()
    schedulers = list()

    for interval in np.arange(min_interval, max_interval, interval_step):
        scheduler = single_test(interval, entries_number, entry_duration, common_queue, priority_queue)

        avg_common_waiting_time = sum(scheduler.common_waiting_times) / len(scheduler.common_waiting_times)
        avg_priority_waiting_time = sum(scheduler.priority_waiting_times) / len(scheduler.priority_waiting_times)

        print(f"Entries interval: {interval}. Entries avg duration: {entry_duration}. Entries number: {entries_number}")
        print(f"Avg length queue. Common: {scheduler.avg_common_queue_len}, priority: {scheduler.avg_priority_queue_len}")
        print(f"Avg waiting time. Common: {avg_common_waiting_time}, priority: {avg_priority_waiting_time}")
        print(f"Idle percentage: {scheduler.idle_percentage}%\n")

        total_common_expired_entries = scheduler.total_common_expired_entries
        percentage_common_expired_entries = total_common_expired_entries * 100 / len(scheduler.common_waiting_times)

        total_priority_expired_entries = scheduler.total_priority_expired_entries
        percentage_priority_expired_entries = total_priority_expired_entries * 100 / len(scheduler.priority_waiting_times)

        print(f"Expired entries.\n"
              f"Common (total / percentage): {total_common_expired_entries} / {percentage_common_expired_entries}%\n"
              f"Priority (total / percentage): {total_priority_expired_entries} / {percentage_priority_expired_entries}%\n")
        print("---------------------------------------------")

        total_expired_entries = total_common_expired_entries + total_priority_expired_entries
        expired_entries_percentages.append(total_expired_entries * 100 / ENTRIES_NUMBER)

        frequency = 1 / interval
        frequencies.append(frequency)
        idle_percentages.append(scheduler.idle_percentage)
        common_waiting_times.append(avg_common_waiting_time)
        priority_waiting_times.append(avg_priority_waiting_time)

        schedulers.append(scheduler)

    return frequencies, idle_percentages, common_waiting_times, priority_waiting_times, schedulers, expired_entries_percentages


common_fifo_queue = q.FIFOQueue(False)
priority_fifo_queue = q.FIFOQueue(True)

common_rm_queue = q.RMQueue(False)
priority_rm_queue = q.RMQueue(True)

common_edf_queue = q.EDFQueue(False)
priority_edf_queue = q.EDFQueue(True)

fifo_result = test(MIN_INTERVAL, MAX_INTERVAL, INTERVAL_STEP, ENTRY_DURATION, ENTRIES_NUMBER, common_fifo_queue, priority_fifo_queue)
rm_result = test(MIN_INTERVAL, MAX_INTERVAL, INTERVAL_STEP, ENTRY_DURATION, ENTRIES_NUMBER, common_rm_queue, priority_rm_queue)
edf_result = test(MIN_INTERVAL, MAX_INTERVAL, INTERVAL_STEP, ENTRY_DURATION, ENTRIES_NUMBER, common_edf_queue, priority_edf_queue)

plt.subplot(231)
plt.plot(fifo_result[0], fifo_result[2], label="FIFO")
plt.plot(rm_result[0], rm_result[2], label="RM")
plt.plot(edf_result[0],  edf_result[2], label="EDF")
plt.legend(loc='lower right')
plt.xlabel(f"Частота вхідних заявок.\nЗагальна черга")
plt.ylabel(f"Середній час очікування в черзі")

plt.subplot(232)
plt.plot(fifo_result[0], fifo_result[3], label="FIFO")
plt.plot(rm_result[0], rm_result[3], label="RM")
plt.plot(edf_result[0], edf_result[3], label="EDF")
plt.legend(loc='lower right')
plt.xlabel(f"Частота вхідних заявок.\nПріоритетна черга")
plt.ylabel(f"Середній час очікування в черзі")

plt.subplot(233)
plt.plot(fifo_result[0], fifo_result[1], label="FIFO")
plt.plot(rm_result[0], rm_result[1], label="RM")
plt.plot(edf_result[0], edf_result[1], label="EDF")
plt.legend(loc='upper right')
plt.xlabel(f"Частота вхідних заявок")
plt.ylabel(f"Відсоток простою ресурсу")

plt.subplot(234)
plt.plot(fifo_result[0], fifo_result[5], label="FIFO")
plt.plot(rm_result[0], rm_result[5], label="RM")
plt.plot(edf_result[0], edf_result[5], label="EDF")
plt.legend(loc='upper left')
plt.xlabel(f"Частота вхідних заявок")
plt.ylabel(f"Відсоток протермінованих заявок")

plt.subplot(235)
plt.hist([fifo_result[4][8].common_waiting_times,
          rm_result[4][8].common_waiting_times,
          edf_result[4][8].common_waiting_times],
         25, label=["FIFO", "RM", "EDF"])
plt.legend(loc='upper right')
plt.xlabel(f"Середній час очікування в черзі.\nІнтервал між заявками {1 / fifo_result[0][8]}.\nЗагальна черга.")
plt.ylabel(f"Кількість заявок")

plt.subplot(236)
plt.hist([fifo_result[4][8].priority_waiting_times,
          rm_result[4][8].priority_waiting_times,
          edf_result[4][8].priority_waiting_times],
         25, label=["FIFO", "RM", "EDF"])
plt.legend(loc='upper right')
plt.xlabel(f"Середній час очікування в черзі.\nІнтервал між заявками {1 / fifo_result[0][8]}.\nПріоритетна черга")
plt.ylabel(f"Кількість заявок")

plt.show()
