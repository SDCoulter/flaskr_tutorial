-- Creating tables and columns for examples - to be removed later for
-- formula 1 data, etc.

-- Drop the tables if they exist already to replace with our correct versions.
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

-- Create the tables how we wish.
CREATE TABLE user (
  if INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  if INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
