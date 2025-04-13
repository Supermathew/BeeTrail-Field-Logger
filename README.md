
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


Here's the **📘 Routes Implementation Explanation** for your `POST /api/register` endpoint, including how the helper `get_user_by_email` works:

---

### 1. **POST `/api/register`**
- **Purpose**: Registers a new user with their email, password, and role (`admin` or `beekeeper`).

- **Workflow**:
  1. Calls `get_user_by_email()` with both `email` and `role` to check if a user already exists with that specific combination.
  2. If a match is found, returns `400 Bad Request` with `Email already registered`.
  3. If not found, calls `create_user()` to store the new user in the MongoDB database.
  4. Returns the created user details (excluding sensitive fields like password).

- **Assumption**:
  - Each role is treated as a unique entity. That is, a user with the same email **but a different role** (e.g., both "beekeeper" and "admin") could potentially register separately. This design allows for role-based separation of accounts with the same email.



### 2. **POST `/api/login`** (Access by Admin user only)
- Authenticates user via email and password.
- Returns: `access_token`, `role`, and `token_type`.
- Role is encoded in the JWT token.

---

### 3. **POST `/api/token/refresh`**
- Accepts a valid refresh token and returns a new access token.
- Validates the `sub` and `role` in the refresh token.

---

### 3. **GET `/api/sync/hives`**
- Fetches hive logs.
- Only accessible to users with role `"admin"`.
- Validates JWT token, extracts role, and authorizes.

---

### 4. **POST `/api/hives`**
- **Purpose**: Create a new hive log entry in the database.
- **Authorization**: ✅ Required
- **Logic**:
  - Calls `create_hive()` to insert the hive into MongoDB.
  - Automatically adds a `timestamp` at creation time.

---

### 5. **GET `/api/hives`**
- **Purpose**: Retrieve a list of hive logs with optional filtering and pagination.
- **Authorization**: ✅ Required
- **Query Parameters**:
  - `skip` (int): Number of records to skip (for pagination).
  - `limit` (int): Maximum number of records to return.
  - `start_date` (Optional[date]): Filter to only include hives placed on or after this date.
  - `end_date` (Optional[date]): Filter to only include hives placed on or before this date.

- **Validation**:
  - If `start_date > end_date`, throws a `400 Bad Request`.

---

### 6. **GET `/api/hives/export`**
- **Purpose**: Export hive logs as a downloadable CSV file.
- **Authorization**: ✅ Required
- **Query Parameters**: Same as `/api/hives` (`skip`, `limit`, `start_date`, `end_date`)

- **Logic**:
  - Uses the same `get_hives()` logic for filtering.
  - Uses `StringIO` and Python’s `csv` module to generate the CSV file in-memory.
  - Returns as a streaming response.

---

---

### 7 `POST /api/crops`

- This route uses the `create_crop()` function to:
  1. Insert a new crop document into the `"crops"` collection in the database.
  2. The crop data includes location and flowering dates.

- Authentication is required before insertion.

---

### 8 `GET /api/crops/nearby`

- This route fetches nearby crops based on:
  - A given `latitude` and `longitude`
  - A radius (in **meters**)
  - A date to filter crops that are **currently flowering**

- Internally, `get_nearby_crops()` performs the following:

  1. **Convert Date**: The given date is combined with time `00:00:00` in UTC to form `query_date`.

  2. **Distance Conversion**: The radius is converted from kilometers (if default) to meters (as required by MongoDB’s `$near` operator).

  3. **Geo Query**:
     - Uses MongoDB’s `$near` with a 2dsphere index on the `location` field.
     - Finds documents within the specified `radius` of the `[longitude, latitude]` point.

  4. **Date Filtering**:
     - Only selects crops where:
       - `floweringStart` is **before or on** the `query_date`
       - `floweringEnd` is **after or on** the `query_date`
     - This ensures that the crop is actively flowering on that day.

  5. **Returns all matching crops** as a list.

---
---

### 9 `GET /api/sync`

**Purpose**:  
To fetch the current **sync token** for the authenticated user.

**Logic**:

1. Ensures the user is authenticated.
2. Looks up the user's existing `sync_token` from the `users` collection.
3. If the token **doesn’t exist**:
   - Generates a **new sync token** using the current UTC timestamp.
   - Updates the user record with this new sync token.
4. Returns the token.

---

### 10 `POST /api/sync/hives`

**Purpose**:  
To synchronize hive data between the client and server.

**Logic**:

1. Checks if the incoming data contains **client-side changes** (from offline or local usage).
2. For each change:
   - Converts `localTimestamp` (if present) to a UTC `datetime` and assigns it to `lastModified`.
   - If not present or invalid, defaults to current UTC time.
   - Checks if a hive with the same `hiveId` already exists in the `hives` collection.
     - If **exists**, updates it using `$set` (ensures the change is reflected on the server).
     - If **not exists**, inserts the new hive document.
   - Removes `_id` field if present to avoid duplication or conflicts in MongoDB.

3. Fetches all **server-side changes** in the `hives` collection that happened **after** the client’s last `syncToken`, using the `lastModified` field for comparison.

4. Updates the user’s `sync_token` with the current timestamp (acts as the latest known sync point).

5. Returns both:
   - Updated sync token.
   - All server-side changes since the last sync.


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

### ✅ Sync token for offline apps
- Token based sync with the server when the app is in offline.

### ✅ Sync token for offline apps
- `/api/sync/hives` enables syncing data between offline clients and server.

### ✅ Export logs as CSV (optional future extension)
- Though not shown in code above, you can add a route like `/api/export/hives` to return CSV files of hive logs.

### ✅ Swagger/OpenAPI docs
- Automatically available at `/docs`.

### ✅ Basic admin dashboard at `/admin`
- Available with protected access to admins only.

---
