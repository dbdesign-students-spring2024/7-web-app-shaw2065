# Flask-MongoDB Web App: TinyLibrary

## Description
**TinyLibrary** is a home library cataloging application designed to help users organize personal collections of various media products, ranging from books to video games. Users need to log into their account to use the application. After logging into TinyLibrary, they have four functions to choose from: **Create**, **Browse**, **Filter**, and **Random**.
### Create
To start building their personal collection, users can click on the **Create** link to begin creating a new entry in the database. Fields including the type of media product, title of the product, the location of the product, status of consumption, and additional notes are prompted to help users organize their collections.
### Browse
**Browse** is a function for viewing the entire collection from the latest entry, presented in the format of a table. It is also where users can choose to edit or delete a specific entry.
### Filter
To better organize the collection or retrieve results based on specific needs, users can use the **Filter** function to retrieve results based on types, location, and consumption status. These three types are specifically chosen as they cater to scenarios where the user specifically wants to read a book, currently resides in a different house, or wishes to pick up a movie they have not watched before. It is also where users can choose to edit or delete a specific entry conveniently.
> [!NOTE]  
> In order to successfully implement **Filter** functoin on webserver, the form action is set to `"/~xh2065/7-web-app-shaw2065/flask.cgi/filter"`, in contrast to the `"/filter"` in the filter.html for local server. This is the only difference between the files in this repository and the edited one on the i6 server.

### Random
**Random** is a unique function designed specifically for people who have trouble deciding what to do in their free time. Despite losing some accuracy in recommendations due to the absence of filters, the complete randomization of results aims to provide users with the most unexpected suggestions from their current collection.

## A link to the deployed copy
[Link to TinyLibrary](https://i6.cims.nyu.edu/~xh2065/7-web-app-shaw2065/flask.cgi/)

## Credits
This is a solo project.