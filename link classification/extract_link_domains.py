import pandas as pd
from tldextract import extract
import matplotlib.pyplot as plt
import csv

"""
Create CSV files with embedded links in one column and their domains on the other.
"""

links = []
domains = []


def get_link(all_links):
    if all_links:
        all_links = all_links.split("||")
        for each in all_links:
            links.append(each)
    else:
        return all_links


# Get raw data
df = pd.read_csv("community_posts_with_links.csv")

# Concatenate all links as a string
df["all_link_values"] = df["all_link_values"] + "||"
all_links = df["all_link_values"].tolist()
all_links = ''.join(all_links)
all_links = all_links[0:-2]
get_link(all_links)

# Extract domains
for link in links:
    tsd, td, tsu = extract(link)
    url = td + '.' + tsu
    if url == ".":
        domains.append("stackoverflow.com")
    else:
        domains.append(url)

# Get number of links from raw data
link_counts = df["all_link_count"].tolist()
actual_total = 0
for count in link_counts:
    actual_total += count

# Get number of links extracted
total = len(links)
print("Total Links:", actual_total, total)

# Export link domains to CSV
with open('link_domains.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(zip(links, domains))
