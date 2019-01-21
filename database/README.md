Build image in this folder by doing

```bash
docker build -t <tag name> .
```

Run the mysql container:

```bash
docker run -p 3306:3306 -e MYSQL_ROOT_PASSWORD="<password>" <image id>
```