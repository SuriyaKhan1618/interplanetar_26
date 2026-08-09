##CONTENTS

Each task is assigned its own workspace as follows:
    Task 1: quad_controller_ws
    Task 2: auto_nav_ws
    Task 3: arm_manip_ws

All three can be run from inside a single Docker container.

##PREREQUISITE SETUP

Before spinning up the container, grant X11 display permissions (host):

```bash
xhost +local:root
```

##RUN

To spin up a container and enter the shell:

```bash
docker compose up -d --build
docker exec -it interplanetar_26 bash
```

To exit:

```bash
exit
```

To stop and remove current container:

```bash
docker compose down
```

Clean previous artifacts:

```bash
rm -rf build install log
```