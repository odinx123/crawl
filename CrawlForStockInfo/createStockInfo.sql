CREATE DATABASE `testForStockInfo`;

USE `testForStockInfo`;

CREATE TABLE `stockInfo` (
    `ID` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(30),
    `url` VARCHAR(255),
    `content` TEXT
);
