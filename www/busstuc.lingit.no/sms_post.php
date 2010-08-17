<?PHP;
$service = 'RUTE';
$prog = "/usr/bin/ttpc" ;

$rcv = $_REQUEST["RCV"];
$snd = $_REQUEST["SND"];
$txt = preg_replace("/$service /i", "", $_REQUEST["TXT"], 1);

header('Content-type: text/plain; charset=iso-8859-1');

setlocale(LC_CTYPE, "iso-8859-1", "nb_NO.iso-8859-1");

$etxt = escapeshellarg($txt);

$cmd = "$prog --phone-number=$snd $etxt";

echo $cmd;
system($cmd);
?>
0
OK
