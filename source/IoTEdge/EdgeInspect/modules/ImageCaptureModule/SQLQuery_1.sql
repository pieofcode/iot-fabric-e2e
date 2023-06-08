select * from sys.databases where name = "EdgeInspect";

IF OBJECT_ID(N'dbo.ImageCaptureLogs', N'U') IS NULL 
BEGIN
    CREATE TABLE ImageCaptureLogs (
        Id int IDENTITY(1,1) PRIMARY KEY,
        ImageId varchar(255) NOT NULL,
        Orientation varchar(255) NOT NULL,
        FilePath varchar(255) NOT NULL,
        Tag varchar(255) NOT NULL,
        Classification VARCHAR(1000),
        CreatedOn DATETIME2
    );
END

DROP TABLE ImageCaptureLogs;

INSERT INTO ImageCaptureLogs (ImageId, Orientation, FilePath, Tag, Classification, CreatedOn) 
VALUES (?, ?, ?, ?, ?, ?)