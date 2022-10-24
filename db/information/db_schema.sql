CREATE TABLE Event ( 
	id                   INTEGER NOT NULL  PRIMARY KEY  ,
	start                DATETIME NOT NULL    ,
	finish               DATETIME NOT NULL    ,
	title                VARCHAR(50) NOT NULL    ,
	repeat               DATETIME     ,
	description          TEXT     
 );

CREATE TABLE User ( 
	id                   INTEGER NOT NULL  PRIMARY KEY  ,
	login                VARCHAR(20) NOT NULL    ,
	password             VARCHAR(80) NOT NULL    ,
	username             VARCHAR(50)     ,
	email                VARCHAR(50)     ,
	teamworking          BOOLEAN  DEFAULT 0   
 );

CREATE TABLE user_event ( 
	user_id              INTEGER NOT NULL    ,
	event_id             INTEGER NOT NULL    ,
	FOREIGN KEY ( user_id ) REFERENCES User( id ) ON DELETE CASCADE ,
	FOREIGN KEY ( event_id ) REFERENCES Event( id ) ON DELETE CASCADE 
 );

CREATE TABLE Category ( 
	Id                   INTEGER NOT NULL  PRIMARY KEY  ,
	Name                 VARCHAR(100) NOT NULL    ,
	Description          TEXT     ,
	User_id              INTEGER NOT NULL    ,
	FOREIGN KEY ( User_id ) REFERENCES User( id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE Category_event ( 
	category_id          INTEGER NOT NULL    ,
	event_id             INTEGER NOT NULL    ,
	FOREIGN KEY ( event_id ) REFERENCES Event( id ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( category_id ) REFERENCES Category( Id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE Task ( 
	id                   INTEGER NOT NULL  PRIMARY KEY  ,
	title                VARCHAR(50) NOT NULL    ,
	description          TEXT     ,
	deadline             DATETIME     ,
	time_to_do           DATETIME     ,
	repeat               DATETIME     ,
	event_id             INTEGER     ,
	user_id              INTEGER NOT NULL    ,
	FOREIGN KEY ( event_id ) REFERENCES Event( id )  ,
	FOREIGN KEY ( user_id ) REFERENCES User( id ) ON DELETE CASCADE 
 );

