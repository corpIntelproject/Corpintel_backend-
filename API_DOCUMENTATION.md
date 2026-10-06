# CorpIntel API Documentation: Authentication Flow

This document outlines the API endpoints required for the Flutter frontend to implement the Registration, OTP Verification, and Login flows.

## Base URL
`http://<YOUR_SERVER_IP>:8000` (Local testing: `http://127.0.0.1:8000`)

---

## 1. Register Company & Admin
Temporarily caches the registration data and sends a 6-digit OTP to the admin's email.

* **Endpoint:** `/api/accounts/register/`
* **Method:** `POST`
* **Auth Required:** No (Public)

### Request Body (JSON)
```json
{
    "company_name": "Acme Innovations",
    "registration_number": "CIN123456789",
    "company_website": "https://acme-innovations.com",
    "headquarters_location": "Kochi, Kerala",
    "industry_type": "Software",
    "admin_name": "John Doe",
    "admin_email": "john@acme.com",
    "admin_password": "StrongPassword123!"
}
```

### Success Response (`200 OK`)
```json
{
    "message": "OTP sent to email. Please verify to complete registration."
}
```

### Common Error Responses (`400 Bad Request`)
```json
{
    "company_name": ["This company name is already registered!"],
    "admin_email": ["A user with this email already exists."]
}
```

---

## 2. Verify OTP
Verifies the 6-digit code. If successful, permanently saves the Company and Admin to the database.

* **Endpoint:** `/api/accounts/verify-otp/`
* **Method:** `POST`
* **Auth Required:** No (Public)

### Request Body (JSON)
```json
{
    "email": "john@acme.com",
    "otp": "123456" 
}
```

### Success Response (`201 Created`)
```json
{
    "message": "Email verified! Company and Admin officially registered.",
    "company_name": "Acme Innovations"
}
```

### Common Error Responses (`400 Bad Request`)
```json
{
    "error": "Invalid OTP code."
}
```
*(Also returns an error if the 15-minute timer has expired).*

---

## 3. Login (Get JWT Tokens)
Authenticates the user and returns the required JWT tokens along with their company profile.

* **Endpoint:** `/account/login/`
* **Method:** `POST`
* **Auth Required:** No (Public)

### Request Body (JSON)
```json
{
    "email": "john@acme.com",
    "password": "StrongPassword123!"
}
```

### Success Response (`200 OK`)
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5...",
    "user_profile": {
        "name": "John Doe",
        "email": "john@acme.com",
        "role": "CORP_ADMIN",
        "company_name": "Acme Innovations"
    }
}
```

### How to use the Tokens in Flutter
For all future authenticated requests (like creating an employee or uploading a PDF), Flutter must attach the **Access Token** in the HTTP Headers like this:
`Authorization: Bearer <your_access_token>`
