split -b 20M fao_dump_20250626_194228.dump.gz ./dump-chunks/chunk_

# Upload chunks (less likely to timeout)
for f in ./dump-chunks/chunk_*; do 
    aws s3 cp "$f" s3://food-oasis-data/dump-chunks/
done