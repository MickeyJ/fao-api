#!/bin/bash

# FAO Database Migration Script
# Dumps local database and restores to Supabase

# FAO Database Migration Script
# Dumps local database and restores to Supabase

# Usage
# screen -S migration
# ./fao_db_migration.sh [--test-connection]
echo ""

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# File paths
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DUMP_DIR="fao_dump_${TIMESTAMP}"
DUMP_FILE="${DUMP_DIR}.dump"
LOG_FILE="migration_${TIMESTAMP}.log"
REMOTE_DUMP_FILE="remote_backup_${TIMESTAMP}.dump"
USE_BASTION=${USE_BASTION:-false}
BASTION_KEY="terraform/bastion-key.pem"
BASTION_USER="ec2-user"
BASTION_IP=$(cd terraform && terraform output -raw bastion_public_ip 2>/dev/null || echo "")


# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# Function to load .env file
load_env() {
    if [ -f "$1" ]; then
        print_status "Loading environment from $1"
        set -a
        source "$1"
        set +a
    else
        print_error "Environment file $1 not found!"
        exit 1
    fi
}

# Add help function
show_help() {
    echo "FAO Database Migration Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --test-connection    Test database connections only"
    echo "  --dump-only         Create dump file without restoring"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --test-connection    # Test connections"
    echo "  $0 --dump-only          # Create backup only"
    echo "  $0                      # Full migration (dump + restore)"
}


# Check for command line arguments
TEST_MODE=""
DUMP_ONLY=""
for arg in "$@"; do
    case $arg in
        --test-connection)
            TEST_MODE="connection"
            ;;
        --dump-only)
            DUMP_ONLY="true"
            ;;
        --backup-remote)
            BACKUP_REMOTE="true"
            ;;
        --restore-only)
            RESTORE_ONLY="true"
            DUMP_FILE="$2"  # Get the dump file as next argument
            shift  # Skip the filename argument
            ;;
        --help)
            show_help
            exit 0
            ;;
    esac
done

# Load environment files
# Assuming you have .env for local and .env.production for remote
# Adjust these paths as needed
load_env "dump.env"  # Local database credentials

# Configuration from environment variables
# Local database (from dump.env)
LOCAL_DB_USER="${LOCAL_DB_USER:-mickey}"
LOCAL_DB_PASSWORD="${LOCAL_DB_PASSWORD}"
LOCAL_DB_HOST="${LOCAL_DB_HOST:-localhost}"
LOCAL_DB_PORT="${LOCAL_DB_PORT:-5432}"
LOCAL_DB_NAME="${LOCAL_DB_NAME:-fao}"

# Remote database (RDS) - using different env var names
# You might need to adjust these based on your dump.env structure
REMOTE_DB_USER="${REMOTE_DB_USER:-postgres.rltlqzgjokukrrpqqvre}"
REMOTE_DB_PASSWORD="${REMOTE_DB_PASSWORD}" 
REMOTE_DB_HOST="${REMOTE_DB_HOST:-aws-0-us-west-1.pooler.supabase.com}"
REMOTE_DB_PORT="${REMOTE_DB_PORT:-5432}"
REMOTE_DB_NAME="${REMOTE_DB_NAME:-postgres}"

# Validate required credentials
if [ -z "$LOCAL_DB_PASSWORD" ]; then
    print_error "LOCAL_DB_PASSWORD not set in environment!"
    exit 1
fi

if [ -z "$REMOTE_DB_PASSWORD" ]; then
    print_error "REMOTE_DB_PASSWORD not set in environment!"
    exit 1
fi

# Function to show progress
show_progress() {
    local file=$1
    while [ -e /proc/$! ]; do
        if [ -f "$file" ]; then
            size=$(ls -lh "$file" 2>/dev/null | awk '{print $5}')
            echo -ne "\rCurrent size: $size" 
        fi
        sleep 1
    done
    echo ""
}

# Enhanced connection test function
test_connections() {
    print_status "=== Testing Database Connections ==="
    
    # Test local connection
    print_status "Testing LOCAL database connection..."
    print_status "Host: $LOCAL_DB_HOST:$LOCAL_DB_PORT"
    print_status "Database: $LOCAL_DB_NAME"
    print_status "User: $LOCAL_DB_USER"
    
    # Test basic connection
    PGPASSWORD=$LOCAL_DB_PASSWORD psql \
        -h $LOCAL_DB_HOST \
        -p $LOCAL_DB_PORT \
        -U $LOCAL_DB_USER \
        -d $LOCAL_DB_NAME \
        -c "SELECT version();" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_status "✓ Local connection successful"
        
        # Get some basic info
        DB_VERSION=$(PGPASSWORD=$LOCAL_DB_PASSWORD psql -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -t -c "SELECT version();" | head -1)
        print_status "PostgreSQL version: ${DB_VERSION:0:50}..."
        
        # Get database size
        DB_SIZE=$(PGPASSWORD=$LOCAL_DB_PASSWORD psql -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -t -c "SELECT pg_size_pretty(pg_database_size('$LOCAL_DB_NAME'));")
        print_status "Database size: $DB_SIZE"
        
        # Get table count
        TABLE_COUNT=$(PGPASSWORD=$LOCAL_DB_PASSWORD psql -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
        print_status "Number of tables: $TABLE_COUNT"
        
    else
        print_error "✗ Local connection FAILED!"
        print_error "Check your credentials and database status"
        return 1
    fi
    
    echo ""
    
    # Test remote connection
    print_status "Testing REMOTE (RDS) database connection..."
    print_status "Host: $REMOTE_DB_HOST:$REMOTE_DB_PORT"
    print_status "Database: $REMOTE_DB_NAME"
    print_status "User: $REMOTE_DB_USER"
    
    PGPASSWORD=$REMOTE_DB_PASSWORD psql \
        -h $REMOTE_DB_HOST \
        -p $REMOTE_DB_PORT \
        -U $REMOTE_DB_USER \
        -d $REMOTE_DB_NAME \
        -c "SELECT version();" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_status "✓ Remote connection successful"
        

        # Get remote database size
        REMOTE_DB_SIZE=$(PGPASSWORD=$REMOTE_DB_PASSWORD psql -h $REMOTE_DB_HOST -p $REMOTE_DB_PORT -U $REMOTE_DB_USER -d $REMOTE_DB_NAME -t -c "SELECT pg_size_pretty(pg_database_size('$REMOTE_DB_NAME'));")
        print_status "Remote database size: $REMOTE_DB_SIZE"

        # Check if any tables exist
        REMOTE_TABLE_COUNT=$(PGPASSWORD=$REMOTE_DB_PASSWORD psql -h $REMOTE_DB_HOST -p $REMOTE_DB_PORT -U $REMOTE_DB_USER -d $REMOTE_DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
        print_status "Number of tables in remote: $REMOTE_TABLE_COUNT"
        
        if [ $REMOTE_TABLE_COUNT -gt 0 ]; then
            print_warning "Remote database is NOT empty! Contains $REMOTE_TABLE_COUNT tables"
            print_warning "Restore operation would DROP these tables!"
        else
            print_status "Remote database is empty (ready for migration)"
        fi
        
    else
        print_error "✗ Remote connection FAILED!"
        print_error "Check your Supabase credentials and connection settings"
        return 1
    fi
    
    echo ""
    print_status "=== Connection tests completed ==="
    return 0
}


backup_remote_database() {
    print_status "=== Backing up REMOTE database before migration ==="

    print_status "Creating backup of remote database..."
    print_status "This will download ~15 GB from Supabase..."
    
    PGPASSWORD=$REMOTE_DB_PASSWORD pg_dump \
        -h $REMOTE_DB_HOST \
        -p $REMOTE_DB_PORT \
        -U $REMOTE_DB_USER \
        -d $REMOTE_DB_NAME \
        --no-owner \
        --no-privileges \
        --no-tablespaces \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="$REMOTE_DUMP_FILE" 2>&1 | tee -a "$LOG_FILE" &
    
    DUMP_PID=$!
    show_progress "$REMOTE_DUMP_FILE"
    wait $DUMP_PID
    
    if [ $? -eq 0 ]; then
        FINAL_SIZE=$(ls -lh "$REMOTE_DUMP_FILE" | awk '{print $5}')
        print_status "Remote backup completed! Size: $FINAL_SIZE"
        print_status "Backup saved as: $REMOTE_DUMP_FILE"
    else
        print_error "Remote backup failed!"
        exit 1
    fi
}


estimate_rows() {
    print_status "Estimating database size..."
    
    PGPASSWORD=$LOCAL_DB_PASSWORD psql -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -c "
    SELECT 
        schemaname,
        relname as table_name,
        to_char(n_live_tup, '999,999,999') as row_count
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
    ORDER BY n_live_tup DESC
    LIMIT 10;"
}


compare_databases() {
    print_status "=== Database Comparison ==="
    
    print_status "Largest tables in LOCAL database:"
    PGPASSWORD=$LOCAL_DB_PASSWORD psql -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -c "
    SELECT 
        schemaname,
        relname as table_name,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS size,
        to_char(n_live_tup, '999,999,999') as row_count
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||relname) DESC
    LIMIT 10;"
    
    TOP_TABLES=$(PGPASSWORD=$LOCAL_DB_PASSWORD psql -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -t -A -c "
    SELECT relname
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||relname) DESC
    LIMIT 3;")
}

# FIXED: Compare tables function
compare_tables() {
    print_status "Comparing local and remote tables..."
    
    PGPASSWORD=$LOCAL_DB_PASSWORD psql -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -t -A -c "
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE' 
    ORDER BY table_name;" > local_tables.txt
    
    PGPASSWORD=$REMOTE_DB_PASSWORD psql -h $REMOTE_DB_HOST -p $REMOTE_DB_PORT -U $REMOTE_DB_USER -d $REMOTE_DB_NAME -t -A -c "
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE' 
    ORDER BY table_name;" > remote_tables.txt
}

# Function to check disk space
check_disk_space() {
    print_status "Checking available disk space..."
    
    # Get database size
    DB_SIZE=$(PGPASSWORD=$LOCAL_DB_PASSWORD psql -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -t -c "
    SELECT pg_size_pretty(pg_database_size('$LOCAL_DB_NAME'));")
    
    # Get available disk space
    AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
    
    print_status "Database size: $DB_SIZE"
    print_status "Available disk space: $AVAILABLE_SPACE"
    
    echo -n "Continue with dump? (y/n): "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_warning "Migration cancelled by user"
        exit 0
    fi
}

# Function to create dump
create_dump() {
    print_status "Starting database dump..."
    print_status "This may take 30-60 minutes for 150M rows..."
    
    # Create dump with Supabase-compatible options
    PGPASSWORD=$LOCAL_DB_PASSWORD pg_dump \
        -h $LOCAL_DB_HOST \
        -p $LOCAL_DB_PORT \
        -U $LOCAL_DB_USER \
        -d $LOCAL_DB_NAME \
        --no-owner \
        --no-privileges \
        --no-tablespaces \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="$DUMP_FILE" 2>&1 | tee -a "$LOG_FILE" &
    
    DUMP_PID=$!
    
    # Show progress
    show_progress "$DUMP_FILE"
    
    wait $DUMP_PID
    
    if [ $? -eq 0 ]; then
        FINAL_SIZE=$(ls -lh "$DUMP_FILE" | awk '{print $5}')
        print_status "Dump completed successfully! Size: $FINAL_SIZE"
    else
        print_error "Dump failed! Check $LOG_FILE for details"
        exit 1
    fi
}

# Function to verify dump
verify_dump() {
    print_status "Verifying dump file..."
    
    # List contents of dump
    pg_restore --list "$DUMP_FILE" > dump_contents.txt 2>&1
    
    if [ $? -eq 0 ]; then
        TABLE_COUNT=$(grep -c "TABLE DATA" dump_contents.txt)
        print_status "Dump contains $TABLE_COUNT tables"
        rm dump_contents.txt
    else
        print_error "Dump verification failed!"
        exit 1
    fi
}

upload_dump_to_s3() {
    print_status "Uploading dump to S3..."
    
    # Ensure AWS CLI is configured
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found! Please install it and configure your credentials."
        exit 1
    fi

    # Create a copy instead of overwriting original
    print_status "Compressing dump file..."
    gzip -c "$DUMP_FILE" > "${DUMP_FILE}.gz"

    # Create directory for chunks (using basename to avoid path issues)
    DUMP_NAME=$(basename "$DUMP_FILE")
    CHUNK_DIR="./chunks_${DUMP_NAME}"
    mkdir -p "$CHUNK_DIR"

    # Split the compressed file
    print_status "Splitting into 20MB chunks..."
    split -b 20M "${DUMP_FILE}.gz" "$CHUNK_DIR/chunk_"

    # Upload chunks with error tracking
    UPLOAD_FAILED=0
    for f in "$CHUNK_DIR"/chunk_*; do 
        print_status "Uploading $(basename "$f")..."
        if ! aws s3 cp "$f" "s3://food-oasis-data/${DUMP_NAME}/$(basename "$f")"; then
            print_error "Failed to upload $(basename "$f")"
            UPLOAD_FAILED=1
        fi
    done
    
    # Clean up chunks if upload succeeded
    if [ $UPLOAD_FAILED -eq 0 ]; then
        print_status "All chunks uploaded successfully to S3"
        rm -rf "$CHUNK_DIR"
        rm "${DUMP_FILE}.gz"  # Optional: remove compressed file
    else
        print_error "Some chunks failed to upload! Check $LOG_FILE for details"
        exit 1
    fi
}

# Function to test remote connection
test_remote_connection() {
    print_status "Testing connection to Supabase..."
    
    PGPASSWORD=$REMOTE_DB_PASSWORD psql \
        -h $REMOTE_DB_HOST \
        -p $REMOTE_DB_PORT \
        -U $REMOTE_DB_USER \
        -d $REMOTE_DB_NAME \
        -c "SELECT version();" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_status "Successfully connected to RDS"
    else
        print_error "Failed to connect to RDS! Check credentials"
        exit 1
    fi
}

restore_dump() {
    if [ "$USE_BASTION" = true ]; then
        restore_via_bastion
    else
        restore_direct
    fi
}

restore_direct() {
    print_status "Starting direct restore to RDS..."
    print_status "This may take 1-3 hours depending on network speed..."
    
    # First drop and recreate database
    print_status "Dropping and recreating database..."
    PGPASSWORD=$REMOTE_DB_PASSWORD psql \
        -h $REMOTE_DB_HOST \
        -U $REMOTE_DB_USER \
        -d postgres << EOF
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$REMOTE_DB_NAME' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS $REMOTE_DB_NAME;
CREATE DATABASE $REMOTE_DB_NAME;
EOF

    # Restore with clean database
    PGPASSWORD=$REMOTE_DB_PASSWORD pg_restore \
        -h $REMOTE_DB_HOST \
        -p $REMOTE_DB_PORT \
        -U $REMOTE_DB_USER \
        -d $REMOTE_DB_NAME \
        --verbose \
        --no-owner \
        --no-privileges \
        --jobs 4 \
        "$DUMP_FILE" 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        print_status "Restore completed successfully!"
    else
        print_error "Restore failed! Check $LOG_FILE for details"
        exit 1
    fi
}

restore_via_bastion() {
    print_status "Starting restore via bastion EC2..."
    
    # Check bastion connectivity
    if ! ssh -i "$BASTION_KEY" -o ConnectTimeout=5 "$BASTION_USER@$BASTION_IP" "echo 'Connected'" &>/dev/null; then
        print_error "Cannot connect to bastion at $BASTION_IP"
        exit 1
    fi
    
    # Create restore script on bastion
    cat > /tmp/restore_script.sh << 'SCRIPT'
#!/bin/bash
set -e

DUMP_NAME=$(basename "$1")
DB_PASSWORD="$2"
DB_HOST="$3"
DB_USER="$4"
DB_NAME="$5"

echo "Downloading chunks from S3..."
mkdir -p "$DUMP_NAME"
aws s3 sync "s3://food-oasis-data/$DUMP_NAME/" "./$DUMP_NAME/"
cat "./$DUMP_NAME/chunk_"* > "$DUMP_NAME.gz"
rm -rf "./$DUMP_NAME"

echo "Unzipping dump..."
gunzip "$DUMP_NAME.gz"

echo "Dropping and recreating database..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d postgres << EOF
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$REMOTE_DB_NAME' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS $REMOTE_DB_NAME;
CREATE DATABASE $REMOTE_DB_NAME;
EOF

echo "Starting restore..."
PGPASSWORD="$DB_PASSWORD" pg_restore \
    -h "$DB_HOST" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --verbose \
    --no-owner \
    --no-privileges \
    --jobs 4 \
    "$DUMP_NAME"

echo "Cleaning up..."
rm -f "$DUMP_NAME"
echo "Restore completed!"
SCRIPT

    # Copy script to bastion
    scp -i "$BASTION_KEY" /tmp/restore_script.sh "$BASTION_USER@$BASTION_IP:~/restore_script.sh"
    
    # Execute restore on bastion
    DUMP_BASENAME=$(basename "$DUMP_FILE")
    
    ssh -i "$BASTION_KEY" "$BASTION_USER@$BASTION_IP" "bash restore_script.sh '$DUMP_BASENAME' '$REMOTE_DB_PASSWORD' '$REMOTE_DB_HOST' '$REMOTE_DB_USER' '$REMOTE_DB_NAME'"
    
    # Cleanup
    ssh -i "$BASTION_KEY" "$BASTION_USER@$BASTION_IP" "rm -f restore_script.sh"
    rm -f /tmp/restore_script.sh
    
    print_status "Bastion restore completed!"
}

# Function to verify restore
verify_restore() {
    print_status "Verifying restored data..."
    
    # Get row counts from remote
    REMOTE_ROWS=$(PGPASSWORD=$REMOTE_DB_PASSWORD psql -h $REMOTE_DB_HOST -p $REMOTE_DB_PORT -U $REMOTE_DB_USER -d $REMOTE_DB_NAME -t -c "
    SELECT to_char(SUM(n_live_tup), '999,999,999') 
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public';")
    
    print_status "Total rows in Supabase: $REMOTE_ROWS"
    
    # Show top tables
    PGPASSWORD=$REMOTE_DB_PASSWORD psql -h $REMOTE_DB_HOST -p $REMOTE_DB_PORT -U $REMOTE_DB_USER -d $REMOTE_DB_NAME -c "
    SELECT 
        relname as table_name,
        to_char(n_live_tup, '999,999,999') as row_count
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
    ORDER BY n_live_tup DESC
    LIMIT 5;"
}

# Function to cleanup
cleanup() {
    echo -n "Delete local dump file? (y/n): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Cleaning up dump file..."
        rm -f "$DUMP_FILE"
        print_status "Cleanup completed"
    else
        print_status "Dump file kept at: $DUMP_FILE"
    fi
}

main() {
    
    # Handle test mode
    if [ "$TEST_MODE" == "connection" ]; then
        test_connections
        exit $?
    fi
    
    # Handle backup-remote mode
    if [ "$BACKUP_REMOTE" == "true" ]; then
        print_status "=== Remote Backup Mode ==="
        test_connections
        if [ $? -ne 0 ]; then
            print_error "Connection test failed. Cannot backup remote."
            exit 1
        fi
        backup_remote_database
        exit $?
    fi
    
    # Handle dump-only mode
    if [ "$DUMP_ONLY" == "true" ]; then
        print_status "=== Dump-Only Mode ==="
        test_connections
        if [ $? -ne 0 ]; then
            print_error "Connection test failed."
            exit 1
        fi
        estimate_rows
        check_disk_space
        create_dump
        verify_dump
        upload_dump_to_s3
        
        print_status "=== Dump-only mode completed ==="
        print_status "Dump file saved at: $DUMP_FILE"
        print_status "Size: $(ls -lh "$DUMP_FILE" | awk '{print $5}')"
        print_status ""
        print_status "To restore this dump later, run:"
        print_status "PGPASSWORD=\$REMOTE_DB_PASSWORD pg_restore \\"
        print_status "  -h $REMOTE_DB_HOST \\"
        print_status "  -p $REMOTE_DB_PORT \\"
        print_status "  -U $REMOTE_DB_USER \\"
        print_status "  -d $REMOTE_DB_NAME \\"
        print_status "  --verbose --no-owner --no-privileges \\"
        print_status "  $DUMP_FILE"
        exit 0
    fi

    if [ "$RESTORE_ONLY" == "true" ]; then
        print_status "=== Restore-Only Mode ==="
        
        if [ ! -f "$DUMP_FILE" ]; then
            print_error "Dump file not found: $DUMP_FILE"
            exit 1
        fi
        
        test_remote_connection
        if [ $? -ne 0 ]; then
            print_error "Remote connection failed."
            exit 1
        fi
        
        print_warning "About to restore to Supabase. This will REPLACE all existing data!"
        echo -n "Continue? (y/n): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_warning "Restore cancelled."
            exit 0
        fi
        
        restore_dump
        verify_restore
        print_status "=== Restore completed ==="
        exit 0
    fi
    
    # Regular full migration mode
    print_status "=== FAO Database Migration Script ==="
    print_status "Migrating from local to Supabase"
    echo ""
    
    # Always test connections first
    test_connections
    if [ $? -ne 0 ]; then
        print_error "Connection test failed. Aborting migration."
        exit 1
    fi
    
    # Continue with rest of migration...
    estimate_rows
    check_disk_space

    if [ "$DUMP_ONLY" != "true" ] && [ "$BACKUP_REMOTE" != "true" ]; then
        print_status "=== Migration Summary ==="
        print_status "Source: LOCAL database (38 GB, 89 tables)"
        print_status "Target: REMOTE database (15 GB, 86 tables)"
        print_status "Action: REPLACE all remote data with local data"
        print_status "Data to transfer: ~38 GB (compressed to ~5-8 GB)"
        print_status "Estimated time: 2-4 hours"
        echo ""
        print_warning "This will DELETE all existing data in remote!"
        echo -n "Continue? (y/n): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_status "Migration cancelled"
            exit 0
        fi
    fi
    
    # Create dump
    create_dump
    verify_dump
    
    # Confirm before restore
    echo ""
    print_warning "About to restore to Supabase. This will REPLACE all existing data!"
    echo -n "Continue with restore? (y/n): "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_warning "Restore cancelled. Dump file saved at: $DUMP_FILE"
        exit 0
    fi
    
    # Restore to remote
    restore_dump
    verify_restore
    
    # Cleanup
    cleanup
    
    print_status "=== Migration completed successfully! ==="
    print_status "Log file: $LOG_FILE"
}

# Run main function
main