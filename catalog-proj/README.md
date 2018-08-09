# Catalog website project
This project creates an application that provides a list of items within a variety of categories, as well as a user registration and authentication system.

We also included a tiny script to populate the database with mock data, for testing purposes.


### Using this project
1. This project was made to be run in a [VM provided by Udacity](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) (to use the VM you will need [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) installed) and the instructions will cover that usage. (alternatively it should be possible to run it if you have psql, Python3, and the psycopg2 package installed).
2. Create a directory `catalog` inside the vagrant directory with the same content as the catalog subdirectory (since you can't clone only a part of a repo and I didn't want to create a repo for this only)
3. Log in to the VM with `vagrant ssh` and run `cd \vagrant\catalog` to enter the correct directory
4. Create the database by running `python database_setup.py`
5. (optional) Populate the database by running `python populatedb.py`
6. Run `python application.db`
7. Visit `http://localhost:8000/` to view the website.
