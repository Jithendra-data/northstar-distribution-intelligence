-- Run in a development SQL Server instance. The static website has no DB dependency.
IF DB_ID(N'NorthStarAnalytics') IS NULL CREATE DATABASE NorthStarAnalytics;
GO
USE NorthStarAnalytics;
GO

