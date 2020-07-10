import socket, select

# send message to a particular peer
def send_to(sock, username, my_username, message):
    check = False
    for socket in connected_list:
        if socket != sock_server:
            i,p=socket.getpeername()
            if usernames[i,p] == username:
                try:
                    check = True
                    socket.send("DELIVERY " + my_username + " " + message + "\n")
                    sock.send("SEND-OK\n")
                except:
                    socket.close()
                    connected_list.remove(socket)
    if (check == False):
        sock.send("UNKNOWN\n")
        
if __name__ == "__main__":
    name=""
    usernames={}
    connected_list = []
    buffer = 10
    port = 3000
    host = "0.0.0.0"

    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock_server.bind((host, port))
    sock_server.listen(10) 

    connected_list.append(sock_server)

    print "\033[93mServer running. On port: " + str(port) + ". Host: " + host + ". \33[0m" 

    while 1:
        rList,wList,error_sockets = select.select(connected_list,[],[])

        for sock in rList:
            # new connection recieved through sock_server 
            if sock == sock_server:
                mysock, index = sock_server.accept()
                data = mysock.recv(2)
                datalong = data

                while (data.find("\n") == -1):
                    data = mysock.recv(2)
                    datalong += data

                data = datalong
                connected_list.append(mysock)
                usernames[index]=""

                if data.startswith( 'HELLO-FROM' ):
                    data_ = data.split('HELLO-FROM ')
                    name = data_[1]
                    name = name.split('\n')
                    name = name[0]

                    # if the username is in use
                    if name in usernames.values():
                        mysock.send("IN-USE\n")
                        del usernames[index]
                        connected_list.remove(mysock)
                        mysock.close()
                        continue
                    else:
                        usernames[index]=name
                        print "\033[32mNew client \033[34m(%s, %s)\033[32m connected." % index," Username: \033[34m(" + usernames[index] + ")\33[0m"
                        mysock.send("HELLO " + name + "\n")
            else:
                # messages from not a new client
                try:
                    data1 = sock.recv(2)
                    datalong = data1

                    while (data1.find("\n") == -1):
                        data1 = sock.recv(2)
                        datalong += data1

                    data=datalong[:datalong.index("\n")]
                    
                    i,p=sock.getpeername()
                    if data == "!quit":
                        print "\r\33[1m"+"\33[31m---Client (%s, %s) has quit the chat" % (i,p),". Username: (" + usernames[(i,p)] + ")\33[0m"
                        del usernames[(i,p)]
                        connected_list.remove(sock)
                        sock.close()
                        continue
                    else:
                        print "Client username: \033[34m@" + usernames[(i,p)] + "\33[0m. Message: \033[34m" + data + "\33[0m"
                        if (data == "WHO"):
                            my_string = ', '.join(usernames.values())
                            sock.send("WHO-OK " + my_string+"\n")
                        elif data.startswith( 'SEND' ) and data.count(" ") > 0:
                            parts = data.split(' ')
                            username_to = parts[1]
                            message = ' '.join(parts[2:len(parts)])
                            send_to(sock, username_to, usernames[(i,p)], message)
                        elif (data.startswith( 'SEND' ) == True or data.startswith( '@' ) == True or data.startswith( '!who' ) == True or data.startswith( 'HELLO-FROM' ) == True):
                            sock.send("BAD-RQST-HDR\n")
                        else: 
                            sock.send("BAD-RQST-BODY\n")
                except:
                    (i,p)=sock.getpeername()
                    print "\r\33[1m"+"\33[31m---Client (%s, %s) is offline (unexpected attempt)" % (i,p),". Username: (" + usernames[(i,p)] + ")\33[0m"
                    del usernames[(i,p)]
                    connected_list.remove(sock)
                    sock.close()
                    continue

sock_server.close()