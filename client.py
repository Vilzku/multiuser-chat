import socket
import threading

username = input("enter username to connect: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 2245))

def disconnect():
  client.close()
  print("disconnected")

def listenMessages():
  while True:
    try:
      message = client.recv(1024).decode("utf-8")
      if message == "REQ_USERNAME":
          client.send(username.encode("utf-8"))
      else:
        print(message)
    except:
      disconnect()
      break

def sendMessage():
  while True:
    try:
      message = input("")

      if message == "/q":
        client.close()
        break

      client.send(message.encode("utf-8"))
    except:
      disconnect()
      break


thread_receive = threading.Thread(target=listenMessages)
thread_receive.start()

thread_send = threading.Thread(target=sendMessage)
thread_send.start()