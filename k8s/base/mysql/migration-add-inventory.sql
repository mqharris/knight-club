-- Add gold and inventory system
USE knightclub;

-- Add gold column to users
ALTER TABLE users
  ADD COLUMN gold INT UNSIGNED NOT NULL DEFAULT 0 AFTER password_hash;

-- Create inventory table
CREATE TABLE IF NOT EXISTS inventory (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  item_id INT UNSIGNED NOT NULL,
  quantity INT UNSIGNED NOT NULL DEFAULT 1,
  equipped_to_knight_id BIGINT UNSIGNED NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_inventory_user_id (user_id),
  KEY idx_inventory_equipped (equipped_to_knight_id),
  CONSTRAINT fk_inventory_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_inventory_knight
    FOREIGN KEY (equipped_to_knight_id) REFERENCES knights(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
