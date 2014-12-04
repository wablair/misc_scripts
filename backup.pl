#!/usr/bin/perl
# Script to backup specified directories and MySQL dump to USB harddrive and
# tarsnap.

my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) =
    localtime(time);

$year += 1900;
$mon += 1;

@dir_list = ("/etc", "/var/www");

my @month_abbr = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);

$datestring = sprintf("%04d%02d%02d", $year, $mon,  $mday);

system("umount -f /mnt");

system("mount /dev/sd1a /mnt") == 0
	or die("could not mount drive: $?");

system("mkdir /mnt/" . $datestring);

$path = "/mnt/" . $datestring . "/";

foreach $dir (@dir_list) {
	system("tar cfz " . $path . $dir .".tar.gz " . $dir);
}

system("/usr/local/bin/mysqldump -hlocalhost -u -p" .
    "--skip-lock-tables --all-databases > " .  $path .  "mysql.dump");

$tarsnap_command = "/usr/local/bin/tarsnap -cf " . $datestring . " " . $path .
    "mysql.dump ";

foreach $dir (@dir_list) {
	$tarsnap_command .= $dir . " ";
}

system($tarsnap_command);

system("cd " . $path . " && tar cfz mysql.dump.tar.gz mysql.dump && " .
    "rm mysql.dump");

system("umount /mnt");
