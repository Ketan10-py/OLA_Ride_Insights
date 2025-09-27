-- SQL Queries for Ride Booking System

-- 1. Retrieve all successful bookings
SELECT * 
FROM Bookings
WHERE status = 'Successful';

-- 2. Find the average ride distance for each vehicle type
SELECT vehicle_type, AVG(distance) AS avg_distance
FROM Bookings
GROUP BY vehicle_type;

-- 3. Get the total number of cancelled rides by customers
SELECT COUNT(*) AS cancelled_by_customers
FROM Bookings
WHERE status = 'Cancelled by Customer';

-- 4. List the top 5 customers who booked the highest number of rides
SELECT customer_id, COUNT(*) AS total_rides
FROM Bookings
GROUP BY customer_id
ORDER BY total_rides DESC
LIMIT 5;

-- 5. Get the number of rides cancelled by drivers due to personal and car-related issues
SELECT COUNT(*) AS cancelled_by_drivers
FROM Bookings
WHERE status = 'Cancelled by Driver'
  AND cancel_reason IN ('Personal', 'Car Issue');

-- 6. Find the maximum and minimum driver ratings for Prime Sedan bookings
SELECT MAX(driver_rating) AS max_rating,
       MIN(driver_rating) AS min_rating
FROM Bookings
WHERE vehicle_type = 'Prime Sedan';

-- 7. Retrieve all rides where payment was made using UPI
SELECT * 
FROM Bookings
WHERE payment_method = 'UPI';

-- 8. Find the average customer rating per vehicle type
SELECT vehicle_type, AVG(customer_rating) AS avg_customer_rating
FROM Bookings
GROUP BY vehicle_type;

-- 9. Calculate the total booking value of rides completed successfully
SELECT SUM(booking_value) AS total_successful_value
FROM Bookings
WHERE status = 'Successful';

-- 10. List all incomplete rides along with the reason
SELECT booking_id, customer_id, driver_id, cancel_reason
FROM Bookings
WHERE status = 'Incomplete';
