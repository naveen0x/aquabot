<?php
require("auth.php");
require("connection.php");

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['end_time'])) {

        $end_time = $_POST['end_time'];

        $sqlSelect = "SELECT * FROM ocean_missions ORDER BY mission_id DESC LIMIT 1"; 

        $result = $connection->query($sqlSelect);

        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $lastId = $row['mission_id'];

            $existingValue = $row['end_time'];

            if ($existingValue === 'ONGOING') {

                $sqlUpdate = "UPDATE ocean_missions SET end_time = '$end_time' WHERE mission_id = $lastId";

                if ($connection->query($sqlUpdate) === TRUE) {
                    echo "Mission ended successfully";
                } else {
                    echo "Error updating record: " . $connection->error;
                }
            } else {
                echo "Mission already ended";
            }
        } else {
            echo "No records found in table";
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
