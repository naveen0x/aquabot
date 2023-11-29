<?php
$headers = apache_request_headers();
$api_key = "12345678";

if (isset($headers['API_KEY'])) {
  $head_key = $headers['API_KEY'];

  if ($api_key != $head_key) {
    echo "Invalid API key!";
    http_response_code(401);
    die();
  }
} else {
  echo "API key is missing!";
  http_response_code(401);
  die();
}
