create database used_cars;
create table all_cars
-- store information of all unique cars in our database
(
    car_id int,     -- uniquely identifies a car                                                                 
    car_make text,  -- Make of the car                                                              
    car_brand text, -- Brand of the car                                                               
    car_year int,   -- Year                                                                
    primary key(car_id)                                                             
);            

