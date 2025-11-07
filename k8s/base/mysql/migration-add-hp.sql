-- Migration to add HP and is_alive columns to existing knights table
-- Run this on your DO droplet if you already have knights in the database

USE knightclub;

-- Add current_hp column
ALTER TABLE knights 
ADD COLUMN current_hp INT UNSIGNED NOT NULL DEFAULT 100;

-- Add max_hp column
ALTER TABLE knights 
ADD COLUMN max_hp INT UNSIGNED NOT NULL DEFAULT 100;

-- Add is_alive column
ALTER TABLE knights 
ADD COLUMN is_alive BOOLEAN NOT NULL DEFAULT TRUE;

-- Verify the changes
DESCRIBE knights;

SELECT CONCAT('Migration complete! Updated ', COUNT(*), ' knights.') as result FROM knights;
