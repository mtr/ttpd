% Arrowhead Modifications for TAOCP
ahangle := 65;
ahlength := 6;
vardef arrowhead expr p =
  save q, e, f, g; path q; pair e; pair f; pair g;
  e = point length p of p;
  q = gobble(p shifted -e cutafter makepath(pencircle scaled 2ahlength))
    cuttings;
  f = point 0 of (q rotated 0.5ahangle) shifted e;
  g = point length q of (reverse q rotated -0.5ahangle) shifted e;
  f .. {dir (angle direction length q of (q rotated 0.5ahangle) - 0.3ahangle)}e
    & e{dir (angle direction 0 of ((reverse q) rotated -0.5ahangle)+0.3ahangle)} .. g
enddef;

def _finarr text t =
  draw _apth t;
  draw arrowhead _apth t        % do not fill
enddef;

def _findarr text t =
  draw _apth t;
  draw arrowhead _apth withpen currentpen t;
  draw arrowhead reverse _apth withpen currentpen t
enddef;


