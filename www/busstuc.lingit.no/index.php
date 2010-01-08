<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">

<html> <head>
<title>SMSTUC</title>
<META  name="description" 
content="A natural language system capable of answering questions about bus
departures in Trondheim, Norway. Pose you questions here as complete
english sentences.">

<META  name="keywords" content="natural language processing, NLP, Bustuc,
Tuc, The Understanding Computer, Sicstus prolog, artificial
intelligence, parsing, automated reasoning, knowledge based systems,
expert systems">

</head>

<FRAMESET rows="320,*">
  <frame src="bust.php" name="smstuc" 
   frameborder="0" marginwidth="10" marginheight="10">
  <frame src="instruksjoner.php" name="ans"
   frameborder="0" marginwidth="10" marginheight="30">
</FRAMESET> 

<noframes>
<body <?PHP include('body_style.inc'); ?> >

<h2>BussTUC - Bussruteorakelet</h2>

<a href="instruksjoner.php" target="ans">Nyttig å vite før du stiller
spørsmål</a><p>
<a href="ombustuc.php" target="ans">Om Busstuc</a><p>
<a href="egenskaper.php" target="ans">Egenskaper ved Busstuc</a>
<img hspace=10 src="../logo/ntnu-logo1.gif">
<a href="../bustuc" target=_top>[English version]</a><p>
<i>Versjon av 26.2.02 </i>

<?PHP include("tucq.inc"); ?>

<hr>
<address>
<A Href="mailto:tagore@idi.ntnu.no"> tagore@idi.ntnu.no</A>
</address>
<!-- hhmts start -->
Last modified: Mon Aug 23 20:11:52 CEST 2004
<!-- hhmts end -->
</body>

</noframes>
</html>
