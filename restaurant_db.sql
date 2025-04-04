create database super_database;

use super_database;


show tables;

select 	*  from restaurant_reservation;

select 	*  from restaurant_table;


insert into restaurant_table(
	seats
)
values(
	5
);


truncate table restaurant_reservation;

delete from restaurant_reservation;