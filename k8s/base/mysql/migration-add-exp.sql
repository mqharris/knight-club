-- Add exp column to knights table
USE knightclub;

ALTER TABLE knights
  ADD COLUMN exp INT UNSIGNED NOT NULL DEFAULT 0 AFTER level;
