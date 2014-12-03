<?php
$db = "";
$user = "";
$password = "";

printf("Connecting...\n");

$conn = odbc_connect($db, $user, $password);

if (!$conn) {
	die("Could not connect to " . $db);
}

printf("Getting tables...\n");

$result = odbc_tables($conn);

if (!$result)
	die("Could not get tables.");
   
$tables = array();

while (odbc_fetch_row($result))
	array_push($tables, odbc_result($result, "TABLE_NAME") );
   
foreach ($tables as $table) {
	$handle = fopen($table . ".csv", "w");

	$result = odbc_columns($conn, "", "", $table);

	if (!$result) {
		printf("Could not get columns for: %s\n", $table);
		fclose($handle);
		continue;
	}

	$column_names = array();

	while ($row = odbc_fetch_array($result)) {
		$column_names[] = $row["COLUMN_NAME"];
	}

	$x = 0;

	foreach ($column_names as $column) {
		$result = odbc_exec($conn, "select " . $column . " from " .
		    $table;

		if (odbc_num_row($result) == 0)
			unset($column_names[$x]);

		$x++;
	}

	$column_names = array_values($column_names);

	fputcsv($handle, $column_names);

	$query = "select * from " . $table;

	$result = odbc_exec($conn, $query);

	if (!$result) {
		printf("Could not execute query: %s\n", $query);
		fclose($handle);
		continue;
	}

	while ($row = odbc_fetch_array($result)) {
		fputcsv($handle, $row);
	}

	fclose($handle);
}

odbc_close($conn);

?>
