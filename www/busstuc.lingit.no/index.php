<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">

<html> 
  <head>
    <title>SMSTUC</title>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <meta name="description" 
	  content="A natural language system capable of answering
		   questions about bus departures in Trondheim,
		   Norway. Pose your questions here as complete
		   English sentences.">

    <meta name="keywords" content="natural language processing, NLP, Bustuc,
				   TUC, The Understanding Computer,
				   SICStus Prolog, artificial
				   intelligence, parsing, automated
				   reasoning, knowledge based systems,
				   expert systems">

</head>

<frameset rows="320,*">
  <frame src="bust.php" name="smstuc" 
   frameborder="0" marginwidth="10" marginheight="10">
  <frame src="instruksjoner.php" name="ans"
   frameborder="0" marginwidth="10" marginheight="30">
<noframes>
<body <?PHP include('body_style.inc'); ?> >

<h2>BussTUC - Bussruteorakelet</h2>

<a href="instruksjoner.php" target="ans">Nyttig å vite før du stiller
spørsmål</a><p>
<a href="ombustuc.php" target="ans">Om Busstuc</a><p>
<a href="egenskaper.php" target="ans">Egenskaper ved Busstuc</a>
<img hspace=10 src="../logo/ntnu-logo1.gif" alt="NTNU-logo">
<a href="../bustuc" target=_top>[English version]</a><p>
<i>Versjon av 26.2.02 </i>

<?PHP include("tucq.inc"); ?>

<hr>
<address>
<a href="mailto:tagore@idi.ntnu.no"> tagore@idi.ntnu.no</a>
</address>
<!-- hhmts start -->
Last modified: Mon Aug 23 20:11:52 CEST 2004
<!-- hhmts end -->
</body>

</noframes>
</frameset> 

</html>
