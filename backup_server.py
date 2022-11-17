import json
import sys
import pickle
import socket            
import threading
import time
import random
import os
server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ports=[6001,6002,6003,6004,6005]
availability=dict()
userfiles=list()
portchunks=dict()
filetonumberofchunks=dict()
lockstatus=dict()
alllogfiles=["lockstatus_info.pickle","ports_info.pickle","availability_info.pickle","userfiles_info.pickle","port_chunks_info.pickle","filetonumberofchunks_info.pickle"]
def logging():
	global server
	global ports
	global availability
	global userfiles
	global portchunks
	global filetonumberofchunks
	# print('23')
	try:

		# with open("server_port_info.pickle", "wb") as file:
		# 	pickle.dump(server,file,pickle.HIGHEST_PROTOCOL)

		with open("ports_info.pickle", "wb") as file:
			pickle.dump(ports,file,pickle.HIGHEST_PROTOCOL)

		with open("availability_info.pickle", "wb") as file:
			pickle.dump(availability,file,pickle.HIGHEST_PROTOCOL)

		with open("userfiles_info.pickle", "wb") as file:
			pickle.dump(userfiles,file,pickle.HIGHEST_PROTOCOL)

		with open("port_chunks_info.pickle", "wb") as file:
			pickle.dump(portchunks,file,pickle.HIGHEST_PROTOCOL)

		with open("filetonumberofchunks_info.pickle", "wb") as file:
			pickle.dump(filetonumberofchunks,file,pickle.HIGHEST_PROTOCOL)

		with open("lockstatus_info.pickle.pickle", "wb") as file:
			pickle.dump(lockstatus,file,pickle.HIGHEST_PROTOCOL)


	except EOFError as err:
		print('39 <-- ',err)





def check_chunkservers(port):
	global ports
	while True:
		time.sleep(10)
		try:
			client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        
			client.connect(('127.0.0.1', port))
			client.send('206'.encode())
			reply=client.recv(1024).decode()
			# print(reply)
			availability[int(port)]=True
			# if port not in ports:
			# 	ports.append(port)
			client.close()
			logging()

		except socket.error as err:   
			availability[int(port)]=False
			# ports.remove(port)
			print('Not connected with ',port,' ',(err))    

def getlogged_data():
	
	global server
	global ports
	global availability
	global userfiles
	global portchunks
	global filetonumberofchunks

	try:
		# with open("server_port_info.pickle", "rb") as file:
		# 	server=pickle.load(file)

		with open("ports_info.pickle", "rb") as file:
			ports=pickle.load(file)

		with open("availability_info.pickle", "rb") as file:
			availability=pickle.load(file)

		with open("userfiles_info.pickle", "rb") as file:
			userfiles=pickle.load(file)

		with open("port_chunks_info.pickle", "rb") as file:
			portchunks=pickle.load(file)

		with open("filetonumberofchunks_info.pickle", "rb") as file:
			filetonumberofchunks=pickle.load(file)

		with open("lockstatus_info.pickle", "rb") as file:
			lockstatus=pickle.load(file)

	    	
	except EOFError:
		server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ports=[6001,6002,6003,6004,6005]
		availability=dict()
		userfiles=list()
		portchunks=dict()
		filetonumberofchunks=dict()


def setup():
	global server
	global availability

	port=5999
	cwd = os.getcwd()
	for file in alllogfiles:

		dir = os.path.join(cwd,file)
		if not os.path.exists(dir):
			f = open(dir, "wb")
			f.close()

	getlogged_data()

	for cserv in ports:
		availability[cserv]=True

	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind(('127.0.0.1',port))
	server.listen(100)

def heartbeat():
	
	for port in ports:
		
		timer = threading.Thread(target=check_chunkservers,args=([port]))
		timer.start()

	
def taskalloter(response,c):
	global userfiles
	global ports
	print(' 131 ',response)
	try:
		command = response.split(" ")
		print(command)
		if command[0]=='upload':
			
			# print(command[1],' -- ',command[2],' -- by',command[3])
			
			if command[1] in userfiles:
				c.sendall('402'.encode())
				c.close()
			else:
				# divide into chunks
				chunks=int(command[2])/(1024)
				reply='401'
				for i in range(0,int(chunks)+1):

					allports=random.choices(ports, k=2)
					# print('<-- 71',allports)
					# print('<--72 ',ports)
					selected_ports=" ".join([str(k) for k in allports])
					# upload_port=str(random.choice(ports))
					reply+=' '+selected_ports

					entry=command[1]+'_'+str(i)
					## entry to filename_i

					if entry not in portchunks:
						portchunks[entry]=list()

					portchunks[entry].append(allports)

				print('<-- 84',reply)
				c.sendall(reply.encode())
				c.close()
				# send 
				filetonumberofchunks[command[1]]=int(chunks)
				userfiles.append(command[1])

		if command[0]=='download':

			reply='401'

			if command[1] not in userfiles:
				c.sendall('402'.encode())
				c.close()

			if lockstatus[command[1]]==True:
				c.sendall('403'.encode())
				c.close()

			chunks=filetonumberofchunks[command[1]]
			
			for i in range(0,chunks+1):
				entry=command[1]+'_'+str(i)

				random_port = random.choice(portchunks[entry])
				random_port = random.choice(random_port)

				if availability[random_port] == False:
					while availability[random_port]==False:
						random_port = random.choice(portchunks[entry])
						random_port = random.choice(random_port)

				# portchunks[entry].append(random_port)
				download_port=str(random_port)
				reply+=' '+download_port
				#entry=command[4]+'_'+str(i)

			# userfiles[command[3]].append(command[1])
			print('107 <--',reply)
			c.sendall(reply.encode())
			c.close()

		if command[0]=='lock_file':

			if command[1] not in userfiles:
				c.sendall('402'.encode())
				c.close()

			lockstatus[command[1]]=True
			c.sendall('401'.encode())
			c.close()


		if command[0]=='unlock_file':

			if command[1] not in userfiles:
				c.sendall('402'.encode())
				c.close()

			lockstatus[command[1]]=False
			c.sendall('401'.encode())
			c.close()
				


		logging()


	
	except socket.error as err:
		print('task alloted')

def main():
	setup()
	heartbeat()
	
	while True:
		
		c,address=server.accept()
		# print('Got a connection from ',address)
		response=c.recv(1024).decode()
		timer = threading.Thread(target=taskalloter,args=([response,c]))
		timer.start()
		# c.sendall('From server'.encode())
		# c.close()	

if __name__ == '__main__':
	main()