import json
import sys
import pickle
import socket            
import threading
import time
import os

servers=[]
filechunks=dict()
chunk_size = 1024 #512*1024 #512KB


class chunkserver():

	def __init__(self, port):
    
	    self.port = port
	    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	    s.bind(('127.0.0.1',port))
	    s.listen(100)
	    self.socket=s


def connection_server(ent):

	while True:
		
		
		c,address=ent.socket.accept()
		print('Got a connection from ',address)
		resp=c.recv(1024).decode()
		c.sendall(str(ent.port).encode())
		c.close()


def setup():
	global servers
	ports=[6001,6002,6003,6004,6005]
	for i in ports:
		entry=chunkserver(i)
		servers.append(entry)

		cwd = os.getcwd()
		dir = os.path.join(cwd,str(i))
		if not os.path.exists(dir):
		    os.mkdir(dir)

	# for ent in servers:
	# 	timer = threading.Thread(target=connection_server,args=[ent])
	# 	timer.start()

def listentoclients(chunks):
	
	while True:
		## download
		c,address=chunks.socket.accept()
		command=c.recv(1024).decode()
		# print(command)
		command1 = command
		
		command=command.split(" ")
		if command[0]=='204':
			## sending the chunk
			rc,up,ch,port= command1.split(" ")	

			filename=ch
			# print('66',filename)
			cwd = os.getcwd()
			dir = os.path.join(cwd,str(chunks.port),filename)
			# print('68',dir)
			### Adding chunk to dictionary
			### filechunks[filename+'_'+command[3]]
			## Added.
			##c.send('204'.encode())
			try:
				f = open(dir, "rb")
				content=f.read(chunk_size)
				#content=c.recv(1024)
				c.sendall(content)
				c.close()
				# print(content)
				#f.write(content)
				f.close()
			except socket.error as err:
				print('line 83 ',err)



		if command[0]=='201': #chunk write request.........
			## upload
			print('90 --> ',command)
			rcode, c1,c2,c3, chunkHandle = command1.split(" ")	
			filename=chunkHandle

			

			cwd = os.getcwd()
			dir = os.path.join(cwd,str(chunks.port),filename)
			#print('94 ',dir,' ',chunks.port,' ',filename,' ',portdirect)
			### Adding chunk to dictionary
			filechunks[filename]=filename
			## Added.
			c.send('204'.encode())
			repeatcontent=''
			try:
				f = open(dir, "ab")
				content=c.recv(chunk_size)
				repeatcontent=content
				
				# print(content)
				f.write(content)
				f.close()

				for i in [c2,c3]:
					reply=''
					while reply!='209':
						print("####################### ",i)
						print("p1")
						copy=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						copy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
						print("p2",'208 '+dir)
						copy.connect(('127.0.0.1',int(i)))
						copy.send(('208 '+dir).encode())
						print("p3")
						reply=copy.recv(1024).decode()
						if reply=='209':
							copy.sendall(repeatcontent)
							print('121 -- done')
							copy.close()
					print(i+" Completed!!")

				c.send('OK'.encode())
				c.close()
			except:
				print('line 66')

			####
			# sending copy to another chunkserver;

			



			####

		if command[0]=='206':
			
			try:
				# print('Got a connection from ',address)
				c.sendall(str(chunks.port).encode())
				c.close()
			except:
				print('line 116')


		if command[0]=='208':
			try:
				c.send('209'.encode())
				content=c.recv(1024)
				dir=command[1]
				filename=dir.split("/")
				filename=filename[-1]
				cwd = os.getcwd()
				dir = os.path.join(cwd,str(chunks.port),filename)

				print(dir,' ')
				try:
					f = open(dir, "ab")
					f.write(content)
					f.close()
				except:
					print('line 152')





			except socket.error as err:
				print('line 133 ',err)





def main():
	global s
	global servers
	setup()

	for chunks in servers:
		timer=threading.Thread(target=listentoclients,args=[chunks])
		timer.start()



if __name__ == '__main__':
	main()