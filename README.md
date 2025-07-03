# FlyAI

A simple prototype for drone-based farming operations. It now includes a minimal
web interface built with Python's standard library.
The app supports both English and Hindi.

## Features
- User registration with mobile number and OTP (English or Hindi)
- Create drone spraying bookings
- View booking history and status
- Static help/contact information
- Bigger, centered text in the web interface

## Running the CLI version
A simple command line prototype for drone-based farming operations.

## Running the app
```bash
python3 app/flyai.py
```

## Running the web version
```bash
python3 app/webapp.py
```

## Running tests
```bash
python3 -m unittest discover -s tests
```