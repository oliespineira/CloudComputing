# ByteBite – Serverless Multi-Restaurant Food Ordering Platform

Cloud Computing Final Project – IE University  
Course: CLOUD COMPUTING (BCSAI2025N-CSAI.2.M.A_C2_493749)  

## Group Members

- Olivia Espiñeira Flores 
- Matteo Giorgetti  
- Laura González Rodriguez  
- Lara Iglesias Perez  
- Habib Rahal  
- Kathy Vo  

## Project Vision

ByteBite is a simplified Uber Eats–style platform built with a **serverless, low-cost Azure architecture**. It supports a complete 3-sided ecosystem:

- **Restaurants** can register meals with images for specific delivery areas.
- **Customers** can browse meals in their area, place orders, and track delivery status.
- **Drivers** can view available deliveries in real-time, accept them, and update delivery status.

The platform demonstrates **clean cloud design** with Azure Functions, Table Storage, Queue Storage, and Blob Storage.

## Architecture

### Azure Services Used

- **Azure Functions** (Python) - Serverless API backend
- **Azure Table Storage** - Data persistence (Users, Restaurants, Meals, Orders, Deliveries)
- **Azure Queue Storage** - Real-time delivery notifications (deliveries-north, deliveries-central, deliveries-south)
- **Azure Blob Storage** - Image storage (mealimages container)
- **JWT Authentication** - Secure user sessions

### Frontend

- Pure HTML/CSS/JavaScript (no frameworks)
- Responsive design
- Auto-detects localhost vs production API
- GitHub Pages deployment

## Core Features

### Authentication System

- **Sign Up**: Create accounts for customers, restaurants, or drivers
- **Login**: JWT-based authentication with role-based access
- **Session Management**: Tokens stored in localStorage
- **Password Security**: bcrypt hashing

**Endpoints:**
- `POST /api/signup` - Create new user account
- `POST /api/login` - Authenticate and get JWT token

### Restaurant Portal

Restaurants can register meals with:

- Restaurant name
- Dish name
- Description
- Price (€)
- Preparation time (minutes)
- Delivery area (North, Central, South)
- **Image Upload** - Direct upload to Azure Blob Storage OR external image URL

**Image Upload Features:**
- File upload support (JPG, PNG, GIF, WebP - max 5MB)
- Base64 encoding and transmission
- Automatic upload to Azure Blob Storage
- Unique filename generation (UUID + extension)
- Image preview before submission
- Backward compatible with external URLs

**Endpoints:**
- `POST /api/RegisterMeal` - Register meal with image upload
- `POST /api/RegisterRestaurant` - Register restaurant info

### Customer Portal

Customers can:

- Select delivery area (North, Central, South)
- Browse available meals with images
- Add multiple meals to cart
- View order summary with totals
- Place orders with delivery details
- See estimated delivery time

**Order Flow:**
1. Select area → Fetch meals via `GetMealsByArea`
2. Add meals to cart
3. Fill delivery form (name, address, phone)
4. Submit order → Creates order and delivery records
5. Delivery notification sent to queue for drivers

**Delivery Time Calculation:**
```
EstimatedTimeMinutes = max(prepTimes) + 10 (pickup) + 20 (delivery)
```

**Endpoints:**
- `GET /api/GetMealsByArea?area={area}` - Get meals by delivery area
- `POST /api/SubmitOrder` - Create order and delivery

### Driver Portal

Drivers can:

- Select their delivery area
- View available deliveries in **real-time** (queue polling every 5 seconds)
- Accept deliveries from queue
- Update delivery status:
  - **Assigned** → **Picked Up** → **In Transit** → **Delivered**
- View active deliveries

**Real-Time Queue System:**
- Azure Queue Storage for instant delivery notifications
- Queue polling every 5 seconds
- Visibility timeout prevents duplicate assignments
- Automatic queue cleanup when delivery accepted

**Endpoints:**
- `POST /api/CheckDeliveryQueue` - Get available deliveries from queue
- `POST /api/AcceptDeliveryFromQueue` - Accept delivery and remove from queue
- `POST /api/UpdateDeliveryStatus` - Update delivery progress
- `GET /api/GetMyDeliveries?driverEmail={email}` - Get driver's assigned deliveries

## API Endpoints

### Authentication
- `POST /api/signup` - Create user account
- `POST /api/login` - Authenticate user

### Restaurant
- `POST /api/RegisterRestaurant` - Register restaurant
- `POST /api/RegisterMeal` - Register meal (supports image upload)

### Customer
- `GET /api/GetMealsByArea?area={area}` - Get meals by area
- `POST /api/SubmitOrder` - Submit order

### Driver
- `POST /api/CheckDeliveryQueue` - Check queue for deliveries
- `POST /api/AcceptDeliveryFromQueue` - Accept delivery
- `POST /api/UpdateDeliveryStatus` - Update delivery status
- `GET /api/GetMyDeliveries?driverEmail={email}` - Get driver deliveries

## Data Storage

### Azure Tables

- **Users** - User accounts (email, password hash, role, name)
- **Restaurants** - Restaurant information
- **Meals** - Meal listings with image URLs
- **Orders** - Customer orders
- **Deliveries** - Delivery assignments and status

### Azure Queues

- **deliveries-north** - Delivery notifications for North area
- **deliveries-central** - Delivery notifications for Central area
- **deliveries-south** - Delivery notifications for South area

### Azure Blob Storage

- **Container**: `mealimages`
- **Access**: Public blob read access
- **Format**: Images stored as binary with UUID filenames
- **Supported**: JPG, JPEG, PNG, GIF, WebP (max 5MB)

## Setup Instructions

### Prerequisites

- Azure account with Storage Account and Function App
- Azure CLI (for setup scripts)
- Python 3.9+ (for local development)

### 1. Azure Resources Setup

Run the setup script to create queues and tables:

```bash
chmod +x setup_azure_queues.sh
./setup_azure_queues.sh
```

This creates:
- 3 delivery queues (north, central, south)
- Required tables (Users, Sessions, Deliveries)

### 2. Environment Variables

Configure in Azure Function App → Configuration → Application settings:

- `AZURE_STORAGE_CONNECTION_STRING` - Storage account connection string
- `JWT_SECRET` - Secret key for JWT tokens (generate with `openssl rand -hex 32`)

### 3. Blob Container Setup

Ensure the `mealimages` container exists and has public access:

```bash
az storage container create \
  --name mealimages \
  --account-name cgp1storage \
  --public-access blob
```

### 4. Deploy Backend

```bash
cd backend
func azure functionapp publish bytebite-functions --python
```

Or deploy via Azure Portal:
1. Go to Function App → Deployment Center
2. Upload `function_app.py` and `requirements.txt`

### 5. Deploy Frontend

Frontend is automatically deployed via GitHub Pages when pushed to `finalBranch`.

Or manually:
```bash
git add docs/
git commit -m "Deploy frontend"
git push origin finalBranch
```

## Local Development

### Frontend

```bash
cd docs
python3 -m http.server 8000
```

Access at: http://localhost:8000

### Backend

1. Create `backend/local.settings.json`:
```json
{
  "Values": {
    "AZURE_STORAGE_CONNECTION_STRING": "your-connection-string",
    "JWT_SECRET": "your-secret-key"
  }
}
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run locally:
```bash
func start
```

Backend runs at: http://localhost:7071/api

## Image Upload Flow

1. **User selects image** → JavaScript reads file
2. **Convert to base64** → `FileReader.readAsDataURL()` creates `data:image/jpeg;base64,...`
3. **Send to API** → POST to `/api/RegisterMeal` with `imageFile` field
4. **Backend processes**:
   - Parse base64 data URL
   - Validate type and size
   - Decode to binary bytes
   - Generate unique filename (UUID + extension)
   - Upload to blob storage
   - Return blob URL
5. **Save to database** → Blob URL stored in Meals table
6. **Display** → Customer page loads image from blob URL

## Project Structure

```
CloudComputing/
├── backend/
│   ├── function_app.py          # All Azure Functions
│   ├── requirements.txt          # Python dependencies
│   ├── host.json                # Function App config
│   └── local.settings.json      # Local env vars (gitignored)
├── docs/                        # Frontend (GitHub Pages)
│   ├── index.html               # Landing page
│   ├── login.html               # Login/Signup
│   ├── restaurant.html          # Restaurant portal
│   ├── customer.html            # Customer portal
│   ├── driver.html              # Driver portal
│   ├── app.js                   # Frontend JavaScript
│   └── styles.css               # Styling
├── setup_azure_queues.sh       # Azure resources setup
└── README.md                    # This file
```

## Testing

### Test Image Upload

1. Go to Restaurant Portal
2. Fill meal details
3. Upload image file OR provide URL
4. Submit
5. Verify blob URL in response
6. Check customer page to see image

### Test Delivery Flow

1. Customer places order
2. Check Azure Queue for message
3. Driver portal shows delivery
4. Driver accepts → Removed from queue
5. Driver updates status → Order progresses

## Technologies

- **Backend**: Python 3.9+, Azure Functions v2 Programming Model
- **Storage**: Azure Table Storage, Queue Storage, Blob Storage
- **Authentication**: JWT (PyJWT), bcrypt
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Deployment**: Azure Functions, GitHub Pages

## Dependencies

### Backend (`backend/requirements.txt`)
```
azure-functions
azure-data-tables
azure-storage-queue
azure-storage-blob
bcrypt
PyJWT
```

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- CORS protection
- Input validation
- File size/type validation

## Future Enhancements

- Payment integration
- Real-time order tracking
- Push notifications
- Rating system
- Order history
- Restaurant dashboard

## License

This project is part of a Cloud Computing course at IE University.

## Contact

For questions or issues, contact the project team members listed above.
