-- Dev-only bootstrap. Runs once, on first creation of the volume.
-- The application connects as bizops_app so Row Level Security is enforced.
CREATE ROLE bizops_app LOGIN PASSWORD 'bizops_app_dev' NOSUPERUSER NOBYPASSRLS;
CREATE DATABASE bizops_test OWNER bizops_owner;