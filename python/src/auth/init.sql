-- Remove the user if it already exists (from any host)
-- This avoids conflicts when re-running the script
DROP USER IF EXISTS 'auth_user'@'%';

-- Create a new user that can connect from any IP address
-- This is important for containerized apps like Kubernetes pods
CREATE USER 'auth_user'@'%' IDENTIFIED BY 'Qwerty123';

-- Delete the database if it already exists
-- Useful during development to reset everything
DROP DATABASE IF EXISTS auth;

-- Create a new database named 'auth'
CREATE DATABASE auth;

-- Give the new user full access to the 'auth' database
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'%';

-- Apply the permission changes immediately
FLUSH PRIVILEGES;

-- Switch to using the 'auth' database
USE auth;

-- Create a table to store user login credentials
-- Note: In production, passwords should be hashed for security
CREATE TABLE user (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

-- Add a sample user for testing login functionality
-- You can change this later or add more users as needed
INSERT INTO user (email, password) VALUES ('kevin@email.com', 'Qwerty123');
