# Visser 

## Quick Start 🚀

Run locally on port 8080
```
uvicorn app.main:app --port 8080
```

Build Docker Image 
```
docker build -t visser .
docker run -d --name visser_container -p 80:80 visser
```