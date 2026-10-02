# Bug Story
## The Phantom Qdrant Timeout

During the final integration, we discovered an invisible bug where the Uvicorn server would completely freeze up on startup, providing zero logs. It turned out that the database initialization was running synchronously at the module level when `app.routes.chat` was imported. Because the Docker container for PostgreSQL 16 was crashing due to an old PostgreSQL 15 volume left behind from a previous project, the SQL connection blocked endlessly.

### The Fix
We implemented a robust connection handling and discovered the project had actually been migrated to `pgvector` but left dead Qdrant configuration variables around. Deleting the old volume (`docker compose down -v`) and running a clean `docker compose up -d` completely resolved the issue, and we purged the dead Qdrant files.
