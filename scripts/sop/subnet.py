import colors
sub = kwargs["node"]
for p in sub.parms():
	p.hide(1)

sub.setColor( hou.Color( colors.subnet ) )
