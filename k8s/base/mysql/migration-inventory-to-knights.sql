-- Migration: Change inventory from user-scoped to knight-scoped
-- This makes each knight have their own inventory, but gold stays with users

USE knightclub;

-- First, drop the equipped_to_knight_id column (no longer needed)
ALTER TABLE inventory DROP FOREIGN KEY fk_inventory_knight;
ALTER TABLE inventory DROP COLUMN equipped_to_knight_id;

-- Change user_id to knight_id
ALTER TABLE inventory DROP FOREIGN KEY fk_inventory_user;
ALTER TABLE inventory DROP INDEX idx_inventory_user_id;
ALTER TABLE inventory CHANGE COLUMN user_id knight_id BIGINT UNSIGNED NOT NULL;

-- Add new foreign key for knight_id
ALTER TABLE inventory ADD KEY idx_inventory_knight_id (knight_id);
ALTER TABLE inventory ADD CONSTRAINT fk_inventory_knight
  FOREIGN KEY (knight_id) REFERENCES knights(id)
  ON DELETE CASCADE;

-- Add is_equipped boolean flag
ALTER TABLE inventory ADD COLUMN is_equipped BOOLEAN NOT NULL DEFAULT FALSE;
