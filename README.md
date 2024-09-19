- Створення Docker image
    
    # x86-64
    docker build -t alltrim/poultramp3:3.2.2 .
    docker image ls | grep poultramp3
    docker tag ID alltrim/poultramp3:latest
    docker push alltrim/poultramp3:3.2.2
    docker push alltrim/poultramp3:latest