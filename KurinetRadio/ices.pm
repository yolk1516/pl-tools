# At least ices_get_next must be defined. And, like all perl modules, it
# must return 1 at the end.

# Function called to initialize your python environment.
# Should return 1 if ok, and 0 if something went wrong.
sub ices_init {
	print "Perl subsystem Initializing:\n";
	return 1;
}

# Function called to shutdown your python enviroment.
# Return 1 if ok, 0 if something went wrong.
sub ices_shutdown {
	my $DB_DRIVER = 'mysql';
	my $DB_NAME = 'ices_db';
	my $DB_HOSTNAME = 'localhost';
	my $DB_USER = 'root';
	my $DB_PASSWORD = 'kurimura';
	
	use DBI;
#	use Jcode;
#	use MP3::Tag;

	$dsn = "DBI:$DB_DRIVER:database=$DB_NAME:host=$DB_HOSTNAME";
	my $dbh = DBI->connect($dsn,$DB_USER,$DB_PASSWORD)|| return 0;

	my $kankyo = DB_kankyo_load($dbh);

	# 今までかけてた曲を次回起動時に再生する
	DB_excute($dbh, "update playlist SET played=1 where no=$kankyo->{'playnum'}");
	$tmp = $kankyo->{'playnum'} - 1;
	DB_excute($dbh,"update kankyo SET num=$tmp where name='playnum'");
	
	print "Perl subsystem shutting down:\n";
}

# Function called to get the next filename to stream. 
# Should return a string.
sub ices_get_next {
	my $DB_DRIVER = 'mysql';
	my $DB_NAME = 'ices_db';
	my $DB_HOSTNAME = 'localhost';
	my $DB_USER = 'root';
	my $DB_PASSWORD = 'kurimura';
	
	use DBI;
#	use Jcode;
#	use MP3::Tag;

#	print "Perl subsystem quering for new track:\n";

	$dsn = "DBI:$DB_DRIVER:database=$DB_NAME:host=$DB_HOSTNAME";
	my $dbh = DBI->connect($dsn,$DB_USER,$DB_PASSWORD)|| return 0;

	my $kankyo = DB_kankyo_load($dbh);

	my $source;
#	print $kankyo->{'playmode'};
	
	if($kankyo->{'playmode'} == 6){		# 1曲選択モード
		my $DATA = DB_data_load($dbh, $kankyo->{'order'}, 2);
		$source = $DATA->{'filepath'};
		# mysqlデータ環境を更新する
		DB_excute($dbh,"update kankyo SET num=$kankyo->{'backmode'} where name='playmode'");
		DB_excute($dbh,"update kankyo SET num=NULL where name='backmode'");
		DB_excute($dbh,"insert into record (id) values ($kankyo->{'order'})");
	}elsif($kankyo->{'playmode'} == 7){	# 随時追加再生モード
		my @musiclist;
		unless(search_mp3(\@musiclist, 4)){
			print "opendir failed.\n";
			return 0;
		}
		print @musiclist."\n";
		if(@musiclist<=0){
			return 0;
		}
		for(@musiclist){
			srand;
			my $index = rand @musiclist;
			if(DB_rireki_check($dbh, $musiclist[$index], 10, @musiclist)){
				my $filepath = $musiclist[$index];
				$filepath =~ s/'/-QQ-/g; #'
				DB_excute($dbh,"insert into rireki (filepath) values ('$filepath')");
				$source = $musiclist[$index];
				last;
			}
			print $source;
		}
	}else{								# その他モード
		if($kankyo->{'artist'} || $kankyo->{'mname'}){
			DB_excute($dbh,"update kankyo SET num=NULL where name='order'");
			DB_excute($dbh,"update kankyo SET value=NULL where name='mname'");
		}
		$source = DB_music_load($dbh,$kankyo);
	}

	$dbh->disconnect();
	$source =~ s/-QQ-/'/g;  #'
	return $source;
}

# If defined, the return value is used for title streaming (metadata)
sub ices_get_metadata {
	my $DB_DRIVER = 'mysql';
	my $DB_NAME = 'ices_db';
	my $DB_HOSTNAME = 'localhost';
	my $DB_USER = 'root';
	my $DB_PASSWORD = 'kurimura';
	
	use DBI;
	use Jcode;
	use MP3::Tag;
	
	my $j = Jcode->new();
	
	$dsn = "DBI:$DB_DRIVER:database=$DB_NAME:host=$DB_HOSTNAME";
	my $dbh = DBI->connect($dsn,$DB_USER,$DB_PASSWORD)|| return "Unknown";

	my $kankyo = DB_kankyo_load($dbh);

	my $id;
	my $DATA;
	
	if($kankyo->{'playmode'} == 7){
		my $path = rireki_first();
		$DATA = get_tag($path);
		$DATA->{'artist'} = $DATA->{TPE1};
		$DATA->{'musicname'} = $DATA->{TIT2};
		$DATA{'filapath'} = $path;
		$path =~ s/(\/.+)*\/([^\/]+\.mp3)$/$+/;
		$DATA->{'filename'} = $path;
	}
	
	if($kankyo->{'mname'} && $kankyo->{'playmode'} != 7){
		$DATA = DB_data_load($dbh, $kankyo->{'order'}, 2);
	}elsif($kankyo->{'playmode'} != 7){
		$DATA = DB_data_load($dbh, $kankyo->{'playnum'}, 1);
	}
	my $restring;
	if($DATA->{'artist'} && $DATA->{'musicname'}){
		$j->set($DATA->{'artist'});
		$DATA->{'artist'} = $j->sjis;
		$j->set($DATA->{'musicname'});
		$DATA->{'musicname'} = $j->sjis;
		$restring = "$DATA->{'artist'} - $DATA->{'musicname'}";
	}elsif($DATA->{'artist'}){
		$j->set($DATA->{'artist'});
		$DATA->{'artist'} = $j->sjis;
		my $filename = $DATA->{'filename'};
		$j->set($filename);
		$filename = $j->sjis;
		$filename =~ s/\.mp3//g;
		$restring = "$DATA->{'artist'} - $filename";
	}elsif($DATA->{'musicname'}){
		$j->set($DATA->{'musicname'});
		$DATA->{'musicname'} = $j->sjis;
		$restring = "Unknown - $DATA->{'musicname'}";
	}elsif($DATA->{'filename'}){
		my $filename = $DATA->{'filename'};
		$j->set($filename);
		$filename = $j->sjis;
		$filename =~ s/\.mp3//g;
		$restring = $filename;
	}else{
		$restring = "Unknown";
	}
	
	$dbh->disconnect();
	
	$restring =~ s/-QQ-/'/g;  #'
	return $restring;
}

# Function used to put the current line number of
# the playlist in the cue file. If you don't care
# about cue files, just return any integer.
sub ices_get_lineno {
	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_rireki_first
#  		
sub DB_rireki_first{
	my $dbh = $_[0];

	my $sth = $dbh->prepare("select filepath from rireki order by no DESC limit 1"); 
	my $result=$sth->execute(); 
	unless($result){
		print $DBI::errstr;
		return 0; 
	}
	my ($no,$filepath); 
	$sth->bind_col(1,\$no); 
	$sth->bind_col(2,\$filepath); 

	while($sth->fetch()){
		$filepath =~ s/'/-QQ-/g; #'
		return $filepath;
	}
	return 0;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_rireki_check
#  		
sub DB_rireki_check{
	my $dbh = $_[0];
	my $path = $_[1];
	my $num = $_[2];
	my $max = $_[3];

	if($num >= $max){
		return 1;
	}

	my $string = "select filepath from rireki order by no DESC limit $num";
	my $sth = $dbh->prepare($string); 
	my $result=$sth->execute(); 
	unless($result){
		print $DBI::errstr;
		return 1; 
	}
	my ($no,$filepath); 
	$sth->bind_col(1,\$no); 
	$sth->bind_col(2,\$filepath); 

	while($sth->fetch()){
		$filepath =~ s/-QQ-/'/g; #'
		if($filepath eq $path){
			return 0;
		}
	}
	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	search_mp3
#  		
sub search_mp3{
	my $array = $_[0];
	my $HANDLE = $_[1];
	my $SEARCH_DIR = '/usr/local/pub/g/mp3/mp3_radio/'.$_[2];
	print $HANDLE."\n";
	opendir($HANDLE, $SEARCH_DIR) || return 0;
	while (defined(my $dir = readdir($HANDLE))) {
		print $SEARCH_DIR.$dir."\n";
		if($dir =~ /\.mp3$/){
			push(@$array, $SEARCH_DIR.$dir);
		}elsif(-d $SEARCH_DIR.$dir && $dir ne '..' && $dir ne '.'){
			$HANDLE++;
			unless(search_mp3($array, $HANDLE, $dir.'/')){
				return 0;
			}
			$HANDLE--;
		}
	}
 	closedir($HANDLE);
	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_excute
#  		
sub DB_excute{
	my $dbh = $_[0];
	my $statement = $_[1];
	
	my $result=$dbh->do($statement);
	unless($result){
		print $DBI::errstr;
		return 0; 
	}
	return $result;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_data_load
#  		
sub DB_data_load{
	my $dbh = $_[0];
	my $no = $_[1];
	my $mode = $_[2];
	my $DATA = {};

	my $string;
	if($mode == 2){
		$string = "select id,artist,musicname,filename,filepath from musiclist where id=$no limit 1";
	}else{
		$string = "select no,artist,musicname,filename,filepath from playlist left join musiclist on playlist.id=musiclist.id where playlist.no=$no limit 1";
	}
	my $sth = $dbh->prepare($string); 
	my $result=$sth->execute(); 
	unless($result){
		print $DBI::errstr;
		return 0; 
	}
	my ($id,$artist,$musicname,$filename,$filepath); 
	$sth->bind_col(1,\$no); 
	$sth->bind_col(2,\$artist); 
	$sth->bind_col(3,\$musicname);
	$sth->bind_col(4,\$filename);
	$sth->bind_col(5,\$filepath); 

	while($sth->fetch()){
		$DATA->{'no'} = $no;
		$DATA->{'artist'} = $artist;
		$DATA->{'musicname'} = $musicname;
		$DATA->{'filename'} = $filename;
		$DATA->{'filepath'} = $filepath;
	}
	return $DATA;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_music_load
#  		
sub DB_music_load{
	my $dbh = $_[0];
	my $kankyo = $_[1];
	my $playmode = $kankyo->{'playmode'};
	my $playno = $kankyo->{'playnum'} + 1;
	my $sth;
	my $sth2;
	my $reset = 0;
	my $count = 1;

	if($playmode >= 1 && $playmode <= 4){		# 全部イッチャウヨ(random)
												# 全部イッチャウヨ(random)radio
												# プレイリスト(random)
												# プレイリスト(random)radio
		$sth = $dbh->prepare("select no,filepath,playlist.id from playlist left join musiclist on playlist.id=musiclist.id where playlist.played=1 order by rand() limit 1");
		$sth2 = $dbh->prepare("select no,filepath,playlist.id from playlist left join musiclist on playlist.id=musiclist.id order by rand() limit 1");
	}elsif($playmode == 5){						# プレイリスト
		if($playno > $kankyo->{'playmax'}){
			$playno = 1;
		}
		$sth = $dbh->prepare("select no,filepath,playlist.id from playlist left join musiclist on playlist.id=musiclist.id where (playlist.played=1) && (no >= $playno) limit 1"); 
		$sth2 = $dbh->prepare("select no,filepath,playlist.id from playlist left join musiclist on playlist.id=musiclist.id where no=$count");
	}else{
		return 0;
	}
	# mysqlデータからファイルパスを抽出
	my $result=$sth->execute();
	if($sth->rows == 0){
		$result=$sth2->execute();
		$sth = $sth2;
		$reset++;
	}
	unless($result){ 
		print $DBI::errstr;
		return 0; 
	}
	my ($no,$path,$id); 
	$sth->bind_col(1,\$tmpno); 
	$sth->bind_col(2,\$tmppath); 
	$sth->bind_col(3,\$id); 
	my $no;
	my $path;
	while($sth->fetch()){ 
		$no = $tmpno;
		$path = $tmppath;
		last;
	}
	
	# mysqlデータにプレイ済と記述する
	if($reset > 0){
		DB_excute($dbh, "update playlist SET played=1 where no<>$no");
	}else{
		DB_excute($dbh, "update playlist SET played=2 where no=$no");
	}
	
	# mysqlデータ環境を更新する
	DB_excute($dbh,"update kankyo SET num=$no where name='playnum'");
	DB_excute($dbh,"insert into record (id) values ($id)");
	
	return $path;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_kankyo_load
#  		
sub DB_kankyo_load{
	my $dbh = $_[0];
	my $kankyo = {};

	my $sth = $dbh->prepare("select name,num,value,stamp from kankyo"); 
	my $result=$sth->execute(); 
	unless($result){ 
		return $DBI::errstr; 
	}
	my ($name,$num,$value,$stamp); 
	$sth->bind_col(1,\$name); 
	$sth->bind_col(2,\$num); 
	$sth->bind_col(3,\$value);
	$sth->bind_col(4,\$stamp); 

	while($sth->fetch()){ 
		if($value ne ''){
			$kankyo->{$name} = $value;
		}else{
			$kankyo->{$name} = $num;
		}
	}
	return $kankyo;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	get_tag
#  		
sub get_tag{
	my $file = $_[0];
	my $mp3 = MP3::Tag->new($file);

	return undef unless defined $mp3;

	$mp3->get_tags();

	my $tag = {};
	if (exists $mp3->{ID3v2}){
		my $id3v2 = $mp3->{ID3v2};
		my $frames = $id3v2->supported_frames();
		while (my ($fname, $longname) = each %$frames){
			# only grab the frames we know
#			next unless exists $supported_frames{$fname};
#			print "exists ID3v2\n";
			$tag->{$fname} = $id3v2->get_frame($fname);
			delete $tag->{$fname} unless defined $tag->{$fname};
			$tag->{$fname} = $tag->{$fname}->{Text} if $fname eq 'COMM';
			$tag->{$fname} = $tag->{$fname}->{URL} if $fname eq 'WXXX';
			$tag->{$fname} = '' unless defined $tag->{$fname};
			
#			print "$fname=$tag->{$fname}\n";
		}
	}
	elsif (exists $mp3->{ID3v1}){
		warn "No ID3 v2 TAG info in $file, using the v1 tag";
		my $id3v1 = $mp3->{ID3v1};
		$tag->{COMM} = $id3v1->comment();
		$tag->{TIT2} = $id3v1->song();
		$tag->{TPE1} = $id3v1->artist();
		$tag->{TALB} = $id3v1->album();
		$tag->{TYER} = $id3v1->year();
		$tag->{TRCK} = $id3v1->track();
		$tag->{TIT1} = $id3v1->genre();
	}
	else{
		warn "No ID3 TAG info in $file, creating it";
		$tag = {
			TIT2 => '',
			TPE1 => '',
			TALB => '',
			TYER => 9999,
			COMM => '',
		};
	}
	return $tag;
}

return 1;