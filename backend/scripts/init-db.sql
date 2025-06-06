-- Database initialization script for Wish Wall
-- This script runs when the MySQL container starts for the first time

-- Set charset and collation for the database
ALTER DATABASE wish_wall CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create additional user if needed (optional)
-- The main database and root user are already created via environment variables

-- Set timezone
SET time_zone = '+00:00';

-- Show database info
SELECT 'Database wish_wall initialized successfully' AS message; 