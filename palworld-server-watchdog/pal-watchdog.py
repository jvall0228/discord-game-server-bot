import socket
import struct
import requests
import time
import env

from rcon import RCONClient

#Time in minutes until restart
RESTART_TIME = 240

#Timeout interval in minutes until shutdown from no players
PLAYER_TIMEOUT = 10

#Time interval in seconds before shutdown
SHUTDOWN_INTERVAL = 10

#Arguments for starting palworld server
PALWORLD_START_ARGS = ''

#returns true on restart
#returns false on shutdown
#returns None on error
def watchServer():
    client = RCONClient()
    shutdown_timer = 0
    timer = 0
    players = []

    while True:
        try:
            #Get Players
            new_player_list = client.ShowPlayers()
            logins = set(new_player_list) - set(players)
            logouts = set(players) - set(new_player_list)

            players = new_player_list

            #Broadcast logins and logouts
            for player in logins:
                client.broadcast(player[0] + ' has logged in')

            for player in logouts:
                client.broadcast(player[0] + ' has logged out')

            #Update timers
            if len(client.showPlayers()) == 0:
                shutdown_timer += 1
            else:
                shutdown_timer = 0

            timer += 1

            #Check backup conditions
            if timer % 3600 == 0:
                client.save()
                backup('hourly')

            #Check shutdown and restart conditions
            if shutdown_timer >= PLAYER_TIMEOUT*60:
                client.save()
                backup('latest')
                client.shutdown(SHUTDOWN_INTERVAL, 'Shutting down in 10 seconds since no players were found')
                time.sleep(SHUTDOWN_INTERVAL+10)
                return False

            if timer/60 == RESTART_TIME*60 - 30*60:
                client.broadcast('Restarting in 30 minutes')

            if timer/60 == RESTART_TIME*60 - 10*60:
                client.broadcast('Restarting in 10 minutes')

            if timer/60 >= RESTART_TIME*60:
                client.save()
                backup('latest')
                client.shutdown(SHUTDOWN_INTERVAL, 'Shutting down in 10 seconds for restart')
                time.sleep(SHUTDOWN_INTERVAL+10)
                return True

            time.sleep(1)
            
        except Exception as error:
            print(error)
            return None
        
def startServer():
    #Start PalWorld.sh script
    raise NotImplementedError

def backup(backupName:str):
    #Make a backup folder of the save using the name
    #Compress the folder
    raise NotImplementedError

def destroyDroplet():
    #Send REST Request to trigger DO function that destroys the droplet
    raise NotImplementedError

startServer()

while True:
    if not watchServer():
        break
    else:
        startServer()

destroyDroplet()