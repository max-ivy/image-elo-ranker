# image-ranker
This is a basic Flask project that allows users to upload images, view them on a homepage, and vote on which image they like better in a "compare" page. The app uses PyMongo to connect to a local MongoDB Compass database to store image metadata such as the image title and filename, as well as the Elo rating of each image. The Elo rating is updated based on user votes, with the winning image's rating increasing and the losing image's rating decreasing. The app also includes a filter feature to view images with Elo ratings within a specified range. This project demonstrates basic web development concepts such as handling form submissions, saving and retrieving data from a database, and using Flask to render templates and handle routing.

Make sure to put the HTML in a "templates" folder, and the CSS + JS in a "static" folder. 

Packages/Modules used:
- flask
- flask_pymongo
- flask_wtf
- wtforms
- PIL
- os
- werkzeug.utils
- random
- bson
- json
- flask_sqlalchemy
- pymongo
- bson.objectid

<img width="677" alt="Screenshot 2023-04-07 at 5 31 12 PM" src="https://user-images.githubusercontent.com/34040500/230695468-b36af176-0423-4921-9663-d64cb8390ee7.png">
<img width="677" alt="Screenshot 2023-04-07 at 5 39 08 PM" src="https://user-images.githubusercontent.com/34040500/230696160-44dfaf5e-0193-4d44-812f-3595779fd5a6.png">
