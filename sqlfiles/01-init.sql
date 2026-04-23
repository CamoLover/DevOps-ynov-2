CREATE DATABASE IF NOT EXISTS app_db;

USE app_db;

CREATE TABLE IF NOT EXISTS utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO utilisateurs (nom, email, role) VALUES
    ('Alice Martin', 'alice.martin@example.com', 'Administrateur'),
    ('Bob Dupont', 'bob.dupont@example.com', 'Développeur'),
    ('Charlie Bernard', 'charlie.bernard@example.com', 'Développeur'),
    ('Diana Petit', 'diana.petit@example.com', 'Chef de projet');
