<?php
require("auth.php");
require("connection.php");

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (
        isset($_POST['temp']) && isset($_POST['pressure']) && isset($_POST['ph']) && isset($_FILES['image']) && isset($_POST['time'])
    ) {

        $temp = $_POST['temp'];
        $pressure = $_POST['pressure'];
        $ph = $_POST['ph'];
        $image = $_FILES['image'];
        $time = $_POST['time'];

        $sqlSelect = "SELECT * FROM ocean_missions ORDER BY mission_id DESC LIMIT 1";
        $result = $connection->query($sqlSelect);

        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $table_name = 'mission_' . $row['mission_id'];

            $sql = "INSERT INTO $table_name (temp, pressure, ph, image, time) 
            VALUES ('$temp', '$pressure', '$ph', 'NULL', '$time')";

            if ($connection->query($sql) === TRUE) {
                $last_inserted_id = $connection->insert_id; // Retrieve the last inserted ID
                $response = array("status" => "success", "message" => "Data uploaded successfully");
                echo json_encode($response);


                //image uploading part
                $targetDirectory = '../dashboard/images/' . $table_name . '/';
                if (!is_dir($targetDirectory)) {
                    mkdir($targetDirectory, 0777, true);
                }

                $uploadedFile = $_FILES['image'];
                $uploadOk = true;
                $originalFileName = $_FILES["image"]["name"];
                $extension = pathinfo($originalFileName, PATHINFO_EXTENSION);
                $newFileName = $last_inserted_id . "." . $extension;
                $targetFile = $targetDirectory . $newFileName;
                $imageFileType = strtolower(pathinfo($targetFile, PATHINFO_EXTENSION));

                // Check if the uploaded file is an image
                $check = getimagesize($uploadedFile['tmp_name']);
                if ($check !== false) {
                    $uploadOk = true;
                } else {
                    $uploadOk = false;
                    echo "File is not an image.";
                }

                // Check if the file already exists
                if (file_exists($targetFile)) {
                    $uploadOk = false;
                    echo "File already exists.";
                }

                // Check file size 
                if ($uploadedFile['size'] > 5000000) {
                    $uploadOk = false;
                    echo "File is too large.";
                }

                // Allow only certain file formats 
                if ($imageFileType != "jpg" && $imageFileType != "png" && $imageFileType != "jpeg" && $imageFileType != "gif") {
                    $uploadOk = false;
                    echo "Only JPG, JPEG, PNG & GIF files are allowed.";
                }

                // If all checks pass, move the file to the specified directory
                if ($uploadOk) {
                    if (move_uploaded_file($uploadedFile['tmp_name'], $targetFile)) {
                        echo "The image " . $newFileName . " has been uploaded.";
                    } else {
                        echo "Error uploading the file.";
                    }
                }
                //image uploading part end


                $img_url = 'http://129.80.123.18/api/dashboard/images/' . $table_name . '/' . $newFileName;
                $sqlUpdate = "UPDATE $table_name SET image = '$img_url' WHERE id = $last_inserted_id";

                if ($connection->query($sqlUpdate) === TRUE) {
                    echo "Image url updated " . $img_url;
                } else {
                    echo "Error updating img url: " . $connection->error;
                }
            } else {
                $response = array("status" => "error", "message" => "Query execute Error");
                echo json_encode($response);
            }
        } else {
            $response = array("status" => "error", "message" => "No ongoing missions");
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
