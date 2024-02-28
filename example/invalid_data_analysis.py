import pandas as pd
import os


limiter = 70*'='
with open(os.path.join("results", "invalid_data"), "w") as file:
    for i in range(1, 3):
        file.write(f"{limiter}\n{20*' '}Data set{i}\n{limiter}\n")
        speed_stats = pd.read_csv(os.path.join("results", f"speed_stats{i}.csv"))
        punctuality_stats = pd.read_csv(os.path.join("results", f"punctuality_stats{i}.csv"))

        invalid_data_speed = len(speed_stats[speed_stats['speed'] > 90])
        invalid_data_punctuality = len(
            punctuality_stats[abs(punctuality_stats['Delay [min]']) > 30])

        file.write(f"Speed data: {len(speed_stats)}, Invalid data: {invalid_data_speed},"
                   f"Percentage: {invalid_data_speed/len(speed_stats) * 100:.2f} %\n")

        file.write(f"Punctuality data: {len(punctuality_stats)}, Invalid data: " 
                   f"{invalid_data_punctuality}, Percentage:"
                   f"{invalid_data_punctuality/len(punctuality_stats) * 100 :.2f} %\n")


