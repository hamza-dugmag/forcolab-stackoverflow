# U of T Forcolab: Organizing *Stack Overflow*

## Community Clustering
Hierarchical density-based spatial clustering to classify *Stack Overflow* community posts by length, activity, popularity, and structure.

Run `.\clustering.sh` (Linux) or `.\clustering.bat` (Windows)

Outputs the `hdbscan_results` folder in the same directory where the script was run.

## Link Classification
Extracts links and tallies domains from all *Stack Overflow* posts.

Run `python extract_links_domains.py` and `python stackoverflow_links.py`

Outputs the 4 files in the same directory where the scripts were run.