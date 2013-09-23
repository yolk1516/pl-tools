#!/usr/bin/perl -w

# Dream Cup サーバ常駐プログラム
# 設定用 インクルードファイル

# 常駐プログラム全般の配置場所
$ROOT_DIR = "/home/two/gameServer/";

# gameServer本体の場所
$DC_SERVER_NAME = "gameServer";
$DC_SERVER = $ROOT_DIR.$DC_SERVER_NAME;

# 常駐→制御の処理のやりとりを扱うファイル
$ACT_ROOT_FILE = $ROOT_DIR."actRoot.dat";
# 常駐←制御の処理のやりとりを扱うファイル
$ACT_EXEC_FILE = $ROOT_DIR."actExec.dat";
# 作業記録を書き出すファイル
$LOG_FILE = $ROOT_DIR."work.log";

@DCS_INI_DIR_STR = (
	"gameServer0",
	"gameServer1",
	"gameServer2",
	"gameServer3",
	"gameServer4"
);

# gameServer.iniの配置場所
@DCS_INI_DIR = (
	"/home/two/$DCS_INI_DIR_STR[0]/",
	"/home/two/$DCS_INI_DIR_STR[1]/",
	"/home/two/$DCS_INI_DIR_STR[2]/",
	"/home/two/$DCS_INI_DIR_STR[3]/",
	"/home/two/$DCS_INI_DIR_STR[4]/"
);
# 各ファイルハンドル
@DCS_FH = (
	DCS0,
	DCS1,
	DCS2,
	DCS3,
	DCS4
);
# gameServer.ini
$DCS_INI = "gameServer.ini";

# 常駐プログラムの場所
$ROOT_FILE = $ROOT_DIR."procserver.pl";
# 制御プログラムの場所
$EXEC_FILE = "";


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

1;
