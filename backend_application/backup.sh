#!/bin/bash

echo "Backup postgres"
postgres pg_dump -U postgres -F t test | gzip >/backups/db-$(date +%Y-%m-%d).tar.gz