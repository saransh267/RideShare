Details of setup:

The project is set up on 3 AWS EC2 instances:
	
1.  Users instance
    
    -It contains the users container which has all the users APIs for ex. add user, view users, delete user etc.
    
    -It gets the request from the user and redirects it to the orchestrator APIs.

2.  Rides instance
    
    -It contains the rides container which has all the rides APIs for ex. add ride, view rides, join ride, delete ride etc.
    
    -It gets the request from the user and redirects it to the orchestrator APIs.

3.  Orchestrator instance
	It contains the following containers:
	-orchestrator
	  It has database read/write APIs, crash slave and container list APIs, auto scaling mechanism, zookeeper functionality and docker-sdk (spawning containers dynamically).
	-master
	  It performs the database write operations.
	-slave
	  It performs the database read operations.
	-shared_db
	  We are using this to make the database persistent and sharable among all slaves.
	-rabbitmq
	  It provides AMQP functionality.
	-zookeeper
	  It provides high availability by keeping watch on the ‘/Workers/’ path which has the z-nodes of the slave containers.

- There is no database operation in users/rides instance.
- All the database operations are happening in the orchestrator instance.
- We are using RPCClient in rabbitmq for sending request to workers and receiving response from them.
- The auto scaling mechanism is there in the orchestrator.
- For auto scaling we spawning containers dynamically using DockerClient.
- For high availability we are creating a z-node for each slave container and storing it in 'Workers' directory.
- We are keeping a watch on the '/Workers/' path using zookeeper which informs us in slave worker is crashed.

Running the project:

1. Create 3 AWS EC2 instances namely users, rides and orchestrator with os as Ubuntu and tier preferably t2.medium and store their pem files safely.
2. In security groups expose port 80 and 22
3. Create target groups for the users and rides instances.
4. Create a load balancer for the application with rules:
    - if path is "/api/v1/users*" forward to users
    - else forward to rides
5. Now in each of the instance install docker and docker-compose.
6. Open the Final Project folder. It has 3 folders: users, rides and orchestrator.
7. Transfer one folder in each instance accordingly using WINSCP.
8. Convert the pem file of each instance in ppk using PuTTYgen.
9. Open each instance in a separate PuTTY terminal by using it's Public IP as hostname and ppk file as authentication.
10. Login to each instance using username "ubuntu" to get sudo access.
11. cd to the working directory in each instance.
12. In users and rides instance update the url which is used to call the orchestrator with the Public IP of orchestrator.
13. Also update the load balacer url used in the codes.
14. Now just do "sudo docker-compose up --build" in each terminal.
15. This will start all the 3 instances and you can check that by sending a request through postman by using the load balancer url.
    - example: create a new user
    - url : CC-Rideshare-1938598602.us-east-1.elb.amazonaws.com/api/v1/users
    - method : PUT
    - header : content-type : application/json
    - raw body : {"username":"qwerty", "password":"3d725109c7e7c0bfb9d709836735b56d943d263f"}
