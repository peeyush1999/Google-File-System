# GoogleFileSystem
An implementation of google file system architecture.

**Dependencies :**

+ python3
+ pickle

**How to Run :**

In one terminal, run python3 chunkserver.py to start chunk servers.
In other terminal, run python3 master_server.py to start master server.
In another terminal, run python3 backup_server.py to start master backup server (optional for fault tolerance).
From the fourth terminal, run python3 client.py.

**Syntax :**

To run Chunk server :

`python3 chunkserver.py`

To run the Master Server :

`python3 master_server.py`

To run the BackUp Master Server :

`python3 backup_server.py`

To run the client :

`python3 Client.py <port_number>`

**Commands in client:**

- Login
- signup
- upload file
- read file
- exit

**Architecture:**

- One Master Server
- One BackUp Master Server
- Four Chunkservers
- Multiple Clients Allowed

**Features:**
+ A single file of client will be divided into chunks and each chunk will be stored in seperate chunk servers.
There will also be 3 duplicate replicas for each chunk of a file which will be stored in seperate chunk servers. This is done so as to increase data availablity to the client.
+ Master Server will only hold the Metadata of all the chunks of the files which will be used by clients and chunkservers to communicate with the appropriate chunkserver. Hence there is no issue of Master Server being overloaded.
+ As Master Server is a single point of failure, hence we have a Backup Master Server making the system more reliable.
+ To check the list of active chunk servers, a thread is created in the Master Server which after every 6 seconds will try to connect to all 4 chunk servers and display list of active chunkservers out of them.

**Other properties:**

- Location awareness : Based on the ip address of the client the master server gets its location (latitude longitude) and returns the chunkserver which is near to the client.
