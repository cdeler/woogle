postgres pg_dump -U postgres -F t db_name | gzip >/backups/db-$(date +%Y-%m-%d).tar.gz