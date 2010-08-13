<?PHP;
$service = 'ATB';
$prog = "/usr/bin/ttpc --service-name=$service";

$rcv = $_REQUEST["RCV"];
$snd = $_REQUEST["SND"];
$txt = $_REQUEST["TXT"];

header('Content-type: text/plain; charset=iso-8859-1');

setlocale(LC_CTYPE, "iso-8859-1", "nb_NO.iso-8859-1");

$etxt = escapeshellarg($txt);

$cmd = "$prog --phone-number=$snd $etxt";

echo $cmd;
system($cmd);
?>
0
OK
