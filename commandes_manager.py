import re
import channel_manager as channelManager
import logger_manager as logger

def cmd_msg(producer, channel, msg, usernameConnected):
    channelName = substring_after(channel, "#")
    # logger.log_info("{channelName} >> {usernameConnected} : {msg}")
    print(channelName, ">>", usernameConnected ,":", msg)
    producer.send(channelName, {usernameConnected: msg})


def cmd_join(consumer, producer, line, channels, currentChannel, usernameConnected):
    patternMatcher = '^#(\w+$)'
    validate = re.match(patternMatcher, line)
    if validate is not None:
        channelName = substring_after(line, "#")
        channelManager.create_channels_if_not_exist(consumer, channels, channelName)
        # informer le channel courant que l'utilisateur quitte le channel
        if currentChannel is not None:
            messageLeft = "has left the channel"
            channelManager.alert_channel(producer, currentChannel, usernameConnected, messageLeft)

        # informer le channel rejoint que nous sommes arriver
        messageJoin = "has joined the channel"
        # channelManager.alert_channel(producer, channelName, usernameConnected, messageJoin)
        channelManager.init_or_refresh_channels(consumer, channels)
        return line
    else:
        logger.log_info("Invalid syntaxe")



def cmd_part(consumer, producer, channelToUnfollow, currentChannel, channelsLoaded):
    # TODO Si l'utilisateur est dans le channel
    # Il peut se désabonner du channel
    currentChannel = substring_after(currentChannel, "#")
    if currentChannel == channelToUnfollow:
        consumer.unsubscribe()
        channelsLoaded.remove(currentChannel)
        consumer.subscribe(channelsLoaded)
        
        # Je dois me désabonner du topic specific
        # Puis mettre à jour le tableau global
        # Peut être avec la fonction channelManager.init_or_refresh_channels
        # Je dois ensuite déplacer l'utilisateur 
        # dans un canal auquel il est toujours abonné
        logger.log_debug("Channel {currentChannel} was unfollowed.")
        logger.log_debug("You will be move to: {channelsLoaded[0]}")
        currentChannel = channelsLoaded[0]
        
    else:
        logger.log_info("This command can only be run throught the channel: {channelToUnfollow}.")
        logger.log_info("Currently channel: {currentChannel}.")

    return { "currentChannel": currentChannel, "channelsLoaded": channelsLoaded }
    

def cmd_log(consumer, channels):
    print('Réel', consumer.topics())
    print('Tableau', channels)

def cmd_quit(producer, line):
    # TODO À compléter
    pass

def substring_after(s, delim):
    return s.partition(delim)[2]
