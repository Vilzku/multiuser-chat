import socket
import threading

host = "localhost"
port = 2245

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print("server running...")

class Client:
  def __init__(self, sock, username, channel):
    self.sock = sock
    self.username = username
    self.channel = channel

clientList = {
  "general": [],
  "random": [],
  "memes": [],
}

def joinChannel(client):
  client.sock.send("talking in '{}'".format(client.channel).encode("utf-8"))
  message = "{} joined".format(client.username)
  clientList[client.channel].append(client)
  broadcastMessage(message, client)

def leaveChannel(client):
  message = "{} left".format(client.username)
  clientList[client.channel].remove(client)
  broadcastMessage(message, client)

def changeChannel (client, channel):
  leaveChannel(client)
  client.channel = channel
  joinChannel(client)

def disconnect(client):
  print("disconnecting", client.username)
  leaveChannel(client)
  client.sock.close()

def sendMessage(client, message):
  try:
    client.sock.send(message.encode("utf-8"))
  except:
    disconnect(client)

def broadcastMessage(message, fromClient):
  for client in clientList[fromClient.channel]:
    if client.username != fromClient.username:
      sendMessage(client, message)

def handleMessage(client):
  while True:
    try:
      message = client.sock.recv(1024).decode("utf-8")

      # Change channel
      if message.startswith("/c"):
        channel = message.replace("/c", "").strip()
        if channel in clientList:
          changeChannel(client, channel)
        else:
          sendMessage(client, "channel does not exist")
        continue

      # Whisper - private message
      if message.startswith("/w"):
        message = message.replace("/w", "").strip().split(" ", 1)
        username = message[0]
        message = message[1]
        for to_client in clientList[client.channel]:
          if to_client.username == username:
            sendMessage(to_client, "whisper from {}: {}".format(client.username, message))
            break
        else:
          sendMessage(client, "user not online")
        continue

      broadcastMessage("{}: {}".format(client.username, message), client)
    except:
      disconnect(client)
      break

def listenForClients():
  while True:
    try:
      sock, addr = server.accept()

      sock.send("REQ_USERNAME".encode("utf-8"))
      username = sock.recv(1024).decode("utf-8")
      channel = next(iter(clientList))

      client = Client(sock, username, channel)
      joinChannel(client)

      print(f"{addr} {username} connected")
      
      thread = threading.Thread(target=handleMessage, args=(client,))
      thread.start()
    except:
      break

listenForClients()