# Boxing
HW2 in BU's CS411 Software Engineering course.

Authored by Davin Martin & Minjie (Zoe) Zuo

# Docker

## List
### List Images
`docker images`
### List Running Containers
`docker ps`
### List All Containers
`docker ps -a`

## Remove
### Remove Image
`docker rmi <image_name>`
### Remove Container
`docker rm <container_name>`
### Remove All Stopped Containers
`docker container prune`

## Build
`docker build -t <image_name>:<version_number> .`

## Run
`docker run --name <container_name> <image_name>:<version_number>`
<br>(`-p <host_port>:<container_port>`)
### Run & Keep Alive & Detach
`docker run -d --name <container_name> <image_name>:<version_number>`
### &nbsp;&nbsp;&nbsp; Attaching & Detaching
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Press `Ctrl + P`, `Ctrl + Q` to detach from the container without stopping it<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Reattach with `docker attach <container_name>`

### Run with Opening CMD
`docker run --name <container_name> <image_name>:<version_number> bash`

## Start
`docker start <container_name>`

## Execute/Open Shell
`docker exec -it my_container sh`<br>
`docker exec -it my_container bash`

## Stop
`docker stop <container_name>`

### Force Stop
`docker stop -f <container_name>`

## Logs
`docker logs <container_name>`

### Follow Logs Live
`docker logs -f <container_name>`

### Last 20 Logs
`docker logs -n 20 <container_name>`

## Running the Boxing App with Docker

### Build the Docker Image
```bash
docker build -t boxing-app .

### run the container 
docker run -d `
  --name boxing-container `
  -v "${PWD}\data:/app/data" ` ##Take the ./data folder on my host and make it accessible at /app/data inside the container.
  -p 5000:5000 `
  boxing-app

###access
http://127.0.0.1:5000/api/health

###verify
{
  "message": "Service is running",
  "status": "success"
}

###useful commands during this part
docker ps        # List running containers
docker logs boxing-container      #View logs
docker exec -it boxing-container sh   #Open shell in container
docker stop boxing-container   #Stop the container
docker rm boxing-container        # Remove the container


