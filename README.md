# Catalog Web Application for Udacity Full-Stack Nanodegree Program

## About
This is an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Included
This project has one main Python module app.py which runs the Flask application. A SQL database is created using the database_setup.py module and you can populate the database with test data using database_init.py. The Flask application uses stored HTML templates in the tempaltes folder to build the front-end of the application. CSS is stored in the static directory.

## How to use
1. Install [Vagrant](https://www.vagrantup.com/) & [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
1. Clone the [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
1. Go to Vagrant directory and either clone this repo or download and place zip    here
1. Launch the Vagrant VM (vagrant up)
1. Log into Vagrant VM (vagrant ssh)
1. Navigate to cd/vagrant/catalog/Catalog
1. The app imports requests which is not on this vm. Run sudo pip install requests
1. Setup application database python database_setup.py
1. Insert fake data python database_init.py (Optional)
1. Run application using python project.py
1. Access the application locally using http://localhost:5000

## JSON Endpoints
JSON Catalog: /catalog/JSON  - This displays the entire catalog
JSON Items: /catalog/<int:category_id>/items/JSON - This displays items for a specific category
