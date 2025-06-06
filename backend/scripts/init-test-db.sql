-- Test Database Initialization Script

-- Create test database if it doesn't exist
CREATE DATABASE IF NOT EXISTS wish_wall_test
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Use the test database
USE wish_wall_test;

-- Grant privileges to test user
GRANT ALL PRIVILEGES ON wish_wall_test.* TO 'wish_wall_test_user'@'%';
GRANT ALL PRIVILEGES ON wish_wall_test.* TO 'root'@'%';

-- Flush privileges
FLUSH PRIVILEGES;

-- Set character set variables for the session
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_database = utf8mb4;
SET character_set_results = utf8mb4;
SET character_set_server = utf8mb4;
SET collation_connection = utf8mb4_unicode_ci;
SET collation_database = utf8mb4_unicode_ci;
SET collation_server = utf8mb4_unicode_ci;

-- Log initialization
SELECT 'Test database wish_wall_test initialized successfully' AS message; 