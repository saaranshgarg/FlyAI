# FlyAI

A simple prototype for drone-based farming operations. It now includes a minimal
web interface built with Python's standard library.

## Features
- User registration with mobile number and OTP (Hindi prompts)
- Create drone spraying bookings
- View booking history and status
- Static help/contact information

## Running the CLI version
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
