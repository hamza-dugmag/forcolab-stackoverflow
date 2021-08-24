docker pull hamzadugmag/forcolab-clustering:1.0
docker run --name hdbscanner hamzadugmag/forcolab-clustering:1.0
docker cp hdbscanner:/usr/src/app hdbscan_results
docker rm hdbscanner
