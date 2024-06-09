from application import create_app, db
import socket, webbrowser


app = create_app()


if __name__ == "__main__":   
    app.config["FLASKENV"] = "development"
    app.debug = True
    
    host = socket.gethostbyname(socket.gethostname())
    port = 9000
    
    web_site = f"http://{host}:{port}"
    print(f"Please type on your browser this web address: {web_site}")
        
    # webbrowser.open(web_site)
    
    app.run(host="0.0.0.0", port=port)
