import pandas as pd
import matplotlib.pyplot as plt

files = [
    "flows_leaf1.csv",
    "flows_leaf2.csv",
    "flows_leaf3.csv",
    "flows_leaf4.csv",
    "flows_leaf5.csv",
]
df_list = [pd.read_csv(f) for f in files]
flows = pd.concat(df_list, ignore_index=True)

flows['timestamp'] = pd.to_datetime(flows['flowStartMilliseconds'], unit='ms')
flows = flows.dropna(subset=['srcAddr', 'dstAddr', 'timestamp', 'bytes'])

flows.set_index('timestamp', inplace=True)
throughput = (
    flows['bytes']
    .resample('1T')                 
    .sum()                          
    .divide(60)                     
)
if 'jitter' in flows.columns:
    jitter = flows['jitter']

talkers = (
    flows
    .groupby('srcAddr')['bytes']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure()
throughput.plot()
plt.title("Network Throughput Over Time (bytes/sec)")
plt.xlabel("Time")
plt.ylabel("Bytes/sec")

if 'jitter' in flows.columns:
    plt.figure()
    plt.hist(jitter, bins=50)
    plt.title("Jitter Distribution")
    plt.xlabel("Jitter (ms)")
    plt.ylabel("Frequency")

plt.figure()
talkers.plot(kind='bar')
plt.title("Top 10 Talkers by Total Bytes")
plt.xlabel("Source IP")
plt.ylabel("Total Bytes")

plt.tight_layout()
plt.show()
