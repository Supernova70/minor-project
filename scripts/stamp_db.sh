#!/bin/sh
# Run this ONCE manually after adding Alembic to an existing database.
# It tells Alembic "the DB is already at 0001, skip that migration."
# After running this, normal "alembic upgrade head" handles everything.
docker-compose exec phishing-guard alembic stamp 0001
