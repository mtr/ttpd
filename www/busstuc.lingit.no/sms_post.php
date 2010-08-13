<?PHP;
$prog = "/usr/bin/ttpc --sms";
$service = 'ATB'
$rcv = $_REQUEST["RCV"];
$snd = $_REQUEST["SND"];
$txt = $_REQUEST["TXT"];

header('Content-type: text/plain; charset=utf-8');

setlocale(LC_CTYPE, "UTF8", "nb_NO.UTF-8");

$txt = escapeshellarg($txt);

system("$prog --phone-number=$snd --service-name=$service '$txt'");

?>
