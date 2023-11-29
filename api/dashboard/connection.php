<?php
$host = 'localhost';
$username = 'naveen';
$password = 'tsedf@#@AS';
$database = 'ocean_data';

$connection = new mysqli($host, $username, $password, $database);

if ($connection->connect_error) {
    die("Connection failed: " . $connection->connect_error);
}

?>