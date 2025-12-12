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

ByteBite is a simplified Uber Eats–style platform built with a **serverless, low-cost Azure architecture**. It supports a basic 3-sided ecosystem:

- **Restaurants** can register meals for specific delivery areas.
- **Customers** can browse meals in their area, place an order, and see the total price and estimated delivery time.
- **Drivers** (advanced feature) can view open orders in their area, accept one, and mark it as delivered.

The focus is on demonstrating **clean cloud design** rather than full authentication or production-grade features.

## Core Features (Matches Course Requirements)

### Restaurant Side

- Web form to register meals with:
  - Dish name  
  - Description  
  - Preparation time (minutes)  
  - Price  
  - Delivery area (e.g., Central, North, South)  
- Data is stored in **Azure Table Storage** (`Meals` table) via an **Azure Function** (`RegisterMeal`).

### Customer Side

- Select a delivery area from a dropdown.
- Retrieve meals in that area via `GetMealsByArea` Azure Function.
- Select multiple meals and enter delivery address.
- Submit order to `SubmitOrder` Azure Function.
- Receive confirmation showing:
  - Total cost  
  - Estimated delivery time  

Delivery time formula:

```text
EstimatedTimeMinutes = sum(prepTimes) + 10 (pickup) + 20 (delivery)
