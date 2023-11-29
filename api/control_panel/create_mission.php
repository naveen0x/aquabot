<?php
require("auth.php");
require("connection.php");

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (
        isset($_POST['mission_name']) && isset($_POST['mission_objective']) && isset($_POST['mission_location']) && isset($_POST['start_time'])
    ) {

        $mission_name = $_POST['mission_name'];
        $mission_objective = $_POST['mission_objective'];
        $mission_location = $_POST['mission_location'];
        $start_time = $_POST['start_time'];
        $end_time = 'ONGOING';


        $sql = "INSERT INTO ocean_missions (mission_name, mission_objective, mission_location, start_time, end_time) 
        VALUES ('$mission_name', '$mission_objective', '$mission_location', '$start_time', '$end_time')";

        if ($connection->query($sql) === TRUE) {
            $last_inserted_id = $connection->insert_id; // Retrieve the last inserted ID
            $response = array("status" => "success", "message" => "New record created successfully. The ID of the new record is: " . $last_inserted_id);
            echo json_encode($response);

            $tableName = 'mission_'.$last_inserted_id;

            $sql2 = "CREATE TABLE IF NOT EXISTS $tableName (
                id INT AUTO_INCREMENT PRIMARY KEY,
                temp FLOAT,
                pressure FLOAT,
                ph FLOAT,
                image VARCHAR(255),
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )";

            // Execute the query2
            if ($connection->query($sql2) === TRUE) {
                $response = array("status" => "success", "message" => "Table created successfully" . $last_inserted_id);
                echo json_encode($response);
            } else {
                $response = array("status" => "error", "message" => "Error creating table: " . $connection->error);
                echo json_encode($response);
            }
        } else {
            $response = array("status" => "error", "message" => "Query execute Error");
            echo json_encode($response);
        }
    } else {
        $response = array("status" => "error", "message" => "Missing required data");
        echo json_encode($response);
    }
} else {
    $response = array("status" => "error", "message" => "Invalid request method");
    echo json_encode($response);
}


$connection->close();
