
# 🐝 BeeTrail Field Logger — API Documentation

A FastAPI-based backend for managing beekeeping field logs with user authentication, role-based access, and offline sync capabilities.

## 🚀 Setup Instructions

1. **Clone the repo**  
   ```bash
   git clone https://github.com/Supermathew/BeeTrail-Field-Logger.git
   cd BeeTrail-Field-Logger
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python -m venv env
   source env/bin/activate     # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**  
   - Create a `.env` file based on `.env.example`  
     ```
     SECRET_KEY=your_secret_key
     MONGO_DETAILS=mongodb+srv://...
     ```

5. **Run the server**  
   ```bash
   uvicorn app.main:app --reload
   ```

6. **API Documentation**  
   Open Swagger UI at: `http://localhost:8000/docs`
   Only admin user can access and login to api.

---

## 📫 Sample Data / Postman Collection

- Import this Postman collection to test endpoints:  
  [Sde-assignment.postman_collection.json](https://github.com/Supermathew/BeeTrail-Field-Logger/blob/main/Sde-assignment.json)

---

## 📘 Routes Implementation Explanation

### 1. **POST `/api/login`** (Access by Admin user only)
- Authenticates user via email and password.
- Returns: `access_token`, `role`, and `token_type`.
- Role is encoded in the JWT token.

---

### 2. **POST `/api/token/refresh`**
- Accepts a valid refresh token and returns a new access token.
- Validates the `sub` and `role` in the refresh token.

---

### 3. **GET `/api/sync/hives`**
- Fetches hive logs.
- Only accessible to users with role `"admin"`.
- Validates JWT token, extracts role, and authorizes.

---

### 4. **POST `/api/sync/hives`**
- Allows admin to sync/upload hive logs.
- Verifies the user token and confirms role is `admin`.

---

### 5. **GET `/admin`**
- Basic dashboard for admin access.
- Requires valid JWT token with role `admin`.
- Could serve as the entry point to a dashboard interface.

---

## 🎁 Bonus Features Implemented

### ✅ User authentication with roles (`beekeeper`, `admin`)
- JWT tokens include the user’s role (`sub` + `role`).
- Role-based checks implemented in protected endpoints.

### ✅ Refresh token support
- Token expiration logic with `/api/token/refresh` to get new tokens.

### ✅ Sync token for offline apps
- `/api/sync/hives` enables syncing data between offline clients and server.

### ✅ Export logs as CSV (optional future extension)
- Though not shown in code above, you can add a route like `/api/export/hives` to return CSV files of hive logs.

### ✅ Swagger/OpenAPI docs
- Automatically available at `/docs`.

### ✅ Basic admin dashboard at `/admin`
- Available with protected access to admins only.

---
