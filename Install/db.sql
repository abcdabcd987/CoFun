SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE TABLE IF NOT EXISTS `Contest` (
  `ContestID` int(9) NOT NULL AUTO_INCREMENT,
  `ContestTitle` varchar(130) NOT NULL,
  `ContestStartTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ContestEndTime` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `ContestDescription` text NOT NULL,
  PRIMARY KEY (`ContestID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000 ;

CREATE TABLE IF NOT EXISTS `ContestProblem` (
  `ContestID` int(9) NOT NULL,
  `ProblemID` int(9) NOT NULL,
  `ProblemTitle` varchar(100) NOT NULL,
  `ProblemOrder` int(9) NOT NULL,
  KEY `cid` (`ContestID`),
  KEY `pid` (`ProblemID`),
  KEY `order` (`ProblemOrder`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Privilege` (
  `PrivilegeID` int(9) NOT NULL AUTO_INCREMENT,
  `UserID` int(9) NOT NULL,
  `Level` int(9) NOT NULL,
  PRIMARY KEY (`PrivilegeID`),
  KEY `uid` (`UserID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `Problem` (
  `ProblemID` int(9) NOT NULL AUTO_INCREMENT,
  `ProblemTitle` varchar(100) NOT NULL,
  `ProblemDescription` text NOT NULL,
  `ProblemInput` text NOT NULL,
  `ProblemOutput` text NOT NULL,
  `ProblemSampleIn` text NOT NULL,
  `ProblemSampleOut` text NOT NULL,
  `ProblemTime` int(9) NOT NULL,
  `ProblemMemory` int(9) NOT NULL,
  `ProblemHint` text,
  `ProblemSource` varchar(100) DEFAULT NULL,
  `ProblemUpdateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ProblemID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000 ;

CREATE TABLE IF NOT EXISTS `Result` (
  `ResultID` int(9) NOT NULL AUTO_INCREMENT,
  `SubmitID` int(9) NOT NULL,
  `Result` tinyint(4) NOT NULL,
  `RunTime` int(9) NOT NULL,
  `RunMemory` int(9) NOT NULL,
  `Diff` text NOT NULL,
  PRIMARY KEY (`ResultID`),
  KEY `sid` (`SubmitID`),
  KEY `res` (`Result`),
  KEY `time` (`RunTime`),
  KEY `memory` (`RunMemory`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `Submit` (
  `SubmitID` int(9) NOT NULL AUTO_INCREMENT,
  `ProblemID` int(9) NOT NULL,
  `ContestID` int(9) NOT NULL,
  `UserID` int(9) NOT NULL,
  `SubmitTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `SubmitLanguage` int(9) NOT NULL,
  `SubmitCode` text NOT NULL,
  `SubmitStatus` tinyint(4) NOT NULL,
  `SubmitRunTime` int(9) NOT NULL,
  `SubmitRunMemory` int(9) NOT NULL,
  `CodeLength` int(9) NOT NULL,
  `JudgeTime` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `CompilerInfo` text NOT NULL,
  PRIMARY KEY (`SubmitID`),
  KEY `uid` (`UserID`),
  KEY `pid` (`ProblemID`),
  KEY `cid` (`ContestID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `User` (
  `UserID` int(9) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(50) NOT NULL,
  `UserEmail` varchar(100) NOT NULL,
  `UserPassword` char(40) NOT NULL,
  `UserRegisterTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `UserEmail_UNIQUE` (`UserEmail`),
  UNIQUE KEY `UserName_UNIQUE` (`UserName`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

