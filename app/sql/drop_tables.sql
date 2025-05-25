DO $$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'food') LOOP
        EXECUTE 'DROP TABLE food.' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;