<?php

$STORE_HOME = "/var/www/store/";

//check for valid hat valley store item
function checkValidItem($filename) {
    if(file_exists($filename)) {
        $first_line = file($filename)[0];
        if(strpos($first_line, "***Hat Valley") !== FALSE) {
            return true;
        }
    }
    return false;
}

//add to cart
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_POST['action'] === 'add_item' && $_POST['item'] && $_POST['user']) {
    $item_id = $_POST['item'];
    $user_id = $_POST['user'];
    $bad_chars = array(";","&","|",">","<","*","?","`","$","(",")","{","}","[","]","!","#"); //no hacking allowed!!

    foreach($bad_chars as $bad) {
        if(strpos($item_id, $bad) !== FALSE) {
            echo "Bad character detected!";
            exit;
        }
    }

    foreach($bad_chars as $bad) {
        if(strpos($user_id, $bad) !== FALSE) {
            echo "Bad character detected!";
            exit;
        }
    }

    if(checkValidItem("{$STORE_HOME}product-details/{$item_id}.txt")) {
        if(!file_exists("{$STORE_HOME}cart/{$user_id}")) {
            system("echo '***Hat Valley Cart***' > {$STORE_HOME}cart/{$user_id}");
        }
        system("head -2 {$STORE_HOME}product-details/{$item_id}.txt | tail -1 >> {$STORE_HOME}cart/{$user_id}");
        echo "Item added successfully!";
    }
    else {
        echo "Invalid item";
    }
    exit;
}

//delete from cart
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_POST['action'] === 'delete_item' && $_POST['item'] && $_POST['user']) {
    $item_id = $_POST['item'];
    $user_id = $_POST['user'];
    $bad_chars = array(";","&","|",">","<","*","?","`","$","(",")","{","}","[","]","!","#"); //no hacking allowed!!

    foreach($bad_chars as $bad) {
        if(strpos($item_id, $bad) !== FALSE) {
            echo "Bad character detected!";
            exit;
        }
    }

    foreach($bad_chars as $bad) {
        if(strpos($user_id, $bad) !== FALSE) {
            echo "Bad character detected!";
            exit;
        }
    }
    if(checkValidItem("{$STORE_HOME}cart/{$user_id}")) {
        system("sed -i '/item_id={$item_id}/d' {$STORE_HOME}cart/{$user_id}");
        echo "Item removed from cart";
    }
    else {
        echo "Invalid item";
    }
    exit;
}

//fetch from cart
if ($_SERVER['REQUEST_METHOD'] === 'GET' && $_GET['action'] === 'fetch_items' && $_GET['user']) {
    $html = "";
    $dir = scandir("{$STORE_HOME}cart");
    $files = array_slice($dir, 2);

    foreach($files as $file) {
        $user_id = substr($file, -18);
        if($user_id === $_GET['user'] && checkValidItem("{$STORE_HOME}cart/{$user_id}")) {
            $product_file = fopen("{$STORE_HOME}cart/{$file}", "r");
            $details = array();
            while (($line = fgets($product_file)) !== false) {
                if(str_replace(array("\r", "\n"), '', $line) !== "***Hat Valley Cart***") { //don't include first line
                    array_push($details, str_replace(array("\r", "\n"), '', $line));
                }
            }
            foreach($details as $cart_item) {
                 $cart_items = explode("&", $cart_item);
                 for($x = 0; $x < count($cart_items); $x++) {
                      $cart_items[$x] = explode("=", $cart_items[$x]); //key and value as separate values in subarray
                 }
                 $html .= "<tr><td>{$cart_items[1][1]}</td><td>{$cart_items[2][1]}</td><td>{$cart_items[3][1]}</td><td><button data-id={$cart_items[0][1]} onclick=\"removeFromCart(this, localStorage.getItem('user'))\" class='remove-item'>Remove</button></td></tr>";
            }
        }
    }
    echo $html;
    exit;
}

?>
