<?PHP;
$prog = "/usr/bin/ttpc --json";
#$quest = $_POST["question"];
$quest = $_GET["question"];

if ($quest)
  {
    # Tegn som skal fjærnes fra input.
    $removes = array("'", '"', '\\', '`', '´', '[', ']');

    # "Snillifiserer" input:
    #
    # - substr kutter all input som kommer etter tegn nummer 1024.
    # - strip_tags fjerner eventuelle HTML (eller XML)-tags.
    # - str_replace fjerner tegnene som ramses opp ovenfor.
    # - trim fjerner eventuelle white-space i starten og slutten av strengen.
    $e = trim(str_replace($removes, "", strip_tags(substr($quest, 0, 1024))));

    # Dersom strengen nå inneholder "ekle" tegn, vil vi ikke behandle den.
    if (! ereg("^[*a-zA-ZæøåÆØÅéÉöÖäÄ0-9,. ?!@:+-/]*$", $e))
      {
	unset($e);
      }
  }

header('Content-type: text/javascript;charset=utf-8');
header('Cache-Control: no-cache, must-revalidate');
header('Access-Control-Allow-Origin: null');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
#header('Content-type: text/x-json;charset=utf-8');
#header('Content-type: text/xml;');


if ($e)
  {
    # Dersom det mangler et '.' i slutten av setningen, legg det til.
    if ($e && (! ereg("[.?!]$", $e)))
      {
	$e = $e.".";
      }
    
    setlocale(LC_CTYPE, "UTF8", "nb_NO.UTF-8");
    $e = escapeshellarg($e);

    print_r($_GET['callback'].'(');
    system("$prog $e");
    print(');');
  }
 else
   {
    print_r($_GET['callback'].'(');
    print '{"error": "No question supplied."}';
    print(');');
   }
  

?>
