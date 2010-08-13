<?PHP;
$service = 'ATB';
$prog = "/usr/bin/ttpc --service-name=$service";

$rcv = $_REQUEST["RCV"];
$snd = $_REQUEST["SND"];
$txt = $_REQUEST["TXT"];

header('Content-type: text/plain; charset=utf-8');

setlocale(LC_CTYPE, "UTF8", "nb_NO.UTF-8");

$etxt = escapeshellarg($txt);

$cmd = "$prog --phone-number=$snd $etxt";

echo $cmd;
system($cmd);
?>
0
OK
