import pandas as pd
import os
import matplotlib.pyplot as plt

no = 10
for i in range(1, 3):
  df = pd.read_csv(os.path.join(
      "results", f"punctuality_stats{i}.csv"))
  df = df[df['Delay [min]'] <30]

  df.sort_values(by='Delay [min]', ascending=False, inplace=True)
  df = df[df['Delay [min]'] > 4]
  line_delay_counts = df['Line'].value_counts()
  
  top_10 = line_delay_counts.head(no)
  plt.figure(figsize=(10, 6))
  top_10.plot(kind='bar', color='red')
  plt.xlabel('Bus Line')
  plt.ylabel('Number of Delays > 4 min')
  plt.title(f'Top {no} Bus Lines with Most Frequent Delays > 4 min')
  plt.savefig(os.path.join("results", "top{no}_data{i}"))