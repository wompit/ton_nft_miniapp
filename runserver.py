from app import app
from config import PORT, HOST

if __name__ == "__main__":
    app.run(port=PORT, host=HOST)
