-- MySQL dump 10.13  Distrib 5.1.69, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: cofun
-- ------------------------------------------------------
-- Server version	5.1.69

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Contest`
--

DROP TABLE IF EXISTS `Contest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Contest` (
  `ContestID` int(9) NOT NULL AUTO_INCREMENT,
  `ContestTitle` varchar(130) NOT NULL,
  `ContestStartTime` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `ContestEndTime` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `ContestDescription` text NOT NULL,
  `ContestPrincipal` int(11) NOT NULL,
  `UpRating` float NOT NULL DEFAULT '0',
  `DownRating` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`ContestID`)
) ENGINE=MyISAM AUTO_INCREMENT=1035 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ContestProblem`
--

DROP TABLE IF EXISTS `ContestProblem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ContestProblem` (
  `ContestID` int(9) NOT NULL,
  `ProblemID` int(9) NOT NULL,
  `ProblemTitle` varchar(100) NOT NULL,
  `ProblemOrder` int(9) NOT NULL,
  KEY `cid` (`ContestID`),
  KEY `pid` (`ProblemID`),
  KEY `order` (`ProblemOrder`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Privilege`
--

DROP TABLE IF EXISTS `Privilege`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Privilege` (
  `PrivilegeID` int(9) NOT NULL AUTO_INCREMENT,
  `UserID` int(9) NOT NULL,
  `Level` int(9) NOT NULL,
  PRIMARY KEY (`PrivilegeID`),
  KEY `uid` (`UserID`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Problem`
--

DROP TABLE IF EXISTS `Problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Problem` (
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
  `ProblemUpdateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `SpecialJudge` tinyint(4) NOT NULL,
  `Solved` int(9) NOT NULL DEFAULT '0',
  `Submit` int(9) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ProblemID`)
) ENGINE=MyISAM AUTO_INCREMENT=1252 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `RatingChanges`
--

DROP TABLE IF EXISTS `RatingChanges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RatingChanges` (
  `UserID` int(9) DEFAULT NULL,
  `ContestID` int(9) DEFAULT NULL,
  `RatingDelta` int(9) DEFAULT NULL,
  `EndRating` int(9) DEFAULT NULL,
  `EndTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Rank` int(9) DEFAULT NULL,
  `ContestTitle` varchar(130) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Result`
--

DROP TABLE IF EXISTS `Result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Result` (
  `ResultID` int(9) NOT NULL AUTO_INCREMENT,
  `SubmitID` int(9) NOT NULL,
  `Result` tinyint(4) NOT NULL,
  `RunTime` int(9) NOT NULL,
  `RunMemory` int(9) NOT NULL,
  `Diff` text NOT NULL,
  `Score` decimal(6,3) NOT NULL,
  PRIMARY KEY (`ResultID`),
  KEY `sid` (`SubmitID`),
  KEY `res` (`Result`),
  KEY `time` (`RunTime`),
  KEY `memory` (`RunMemory`)
) ENGINE=MyISAM AUTO_INCREMENT=145911 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Series`
--

DROP TABLE IF EXISTS `Series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Series` (
  `SeriesID` int(11) NOT NULL AUTO_INCREMENT,
  `SeriesTitle` varchar(130) NOT NULL,
  `SeriesCreateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `SeriesDescription` text NOT NULL,
  PRIMARY KEY (`SeriesID`),
  KEY `createtime` (`SeriesCreateTime`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SeriesProblem`
--

DROP TABLE IF EXISTS `SeriesProblem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SeriesProblem` (
  `SPID` int(11) NOT NULL AUTO_INCREMENT,
  `SeriesID` int(11) NOT NULL,
  `ProblemID` int(11) NOT NULL,
  `ProblemOrder` int(11) NOT NULL,
  PRIMARY KEY (`SPID`),
  KEY `pid` (`ProblemID`),
  KEY `sid` (`SeriesID`)
) ENGINE=InnoDB AUTO_INCREMENT=199 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Submit`
--

DROP TABLE IF EXISTS `Submit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Submit` (
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
  `SubmitScore` decimal(7,3) NOT NULL,
  `CodeLength` int(9) NOT NULL,
  `JudgeTime` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `CompilerInfo` text NOT NULL,
  `ContestPrincipal` int(9) NOT NULL DEFAULT '0',
  `Rating` int(9) DEFAULT '1500',
  PRIMARY KEY (`SubmitID`),
  KEY `uid` (`UserID`),
  KEY `pid` (`ProblemID`),
  KEY `cid` (`ContestID`)
) ENGINE=MyISAM AUTO_INCREMENT=14399 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `User` (
  `UserID` int(9) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(50) NOT NULL,
  `UserEmail` varchar(100) NOT NULL,
  `UserPassword` char(40) NOT NULL,
  `UserRegisterTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `RealName` varchar(50) DEFAULT NULL,
  `Submit` int(9) NOT NULL DEFAULT '0',
  `Solved` int(9) NOT NULL DEFAULT '0',
  `Signature` varchar(200) DEFAULT NULL,
  `Rating` int(9) DEFAULT '1500',
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `UserEmail_UNIQUE` (`UserEmail`),
  UNIQUE KEY `UserName_UNIQUE` (`UserName`)
) ENGINE=MyISAM AUTO_INCREMENT=130 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Wait`
--

DROP TABLE IF EXISTS `Wait`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Wait` (
  `ContestID` int(9) NOT NULL,
  PRIMARY KEY (`ContestID`),
  UNIQUE KEY `ContestID` (`ContestID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-11-19  7:51:03
