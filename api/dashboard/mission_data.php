<?php
require("auth.php");
require("connection.php");

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['MISSION_ID'])) {
        $mission_id = $_POST['MISSION_ID'];
        $dbname = 'mission_' . $mission_id;

        $sql = "SELECT * FROM ocean_missions WHERE mission_id = $mission_id";
        $idresult = $connection->query($sql);

        if ($idresult->num_rows > 0) {
            $row = $idresult->fetch_assoc();
            $data[] = $row;
        } else {
            echo "No records found with ID: $dbname";
        }

        $query = "SELECT * FROM $dbname ORDER BY id DESC";
        $result = $connection->query($query);

        if ($result->num_rows > 0) {
            while ($row = $result->fetch_assoc()) {
                $data[] = $row;
            }
        } else {
            $data[] = "No data found!";
        }
    } else {

        $q = "SELECT * FROM ocean_missions ORDER BY mission_id DESC LIMIT 1";
        $dbname = $connection->query($q);
        $row = $dbname->fetch_assoc();
        $data[] = $row;

        $db_tb_var = 'mission_' . $row["mission_id"];
        $query = "SELECT * FROM $db_tb_var ORDER BY id DESC";
        $result = $connection->query($query);

        if ($result->num_rows > 0) {

            while ($row = $result->fetch_assoc()) {
                $data[] = $row;
            }
        } else {
            $data[] = "No data found!";
        }
    }
    header('Content-Type: application/json');
    echo json_encode($data);
} else {
    http_response_code(405);
    echo "Method Not Allowed!";
}

$connection->close();
