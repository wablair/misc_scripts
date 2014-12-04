#!/usr/bin/perl -W
# Create zip files of CVS projects and remove "CVS" dirs.

my $tmp_dir = "tmp";
my $output_dir = "code";
my $cvs_dir = "cvs";

my @module_list = ("");

chdir($tmp_dir);

my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) =
    localtime(time);

$year += 1900;

my $date = sprintf("%04d%02d%02d", $year, $mon + 1, $mday);

system("rm " . $output_dir . "/*.zip");

my $cvs_cmd = "cvs -Qd " . $cvs_dir . " get ";

foreach (@module_list) {
	$cvs_cmd .= $_ . " ";
}

system($cvs_cmd);

system("find . -name \"CVS\" -exec rm -dr \\{\\} CVS \\;");

foreach (@module_list) {
	system("7z a " . $output_dir . "/" . $_ . "_" . $date . ".zip " .
	    $_);
	system("rm -rf " . $_);
}
