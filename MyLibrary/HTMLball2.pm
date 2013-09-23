#!/usr/bin/perl -w

package HTMLball;

my $TITLE;
my $BODY;
my $CSS;
my $AUTHOR;
my $CHARSET;

sub new{
	my $pkg = shift;
	$TITLE = shift;
	$BODY = "<BODY>";
	$CSS = "";
	$CHARSET = "euc-jp";
	bless {},$pkg;
}
sub contentType{
	my $pkg = shift;
	my $print = "Content-type: text/html; charset: $CHARSET\n";
	$print .= "Content-Language: ja\n";
	$print .= "\n";
	return $print;
}
sub header{
	my $pkg = shift;
	my $HTML;
	my $tmpTitle = shift || $TITLE;
	my $reload = shift;

	$HTML = qq(<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n);
	$HTML .= qq(<HTML LANG="ja" DIR="ltr">\n);
	$HTML .= qq(<HEAD>\n);
	$HTML .= qq(<META HTTP-EQUIV="REFRESH" CONTENT="$reload">\n) if($reload);
	$HTML .= qq(<META NAME="Author" CONTENT="$AUTHOR">\n) if($AUTHOR);
	$HTML .= qq(<meta http-equiv="Content-Type" content="text/html; charset=$CHARSET">\n) if($CHARSET);
	
	$HTML .= qq(<LINK REL="stylesheet" TYPE="text/css" HREF="$CSS">\n) if($CSS);
	$HTML .= qq(<TITLE>$tmpTitle</TITLE>\n);
	$HTML .= qq(</HEAD>\n);
	return $HTML;
}

sub frame2rows{
	my $pkg = shift;
	my $topframe = '25%';
	my $bottomframe = '75%';
	my $topurl = shift;
	my $bottomurl = shift;
	my $topname = 'menu';
	my $bottomname = 'main';
	my $NOFRAMESBODY;
	my $HTML = "";

	$NOFRAMESBODY =<<"_EOT_";
<BODY background="./back03.gif">
　あなたのブラウザでは-Gathering chat-フレーム版をご利用することはできません。<BR>
　<A HREF="./chat.cgi?chat=2&mode=1">こちら</A>から通常版へお戻り下さい。
</BODY>
_EOT_

	$HTML .= qq(<FRAMESET ROWS="$topframe,$bottomframe">\n);
	$HTML .= qq(<FRAME SRC="$topurl" NAME="$topname">\n);
	$HTML .= qq(<FRAME SRC="$bottomurl" NAME="$bottomname">\n);
	$HTML .= qq(<NOFRAMES>\n);
	$HTML .= qq($NOFRAMESBODY);
	$HTML .= qq(</NOFRAMES>\n);
	$HTML .= qq(</FRAMESET>\n);
	
	return $HTML;
}

sub setTitle{
	my $pkg = shift;
	$TITLE = shift;
}
sub setAuthor{
	my $pkg = shift;
	$AUTHOR = shift;
}
sub setCss{
	my $pkg = shift;
	$CSS = shift;
}
sub setCharset{
	my $pkg = shift;
	$CHARSET = shift;
}
sub setBody{
	my $pkg = shift;
	$BODY = shift;
}
sub getBody{
	my $pkg = shift;
	my $tmpbody = shift || $BODY;
	return $tmpbody;
}
sub getBodyln{
	my $pkg = shift;
	return $pkg->getBody(shift)."\n";
}
sub footer{
	my $pkg = shift;
	my $ver = shift;
	my $HTML = "";
	if($ver){
		$HTML .= qq(<HR>\n);
		$HTML .= qq(<DIV ALIGN="right">\n);
		$HTML .= qq(<FONT SIZE="2">$ver</FONT>\n);
		$HTML .= qq(</DIV>\n);
	}
	$HTML .= qq(</BODY>\n);
	$HTML .= qq(</HTML>\n);
	return $HTML;
}

sub err{
	my $pkg = shift;
	my $errmsg = shift;
	print $pkg->contentType;
	print $pkg->header("Exec ERROR");
	print $pkg->getBodyln;
	print qq(<H1>Exec ERROR</H1>\n);
	print qq(<P>$errmsg</P>\n);
	print $pkg->footer;
	exit(1);
}

1;
