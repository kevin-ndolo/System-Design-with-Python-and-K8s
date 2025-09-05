-- Remove the user if it already exists (from any host)
-- This prevents errors when re-running the script during development
DROP USER IF EXISTS 'auth_user'@'%';

-- Create a new user who can connect from any IP address
-- This is important when your app runs in containers or on remote servers
CREATE USER 'auth_user'@'%' IDENTIFIED BY 'Qwerty123';

-- Delete the database if it already exists
-- Useful for resetting the database during testing or development
DROP DATABASE IF EXISTS auth;

-- Create a new database named 'auth'
-- This will store user login information
CREATE DATABASE auth;

-- Give the new user full access to everything in the 'auth' database
-- '@%' means the user can connect from any machine, not just localhost
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'%';

-- Apply the permission changes immediately
FLUSH PRIVILEGES;

-- Switch to using the 'auth' database
USE auth;

-- Create a table to store user credentials
-- Note: In real applications, passwords should be encrypted or hashed
CREATE TABLE user (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

-- Add a sample user to test the login functionality
-- You can change or remove this later as needed
INSERT INTO user (email, password) VALUES ('kevin@email.com', 'Qwerty123');
