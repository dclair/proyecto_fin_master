# Automated Backups (MariaDB & Media)

## Context
This project uses Docker Compose for deployment on Oracle Cloud (OCI). The database is MariaDB and user-uploaded content is stored in the `media_volume`. To ensure data safety without polluting the containers, an automated backup strategy was implemented at the host OS level.

## Implementation Details
- **Script Location:** `scripts/backup.sh`
- **Execution Environment:** Host OS (Ubuntu on OCI), triggered via `cron`.
- **Secrets Management:** The script dynamically parses `.env.prod` to retrieve database credentials, avoiding hardcoded secrets.
- **Database Backup:** Uses `docker compose exec -T db mariadb-dump` to create an `.sql.gz` file directly on the host.
- **Media Backup:** Spins up a temporary, ephemeral `alpine` container that mounts `media_volume` and compresses it via `tar czf` into a `.tar.gz` file.
- **Retention Policy:** The script automatically deletes any backups older than 7 days using `find ... -mtime +7 -exec rm {} \;`.

## Cron Configuration
To apply this in a new deployment or after migrating servers, add the following to the root or designated user's crontab (`crontab -e`):

```bash
0 3 * * * /home/ubuntu/proyecto_fin_master/scripts/backup.sh >> /home/ubuntu/backups/aficionados_network/backup_cron.log 2>&1
```
*Note: Adjust `/home/ubuntu/proyecto_fin_master` and backup output directories as needed based on the deployment environment.*

## Manual Verification
To test the backup script manually:
```bash
cd /path/to/project
./scripts/backup.sh
```
Check the output directory to verify `.sql.gz` and `.tar.gz` creation.
