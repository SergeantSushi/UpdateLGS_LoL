#!/usr/bin/env python2

'''
PLEASE READ THIS SCRIPT BEFORE RUNNING IT!

By using this script you accept full liability for what this script may do to 
your computer.  The only legitimate source for obtaining this script is listed 
below.  If you downloaded this script from anywhere else, it may have been 
repurposed to do nefarious things to your computer in addition to updating your
LGS profile.

Original script: https://github.com/SergeantSushi/UpdateLGS_LoL
Can I make modifications to fix bugs/suit my needs? Yes
Can I share this? Only if you provide credit to the original author with a link
                  to the aforementioned repository.
Can I profit from or market from this script with a paid product? No

'''

import os
import sys
import subprocess

'''
Closes a process through the Windows CMD
Input:  aProcess - The process to close
Output:          - The path to the process
        ""         Empty string for no process found
'''
def closeProcess( aProcess ):
    try:
        print "Attempting to close " + aProcess + "!"
        lLCoreLoc = runWindowsCMD( "wmic process where \"name=\'" + aProcess + "\'\" get ExecutablePath" )
        lLCoreLoc = lLCoreLoc.strip()
        lLCoreLoc = lLCoreLoc.replace("\r","\n")
        lLCoreLocLines = lLCoreLoc.split("\n")
        for lLine in lLCoreLocLines:
            if not lLine.find( aProcess ) < 0:
                runWindowsCMD( "taskkill /im " + aProcess + " /f" )
                runWindowsCMD( "timeout /t 1" )
                return lLine
        return ""
    except:
        print "Failed to close " + aProcess + "!"
        return ""

'''
Identifies which Logitech Gaming Software profile pertains to "League of Legends"
Input:  aProfileDir - The directory the LGS profiles are in.
        aStandard   - The identifier to look for in the profile.
Output:             - The name of the identified profile.
        -1 - Error code for no profile found
'''
def identifyLeagueProfile( aProfileDir, aStandard ="League of Legends" ):
    lProfiles = os.listdir( aProfileDir )
    for lProfile in lProfiles:
        try:
            lFile = open( aProfileDir + lProfile, "r" )
            lContents = lFile.read()
            if aStandard in lContents:
                lFile.close()
                return lProfile
            lFile.close()
        except:
            print "WARNING: Error parsing " + lProfile + "!"
            continue
    print "Failed to find Logitech profile named \"" + aStandard + "\""
    return -1

'''
Sanitization sold separately.
'''
def runWindowsCMD( aCMD ):
    return subprocess.Popen( aCMD, stdout=subprocess.PIPE, shell=True ).communicate()[0]

'''
Finds the user's League of Legends directory.
Input:  [None]
Output: lReturn - A list of paths associated with League of Legends
'''
def generateLeaguePath():
    #If you have a swanky League path this probably won't find it.
    lReturn = list()
    lPoss = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lLPath = "\\RADS\\solutions\\lol_game_client_sln\\releases"
    lDrives = list( "%s:" % d for d in lPoss if os.path.exists("%s:" % d) )
    #Some logical places for League to be in.
    lLocations = [ "\\Riot Games\\League of Legends", 
                   "\\Program Files\\Riot Games\\League of Legends", 
                   "\\Program Files (x86)\\Riot Games\\League of Legends", 
                   "\\PBE", 
                   "\\Program Files\\PBE", 
                   "\\Program Files (x86)\\PBE" 
                   ]
    #Create a list of league paths
    for lDrive in lDrives:
        for lLoc in lLocations:
            if( os.path.isdir( lDrive + lLoc + lLPath ) ):
                lPostPath = findPostPath( lDrive + lLoc + lLPath )
                lReturn.append ( lDrive + lLoc + lLPath + lPostPath )
    return lReturn

'''
Determines which patch folder to use.
Input:  aPath - The League of Legends file path up to the particular patch.
Output:       - The path to the most current League of Legends executable.
Output: -1    - Error code for non numeric file paths.
'''
def findPostPath( aPath ):
    #Add the part that changes so the SOON TM replays will work.
    lFolders = os.listdir( aPath )
    lVersions = list()
    #Some dank code below
    for lFolder in lFolders:
        try:
            lFolderInt = int( lFolder.replace( ".", "" ) )
            lVersions.append( (lFolderInt,lFolder) )
        except:
            pass
    sorted( lVersions, key=lambda x: x[1] )
    return "\\" + lVersions[ len( lVersions ) - 1 ][1] + "\\deploy\\League of Legends.exe"

'''
Updates the Logitech Gaming Software profile associated with League of Legends
Input:  aLGSLeagueProfile - The path to the LGS profiles.
Output: 0                 - Finished without errors.
'''
def updateLeagueProfile( aLGSLeagueProfile ):
    #Set start and end tags
    lStartTag = "</description>"
    lEndTag = "<signature"
    
    #Close LGS process to prevent interference
    lLCoreLoc = closeProcess( "LCore.exe" )
    
    #Update league path
    lFile = open( aLGSLeagueProfile, "r" )
    lContents = lFile.read()
    lFile.close()
    
    '''
    This is not worth importing an XML parser.
    This will probably break next patch when Rito figures out how to not change 
    the location of the game's executable every patch.
    '''
    
    lStart = lContents.find( lStartTag ) + len( lStartTag ) + 1
    lEnd = lContents.find( lEndTag ) - 5
    lPrePath = lContents[:lStart]
    lPostPath = lContents[lEnd:]
    #Write new config file
    lLeaguePaths = generateLeaguePath()
    lFile = open( aLGSLeagueProfile, "w" )
    lFile.write( lPrePath )
    for lPath in lLeaguePaths:
        lFile.write( "    <target path=\"" + lPath + "\"/>" )
        if lPath != lLeaguePaths[ len( lLeaguePaths ) - 1 ]:
            lFile.write( "\n" )
    lFile.write( lPostPath )
    lFile.close()
    if not lLCoreLoc == "":
        print "Attempting to open " + lLCoreLoc + "!\nYou may close this window now!"
        runWindowsCMD( lLCoreLoc )
    return 0

'''
Main method for stringing this plate of spagetti together.
Input:  argc - Number of command line arguments.
Input:  argv - List of the command line arguments.
Output: 0    - The program finished without errors.
'''
def main( argc, argv ):
    lLGSPath = "\\AppData\\Local\\Logitech\\Logitech Gaming Software\\profiles\\"
    lLGSPath = runWindowsCMD( "echo %USERPROFILE%" ) + lLGSPath
    lLGSPath = lLGSPath.replace( "\r","" )
    lLGSPath = lLGSPath.replace( "\n","" )
    
    if argc == 2:
        lLeagueProfile = identifyLeagueProfile( lLGSPath, argv[ 1 ] )
        if lLeagueProfile < 0:
            return -1
    else:
        lLeagueProfile = identifyLeagueProfile( lLGSPath )
    updateLeagueProfile( lLGSPath + lLeagueProfile )
    return 0

main( len( sys.argv ), sys.argv )