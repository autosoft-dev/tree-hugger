<?php

function foo($arg_1, $arg_2, $arg_n) {
    echo "Example\n";
    return $retval;
}

function test() {
    echo "Example\n";
    return $retval;
}

class Car {
    function Car() {
        $this->model = "Tesla";
    }
    public function bar() {
        return 'method';
    }
}

// create an object
$Lightning = new Car();

// show object properties
echo $Lightning->model;

?>
