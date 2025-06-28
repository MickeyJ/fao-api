
### zip dump
```bash
# Zip the dump file
gzip fao_dump_20250626_194228.dump
# This creates: fao_dump_20250626_194228.dump.gz
```

-----------------
### upload to S3
```bash
# Upload to S3
aws s3 cp fao_dump_20250626_194228.dump.gz s3://food-oasis-data/
```
### Or in small chunks with slow connection
```bash
mkdir dump-chunks

split -b 20M fao_dump_20250626_194228.dump.gz ./dump-chunks/chunk_

# Upload chunks (less likely to timeout)
for f in ./dump-chunks/chunk_*; do 
    aws s3 cp "$f" s3://food-oasis-data/dump-chunks/
done
```
-----------------

### ssh into ec2
```bash
# Get bastion IP (if using terraform)
cd ./terraform && terraform output bastion_public_ip

# SSH into bastion
ssh -i terraform/bastion-key.pem ec2_user@54.203.52.172
# Replace IP with your actual bastion IP
```

### download dump
```bash
aws s3 cp s3://food-oasis-data/fao_dump_20250626_194228.dump.gz ~/
```
-----------------
### or chunks
```bash
mkdir dump-chunks
aws s3 sync s3://food-oasis-data/dump-chunks ./dump-chunks
cat ./dump-chunks/chunk_* > fao_dump_20250626_194228.dump.gz
```
-----------------
### unzip dump
```bash
# Unzip
gunzip fao_dump_20250626_194228.dump.gz
```
-----------------
### restore from dump
```bash
# drop and create db just to be sure
PGPASSWORD='your-password' psql -h fao-api-db.cloe4i4o0hs7.us-west-2.rds.amazonaws.com -U faoadmin -d postgres << EOF
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'fao' AND pid <> pg_backend_pid();
DROP DATABASE fao;
CREATE DATABASE fao;
EOF


# Restore the database (no tunnel needed from bastion)
PGPASSWORD='your-password' pg_restore \
  -h fao-api-db.cloe4i4o0hs7.us-west-2.rds.amazonaws.com \
  -U faoadmin \
  -d fao \
  --verbose \
  --no-owner \
  --no-privileges \
  --jobs 4 \
  ~/fao_dump_20250626_194228.dump
```


