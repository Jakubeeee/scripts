rem use this script to call maven with any java version
rem this package should be included in the PATH environmental variable
rem the JAVA_X_HOME environmental variable should be declared (where X is the desired java version)
rem e.g. to run maven with java 17 use: mvnx 17 clean install
@echo off
setLocal enableDelayedExpansion
echo temporary java version: %1
set JAVA_XX_VARIABLE=!JAVA_%1_HOME!
set JAVA_HOME=!JAVA_XX_VARIABLE!
echo temporary java home: %JAVA_HOME%
for /f "tokens=1,* delims= " %%a in ("%*") do set MAVEN_OPTIONS=%%b
echo maven command: mvn %MAVEN_OPTIONS%
call mvn %MAVEN_OPTIONS%