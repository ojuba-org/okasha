%_r.title="Fav Colors :: Bottle Test"

%include bottle-header title="Fav Color"

%if colors:
%for c in colors:
    <p>I like <strong>{{c}}</strong> apple</p>
%end
%else:
    <p>no color is provided</p>
%end
  <p>for more details on this template visit <a href="http://bottle.paws.de/docs/dev/stpl.html">Bottle Docs</a></p>

%rebase bottle-base

