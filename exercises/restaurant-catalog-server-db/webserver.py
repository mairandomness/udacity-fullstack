from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                output += "<h3><a href='/restaurants/new'>Create a new restaurant</a></h3>"
                restaurants = session.query(Restaurant).all()

                for restaurant in restaurants:
                    item = "<p> %s<br> " % restaurant.name
                    item += "<a href='restaurants/%s/edit'>Edit</a><br>" % restaurant.id
                    item += "<a href='restaurants/%s/delete'>Delete</a><br></p>" % restaurant.id
                    output += item

                output += "</body></html>"

                self.wfile.write(output)
                print(output)
                return


            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Type in the new restaurant name</h2><input name='newRestaurantName' value='New restaurant name' type='text' ><input type='submit' value='Create'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print(output)
                return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if restaurant != [] :
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1> %s </h1>" % restaurant.name
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'><h2>Type in the new restaurant name</h2><input name='newRestaurantName' value='%s' type='text' ><input type='submit' value='Rename'></form>" % (restaurant.id, restaurant.name)
                    output += "</body></html>"
                    self.wfile.write(output)
                    print(output)
                    return


            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if restaurant != [] :
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>Are you sure you want to delete %s?</h1>" % restaurant.name
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'><input type='submit' value='Delete'></form>" % restaurant.id
                    output += "</body></html>"
                    self.wfile.write(output)
                    print(output)
                    return



        except IOError:
            self.send_error(404, "File not found %s" % self.path)


    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                newRestaurant = Restaurant(name = messagecontent[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(303)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                restaurantIDPath = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if restaurant != []:
                    restaurant.name = messagecontent[0]
                    session.commit()
                    self.send_response(303)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                restaurantIDPath = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if restaurant != []:
                    session.delete(restaurant)
                    session.commit()
                    self.send_response(303)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
