def create_channels_if_not_exist(consumer, channels, channelName):
    exisistingChannels = consumer.topics()
    if channelName not in exisistingChannels:
        channels.append(channelName)
        consumer.subscribe(channelName)
        print("Channel", channelName, "has been created.")
    else:
        print("Channel ",channelName, "already exist.")

def init_or_refresh_channels(consumer, channels):
    exisistingChannels = list(consumer.topics())
    for channel in exisistingChannels:
        if channel not in channels: 
            print("Channel", channel, "has been fetched then initialized.")
            channels.append(channel)

    return channels


def alert_channel(producer, channelName, value, usernameConnected):
    producer.send(channelName, { usernameConnected: value })

# def check_if_refresh(consumer, channels):
#     refresh = False
#     exisistingChannels = list(consumer.topics())
#     if len(channels) > 0: 
#         for channel in exisistingChannels:
#             if channel not in channels: 
#                 refresh = True
#     else:
#         refresh = True

#     return refresh