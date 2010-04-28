<?PHP
$topics = array ("today" => "Today",
		 "this_week" => "This Week",
		 "last_week" => "Last Week",
                 "last_52_weeks" => "Last 52 Weeks",
		 );

function select_topic()
{
  $t = $_REQUEST["t"];
  
  if ($t != '')
    {
      return $t;
    }
  else
    {
      return 'today';
    }
}

$topic = select_topic();
$ftopic = $topics[$topic];
?>
<!doctype html public "-//W3C//DTD HTML 4.0//EN">
<html>
<head>

<link rel="Shortcut Icon" href="http://www.ranang.org/graphics/r-icon.png">
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<meta name="author" content="Martin Thorsen Ranang">
<meta name="copyright" content="&copy; 2004 Martin Thorsen Ranang">
<meta name="keywords" content="ranang,statistics,developer">

<title>Statistics --> <? echo $ftopic; ?></title>
</head>
<body bgcolor="#ffffff" text="#000000" link="#0080ff" vlink="#0040ff">

  <table colspan=3 width="100%" border=0>

  <!-- The menus in the middle, including the topic area. -->
  <tr align="left" valign="top">
  <td bgcolor="#ffffff" align="left" width="25%">
  <h1>Menu</h1>

<ul>
<?
while (list ($k, $v) = each ($topics))
  {
    echo '<li><a href="./?l='; echo $lan;
    echo '&t=', urlencode ($k), "\">$v</a></li>\n";
  }
?>
<li><a href="/~tore/smstuc/">SMSTUC</a></li>
</ul>
</td>
<td bgcolor="#ffffff" width=4>&nbsp;</td>
<td bgcolor="#ffffff" width="85%" align="left">
<?PHP
if ($topic == 'last_52_weeks')
  {
    printf('<h1>%s: Weekly</h1><p><img src="graphics/%s_weeks.png" border=1>',
	   $ftopic, $topic);
  }
 else
   {
     printf('<h1>%s: Hourly</h1><p><img src="graphics/%s_hours.png" border=1>',
	    $ftopic, $topic);
   }
?>

<p>Below, you can see the per-day total(s) for the same period that the
above graph shows.  You can also get the exact 
<?PHP
if ($topic != 'last_52_weeks')
  {
    printf('<a href="%s_hours.txt">hourly', $topic);
  }
 else
   {
     printf('<a href="%s_weeks.txt">weekly', $topic);
   }
?> information in a plain-text file</a>.

<?PHP
if ($topic != 'today' && $topic != 'last_52_weeks')
  {
    printf('<h1>%s: Daily</h1><p><img src="graphics/%s_days.png" border=1>',
    $ftopic, $topic);
  }
?>

<p>
<pre><?PHP
if ($topic != 'last_52_weeks')
  {
    include("$topic"."_days.txt");
  }
?></pre>

<P>
This information was last updated
<?PHP
if ($topic != 'last_52_weeks')
  {
    echo date("F d Y H:i:s.", filectime("$topic"."_days.txt"));
  }
 else
   {
     echo date("F d Y H:i:s.", filectime("$topic"."_weeks.txt"));
   }
?>

</td>
</tr></table>

<hr>
<address>
Developed by Martin Thorsen Ranang, 2004--2006.
</address>

</body>
</html>
