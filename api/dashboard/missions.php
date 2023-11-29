<?php
require("auth.php");
require("connection.php");
if ($_SERVER["REQUEST_METHOD"] == "GET") {
    $query = "SELECT * FROM ocean_missions";
    $result = $connection->query($query);

    if ($result->num_rows > 0) {

        while ($row = $result->fetch_assoc()) {
            $data[] = $row;
        }

        header('Content-Type: application/json');
        echo json_encode($data);
    } else {
        echo "No data found!";
    }
} else {
    http_response_code(405);
    echo "Method Not Allowed!";
}

$connection->close();
