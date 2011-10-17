% Copyright (C) 2003, 2004 by Lingit AS

verbatimtex
\documentclass{article}
\begin{document}
etex;

input rboxes
input taocparrows
% Breadth of arrowheads (MetaPost default is 45)
ahangle := 35;
% Length of arrowheads (MetaPost default is 4bp)
%ahlength := 4;

numeric u;
u = 1cm;

beginfig(1);
% for temporary paths (might be unused)
path p[];
pair o, p, q, r;


% First, define and draw all the states
rboxit.s1(btex
  \begin{minipage}{3cm}
  \begin{center}
  \small
  \strut TUC Transfer Protocol \strut Daemon
  \end{center}
  \end{minipage}
  etex);

rboxit.s2(btex
  \begin{minipage}{3cm}
  \begin{center}
  \small
  \strut Request Handler
  \end{center}
  \end{minipage}
  etex);

circleit.s3(btex
  \begin{minipage}{1.5cm}
  \begin{center}
  \small
  \strut TUC-Thread Pool
  \end{center}
  \end{minipage}
  etex);

rboxit.s4(btex
  \begin{minipage}{3cm}
  \begin{center}
  \small
  \strut TUC Thread
  \end{center}
  \end{minipage}
  etex);

rboxit.s5(btex
  \begin{minipage}{3cm}
  \begin{center}
  \small
  \strut TUC
  \end{center}
  \end{minipage}
  etex);

rboxit.s6(btex
  \begin{minipage}{3cm}
  \begin{center}
  \small
  \strut TUC Alert Daemon
  \end{center}
  \end{minipage}
  etex);

circleit.s7(btex
  \begin{minipage}{1.5cm}
  \begin{center}
  \small
  \strut Socket
  \end{center}
  \end{minipage}
  etex);

boxit.s8(btex
  \begin{minipage}{1.5cm}
  \begin{center}
  \small
  \strut TAD Log
  \end{center}
  \end{minipage}
  etex);

% rboxit.s9(btex
%   \begin{minipage}{3cm}
%   \begin{center}
%   \small
%   \strut Semantic Network
%   \end{center}
%   \end{minipage}
%   etex);

s1.c = (0, 0);
s2.n = s1.s - (0, 1u);
s3.n = s2.s - (0, 1u);
s4.n = s3.s - (0, 1u);
s5.n = s4.s - (0, 1u);

%s5.e = s1.w - (1u, -.5u);
%s6.w = s3.e + (2u, 0);
r = (1.5u, 0) + .5[s2.e, s4.e];
s6.c = r;

s7.s = s1.n + (0, 1u);
%s8.e = s2.w - (1u, 0);
%s9.w = .5[s2.e,s3.e] + (1u, 0);

%s5.s = s6.n + (0, .5u);
%.5[s5.se, s6.ne] = s1.w - (1u, 0);

s8.w = s6.e + (1u, 0);

drawboxed(s1,s2,s3,s4,s5,s6,s7,s8);
% ,s6,s7,s8,s9

drawarrow s6.e..s8.w;
drawarrow s8.w..s6.e;
%drawarrow s7.w..s1.e;
%drawarrow s8.e..s2.w;
%drawarrow s9.w..s2.e;
%drawarrow s9.w..s3.e;

% Then, define and draw all the flows.
vardef cuta(suffix a, b) expr p =
  drawarrow p cutbefore bpath.a cutafter bpath.b;
  point .5 * length p of p
enddef;

%p = s1.n + (0, .5u);
%drawarrow p..s1.n;

label.lft(btex
  \begin{minipage}{3cm}
%  \begin{center}
  \flushright
  \small
  \strut Client Query
%  \end{center}
  \end{minipage}
  etex, cuta(s7, s1) s7.s..s1.n);

label.lft(btex
  \begin{minipage}{3cm}
%  \begin{center}
  \flushright
  \small
  \strut (Request, Client Connection)
%  \end{center}
  \end{minipage}
  etex, cuta(s1, s2) s1.s..s2.n);

label.rt(btex
  \begin{minipage}{3cm}
%  \begin{center}
  \flushleft
  \small
  \strut (Query, Result Container)
%  \end{center}
  \end{minipage}
  etex, cuta(s2, s3) s2.s..s3.n);

% label.lft(btex
%   \begin{minipage}{4cm}
%   \begin{center}
%   \small
%   \strut Logical Query 
%   \end{center}
%   \end{minipage}
%   etex, cuta(s3, s4) s3.s..s4.n);

label.rt(btex
  \begin{minipage}{3cm}
  \flushleft
%  \begin{center}
  \small
  \strut (Query, Result Container)
%  \end{center}
  \end{minipage}
  etex, cuta(s3, s4) s3.s..s4.n);
  %etex, cuta(s3, s4) s3.s - (.5u, 0)..s4.n - (.5u, 0));

label.lft(btex
  \begin{minipage}{3cm}
  \flushright
%  \begin{center}
  \small
  \strut Query
%  \end{center}
  \end{minipage}
  etex, cuta(s4, s5) s4.s - (.5u, 0)..s5.n - (.5u, 0));

label.rt(btex
  \begin{minipage}{3cm}
  \flushleft
%  \begin{center}
  \small
  \strut Answer
%  \end{center}
  \end{minipage}
  etex, cuta(s5, s4) s5.n + (.5u, 0)..s4.s + (.5u, 0));
  %etex, cuta(s3, s4) s3.s - (.5u, 0)..s4.n - (.5u, 0));

q = (-1.5u, 0) + .5[s2.w, s4.w];
%dotlabel.bot("q", q);

label.rt(btex
  \begin{minipage}{3cm}
  \flushleft
%  \begin{center}
  \small
  \strut Answer
%  \end{center}
  \end{minipage}
  etex, cuta(s4, s2) s4.w..q..s2.w);

%q = .5[s2.e, s4.e];

%q = s4.e + (.5u, 0);
%drawarrow s4.e..q;

path m;
m = (s2.e..r..s4.e);

label.rt(btex
  \begin{minipage}{4cm}
  %\begin{center}
  \flushleft
  \small
  \strut (Moment, ID, Message)
  %\end{center}
  \end{minipage}
  etex, cuta(s2, s6) subpath (0, 1) of m);

o = (xpart r, ypart s2.e) + (0, (ypart s2.e - ypart r));
%dotlabel.bot("o", o);

label.rt(btex
  \begin{minipage}{4cm}
  %\begin{center}
  \flushleft
  \small
  \strut (Answer [, ID])
  %\end{center}
  \end{minipage}
  etex, cuta(s2, s7) s2.e..o..s7.e);

% boxit.bb();
% bb.nw = s7.nw + (-.5u, .5u);
% bb.se = s9.se + (.5u, -1u);
% draw bpath.bb dashed evenly;

% label.top(btex
%   \begin{minipage}{4cm}
%   %\begin{center}
%   \flushright
%   \small
%   \strut Partly Domain Dependent
%   %\end{center}
%   \end{minipage}
%   etex, bb.s);

endfig;

end
