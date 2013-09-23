#!/usr/bin/perl -w

# ---------- ---------- ---------- ---------- ---------- ----------
#  LAY-EL.NET PERL ROUTINE LIBRARY
#  	Script writton by WASHI
$lib_ver = "LAY-EL.NET PERL ROUTINE LIBRARY - ". '0.02';
$lib_root = "/home/1/washi/www/mylib";

# ---------- ---------- ---------- ---------- ---------- ----------
#  	INIT
#  		NEED->	$bodytag
#  			$cssfile
#  			$jno
$jcodefile = $lib_root ."/jcode.pl";
@jcode = ("EUC-JP", "Shift_JIS", "iso-2022-jp");
@jmark = ("euc", "sjis", "jis");
$body = $bodytag;
$css   = $cssfile if($cssfile);
$charset = $jcode[$jno];
$charmark = $jmark[$jno];

# ---------- ---------- ---------- ---------- ---------- ----------
#  	Filelock (flock)
#  		&flock(LOCKFILE);
#  		&Unflock(LOCKFILE);
sub flock {
	my $lock = $_[0];
	open(LOCK, "+<$lock");
	flock(LOCK, 2) || &err("ロック失敗");
	return 1;
}
sub Unflock{
	close(LOCK);
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	Filelock(rename)
#  		&fileLock(LOCKFILE);
#  		&fileUnLock(LOCKFILE);
sub fileLock{
    my $now = time();
    my $lock = $_[0];
    my $locking = "$lock.now";

    unless(-e $lock || -e $locking){ 
        open(F, ">".$lock) ;
        close(F);
    }

    if(-e $locking){
        if($now-(stat(_))[9]>60){
            utime($now, $now, $locking) and return;
        }
    }
    for($_=5; $_>=0; $_--){
        if(rename($lock, $locking)){
            utime($now, $now, $locking);
            return;
        }
        sleep 1 if $_;
    }
    &err("ロック失敗");
}

sub fileUnLock{
    my $lock = $_[0];
    rename("$lock.now", $lock);
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	File writing ROUTINE
#  		&writeLog(LOGFILE, %ARRAY);
sub writeLog{
	my $writefile = $_[0];
	my $po = $_[1];

	open(OUT, '>'.$writefile) || &err("writefile Not found.");
	while (my($name, $value) = each(%$po)) {
		print OUT $name ."<=>". $value ."\n";
	}
	close(OUT);

	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	File Reading ROUTINE
#  		&readLog(LOGFILE, %ARRAY);
sub readLog{
	my $readfile = $_[0];
	my $po = $_[1];

	open(IN, $readfile) || &err("readfile Not found.");
	foreach (<IN>){
		my($name, $value) = split("<=>", $_, 2);
		$value =~ s/\n$//;
		$po->{$name} = $value;
	}
	close(IN);

	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	File making ROUTINE
#  		&makeFile(FILENAME);
sub makeFile{
	my $makefile = $_[0];
	unless(-e $makefile){
		open(F, ">".$makefile);
		close(F);
	}
	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	Argument analysis ROUTINE
#  		&Read_Parse(%FORM, %COOKIE, $NON_TAG_CHECK);
sub Read_Parse {
    my ($form, $cookie, $tagcheck) = @_;
    my $query_string;

    if ( $ENV{'REQUEST_METHOD'} eq 'POST') {
	if ( $ENV{CONTENT_LENGTH} > 100000){
	    &err("データの量が多すぎます。発言を短くして下さい。");
	}
	read(STDIN, $query_string, $ENV{CONTENT_LENGTH});
    } else {
	$query_string = $ENV{QUERY_STRING};
    }

    foreach ( split(/&/, $query_string) ) {
	my ($name, $value) = split(/=/, $_);
	if ( ! defined $value ){ $value=""; }
	$value =~ tr/+/ /;
	$value =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C", hex($1))/eg;

	if ( defined &jcode::convert ){
	    &jcode::convert(\$value, $charmark);
	}
	
	unless($tagcheck){
		$value =~ s/&/&amp;/g;
		$value =~ s/\"/&quot;/g;
		$value =~ s/</&lt;/g;
		$value =~ s/>/&gt;/g;
	}

	$value =~ s/^[\r\n]+//;
	$value =~ s/[\r\n]+$//;

	if ( exists $form->{$name} ){
	    $form->{$name} .= ",$value";
	} else {
	    $form->{$name} = $value;
	}
    }

    if ( $ENV{HTTP_COOKIE} && $cookie ){
	foreach ( split(/\s*;\s*/,$ENV{HTTP_COOKIE}) ){
	    foreach ( split(/[\+,]/,$_) ){
		my ($name,$value) = split(/=/,$_);
		$value =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C", hex($1))/eg;
		&jcode::convert(\$value, $charmark);
		$cookie->{$name} = $value;
	    }
	}
    }
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	SET COOKIE Routine
#  		&setCookie(%COOKIE);
sub setCookie{
	my $po = $_[0];
	my $cookie_data;
	$cookie_data = "Set-Cookie: ";
	while (my($name, $value) = each(%$po)) {
		$cookie_data = join("+", $cookie_data, $name ."=". $value);
	}
	$cookie_data .= "; expires=Mon, 30 Dec 2020 23:59:59 GMT\n";
	print $cookie_data;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	Get Date Routine
#  		&getDate(TIME);
#		@dateFormat = (SEC, MIN, HOUR, DATE, MONTH, YEAR, DAY);
sub getDate {
	my @dateFormat = localtime($_[0]);
	my @week = ("Sun", "Mon", "Tue", "Wed", "Thu", "fri", "Sat");
	$dateFormat[6] = $week[$dateFormat[6]];
	$dateFormat[5] = sprintf("%02d", $dateFormat[5] + 1900);
	$dateFormat[4] = sprintf("%02d", $dateFormat[4] + 1);
	$dateFormat[3] = sprintf("%02d", $dateFormat[3]);
	$dateFormat[2] = sprintf("%02d", $dateFormat[2]);
	$dateFormat[1] = sprintf("%02d", $dateFormat[1]);
	$dateFormat[0] = sprintf("%02d", $dateFormat[0]);
	return @dateFormat;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	Auto link Routine
#  		&auto_link(COMMENT);
#
sub auto_link {
	$_[0] =~ s/([^=^\"]|^)(http\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#]+)/$1<a href=$2 target=_top>$2<\/a>/g;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	HTML HEADER Routine
#  		&header(TITLE, FORMAT);
#  			FORMAT=>	0...Standard
#  					1...OUTPUT
sub header {
	my ($title, $format) = @_;
	my $HTML_HEADER;
	unless($format){
		$HTML_HEADER .= "Content-Type: text/html; charset=". $charset ."\n";
		$HTML_HEADER .= "Content-Language: ja\n\n";
	}
	$HTML_HEADER .= '<HTML LANG="ja" DIR="ltr">'."\n";
	$HTML_HEADER .= '<HEAD>'."\n";
	$HTML_HEADER .= '<META HTTP-EQUIV="Content-Script-Type" CONTENT="text/javascript">'."\n";
	$HTML_HEADER .= '<META HTTP-EQUIV="Content-Style-Type" CONTENT="text/css">'."\n";
	if($css){
		$HTML_HEADER .= '<LINK REL="stylesheet" TYPE="text/css" HREF="'. $css .'">' . "\n";
	}
	$HTML_HEADER .= '<TITLE>'. $title .'</TITLE>'."\n";
	$HTML_HEADER .= '</HEAD>'."\n";
	$HTML_HEADER .= $body ."\n";

	return $HTML_HEADER;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	HTML FOOTER Routine
#  		&footer();
sub footer {
	my $HTML_FOOTER = "</BODY>\n</HTML>\n";
	return $HTML_FOOTER;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	ERROR
#  		&errAndUL(MESSAGE);
#  		&err(MESSAGE);
sub errAndUL{
	&fileUnLock();		#ファイルロック解除
	&err($_[0]);
}

sub err
{
	my $mes = $_[0];
	print &header("Error");
	print <<"_EOF_";
<P CLASS="ber">
[My library] / error
</P>
<HR>
<DIV ID="title_top">
<H3>error</H3>
</DIV>

<P>$mes</P>
_EOF_
	print &footer();
	exit;
}

1; #return true
