#!/usr/local/bin/php-5.5
<?php

$db_name = "well_data.db";
$csv_file = "weldta.txt";
$table_name = "twdb_well_data";

try {
	$db = new PDO("sqlite:" . $db_name);
} catch (PDOException $e) {
	exit(1);
}

$input = fopen($csv_file, "r");

if (!$input)
	exit(1);

$columns = fgetcsv($input);

$num_columns = count($columns);

$integer = array_fill(0, $num_columns, true);
$real = array_fill(0, $num_columns, true);
$date = array_fill(0, $num_columns, true);
$text = array_fill(0, $num_columns, false);

while ($row = fgetcsv($input)) {
	for ($y = 0; $y < $num_columns; $y++) {

		$field = trim($row[$y]);

		if ($field == "") 
			continue;

		if (contains_char($field)) {
			$text[$y] = true;
			$integer[$y] = 0;
			$real[$y] = 0;
		} else if (ctype_digit($field)) {
			$integer[$y] &= true;
			$real[$y] = 0;
		} else {
			$real[$y] = true;
			$integer[$y] = 0;
		}

		if (substr_count($field, "/") == 2 && substr_count($field,
		    ":") == 2)
			$date[$y] &= true;
		else
			$date[$y] = 0;

	}
}

$query = sprintf("create table %s (", $table_name);

for ($x = 0; $x < $num_columns; $x++) {
	$query = sprintf("%s%s %s%s", $query, $columns[$x], ($integer[$x] &&
	    !$real[$x] ? "integer" : ($real[$x] ? "real" : "text")), $x ==
	    $num_columns - 1 ? ")" : ", ");
}

$db->exec($query);

fclose($input);

$input = fopen($csv_file, "r");

if (!$input)
	exit(1);

fgetcsv($input);

while ($row = fgetcsv($input)) {
	$query = sprintf("insert into %s values (", $table_name);

	for ($y = 0; $y < $num_columns; $y++) {
		$field = trim($row[$y]);

		if ($field == "")
			$query = sprintf("%snull", $query);
		else if ($integer[$y] || $real[$y])
			$query = sprintf("%s%s", $query, $field);
		else if (!$date[$y])
			$query = sprintf("%s'%s'", $query,
			    str_replace("'", "''", $field));
		else if ($date[$y]) {
			$datefield = date("Y-m-d H:i:s", strtotime($field));
			$query = sprintf("%s'%s'", $query, $datefield);
		}

		$query = sprintf("%s%s", $query, $y == $num_columns - 1 ? ")" :
		    ", ");
	}

	$result = $db->exec($query);

	if (!$result)
		printf("%s\n", $query);
}

function
contains_char($str)
{
	$len = strlen($str);

	for ($x = 0; $x < $len; $x++) {
		if ($str[$x] >= 'a' && $str[$x] <= 'z')
			return true;
	
		if ($str[$x] >= 'A' && $str[$x] <= 'Z')
			return true;

		if ($str[$x] == "'" || $str[$x] == "\"" || $str[$x] == "," ||
		    $str[$x] == "/" || $str[$x] == ":")
			return true;
	}
	
	return false;
}
?>
