import pandas as pd
from tldextract import extract
import matplotlib.pyplot as plt
import csv

"""
Count the number of domains embedded in Stack Overflow posts and their frequencies.
"""

link_type = {
    'images': 0,
    'documentations': 0,
    'blogs': 0,
    'pdf': 0,
    'stackoverflow': 0,
    'medium': 0,
    'wikipedia': 0,
    'jsfiddle': 0,
    'w3schools': 0
    # 'others': 0
}

blogs = []
docs = []
others = []


def get_link(all_links):
    if all_links:
        all_links = all_links.split("||")
        for each in all_links:
            if each.endswith('.jpg') or each.endswith('.png') or each.endswith('.gif'):
                link_type['images'] += 1
            elif each.endswith('.pdf'):
                link_type['pdf'] += 1
            elif 'stackoverflow.com' in each:
                link_type['stackoverflow'] += 1
            elif 'blog' in each:
                if "blog." not in each and 'blog/' not in each and 'blogs/' not in each and 'blogs.' not in each:
                    blogs.append(each)
                link_type['blogs'] += 1
            elif 'medium.com' in each:
                link_type['medium'] += 1
            elif 'wikipedia' in each:
                link_type['wikipedia'] += 1
            elif 'docs' in each or 'api' in each or 'documentation' in each or 'apis' in each or 'doc' in each:
                if 'docs/' not in each and 'docs.' not in each and 'api/' not in each and 'api.' not in each and 'apis/' not in each and 'apis' not in each and 'documentation/' not in each and 'documentation.' not in each and 'apidock' not in each and 'lodash.com/' not in each and '/doc/' not in each:
                    docs.append(each)
                link_type['documentations'] += 1
            elif 'jsfiddle' in each:
                link_type['jsfiddle'] += 1
            elif 'w3schools' in each:
                link_type['w3schools'] += 1
            else:
                # link_type['others'] += 1
                others.append(each)

            if 'http://https://' in each:
                each = each[7:]
            if "http://'https://" in each:
                each = each[8:]
            if "http://%20%20'https://" in each:
                each = each[14:]
            if "http://%20%20%20%20'https://" in each:
                each = each[20:]

    else:
        return all_links


# Get raw data
df = pd.read_csv("community_posts_with_links.csv")

# Get all links as a string
df["all_link_values"] = df["all_link_values"] + "||"
all_links = df["all_link_values"].tolist()
all_links = ''.join(all_links)
all_links = all_links[0:-2]
get_link(all_links)

# Extract Others domains -- https://stackoverflow.com/a/44114461
other_doms = {}
for link in others:
    tsd, td, tsu = extract(link)
    url = td + '.' + tsu
    if url == ".":
        link_type["stackoverflow"] += 1
    else:
        other_doms[url] = other_doms.get(url, 0) + 1

# Merge dictionaries and sort
link_type.update(other_doms)

sorted_links = {}
sorted_keys = sorted(link_type, key=link_type.get, reverse=True)
for w in sorted_keys:
    sorted_links[w] = link_type[w]

# Get number of links from raw data
link_counts = df["all_link_count"].tolist()
actual_total = 0
for count in link_counts:
    actual_total += count

# Get number of links extracted
total = 0
for count in sorted_links.values():
    total += count
print("Total Links:", actual_total, total)

# Export tally of domains to CSV
with open('domain_tally.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in sorted_links.items():
        writer.writerow([key, value])

# Export list of blogs and documentations to CSV
with open('docs_and_blogs.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(zip(blogs))
    writer.writerow(["^ BLOGS ====================================================================================================================================================================== DOCS v"])
    writer.writerows(zip(docs))

# Plot tally of domains
num_bins = 6
keys = list(sorted_links.keys())[:num_bins]
values = list(sorted_links.values())[:num_bins]
plt.figure(figsize=(20, 5))
plt.title("Total Links Plotted: " + str(sum(values)) + " (" + str(round(100*sum(values)/total, 1)) + "%)")
plt.bar(keys, values)
plt.savefig("domain_tally_plot.png")
plt.clf()
