# Flask Blog API

A **RESTful API** for a blogging platform built with Flask and MongoDB.  
Supports secure user authentication, CRUD operations for blogs, and search functionality.

## Tech Stack
- **Backend:** Python, Flask  
- **Database:** MongoDB (NoSQL)  
- **Authentication:** JWT (JSON Web Tokens)  
- **Security:** Flask-Bcrypt for password hashing  
- **Other:** Flask-CORS for cross-origin requests

## Features
- User Signup, Login, Logout, and profile retrieval
- Create, Read, Update, Delete blogs
- Search blogs by title (case-insensitive)
- Pagination for blog listing
- JWT authentication with cookie-based storage
- Secure password hashing with bcrypt