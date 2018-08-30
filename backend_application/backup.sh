#!/bin/bash

echo "Backup postgres"
pg_dump -U postgres -F t postgres | gzip >/backups/db-$(date +%Y-%m-%d).tar.gz