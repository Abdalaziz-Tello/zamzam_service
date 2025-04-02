# Zamzam Water Service

A simple FastAPI-based system for ordering Zamzam water with delivery or pickup options.

## Features

- User authentication with JWT security
- User registration and login
- View water companies and their offers
- Place orders for water delivery or pickup
- View order history
- Location-based delivery

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /token` - Login to get access token

### Users
- `POST /users/` - Create a new user

### Water Companies
- `GET /companies/` - List all water companies

### Offers
- `GET /offers/` - List all water offers

### Orders
- `POST /orders/` - Create a new order
- `GET /orders/` - List user's orders
- `GET /orders/{order_id}` - Get specific order details

## Security

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:
1. Login using `/token` endpoint
2. Include the token in the Authorization header: `Bearer <your_token>` 